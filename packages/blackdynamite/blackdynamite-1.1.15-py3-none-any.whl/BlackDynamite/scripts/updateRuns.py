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
import BlackDynamite as BD
################################################################
import os
import sys
import argparse
################################################################


def main(argv=None):
    parser = BD.BDParser(description='updateRuns')
    group = parser.register_group('updateRuns')
    group.add_argument("--run_id", type=int,
                       help="The id of the run to update")
    group.add_argument(
        "command", nargs=argparse.REMAINDER,
        help="The updates to perform. Syntax should be 'key = newval'")

    params = parser.parseBDParameters(argv)

    if params['command']:
        params['updates'] = ' '.join(
            [e for e in params['command'] if not e.startswith('--')])
        params['updates'] = [e.strip() for e in params['updates'].split(',')]

    if "user" not in params.keys():
        params["user"] = os.getlogin()
    base = BD.Base(**params)

    try:
        myrun, myjob = BD.getRunFromScript()
        params['run_id'] = myrun.id
    except Exception:
        pass

    if "run_id" in params:
        if "constraints" not in params:
            params["constraints"] = []
        params["constraints"].append("runs.id = " + str(params["run_id"]))

    runSelector = BD.RunSelector(base)

    run_list = runSelector.selectRuns(params)

    if len(run_list) == 0:
        print("No runs to be updated")

    if "updates" not in params:
        print("No update to be performed: should be passed at command line")
        sys.exit(-1)

    for r, j in run_list:
        r.setFields(params["updates"])
        if params["truerun"] is True:
            r.update()
            base.commit()


if __name__ == "__main__":
    main()
