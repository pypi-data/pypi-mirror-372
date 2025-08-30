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
################################################################
import os
import sys
################################################################
from abc import ABC, abstractmethod

################################################################
from . import bdlogging, bdparser, jobselector

__all__ = ["Base"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class AbstractBase(ABC):
    """ """

    @property
    def Job(self):
        raise RuntimeError("abstractmethod")

    @property
    def Run(self):
        raise RuntimeError("abstractmethod")

    @abstractmethod
    def getSchemaList(self, filter_names=True):
        return []

    @abstractmethod
    def retreiveSchemaName(self, creation=False, **kwargs):
        pass

    @abstractmethod
    def insert(self, zeoobject, keep_state=False):
        pass

    @abstractmethod
    def commit(self):
        pass

    def getRunFromID(self, run_id):
        myrun = self.Run(self)
        myrun["id"] = run_id
        myrun.id = run_id
        run_list = myrun.getMatchedObjectList()
        if len(run_list) != 1:
            raise Exception("Unknown run {0}".format(run_id))

        return run_list[0]

    def getJobFromID(self, job_id):
        myjob = self.Job(self)
        myjob["id"] = job_id
        myjob.id = job_id
        job_list = myjob.getMatchedObjectList()
        if len(job_list) != 1:
            raise Exception("Unknown run {0}".format(job_id))

        return job_list[0]

    def _createParameterSpace(self, entries, entry_nb=0, entries_desc=None):
        """
        This function is a recursive call to generate the points
        in the parametric space

        The entries of the jobs are treated one by one
        in a recursive manner
        """

        created_entries = []
        keys = list(entries.keys())
        nparam = len(keys)

        if entry_nb == nparam:
            return [entries]

        key = keys[entry_nb]
        e = entries[key]

        if not isinstance(e, list):
            e = [e]

        if entries_desc is not None:
            if entries_desc.types[key] == list:
                tmp_entries = dict(entries)
                return self._createParameterSpace(tmp_entries, entry_nb + 1)

        for value in e:
            tmp_entries = dict(entries)
            tmp_entries[key.lower()] = value
            created_entries += self._createParameterSpace(tmp_entries, entry_nb + 1)

        return created_entries

    def createParameterSpace(
        self,
        myjob,
        progress_report=False,
        params={"yes": False},
    ):
        """
        This function is a recursive call to generate the points
        in the parametric space

        The entries of the jobs are treated one by one
        in a recursive manner
        """

        space = self._createParameterSpace(dict(myjob.entries))
        space_size = len(space)

        if space_size > 100:
            validated = bdparser.validate_question(
                f"You are about to create/update {space_size} jobs",
                params,
                False,
            )
            if validated is False:
                return 0

        if progress_report:
            from tqdm import tqdm
        else:

            def original_tqdm(x):
                return x

            tqdm = original_tqdm

        nb_inserted = 0

        for e in tqdm(space):
            tmp_job = self.Job()
            tmp_job.entries = e
            jselect = jobselector.JobSelector(self)
            jobs = jselect.selectJobs(tmp_job, quiet=True)

            # check if already inserted
            if len(jobs) > 0:
                continue

            # insert it
            nb_inserted += 1
            logger.debug(
                "insert job #{0}".format(nb_inserted) + ": " + str(tmp_job.entries)
            )
            self.insert(tmp_job)

        if self.truerun:
            self.commit()
        return nb_inserted

    @abstractmethod
    def getStudySize(self, study):
        raise RuntimeError("abstract method")

    def checkStudy(self, dico):
        if "study" not in dico:
            schemas = self.getSchemaList()
            if len(schemas) == 1:
                dico["study"] = schemas[0]
                return
            message = "\n" + "*" * 30 + "\n"
            message += "Parameter 'study' must be provided at command line\n"
            message += "possibilities are:\n"
            for s in schemas:
                message += "\t" + s + "\n"
            message += "\n"
            message += "FATAL => ABORT\n"
            message += "*" * 30 + "\n"
            logger.error(message)
            sys.exit(-1)

    def __init__(self, read_only=False, connection=None, truerun=False, **kwargs):
        self.read_only = read_only
        self.connection = connection

        if "user" in kwargs:
            self.user = kwargs["user"]
        else:
            self.user = getpass.getuser()

        if "should_not_check_study" not in kwargs:
            self.checkStudy(kwargs)

        self.truerun = truerun

        if "list_parameters" in kwargs and kwargs["list_parameters"] is True:
            message = self.getPossibleParameters()
            logger.debug("\n{0}".format(message))
            sys.exit(0)

    def getPossibleParameters(self):
        myjob = self.Job()
        message = ""
        message += "*" * 65 + "\n"
        message += "Job parameters:\n"
        message += "*" * 65 + "\n"
        params = [str(j[0]) + ": " + str(j[1]) for j in myjob.types.items()]
        message += "\n".join(params) + "\n"

        myrun = self.Run()
        message += "*" * 65 + "\n"
        message += "Run parameters:\n"
        message += "*" * 65 + "\n"
        params = [str(j[0]) + ": " + str(j[1]) for j in myrun.types.items()]
        message += "\n".join(params)
        return message


################################################################


def find_root_path(path="./"):
    path = os.path.abspath(path)
    tmp = os.path.join(path, ".bd")
    if os.path.exists(tmp):
        return os.path.abspath(path)

    abs_path = os.path.abspath(path)
    head, tail = os.path.split(abs_path)
    while (head != "") and (head != "/"):
        tmp = os.path.join(head, ".bd")
        if os.path.exists(tmp):
            return os.path.abspath(head)
        head, tail = os.path.split(head)
    raise RuntimeError(f"Could not find a BlackDynamite root directory from {path}")


################################################################


def Base(**params):
    if "host" in params and params["host"] is not None:
        host = params["host"]
        host_split = host.split("://")
        if host_split[0] == "file":
            raise RuntimeError("cannot use sqlit anymore")
        # from . import base_sqlite
        # params['host'] = host_split[1]
        # return base_sqlite.BaseSQLite(**params)
    from . import base_zeo

    return base_zeo.BaseZEO(**params)
