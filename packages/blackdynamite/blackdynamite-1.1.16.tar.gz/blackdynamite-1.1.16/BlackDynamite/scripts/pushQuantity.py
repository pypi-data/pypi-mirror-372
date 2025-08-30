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


def main(argv=None):
    parser = BD.BDParser(description='pushQuantity')
    group = parser.register_group('pushQuantity')
    group.add_argument('--run_id', type=int,
                       help="The id of the run to update")
    group.add_argument('--quantity_id', type=str,
                       help="ID of the Quantity to push")
    group.add_argument('--value', type=str,
                       help="Value tu push for the quantity")
    group.add_argument('--values', type=list,
                       help="Vectorial value tu push for the quantity")
    group.add_argument('--step', type=int, default=0,
                       help="Step at which the data is generated")

    params = parser.parseBDParameters(argv)

    if "run_id" not in params:
        myrun, myjob = BD.getRunFromScript()
        params['run_id'] = myrun.id
    if "quantity_id" not in params:
        raise Exception("The quantity id should be set")
    if "value" not in params and "values" not in params:
        raise Exception("The value should be set")

    is_vector = False
    if "values" in params:
        is_vector = True
        if "value" in params:
            raise Exception(
                "You cannot define values and value at the same time")

    base = BD.Base(**params)

    if "run_id" in params:
        if "constraints" not in params:
            params["constraints"] = []
            params["constraints"].append("runs.id = " + str(params["run_id"]))

    runSelector = BD.RunSelector(base)
    run_list = runSelector.selectRuns(params)

    if not len(run_list) == 1:
        raise Exception("No or too many runs selected")

    r = run_list[0][0]

    if params["truerun"] is True:
        if is_vector is False:
            r.pushScalarQuantity(
                params["value"], params["step"], params["quantity_id"])
        else:
            r.pushVectorQuantity(
                params["values"], params["step"], params["quantity_id"])
        base.commit()


if __name__ == '__main__':
    main()
