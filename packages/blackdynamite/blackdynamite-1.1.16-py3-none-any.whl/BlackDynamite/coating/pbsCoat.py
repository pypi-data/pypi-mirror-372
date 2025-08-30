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
import os
import stat
import subprocess
import re
import socket


admissible_params = {"walltime": str,
                     "email": str,
                     "nproc": int,
                     "pbs_option": [str],
                     "module": [str],
                     "mpiprocs": int,
                     "ncpus": int,
                     "cwd": bool}
default_params = {"walltime": "48:00:00",
                  "cwd": True}
help = {"walltime": "Specify the wall time for the runs",
        "email": "Specify the email to notify",
        "nproc": "Force the number of processors and update the run",
        "pbs_option": "Allow to provide additional PBS options",
        "module": "List of module to load",
        "ncpus": "Number of cpus per nodes",
        "mpiprocs": "Number of mpi processus per nodes",
        "cwd": "Run by default in the run folder"}


def launch(run, params):

    _exec = run.getExecFile()
    head = \
        """#!/bin/bash

#PBS -l walltime={0}
""".format(params["walltime"])

    if ("email" in params):
        head += "#PBS -m abe\n"
        head += "#PBS -M {0}\n".format(params["email"])

    pbs_head_name = "#PBS -N {0}_{1}\n".format(run["run_name"], run.id)
    head += pbs_head_name

    run["state"] = "PBS submit"
    if ("nproc" in params):
        run["nproc"] = params["nproc"]

    nproc = run["nproc"]
    if ("mpiprocs" in params or "npcus" in params):
        args = []
        if "ncpus" in params:
            npernode = params["ncpus"]
            args.append("ncpus={0}".format(npernode))

        if "mpiprocs" in params:
            npernode = min(params["mpiprocs"], nproc)
            args.append("mpiprocs={0}".format(npernode))

        select = max(1, nproc/npernode)
        args.insert(0, "#PBS -l select={0}".format(select))
        select_str = ":".join(args)
        print(select_str)
        head += select_str + "\n"
    else:
        head += "#PBS -l nodes=" + str(nproc) + "\n"

    if ("pbs_option" in params):
        for i in params["pbs_option"]:
            head += "#PBS {0}\n".format(i)

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
updateRuns.py --updates \"state = PBS killed\" --truerun
exit 0
}

on_stop()
{
updateRuns.py --updates \"state = PBS stopped\" --truerun
exit 0
}

# Execute function on_die() receiving TERM signal
#
trap on_stop SIGUSR1
trap on_stop SIGTERM
trap on_kill SIGUSR2
trap on_kill SIGKILL
"""

    if (params["cwd"]):
        head += """
cd __BLACKDYNAMITE__run_path__
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
