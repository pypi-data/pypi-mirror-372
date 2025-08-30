#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import getpass
import os
import pwd
import re
import socket
import subprocess
import sys

import psutil
################################################################
import yaml
import ZEO
import ZODB
from BTrees.OOBTree import BTree, OOSet

################################################################
from . import (base, bdlogging, bdparser, conffile_zeo, job, lowercase_btree,
               run_zeo, zeoobject)
from .constraints_zeo import ZEOconstraints

################################################################
__all__ = ["BaseZEO"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
PBTree = lowercase_btree.PersistentLowerCaseBTree
################################################################


class BaseZEO(base.AbstractBase):
    singleton_base = None

    @property
    def Job(self):
        return job.JobZEO

    @property
    def Run(self):
        return run_zeo.RunZEO

    def setHostsConfig(self):
        bd_conf_dir = os.path.expanduser("~/.blackdynamite")
        if not os.path.exists(bd_conf_dir):
            return {}
        bd_conf_files = [
            os.path.join(bd_conf_dir, f)
            for f in os.listdir(bd_conf_dir)
            if os.path.isfile(os.path.join(bd_conf_dir, f))
            and os.path.splitext(f)[1] == ".bd"
        ]
        bd_conf_files = [
            (e, yaml.safe_load(open(e, "r").read())) for e in bd_conf_files
        ]
        bd_conf_files = [(os.path.basename(e), f) for e, f in bd_conf_files]
        bd_conf_files = [(os.path.splitext(e)[0], f) for e, f in bd_conf_files]
        self.bd_conf_files = dict(bd_conf_files)

    def __init__(self, start_daemon=False, **kwargs):
        if "config" not in kwargs:
            parser = bdparser.BDParser()
            params = parser.parseBDParameters([])
            kwargs.update(params)

        super().__init__(**kwargs)

        self.setHostsConfig()
        BaseZEO.singleton_base = self
        self.ConfFile = conffile_zeo.ConfFile
        self.BDconstraints = ZEOconstraints
        logger.debug("connection arguments: {0}".format(kwargs))

        if "host" not in kwargs or kwargs["host"] is None:
            path = base.find_root_path(os.path.realpath("./"))
            kwargs["host"] = "zeo://" + path
            no_host_provided = True
        else:
            no_host_provided = False

        zeo_params = ["host", "creation", "port", "creation"]
        connection_params = bdparser.filterParams(zeo_params, kwargs)
        logger.debug("connection arguments: {0}".format(connection_params))

        # host = connection_params['host'] must be in the form
        # 1) zeo://existing_directory_path
        # 2) zeo://hostname:port
        self.host = connection_params["host"]
        try:
            protocol, addr = self.host.split("://")
        except ValueError:
            raise RuntimeError(
                f"FATAL: Invalid host: {self.host}\n"
                "Should be in the form zeo://directory_path "
                "or zeo://host:port"
            )
        logger.debug(f"addr {addr}")

        if protocol != "zeo":
            raise RuntimeError(f"wrong protocol with this database: {type(self)}")

        # it is not a remote tcp connection
        if ":" not in addr:
            self.root_dir = base.find_root_path(addr)
        else:
            self.root_dir = base.find_root_path()
        # fetch/create the configuration path
        self.setConfPaths(**connection_params)

        fname = os.path.join(self.root_dir, "bd.yaml")
        with open(fname) as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)

        creation = connection_params.get("creation", False)
        if creation is False:
            if no_host_provided or (start_daemon is False):
                addr_ = self.checkActualConfig(self.zeo_conf)
                logger.debug(f"addr_ {addr_}")
                if addr_ is not None:
                    addr = addr_

        unix_flag = False
        if self.isOpenedUnixSocket(addr):
            unix_flag = True
            if self.zeo_socket != addr:
                self.zeo_socket = addr

        if addr == self.zeo_socket:
            unix_flag = True
        if os.path.abspath(addr) == self.root_dir:
            unix_flag = True

        logger.debug(f"unix_flag: {unix_flag}, start_daemon: {start_daemon}")

        if unix_flag or creation:
            self.initUnix(addr, **connection_params)
        else:
            self.initTCP(addr, start_daemon=start_daemon, **connection_params)

        if "study" in kwargs:
            self.retreiveSchemaName(**kwargs)
        logger.debug("Base created and connected")

    def initTCP(self, addr, start_daemon=False, **kwargs):
        logger.debug(addr)
        logger.debug(start_daemon)
        m = re.match(r"(.+):([0-9]+)", addr)
        if m:
            self.dbhost = m[1].strip()
            self.port = int(m[2].strip())
        else:
            raise RuntimeError(f"could not understand host: {self.host}")

        if start_daemon is True:
            if not self.check_tcp_socket():
                self._create_tcp_socket(kwargs)

        socket_name = self.getSocketName()
        logger.debug(
            "Make a tcp connection to " f"zeo://{socket_name[0]}:{socket_name[1]}"
        )

        self.buildConnection(socket_name)

    def initUnix(self, addr, **kwargs):
        if not self.check_file_socket():
            self._create_unix_socket()

        socket_name = self.getSocketName()
        logger.debug(f"Make a connection to zeo://{socket_name}")

        self.buildConnection(socket_name)

    def check_file_socket(self):
        socket_name = self.zeo_socket
        if not os.path.exists(socket_name):
            return False
        conns = psutil.net_connections(kind="all")
        addrs = [s.laddr for s in conns if s.laddr != ""]
        for a in addrs:
            if a == socket_name:
                logger.debug("Found already running zeo server")
                return True
        return False

    def check_tcp_socket(self):
        socket_name = self.dbhost, self.port
        conns = psutil.net_connections(kind="tcp")
        addrs = [s.laddr for s in conns if s.laddr != ""]
        for a in addrs:
            if a.port == socket_name[1] and a.ip == socket.gethostbyname(
                socket_name[0]
            ):
                logger.debug("Found already running zeo server")
                return True
        return False

    @classmethod
    def checkActualConfig(cls, zeo_conf):
        from html.parser import HTMLParser

        class MyHTMLParser(HTMLParser):
            def __init__(self):
                self._data = {}
                self._current_tags = []
                super().__init__()

            def handle_starttag(self, tag, attrs):
                self._current_tags.append(tag)

            def handle_endtag(self, tag):
                self._current_tags.pop()

            def handle_data(self, data):
                if not self._current_tags:
                    return

                _key = ".".join(self._current_tags)
                self._data[_key] = data.strip()

        parser = MyHTMLParser()
        try:
            conf = open(zeo_conf).read()
            logger.debug(conf)

            parser.feed(conf)
            logger.debug(parser._data["zeo"])
            logger.debug(parser._data["zeo"])
            m = re.match(r"address\w*(.*)", parser._data["zeo"])
            logger.debug(m)
            logger.debug(m[1].strip())
            if m:
                return m[1].strip()
            # m = re.match(r'blob-dir\w*(.+):([0-9]+)',
            # parser._data['filestorage'])
            # if m:
            #     dbhost = m[1].strip()
            #     port = int(m[2].strip())
            #     logger.debug(dbhost)
            #     logger.debug(port)
            #     return dbhost, port

        except FileNotFoundError:
            logger.warning(f"Zeo config not found {zeo_conf}")
            return None

    def setConfPaths(self, creation=False, **kwargs):
        if not creation:
            self.bd_dir = os.path.join(self.root_dir, "./.bd")
        else:
            self.bd_dir = "./.bd"
        self.bd_dir = os.path.abspath(self.bd_dir)
        if creation and not os.path.exists(self.bd_dir):
            os.mkdir(self.bd_dir)
        elif not os.path.exists(self.bd_dir):
            raise RuntimeError(f"{os.getcwd()} is not a blackdynamite directory")

        self.zeo_conf = os.path.join(self.bd_dir, "zeo.conf")
        self.zeo_db = os.path.join(self.bd_dir, "bd.zeo")
        self.zeo_log = os.path.join(self.bd_dir, "zeo.log")
        self.zeo_socket = os.path.join(self.bd_dir, "zeo.socket")
        self.zeo_blob = os.path.join(self.bd_dir, "zeo.blob")
        self.zdaemon_socket = os.path.join(self.bd_dir, "zdaemon.socket")
        self.zdaemon_conf = self.getZdaemonConf(self.bd_dir)

    @classmethod
    def getZdaemonConf(cls, bd_dir):
        return os.path.join(bd_dir, "zdaemon.conf")

    def createZEOconfig(self, socket_name):
        if isinstance(socket_name, tuple):
            socket_name = socket_name[0] + ":" + str(socket_name[1])
        logger.debug(socket_name)

        zeo_server_conf = f"""
<zeo>
  address {socket_name}
</zeo>

<filestorage>
  path {self.zeo_db}
  blob-dir {self.zeo_blob}
</filestorage>

<eventlog>
  <logfile>
    path {self.zeo_log}
    format %(asctime)s %(message)s
  </logfile>
</eventlog>
"""
        logger.debug(self.zeo_conf)
        with open(self.zeo_conf, "w") as f:
            f.write(zeo_server_conf)

    def getSocketName(
        self,
    ):
        if hasattr(self, "dbhost"):
            return self.dbhost, self.port
        else:
            return self.zeo_socket

    def _create_unix_socket(self):
        socket_name = self.zeo_socket
        self.createZEOconfig(socket_name)
        self.launchZdaemon()

    def _create_tcp_socket(self, connection_params):
        host = connection_params["host"]
        m = re.match(r"zeo://(.+):([0-9]+)", host)
        if m:
            self.dbhost = m[1].strip()
            self.port = int(m[2].strip())

        self.setConfPaths("./.bd", **connection_params)
        socket_name = self.getSocketName()
        logger.debug(socket_name)
        self.createZEOconfig(socket_name)
        if not isinstance(socket_name, tuple):
            raise RuntimeError(
                "this method should be called only"
                f" to create a daemon: {socket_name}"
            )

        self.launchZdaemon()

    @classmethod
    def stopZdaemon(cls):
        zdaemon_conf = cls.getZdaemonConf("./.bd")
        zdaemon_processes = cls.getRunningZdaemons(zdaemon_conf)
        if not zdaemon_processes:
            logger.warning("Server not running (locally): doing nothing")
            return
        cmd = f"zdaemon -C {zdaemon_conf} stop"
        logger.debug("Stop zeo server: " + cmd)
        ret = subprocess.call(cmd, shell=True)
        if ret:
            raise RuntimeError(
                "An error occurred while stopping the "
                f"server on host: {cls.getSocketName()}"
            )
        zdaemon_processes = cls.getRunningZdaemons(zdaemon_conf)
        for pid, v in zdaemon_processes.items():
            p = psutil.Process(pid)
            p.kill()

    @classmethod
    def getRunningZdaemons(cls, zdaemon_conf):
        zdaemon_conf = os.path.abspath(zdaemon_conf)
        zdaemon_processes = {}

        for p in psutil.process_iter(["pid", "username"]):
            username = p.username()
            if username != getpass.getuser():
                continue
            pid = p.pid
            if p.status() == psutil.STATUS_ZOMBIE:
                p.kill()
                continue
            if "runzeo" not in p.cmdline():
                continue

            cmd = p.cmdline()
            if "-C" not in cmd:
                continue

            conf_zdaemon = None
            conf_zeo = None
            for i in range(len(cmd)):
                if cmd[i] == "-C":
                    if conf_zdaemon is None:
                        conf_zdaemon = cmd[i + 1]
                    else:
                        conf_zeo = cmd[i + 1]
                        break

            if conf_zdaemon != zdaemon_conf:
                continue

            zdaemon_processes[pid] = {
                "ZDaemonConf": conf_zdaemon,
                "ZeoConf": conf_zeo,
                "cwd": p.cwd(),
            }
        return zdaemon_processes

    @classmethod
    def statusZdaemon(cls):
        zdaemon_conf = cls.getZdaemonConf("./.bd")
        zdaemon_processes = cls.getRunningZdaemons(zdaemon_conf)
        for pid, v in zdaemon_processes.items():
            cmd = f"zdaemon -C {zdaemon_conf} status"
            logger.info(f"Status of zeo server {pid}")
            ret = subprocess.call(cmd, shell=True)
            if ret:
                raise RuntimeError(
                    "Error or Not running [server Config]:"
                    f" {open(zdaemon_conf).read()}"
                )
        if not zdaemon_processes:
            logger.warning("No daemon running (remote database?)")

    @classmethod
    def statusConnection(cls):
        zeo_conf = os.path.join("./.bd", "zeo.conf")
        host_port = cls.checkActualConfig(zeo_conf)
        if host_port is None:
            logger.error("Server configuration not found")
            return

        m = re.match(r"(.+):([0-9]+)", host_port)
        if not m:
            cls.statusUnixSocketConnection(host_port)
        else:
            logger.debug(m.groups())
            host, port = m[1].strip(), int(m[2].strip())
            cls.statusTCPConnection(host, port)

    @classmethod
    def statusTCPConnection(cls, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        if result == 0:
            logger.info(f"{host}:{port} is opened")
        else:
            logger.info(f"{host}:{port} is closed")
        sock.close()

        try:
            db = ZEO.DB((host, port))
            connection = db.open()
            logger.info(
                f"connection to {host}:{port} OK: "
                f"{[e for e in connection.root.schemas]}"
            )
        except Exception:
            logger.warning(f"Cannot connect to database {host}:{port}")

        current_host = socket.gethostname()
        current_ip = socket.gethostbyname(current_host)
        logger.debug(current_ip)
        host_ip = socket.gethostbyname(host)
        logger.debug(current_ip)
        logger.debug(host_ip)

    @classmethod
    def isOpenedUnixSocket(cls, path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        result = sock.connect_ex(path)
        is_opened = False
        if result == 0:
            is_opened = True
        else:
            is_opened = False
        sock.close()
        return is_opened

    @classmethod
    def statusUnixSocketConnection(cls, socket_name):
        if not os.path.exists(socket_name):
            logger.info("No socket")
            return
        is_opened = cls.isOpenedUnixSocket(socket_name)
        logger.info(f"socket {socket_name} is {'opened' if is_opened else 'closed'}")
        if not is_opened:
            return

        try:
            db = ZEO.DB(socket_name)
            connection = db.open()
            logger.info(
                f"connection to {socket_name} OK: "
                f"{[e for e in connection.root.schemas]}"
            )
        except Exception:
            logger.warning(f"Cannot connect to database {socket_name}")

    def launchZdaemon(self):
        _zdaemon_conf = f"""
<runner>
 program runzeo -C {self.zeo_conf}
 socket-name {self.zdaemon_socket}
</runner>
"""
        logger.debug(f"zdaemon_config: {self.zdaemon_conf}")
        with open(self.zdaemon_conf, "w") as f:
            f.write(_zdaemon_conf)

        cmd = f"zdaemon -C {self.zdaemon_conf} start"
        logger.debug("Spawning new zeo server: " + cmd)
        ret = subprocess.call(cmd, shell=True)
        if ret:
            raise RuntimeError(f"cannot spawn a server on host: {self.getSocketName()}")

    def buildConnection(self, socket_name):
        self.connection = ZEO.connection(
            socket_name,
            read_only=self.read_only,
            server_sync=False,
            blob_dir=self.zeo_blob,
            shared_blob_dir=True,
            wait_timeout=5,
        )
        self.root = self.connection.root
        logger.debug("connected to base")
        assert isinstance(self.connection, ZODB.Connection.Connection)

    def getSchemaList(self, filter_names=True):
        try:
            schemas = self.root.schemas
        except AttributeError:
            self.root.schemas = PBTree(key_string="study_")
            schemas = self.root.schemas
        filtered_schemas = []
        if filter_names is True:
            for s in schemas:
                m = re.match("(.+)_(.+)", s)
                if m:
                    s = m.group(2)
                filtered_schemas.append(s)
        else:
            filtered_schemas = schemas
        return filtered_schemas

    def getSchemasUser(self, study_name):
        try:
            schemas = self.root.schemas
        except AttributeError:
            self.root.schemas = PBTree(key_string="study_")
            schemas = self.root.schemas
        for s in schemas:
            m = re.match(f"(.+)_{study_name}", s)
            if m:
                return m.group(1)
        raise RuntimeError(
            f"not found study: '{study_name}' within {[e for e in schemas]}"
        )

    def getStudySize(self, study):
        raise RuntimeError("to be implemented")

    def createSchema(self, params={"yes": False}):
        # create the schema of the simulation
        if not hasattr(self.root, "schemas"):
            self.root.schemas = PBTree(key_string="study_")
        if self.schema in self.root.schemas:
            validated = bdparser.validate_question(
                "Are you sure you want to drop the schema named '" + self.schema + "'",
                params,
                False,
            )
            if validated is True:
                del self.root.schemas[self.schema]
            else:
                logger.debug("creation canceled: exit program")
                sys.exit(-1)
        self.root.schemas[self.schema] = PBTree()
        self.root.schemas[self.schema]["Quantities"] = OOSet()
        self.root.schemas[self.schema]["Jobs"] = PBTree(key_string="job_")
        self.root.schemas[self.schema]["JobsIndex"] = BTree()
        self.root.schemas[self.schema]["RunsIndex"] = BTree()
        self.root.schemas[self.schema]["Runs"] = PBTree(key_string="run_")
        self.root.schemas[self.schema]["ConfigFiles"] = BTree()
        self.root.schemas[self.schema]["Jobs_counter"] = 1
        self.root.schemas[self.schema]["Runs_counter"] = 1

    def get_descriptor(self, descriptor):
        if not hasattr(self.root, "schemas"):
            return
        if (
            self.schema in self.root.schemas
            and descriptor in self.root.schemas[self.schema]
        ):
            desc = self.root.schemas[self.schema][descriptor]
            return desc

    def prepare(self, obj, descriptor):
        if not hasattr(self.root, "schemas"):
            return
        if (
            self.schema in self.root.schemas
            and descriptor in self.root.schemas[self.schema]
        ):
            desc = self.root.schemas[self.schema][descriptor]
            for t in desc.types.keys():
                obj.types[t] = desc.types[t]
                if t not in obj:
                    obj.t = None

    def createBase(self, job_desc, run_desc, **kwargs):
        self.createSchema(kwargs)

        self.root.schemas[self.schema]["job_desc"] = job_desc
        self.root.schemas[self.schema]["run_desc"] = run_desc

        if self.truerun:
            self.commit()

    @property
    def configfiles(self):
        return self.root.schemas[self.schema]["ConfigFiles"]

    def _get_jobs(self):
        return self.root.schemas[self.schema]["Jobs"]

    @property
    def jobs(self):
        return self._get_jobs()

    @jobs.setter
    def jobs(self, val):
        self.root.schemas[self.schema]["Jobs"] = val

    @property
    def jobs_index(self):
        return self._get_jobs_index()

    @jobs_index.setter
    def jobs_index(self, val):
        self.root.schemas[self.schema]["JobsIndex"] = val

    @property
    def runs_index(self):
        return self._get_runs_index()

    @runs_index.setter
    def runs_index(self, val):
        self.root.schemas[self.schema]["RunsIndex"] = val

    @property
    def quantities(self):
        return self.root.schemas[self.schema]["Quantities"]

    @quantities.setter
    def quantities(self, value):
        self.root.schemas[self.schema]["Quantities"] = value

    @property
    def jobs_counter(self):
        return self.root.schemas[self.schema]["Jobs_counter"]

    @jobs_counter.setter
    def jobs_counter(self, val):
        self.root.schemas[self.schema]["Jobs_counter"] = val

    def _get_runs(self):
        return self.root.schemas[self.schema]["Runs"]

    def _get_runs_index(self):
        return self.root.schemas[self.schema]["RunsIndex"]

    def _get_jobs_index(self):
        return self.root.schemas[self.schema]["JobsIndex"]

    @property
    def runs(self):
        return self._get_runs()

    @runs.setter
    def runs(self, val):
        self.root.schemas[self.schema]["Runs"] = val

    @property
    def runs_counter(self):
        return self.root.schemas[self.schema]["Runs_counter"]

    @runs_counter.setter
    def runs_counter(self, val):
        self.root.schemas[self.schema]["Runs_counter"] = val

    def select(self, _types, constraints=None, sort_by=None):
        if not isinstance(_types, list):
            _types = [_types]

        _type = _types[0]
        if isinstance(_type, zeoobject.ZEOObject):
            _type = type(_type)
        if _type == self.Job:
            obj_container = self._get_jobs()
            obj_index = self.jobs_index
        elif _type == self.Run:
            obj_container = self._get_runs()
            obj_index = self.runs_index
        else:
            raise RuntimeError(f"{type(_types)}")

        if (sort_by is not None) and (not isinstance(sort_by, str)):
            raise RuntimeError(f"sort_by argument is not correct: {sort_by}")

        if isinstance(constraints, zeoobject.ZEOObject):
            if hasattr(constraints, "id") and constraints.id is not None:
                obj = obj_container[constraints.id]
                if isinstance(obj, self.Run):
                    obj = (obj, self._get_jobs()[obj.job_id])
                return [obj]
            else:
                constraints = constraints.copy()
                constraints.evalFunctorEntries()
                params = constraints.get_params()
                keys = constraints.get_keys()
                n_params = len(keys)

                if len(params) == n_params:
                    logger.debug(constraints)
                    logger.debug(params)
                    logger.debug(obj_index)
                    logger.debug([j for j in obj_index])

                    if params in obj_index:
                        return [obj_container[obj_index[params]]]
                    else:
                        return []

        const = ZEOconstraints(self, constraints)

        # detect if run_id is passed
        if _types[0] == run_zeo.RunZEO:
            logger.debug(const.constraints)
            for c in const.constraints:
                m = re.match("runs.id = ([0-9]+)", c)
                if m:
                    r = obj_container[int(m[1])]
                    j = self.jobs[r.job_id]
                    return [(r, j)]

        condition = const.getMatchingCondition()

        obj_list = []
        for key, obj in obj_container.items():
            objs = [obj]
            if _type == self.Run:
                j = self._get_jobs()[obj.job_id]
                objs.append(j)
            if condition(objs):
                if len(objs) == 1:
                    obj_list.append(objs[0])
                else:
                    obj_list.append(objs)

        return obj_list

    def insert(self, zeoobject, keep_state=False):
        if isinstance(zeoobject, self.Job):
            objs = self.jobs
            zeoobject = zeoobject.copy()
            zeoobject.evalFunctorEntries()
            logger.debug(zeoobject)
            if not keep_state:
                zeoobject["id"] = self.jobs_counter
                self.jobs_counter += 1
            params = zeoobject.get_params()
            self.jobs_index[params] = zeoobject["id"]

        elif isinstance(zeoobject, self.Run):
            objs = self.runs
            zeoobject = zeoobject.copy()
            if not keep_state:
                zeoobject["id"] = self.runs_counter
                zeoobject["state"] = "CREATED"
                job_id = zeoobject["job_id"]
                run_id = zeoobject["id"]
                job = self.jobs[job_id]
                if not hasattr(job, "runs"):
                    job.runs = PBTree(key_string="runs_")
                job.runs[run_id] = zeoobject
                self.runs_counter += 1
                params = zeoobject.get_params()
                self.runs_index[params] = zeoobject["id"]

        else:
            raise RuntimeError(f"cannot insert object of type {type(zeoobject)}")

        objs[zeoobject.id] = zeoobject.copy()
        return zeoobject.id

    def setObjectItemTypes(self, zeoobject):
        if isinstance(zeoobject, self.Job):
            zeoobject.types = self.root.schemas[self.schema]["job_desc"].types
        elif isinstance(zeoobject, self.Run):
            zeoobject.types = self.root.schemas[self.schema]["run_desc"].types
        else:
            raise RuntimeError(f"{type(zeoobject)}")

    def commit(self):
        import transaction

        transaction.commit()

    def pack(self):
        self.connection.db().pack()

    def close(self):
        import transaction

        transaction.abort()

    def retreiveSchemaName(self, creation=False, study=None, **kwargs):
        # Need this because getSchemaList strips prefix
        match = re.match("(.+)_(.+)", study)
        study_name = None
        if match:
            self.schema = study
            study_name = match.group(2)
        else:
            try:
                study_name = study
                self.schema = self.getSchemasUser(study) + "_" + study

            except RuntimeError as e:
                if creation is False:
                    raise e
                detected_user = pwd.getpwuid(os.getuid())[0]
                self.schema = detected_user + "_" + study

        if (creation is not True) and (study_name not in self.getSchemaList()):
            logger.error(study_name)
            raise RuntimeError(
                f"Study name '{study_name}' invalid: "
                f"possibilities are {self.getSchemaList()}"
            )

    def manualLaunch(self, job, run, run_name="manual", nproc=1, **params):
        from . import jobselector, runselector

        n_insertion = self.createParameterSpace(job)
        logger.info(f"Inserted {n_insertion} new jobs")
        jobSelector = jobselector.JobSelector(self)
        job_list = jobSelector.selectJobs(job, quiet=True)
        if len(job_list) != 1:
            logger.error(
                "For a manual launch all parameters of jobs " "have to be specified"
            )
        else:
            job = job_list[0]
        logger.debug(job)

        run["run_name"] = run_name
        run["nproc"] = nproc
        run["machine_name"] = socket.gethostname()

        fname = "bd.yaml"
        with open(fname) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        # add a configuration file
        for f in config["config_files"]:
            run.addConfigFiles(f)

        # set the entry point (executable) file
        run.setExecFile(config["exec_file"])
        runSelector = runselector.RunSelector(self)

        run_list = runSelector.selectRuns(run, quiet=True)
        logger.debug(job)
        logger.debug(run)
        already_created = False
        if len(run_list) > 0:
            for r, j in run_list:
                if j.id != job.id:
                    continue
                logger.debug([e for e in r.configfiles])
                logger.debug([e for e in run.configfiles])

                if [e for e in r.configfiles] != [e for e in run.configfiles]:
                    continue
                if r["state"] == "FINISHED":
                    logger.warning(
                        "Exact same run was already executed: not re-running"
                    )
                    return r, j
                else:
                    run = r
                    already_created = True
                    break
        if already_created is False:
            run.attachToJob(job_list[0])
            self.commit()
            run_list = runSelector.selectRuns(run, quiet=True)
            run = run_list[0][0]

        if "outpath" not in params:
            params["outpath"] = "./"
        if "study" not in params:
            params["study"] = config["study"]

        params["truerun"] = True

        if "generator" not in params:
            from . import bdparser

            parser = bdparser.BDParser()
            params["generator"] = parser.loadModule({}, "bashCoat", {})

        logger.warning(params)
        self.launchRuns([(run, job)], params)
        return run, job

    def launchRuns(self, run_list, params):
        if len(run_list) == 0:
            logger.error("No runs to be launched")

        mydir = os.path.join(params["outpath"], "BD-" + params["study"] + "-runs")
        if not os.path.exists(mydir):
            os.makedirs(mydir)

        cwd = os.getcwd()
        os.chdir(mydir)

        for r, j in run_list:
            logger.warning(f"Dealing with job {j.id}, run {r.id}")
            r["run_path"] = os.path.join(mydir, "run-" + str(r.id))
            j.update()
            r.update()

            if not os.path.exists("run-" + str(r.id)):
                os.makedirs("run-" + str(r.id))

            os.chdir("run-" + str(r.id))

            conffiles = r.getConfigFiles()
            for conf in conffiles:
                logger.warning("create file " + conf["filename"])
                f = open(conf["filename"], "w")
                f.write(conf["file"])
                f.close()

            logger.warning("launch in '" + mydir + "/" + "run-" + str(r.id) + "/'")
            mymod = params["generator"]
            logger.warning(mymod)
            mymod.launch(r, params)

            os.chdir("../")

        os.chdir(cwd)
        if params["truerun"] is True:
            self.commit()


################################################################
