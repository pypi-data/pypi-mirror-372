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

import BlackDynamite as BD
import os
import sys
import subprocess


def saveSchema(params):
    if "out_file" not in params:
        out_file = os.path.join("./", params["study"] + ".db")
    else:
        out_file = params["out_file"]

    r, ext = os.path.splitext(out_file)
    if (not ext == ".gz"):
        out_file += ".gz"

    print("Saving study " + params["study"] + " to file " + out_file)

    command = ("pg_dump --dbname blackdynamite --host " + params["host"] +
               " --schema=" + params["study"] + " -C -f " +
               out_file + " --compress=9")

    if params["verbose"] is True:
        command += " --verbose"

    print(command)
    command = command.split(" ")
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)

    out = p.stdout.read()
    out = p.stderr.read()
    p.stdin.write(params["password"].encode())
    print(out)
    p.wait()
    if not p.returncode == 0:
        sys.exit("pg_dump error")


def main(argv=None):
    if isinstance(argv, str):
        argv = argv.split()

    parser = BD.BDParser()
    parser.register_params(
        group="saveBDStudy.py",
        params={"out_file": str, "verbose": bool, "study": str},
        help={"out_file": "Specify the filename where to save the study",
              "verbose": "Activate the verbose mode of pg_dump",
              "study": "specify the study to backup. \
    If none provided all studies are backed up"})

    params = parser.parseBDParameters(argv=argv)
    params["should_not_check_study"] = True
    mybase = BD.Base(**params)

    if ("study" in params):
        saveSchema(params)
    else:
        if "out_file" in params:
            del params["out_file"]
        sch_list = mybase.getSchemaList()
        for s in sch_list:
            params["study"] = s
            saveSchema(params)


if __name__ == '__main__':
    main()
