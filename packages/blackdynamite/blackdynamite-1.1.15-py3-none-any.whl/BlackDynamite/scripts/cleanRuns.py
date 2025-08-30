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
################################################################
################################################################
import os
import re
import shutil
import socket
import sys

import tqdm

import BlackDynamite as BD

################################################################


def validate(question, params):
    if params["truerun"] is True:
        validated = BD.bdparser.validate_question(question, params)
    else:
        print("{0}? Forced N".format(question))
        validated = False

    return validated

################################################################


def main(argv=None):
    parser = BD.BDParser(description='cleanRuns')
    group = parser.register_group("cleanRuns")
    group.add_argument(
        "--run_id", type=int,
        help="In case cleaning a single run: ID of this specific run")
    group.add_argument("--clean_orphans", type=str)
    group.add_argument("--machine_name", type=str, default=socket.gethostname(),
                       help="Machine name for desired runs")
    group.add_argument("--delete", action='store_true',
                       help="Entirely remove runs from database")

    params = parser.parseBDParameters(argv)
    if "constraints" not in params:
        params["constraints"] = []

    if "run_id" in params:
        params["constraints"].append("runs.id = " + str(params["run_id"]))

    if "machine_name" in params:
        machine_already_constrained = False
        for e in params["constraints"]:
            if 'machine_name' in e:
                machine_already_constrained = True
        if not machine_already_constrained:
            params["constraints"].append(
                "machine_name = " + params["machine_name"])

    base = BD.Base(**params)
    runSelector = BD.RunSelector(base)

    if "clean_orphans" in params:
        run_list = runSelector.selectRuns([])
        run_ids = [r.id for r, j in run_list]
        resdir = params["clean_orphans"] + "/BD-" + params["study"] + "-runs"
        print("clean orphans from " + resdir)

        if not os.path.exists(resdir):
            print("Directory '" + resdir + "' do not exists")
            sys.exit(-1)

        to_delete = {}
        for filename in os.listdir(resdir):
            fullname = os.path.join(resdir, filename)
            # print(fullname)
            if (os.path.isdir(fullname)):
                match = re.match("run-([0-9]+)", filename)
                if (match):
                    # print(filename)
                    id = int(match.group(1))
                    if (id not in run_ids):
                        to_delete[id] = fullname
        if (len(to_delete.keys()) == 0):
            print("No orphans found")
            sys.exit(0)

        validated = validate("Delete output from runs " +
                             str(to_delete.keys()), params)
        if validated:
            for id, fullname in to_delete.items():
                # print("Delete output from run " + str(id))
                shutil.rmtree(fullname)

        sys.exit(0)

    runSelector = BD.RunSelector(base)
    run_list = runSelector.selectRuns(params, quiet=True)

    if len(run_list) == 0:
        print("No runs selected")
        sys.exit()

    delete_flag = params["delete"]
    if delete_flag:
        validated = validate(f"Delete {len(run_list)} runs", params)
    else:
        validated = validate(f"Reset {len(run_list)} runs", params)

    for i, (r, j) in enumerate(tqdm.tqdm(run_list)):

        if "run_path" in r:
            run_path = r["run_path"]
        else:
            run_path = None
        if run_path:
            if os.path.exists(run_path):
                if (validated):
                    # print("Deleting directory: " + run_path)
                    shutil.rmtree(run_path)
                else:
                    # print("Simulate deletion of directory: " + run_path)
                    pass
            else:
                print("output directory: '" + run_path +
                      "' not found: are we on the right machine ?")

        if delete_flag:
            if validated:
                # print("Deleting run " + str(r.id) + " from base")
                r.delete()
            else:
                print("Simulate deletion of run " + str(r.id) + " from base")
        else:
            if validated:
                # print("Deleting data associated with run " + str(r.id))
                r.deleteData()
                r["STATE"] = "CREATED"
                r["start_time"] = None
                r.update()
            else:
                # print("Simulate deletion of data associated with run " + str(r.id))
                pass

        if i % 1000 == 0:
            # if truerun, commit the changes to the base
            if params["truerun"] is True:
                base.commit()

    if validated:
        base.pack()


if __name__ == "__main__":
    main()
