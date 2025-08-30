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

from . import conffile
from . import run
from . import bdparser


class RunLM(run.Run):
    """
    """

    def attachToJob(self, job):
        if "exec" not in self.entries:
            self.createLaunchFile()

        if "lm_conf" in self.entries:
            self.addConfigFiles([self.entries["lm_conf"]])

        run.Run.attachToJob(self, job)

    def addConfigFiles(self, file_list, regex_params='LET\s+%p\s*=\s*%v'):
        run.Run.addConfigFiles(self, file_list, regex_params=regex_params)
        return self.configfiles

    def createLaunchFile(self):
        self.execfile = conffile.addFile("launch.sh", self.base,
                                         content="""
export HOST=__BLACKDYNAMITE__dbhost__
export SCHEMA=__BLACKDYNAMITE__study__
export RUN_ID=__BLACKDYNAMITE__run_id__
export DEBUG_LEVEL=0
mpirun __BLACKDYNAMITE__mpi_option__ -np __BLACKDYNAMITE__nproc__ \
__BLACKDYNAMITE__amel_path__ __BLACKDYNAMITE__lm_conf__ \
__BLACKDYNAMITE__nsteps__
if [ $? != 0 ]; then
updateRuns.py --study=$SCHEMA --host=$HOST --run_constraints="id = $RUN_ID" \
--updates="state = LM FAILED" --truerun
fi
""")
        self["exec"] = self.execfile.id
        return self.execfile

    def __init__(self, base):
        run.Run.__init__(self, base)

        self.types["amel_path"] = str
        self.types["nsteps"] = int
        self.types["lm_conf"] = str
        self.types["mpi_option"] = str
        self.types["lm_release_info"] = str
        self.allowNull["lm_release_info"] = True

################################################################


class RunLMParser(bdparser.RunParser):

    def parseBDParameters(self):
        params = bdparser.RunParser.parseBDParameters(self)

        return params

    def __init__(self):
        bdparser.RunParser.__init__(self)
        self.mandatory["nsteps"] = True
        self.mandatory["amel_path"] = True
        self.mandatory["lm_conf"] = True

        self.admissible_params["nsteps"] = int
        self.help["nsteps"] = "Set the number of steps to run"
        self.admissible_params["amel_path"] = str
        self.help["amel_path"] = (
            "The path to the libmultiscale client executable AMEL")
        self.admissible_params["lm_conf"] = str
        self.help["lm_conf"] = (
            "The name of the configuration file for libmultiscale")
        self.admissible_params["mpi_option"] = str
        self.help["mpi_option"] = "optional MPI option"

        self.default_params["mpi_option"] = " "

        self.group_params["RunLM"] = [
            "amel_path",
            "nsteps",
            "lm_conf",
            "mpi_option",
            "lm_release_info"]

################################################################
