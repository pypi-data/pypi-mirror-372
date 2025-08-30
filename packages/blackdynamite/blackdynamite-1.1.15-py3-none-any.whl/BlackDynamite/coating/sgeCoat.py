#!/usr/bin/env python
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

from BlackDynamite import *
import subprocess

admissible_params = {"walltime": str, "email": str,
                     "nproc": int, "sge_option": [str], "module": [str]}
# default_params = {"walltime":"00:05:00"}
help = {"walltime": "Specify the wall time for the runs",
        "email": "Specify the email to notify",
        "nproc": "Force the number of processors and update the run",
        "sge_option": "Allow to provide additional SGE options",
        "module": "List of module to load"}


def launch(run, params):

    _exec = run.getExecFile()

    if ("walltime" not in params):
        raise Exception("walltime not set for this job {0}".format(run.id))

    head = \
        """#!/bin/bash
#$ -S /bin/sh
#$ -cwd
#$ -j y
#$ -notify
#$ -l walltime={0}
""".format(params["walltime"])

    if ("email" in params):
        head += "#$ -m eas -M {0}\n".format(params["email"])

    sge_head_name = "#$ -N " + "run" + \
        str(run.id) + "-" + run["run_name"] + "\n"
    sge_head_name = sge_head_name.replace(":", "_")
    head += sge_head_name

    run["state"] = "SGE submit"
    if ("nproc" in params):
        run["nproc"] = params["nproc"]

    nproc = run["nproc"]
    if (nproc % 12 == 0 and nproc % 8 == 0):
        head += "#$ -pe orte* " + str(nproc) + "\n"
    elif (nproc % 12 == 0):
        head += "#$ -pe orte12 " + str(nproc) + "\n"
    elif (nproc % 8 == 0):
        head += "#$ -pe orte8 " + str(nproc) + "\n"

    if ("sge_option" in params):
        for i in params["sge_option"]:
            head += "#$ {0}\n".format(i)

    if ("module" in params):
        for i in params["module"]:
            head += "module load {0}\n".format(i)

    run.update()

    head += """

export BLACKDYNAMITE_HOST=__BLACKDYNAMITE__dbhost__
export BLACKDYNAMITE_SCHEMA=__BLACKDYNAMITE__study__
export BLACKDYNAMITE_STUDY=__BLACKDYNAMITE__study__
export BLACKDYNAMITE_RUN_ID=__BLACKDYNAMITE__run_id__
export BLACKDYNAMITE_USER=""" + params["user"] + """

on_kill()
{
updateRuns.py --updates \"state = SGE killed\" --truerun
exit 0
}

on_stop()
{
updateRuns.py --updates \"state = SGE stopped\" --truerun
exit 0
}

# Execute function on_die() receiving TERM signal
#
trap on_stop SIGUSR1
trap on_kill SIGUSR2

"""

    _exec["file"] = run.replaceBlackDynamiteVariables(head) + _exec["file"]

    f = open(_exec["filename"], 'w')
    f.write(_exec["file"])
    f.close()
    # os.chmod(_exec["filename"], stat.S_IRWXU)
    print("execute qsub ./" + _exec["filename"])
    print("in dir ")
    subprocess.call("pwd")
    if params["truerun"] is True:
        ret = subprocess.call("qsub " + _exec["filename"], shell=True)
