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

from __future__ import print_function
################################################################
from . import runconfig
from . import conffile_sql
from . import sqlobject
from . import bdparser
from . import base
from . import runselector
from . import bdlogging

import sys
import re
import numpy as np
import datetime
import subprocess
import socket
import os
################################################################
__all__ = ['RunSQL', 'getRunFromScript']
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class RunSQL(sqlobject.SQLObject):
    """
    """

    table_name = 'runs'

    def getJob(self):
        return self.base.getJobFromID(self.entries["job_id"])

    def start(self):
        self.entries['state'] = 'START'
        logger.debug('starting run')
        self.update()
        logger.debug('update done')
        self.base.commit()
        logger.debug('commited')

    def finish(self):
        self.entries['state'] = 'FINISHED'
        logger.debug('finish run')
        self.update()
        logger.debug('update done')
        self.base.commit()
        logger.debug('commited')

    def attachToJob(self, job):
        self["job_id"] = job.id
        self.base.insert(self)
        self.addConfigFile(self.execfile)
        for cnffile in self.configfiles:
            self.addConfigFile(cnffile)

    def getExecFile(self):
        return self.getUpdatedConfigFile(self.entries["exec"])

    def setExecFile(self, file_name, **kwargs):
        # check if the file is already in the config files
        for f in self.configfiles:
            if f.entries["filename"] == file_name:
                self.execfile = f
                self.entries["exec"] = f.id
                return f.id

        # the file is not in the current config files
        # so it has to be added
        conf = conffile_sql.addFile(file_name, self.base, **kwargs)
        self.configfiles.append(conf)
        self.execfile = conf
        self.entries["exec"] = conf.id
        return conf.id

    def listFiles(self, subdir=""):
        """List files in run directory / specified sub-directory"""
        command = 'ls {0}'.format(os.path.join(self['run_path'], subdir))
        if not self['machine_name'] == socket.gethostname():
            command = 'ssh {0} "{1}"'.format(self['machine_name'], command)
        logger.info(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.readlines()
        out = [o.strip().decode() for o in out]
        return out

    def getFile(self, filename, outpath='/tmp'):
        dest_path = os.path.join(
            outpath, "BD-" + self.base.schema + "-cache",
            "run-{0}".format(self.id))
        dest_file = os.path.join(dest_path, filename)

        if self['machine_name'] == socket.gethostname():
            return self.getFullFileName(filename)

        # In case filename contains sub-directories
        dest_path = os.path.dirname(dest_file)

        logger.info(dest_path)
        logger.info(dest_file)

        # Making directories
        try:
            os.makedirs(dest_path, exist_ok=True)
        except Exception as e:
            logger.error(e)
            pass

        if os.path.isfile(dest_file):
            return dest_file
        cmd = 'scp {0}:{1} {2}'.format(self['machine_name'],
                                       self.getFullFileName(filename),
                                       dest_file)
        logger.info(cmd)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        logger.info(p.stdout.read())
        return dest_file

    def getFullFileName(self, filename):
        return os.path.join(self['run_path'], filename)

    def addConfigFiles(self, file_list, regex_params=None):

        if not type(file_list) == list:
            file_list = [file_list]
        params_list = list(self.types.keys())
        myjob = self.base.Job(self.base)
        params_list += list(myjob.types.keys())

        # logger.debug (regex_params)
        file_ids = [f.id for f in self.configfiles]
        files_to_add = [
            conffile_sql.addFile(
                fname, self.base,
                regex_params=regex_params,
                params=params_list)
            for fname in file_list]

        for f in files_to_add:
            if (f.id not in file_ids):
                self.configfiles.append(f)
        return self.configfiles

    def addConfigFile(self, configfile):
        myrun_config = runconfig.RunConfig(self.base)
        myrun_config.attachToRun(self)
        myrun_config.addConfigFile(configfile)
        self.base.insert(myrun_config)

    def getConfigFiles(self):
        # myjob = job.Job(self.base)
        # myjob["id"] = self.entries["job_id"]
        # myjob = self.getMatchedObjectList()[0]

        runconf = runconfig.RunConfig(self.base)
        runconf["run_id"] = self.id
        runconf_list = runconf.getMatchedObjectList()
        logger.info(runconf_list)
        conffiles = [
            self.getUpdatedConfigFile(f["configfile_id"])
            for f in runconf_list]
        return conffiles

    def getConfigFile(self, file_id):
        # runconf = runconfig.RunConfig(self.base)
        conf = conffile_sql.ConfFile(self.base)
        conf["id"] = file_id
        conf = conf.getMatchedObjectList()[0]
        return conf

    def replaceBlackDynamiteVariables(self, text):
        myjob = self.base.Job(self.base)
        myjob["id"] = self.entries["job_id"]
        myjob = myjob.getMatchedObjectList()[0]

        for key, val in myjob.entries.items():
            tmp = text.replace("__BLACKDYNAMITE__" + key + "__",
                               str(val))
            if ((not tmp == text) and val is None):
                raise Exception("unset job parameter " + key)
            text = tmp

        for key, val in self.entries.items():
            tmp = text.replace("__BLACKDYNAMITE__" + key + "__",
                               str(val))
            if ((not tmp == text) and val is None):
                logger.debug(self.entries)
                raise Exception("unset run parameter " + key)
            text = tmp

        text = text.replace("__BLACKDYNAMITE__dbhost__",
                            self.base.dbhost)
        text = text.replace("__BLACKDYNAMITE__study__",
                            self.base.schema)
        text = text.replace("__BLACKDYNAMITE__run_id__",
                            str(self.id))
        return text

    def getUpdatedConfigFile(self, file_id):
        conf = self.getConfigFile(file_id)
        conf["file"] = self.replaceBlackDynamiteVariables(conf["file"])
        return conf

    def listQuantities(self):
        request = "SELECT id,name FROM {0}.quantities".format(self.base.schema)
        curs = self.base.performRequest(request)
        all_quantities = [res[1] for res in curs]
        return all_quantities

    def getScalarQuantities(self, names, additional_request=None):

        request = ("SELECT id,name FROM {0}.quantities "
                   "WHERE (is_vector) = (false)").format(
                       self.base.schema)
        params = []
        if (names):
            if (not type(names) == list):
                names = [names]
            request += " and ("
            for name in names:
                similar_op_match = re.match(r"\s*(~)\s*(.*)", name)
                op = " = "
                if (similar_op_match):
                    op = " ~ "
                    name = similar_op_match.group(2)
                request += " name " + op + "%s or"
                params.append(str(name))
            request = request[:len(request)-3] + ")"
            # logger.debug (request)
            # logger.debug (params)
        curs = self.base.performRequest(request, params)

        quantities = [res[1] for res in curs]
        if (len(quantities) == 0):
            logger.error("No quantity matches " + str(names))
            logger.error("Quantities declared in the database are \n" +
                         "\n".join(
                             [res for res in self.listQuantities()]))
            sys.exit(-1)
            return None

        try:
            quant_indexes = [quantities.index(n) for n in names]
            logger.debug(quant_indexes)
            quantities = names
        except:
            # quant_indexes = None
            pass

        # logger.debug (quant)
        results = []
        for key in quantities:
            step, q = self.getScalarQuantity(key, additional_request)
            if (q is not None):
                results.append([key, step, q])
                logger.debug("got Quantity " + str(key) + " : " +
                             str(q.shape[0]) + " values")
        return results

    def getLastStep(self):

        request = """SELECT max(b.max),max(b.time) from (
SELECT max(step) as max,max(computed_at) as time
from {0}.scalar_integer where run_id = {1}
union
SELECT max(step) as max,max(computed_at)
as time from {0}.scalar_real where run_id = {1}
union
SELECT max(step) as max,max(computed_at)
as time from {0}.vector_integer where run_id = {1}
union
SELECT max(step) as max,max(computed_at) as time
from {0}.vector_real where run_id = {1}) as b
""".format(self.base.schema, self.id)
        # logger.debug (request)
        curs = self.base.performRequest(request, [])
        item = curs.fetchone()
        if (item is not None):
            return item[0], item[1]

    def getQuantityID(self, name, is_integer=None, is_vector=None):
        request = """
SELECT id,is_integer,is_vector FROM {0}.quantities WHERE (name) = (%s)
""".format(self.base.schema)
        curs = self.base.performRequest(request, [name])
        item = curs.fetchone()
        if (item is None):
            raise Exception("unknown quantity \"" + name + "\"")

        if ((is_integer is not None) and (not is_integer == item[1])):
            raise Exception("quantity \"" + name + "\" has is_integer = " +
                            str(item[1]))
        if ((is_vector is not None) and (not is_vector == item[2])):
            raise Exception("quantity \"" + name + "\" has is_vector = " +
                            str(item[2]))

        return item[0], item[1], item[2]

    def getScalarQuantity(self, name, additional_request=None):
        quantity_id, is_integer, is_vector = self.getQuantityID(name)
        if is_vector is True:
            raise Exception("Quantity " + name + " is not scalar")

        request = """
SELECT step,measurement from {0}.{1} WHERE (run_id,quantity_id) = ({2},{3})
""".format(self.base.schema,
           "scalar_real" if (is_integer is False)
           else "scalar_integer",
           self.id,
           quantity_id)

        if (additional_request):
            request += " and " + " and ".join(additional_request)
        request += " ORDER BY step"
        curs = self.base.performRequest(request, [name])
        fetch = curs.fetchall()
        if (not fetch):
            return None
        res = np.array([(val[0], val[1]) for val in fetch])
        return res[:, 0], res[:, 1]

    def getVectorQuantity(self, name, step):
        quantity_id, is_integer, is_vector = self.getQuantityID(name)
        if (is_vector is False):
            raise Exception("Quantity " + name + " is not vectorial")

        request = """
SELECT measurement from {0}.{1} WHERE (run_id,quantity_id,step) = ({2},{3},{4})
""".format(self.base.schema, "vector_real"
           if (is_integer is False)
           else "vector_integer",
           self.id, quantity_id, step)
        curs = self.base.performRequest(request, [name])
        fetch = curs.fetchone()
        if (fetch):
            return np.array(fetch[0])
        return None

    def pushVectorQuantity(self, vec, step, name,
                           is_integer, description=None):
        logger.debug('pushing {0}'.format(name))
        try:
            quantity_id, is_integer, is_vector = self.getQuantityID(
                name, is_integer=is_integer, is_vector=True)
        except Exception as e:
            typecode = "int"
            if is_integer is False:
                typecode = "float"
            typecode += ".vector"
            quantity_id = self.base.pushQuantity(name, typecode, description)

        array = [i for i in vec]
        # if is_integer is True:
        #    array_format = ",".join(["{:d}".format(i) for i in vec])
        request = """
INSERT INTO {0}.{1} (run_id,quantity_id,measurement,step) VALUES (%s,%s,%s,%s)
""".format(self.base.schema, "vector_real"
           if is_integer is False
           else "vector_integer")
        curs = self.base.performRequest(request, [self.id, quantity_id,
                                                  array, step])
        logger.debug(curs)
        logger.debug('ready to commit')
        self.base.commit()
        logger.debug('commited')

    def pushScalarQuantity(self, val, step, name,
                           is_integer, description=None):
        logger.debug('pushing {0}'.format(name))
        try:
            quantity_id, is_integer, is_vector = self.getQuantityID(
                name, is_integer=is_integer, is_vector=False)
        except Exception as e:
            typecode = "int"
            if is_integer is False:
                typecode = "float"
            quantity_id = self.base.pushQuantity(name, typecode, description)

        request = """
INSERT INTO {0}.{1} (run_id,quantity_id,measurement,step) VALUES (%s,%s,%s,%s)
""".format(self.base.schema, "scalar_real"
           if is_integer is False
           else "scalar_integer")
        curs = self.base.performRequest(request,
                                        [self.id, quantity_id, val, step])
        logger.debug(curs)
        logger.debug('ready to commit')
        self.base.commit()
        logger.debug('commited')

    def getAllVectorQuantity(self, name):
        quantity_id, is_integer, is_vector = self.getQuantityID(
            name, is_vector=True)

        request = """
SELECT step,measurement from {0}.{1}
WHERE (run_id,quantity_id) = ({2},{3}) order by step
""".format(self.base.schema, "vector_real"
           if is_integer is False
           else "vector_integer", self.id, quantity_id)
        curs = self.base.performRequest(request, [name])
        fetch = curs.fetchall()
        if (not fetch):
            return [None, None]
        matres = np.array([val[1] for val in fetch])
        stepres = np.array([val[0] for val in fetch])
        return (stepres, matres)

    def deleteData(self):
        request, params = (
            "DELETE FROM {0}.scalar_real WHERE run_id={1}".format(
                self.base.schema, self.id), [])
        self.base.performRequest(request, params)
        request, params = (
            "DELETE FROM {0}.scalar_integer WHERE run_id={1}".format(
                self.base.schema, self.id), [])
        self.base.performRequest(request, params)
        request, params = (
            "DELETE FROM {0}.vector_real WHERE run_id={1}".format(
                self.base.schema, self.id), [])
        self.base.performRequest(request, params)
        request, params = (
            "DELETE FROM {0}.vector_integer WHERE run_id={1}".format(
                self.base.schema, self.id), [])
        self.base.performRequest(request, params)

    def __init__(self):
        sqlobject.SQLObject.__init__(self, base)
        self.foreign_keys["job_id"] = "jobs"
        self.types["machine_name"] = str
        self.types["run_path"] = str
        self.allowNull["run_path"] = True
        self.types["job_id"] = int
        self.types["nproc"] = int
        self.types["run_name"] = str
        self.types["wait_id"] = int
        self.allowNull["wait_id"] = True
        self.types["start_time"] = datetime.datetime
        self.allowNull["start_time"] = True
        self.types["state"] = str
        self.allowNull["state"] = True
        self.execfile = None
        self.configfiles = []
        self.types["exec"] = str

################################################################


def getRunFromScript():
    parser = bdparser.BDParser()
    parser.register_params(params={"run_id": int})
    params = parser.parseBDParameters(argv=[])
    mybase = base.Base(**params)
    runSelector = runselector.RunSelector(mybase)
    run_list = runSelector.selectRuns(params)
    if len(run_list) > 1:
        raise Exception('internal error')
    if len(run_list) == 0:
        raise Exception('internal error')
    myrun, myjob = run_list[0]
    # myrun.setEntries(params)
    return myrun, myjob
