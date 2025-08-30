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
################################################################
import os
import stat
import subprocess
################################################################


def register_param(parser):
    group = parser.register_group("bashCoat")
    group.add_argument(
        "--stdout", action='store_true',
        help="Specify if you want the standard output instead of a file")
    group.add_argument(
        "--stop_on_error", action='store_true',
        help="Specify if should raise an error in case "
        "of an error in the bash script")

################################################################


def launch(run, params):

    _exec = run.getExecFile()
    head = \
        """#!/bin/bash
export BLACKDYNAMITE_HOST=__BLACKDYNAMITE__dbhost__
export BLACKDYNAMITE_STUDY=__BLACKDYNAMITE__study__
export BLACKDYNAMITE_SCHEMA=__BLACKDYNAMITE__study__
export BLACKDYNAMITE_RUN_ID=__BLACKDYNAMITE__run_id__
export BLACKDYNAMITE_USER={0}
""".format(params["user"])

    _exec["file"] = run.replaceBlackDynamiteVariables(head) + _exec["file"]
    f = open(_exec["filename"], 'w')
    f.write(_exec["file"])
    f.close()
    os.chmod(_exec["filename"], stat.S_IRWXU)
    print("execute ./" + _exec["filename"])
    run.commit()
    if params["truerun"] is True:
        run["state"] = "launched"
        run.update()
        run.commit()
        filename = run["run_name"] + ".o" + str(run.id)
        filename_err = run["run_name"] + ".e" + str(run.id)

        if params["stdout"] is True:
            ret = subprocess.call("./" + _exec["filename"])
        else:
            with open(filename, "w") as outfile:
                with open(filename_err, "w") as errfile:
                    ret = subprocess.call(
                        "./" + _exec["filename"],
                        stdout=outfile,
                        stderr=errfile)

        if ret == 0:
            run["state"] = "FINISHED"
        else:
            run["state"] = "BASH error"
        run.update()
        run.commit()

        if (("stop_on_error" in params) and
                (params["stop_on_error"] is True) and
                not ret == 0):
            raise Exception(
                "The underlying bash script returned "
                "with the error code {0}.".format(ret))
        pass
