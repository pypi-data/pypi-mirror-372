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

import datetime
import os
import socket
import subprocess

################################################################
import BTrees
################################################################
import numpy as np
from ZODB import blob

from . import base, bdlogging, bdparser, conffile_zeo, zeoobject
from .conffile_zeo import ConfFile

################################################################
__all__ = ["RunZEO", "getRunFromScript"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
# PBTree = lowercase_btree.PersistentLowerCaseBTree
BTree = BTrees.OOBTree.BTree
OOSet = BTrees.OOBTree.OOSet

################################################################


class UnknownQuantity(RuntimeError):
    pass


class RunZEO(zeoobject.ZEOObject):
    """ """

    def get_params(self):
        base = self.base
        study = base.root.schemas[base.schema]
        desc = study["run_desc"]
        params = tuple(
            [v for e, v in desc.entries.items() if (e != "id" and v is not None)]
        )
        return params

    def getJob(self):
        return self.base.getJobFromID(self.entries["job_id"])

    def start(self):
        # logger.error(self.entries['state'])
        self.entries["state"] = "START"
        self.start_time = datetime.datetime.now()
        # logger.error(self['state'])
        logger.debug("starting run")
        self.base.commit()
        logger.debug("committed")

    def finish(self):
        self.entries["state"] = "FINISHED"
        logger.debug("finish run")
        self.base.commit()
        logger.debug("committed")

    def fail(self, state="FAILURE"):
        self.entries["state"] = state
        logger.debug("failed run")
        self.base.commit()
        logger.debug("committed")

    def attachToJob(self, job):
        self["job_id"] = job.id
        return self.base.insert(self)

    def getExecFile(self):
        conf_exec = self.base.configfiles[self.exec]
        return self.getUpdatedConfigFile(conf_exec)

    def setExecFile(self, file_name, **kwargs):
        # check if the file is already in the config files
        for _id in self.configfiles:
            f = self.base.configfiles[_id]
            if f.filename == file_name:
                self.entries["exec"] = f.id
                return f.id

        # the file is not in the current config files
        # so it has to be added
        _ids = self.addConfigFiles(file_name)
        self.entries["exec"] = _ids[0]
        return _ids[0]

    def annotateHostName(self, host):
        host = self["machine_name"]
        if hasattr(self.base, "bd_conf_files"):
            if host in self.base.bd_conf_files:
                conf = self.base.bd_conf_files[host]
                if "user" in conf:
                    host = conf["user"] + "@" + host
            logger.debug(self.base.bd_conf_files.keys())
        logger.debug(host)
        return host

    def listFiles(self, subdir="", cache=None):
        """List files in run directory / specified sub-directory"""
        command = "ls {0}".format(os.path.join(self["run_path"], subdir))
        if (
            not self["machine_name"] == socket.gethostname()
            and self["machine_name"] != "localhost"
            and cache is None
        ):
            host = self.annotateHostName(self["machine_name"])
            command = f'ssh {host} "{command}"'
        elif cache is not None:
            dest_path = os.path.join(
                cache, "BD-" + self.base.schema + "-cache", f"run-{self.id}"
            )
            command = f"ls {os.path.join(dest_path, subdir)}"
        logger.debug(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.readlines()
        out = [o.strip().decode() for o in out]
        return out

    def getFile(self, filename, cache=None):
        if cache is None:
            cache = self.base.root_dir
        dest_path = os.path.join(
            cache, "BD-" + self.base.schema + "-cache", "run-{0}".format(self.id)
        )
        dest_file = os.path.join(dest_path, filename)

        full_filename = self.getFullFileName(filename)

        # Check if file is local
        if os.path.isfile(full_filename):
            return full_filename

        # If file is distant, prepare cache directory hierarchy
        dest_path = os.path.dirname(dest_file)

        logger.debug("Directories: " + dest_path)
        logger.debug("File: " + dest_file)

        # Making directories
        try:
            os.makedirs(dest_path, exist_ok=True)
        except Exception as e:
            logger.error(e)
            pass

        if os.path.isfile(dest_file):
            logger.debug("File {} already cached".format(dest_file))
            return dest_file

        host = self.annotateHostName(self["machine_name"])

        cmd = "scp {0}:{1} {2}".format(host, self.getFullFileName(filename), dest_file)
        logger.debug(cmd)
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        errors = bytes(p.stderr.read()).decode().strip()
        if errors:
            logger.warning(errors)
        return dest_file

    def getFullFileName(self, filename):
        return os.path.join(self["run_path"], filename)

    def addConfigFiles(self, file_list, regex_params=None):

        if not isinstance(file_list, list):
            file_list = [file_list]
        params_list = list(self.types.keys())
        myjob = self.base.Job()
        params_list += list(myjob.types.keys())

        # logger.debug (regex_params)
        # file_ids = [f for f in self.configfiles]
        files_to_add = [
            conffile_zeo.addFile(fname, regex_params=regex_params, params=params_list)
            for fname in file_list
        ]

        added_files = []
        for f in files_to_add:
            if f.id not in self.configfiles:
                self.configfiles.add(f.id)
                self.base.configfiles[f.id] = f
                added_files.append(f.id)
        self.base.commit()
        return added_files

    def getConfigFiles(self):
        files = [self.base.configfiles[_id] for _id in self.configfiles]

        conffiles = [self.getUpdatedConfigFile(f) for f in files]

        return conffiles

    def getConfigFile(self, file_id):
        return self.configfiles[file_id]

    def replaceBlackDynamiteVariables(self, text):
        myjob = self.base.Job()
        myjob["id"] = self.entries["job_id"]
        myjob = myjob.getMatchedObjectList()[0]

        for key, val in myjob.entries.items():
            tmp = text.replace("__BLACKDYNAMITE__" + key + "__", str(val))
            if (not tmp == text) and val is None:
                raise Exception("unset job parameter " + key)
            text = tmp

        for key, val in self.entries.items():
            tmp = text.replace("__BLACKDYNAMITE__" + key + "__", str(val))
            if (not tmp == text) and val is None:
                logger.debug(self.entries)
                raise Exception("unset run parameter " + key)
            text = tmp

        text = text.replace("__BLACKDYNAMITE__dbhost__", self.base.host)
        text = text.replace("__BLACKDYNAMITE__study__", self.base.schema)
        text = text.replace("__BLACKDYNAMITE__run_id__", str(self.id))
        return text

    def getUpdatedConfigFile(self, conf):
        conf = ConfFile(conf.filename, content=conf.file)
        conf["file"] = self.replaceBlackDynamiteVariables(conf["file"])
        return conf

    def listQuantities(self):
        return self.base.quantities

    def getLastStep(self):
        if "last_step" in self.entries:
            return self.last_step, self.last_step_time
        else:
            return None, None

    def getScalarQuantity(self, name, additional_request=None):
        if name not in self.quantities:
            raise UnknownQuantity(
                f"for run {self}\n"
                f"unknown quantity '{name}'\n"
                "possible quantities are"
                f" {[e for e in self.quantities.keys()]}"
            )
        step, array = self.getQuantityArrayFromBlob(name)
        return step, array

    def getScalarQuantities(self, names, additional_request=None):
        res = []
        for q in names:
            try:
                step, array = self.getScalarQuantity(q)
                res.append((q, step, array))
            except UnknownQuantity:
                logger.warning(f"run {self.id} has no quantity: {q}")
                return None
        return res

    def getVectorQuantity(self, name, step):
        step_array, array = self.getQuantityArrayFromBlob(name)
        i = np.where(step_array == step)[0]
        if i.shape[0] == 0:
            raise RuntimeError("the step {step} could not be found")
        if i.shape[0] > 1:
            raise RuntimeError("the step {step} was registered more than once")
        i = i[0]
        return array[i]

    @zeoobject._transaction
    def saveStepTimeStamp(self, step):
        self.last_step = step
        self.last_step_time = datetime.datetime.now()

    @zeoobject._transaction
    def pushVectorQuantity(self, vec, step, name, description=None):

        quantities = self.base.quantities
        quantities.add(name)
        if name not in self.quantities:
            list_vec = np.array([vec], dtype=object)
            array_step = np.array([step])

        else:
            array_step, list_vec = self.getQuantityArrayFromBlob(name)
            array_step = np.append(array_step, [step], axis=0)
            if (len(list_vec.shape) == 2 and list_vec.shape[1] != vec.shape[0]) or len(
                list_vec.shape
            ) == 1:
                list_vec = np.array([e for e in list_vec] + [vec], dtype=object)
            else:
                list_vec = np.append(list_vec, [vec], axis=0)
        self.saveQuantityArrayToBlob(name, array_step, list_vec)
        self.saveStepTimeStamp(step)
        self.base.commit()

    @zeoobject._transaction
    def pushScalarQuantity(self, val, step, name, description=None):
        quantities = self.base.quantities
        quantities.add(name)
        if name not in self.quantities:
            array_val = np.array([val])
            array_step = np.array([step])
        else:
            array_step, array_val = self.getQuantityArrayFromBlob(name)
            array_step = np.append(array_step, [step], axis=0)
            array_val = np.append(array_val, [val], axis=0)

        self.saveQuantityArrayToBlob(name, array_step, array_val)
        self.saveStepTimeStamp(step)
        self.base.commit()

    @zeoobject._transaction
    def pushScalarQuantities(self, vals, steps, name, description=None):
        quantities = self.base.quantities
        quantities.add(name)
        if name not in self.quantities:
            array_val = np.array(vals)
            array_step = np.array(steps)
        else:
            array_step, array_val = self.getQuantityArrayFromBlob(name)
            array_step = np.append(array_step, steps, axis=0)
            array_val = np.append(array_val, vals, axis=0)

        self.saveQuantityArrayToBlob(name, array_step, array_val)
        self.saveStepTimeStamp(steps[-1])
        self.base.commit()

    def getQuantityBlob(self, name):
        if name not in self.quantities:
            logger.info(f"create quantity {name}")
            self.quantities[name] = blob.Blob()
        return self.quantities[name]

    def getQuantityArrayFromBlob(self, name):
        buf = self.getQuantityBlob(name).open()
        # logger.error(name)
        # logger.error(buf.name)
        try:
            _f = np.load(buf, allow_pickle=True)
        except IOError as e:
            logger.error(e)
            raise RuntimeError(f"Cannot read file {buf.name} for quantity {name}")
        # logger.error(f'{name} {_f["step"]}')
        return _f["step"], _f["val"]

    def saveQuantityArrayToBlob(self, name, array_step, array_val):
        buf = self.getQuantityBlob(name).open("w")
        # logger.error(f'{name} {buf.name}')
        # logger.error(f'{name} {array_step}')
        np.savez_compressed(buf, val=array_val, step=array_step)

    def getAllVectorQuantity(self, name):
        quantity_id, is_integer, is_vector = self.getQuantityID(name, is_vector=True)

        request = """
SELECT step,measurement from {0}.{1}
WHERE (run_id,quantity_id) = ({2},{3}) order by step
""".format(
            self.base.schema,
            "vector_real" if is_integer is False else "vector_integer",
            self.id,
            quantity_id,
        )
        curs = self.base.performRequest(request, [name])
        fetch = curs.fetchall()
        if not fetch:
            return [None, None]
        matres = np.array([val[1] for val in fetch])
        stepres = np.array([val[0] for val in fetch])
        return (stepres, matres)

    def delete(self):
        job_id = self["job_id"]
        job = self.base.jobs[job_id]
        del job.runs[self.id]
        del self.base.runs[self.id]
        self.base.commit()

    def deleteData(self):
        for name in self.quantities:
            blob = self.getQuantityBlob(name)
            logger.warning(f"{blob} was not deleted (and should have)")

        del self.quantities
        self.quantities = BTree()
        self.base.commit()

    def __init__(self):
        super().__init__()
        self.configfiles = OOSet()
        self.quantities = BTree()
        # logger.error(self.quantities)
        self.base.prepare(self, "run_desc")
        self["id"] = None
        self.types["id"] = int
        self.types["machine_name"] = str
        self.types["run_path"] = str
        self.allowNull["run_path"] = True
        self.types["job_id"] = int
        self.types["nproc"] = int
        self.types["run_name"] = str
        self.types["start_time"] = datetime.datetime
        self.allowNull["start_time"] = True
        self.types["state"] = str
        self.allowNull["state"] = True
        self.types["exec"] = str
        self.types["last_step"] = int
        self.types["last_step_time"] = datetime.datetime

        self["last_step"] = None
        self["last_step_time"] = None
        self["start_time"] = None


################################################################


def getRunFromScript():
    from .base_zeo import BaseZEO

    if BaseZEO.singleton_base is not None:
        mybase = BaseZEO.singleton_base
    else:
        parser = bdparser.BDParser()
        group = parser.register_group("getRunFromScript")
        group.add_argument("--run_id", type=int)
        params = parser.parseBDParameters(argv=[])
        mybase = base.Base(**params)
    myrun = mybase.runs[params["run_id"]]
    myjob = mybase.jobs[myrun.job_id]
    return myrun, myjob
