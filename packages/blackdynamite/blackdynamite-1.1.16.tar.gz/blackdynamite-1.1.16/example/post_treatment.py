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
import matplotlib.pyplot as plt
################################################################
# basic connection
parser = BD.BDParser()
group = parser.register_group("post_treatment")
group.add_argument('--no_show', action='store_true')
params = parser.parseBDParameters()
no_show = params['no_show']
mybase = BD.Base(**params)
################################################################


# function to plot things (user's job)
def plot(run_list, no_show):
    for r, j in run_list:
        step, ekin = r.getScalarQuantity('ekin')
        if ekin is None:
            continue
        print(j)
        list_files = r.listFiles()
        print(list_files)
        fname = r.getFile(list_files[3])
        print(fname + ':')
        _file = open(fname)
        print(_file.read())
        plt.plot(step, ekin, 'o-',
                 label='$p_2 = {0}$'.format(j['param2']))

        vect = r.getVectorQuantity('random_vect', 1)
        print(vect)
    plt.legend(loc='best')
    if not no_show:
        plt.show()
################################################################


# selecting some runs
runSelector = BD.RunSelector(mybase)
run_list = runSelector.selectRuns(params)
plot(run_list, no_show)

# selecting some other runs
params['constraints'] = ['run_name = test', 'state = FINISHED', 'param2 > 1']
run_list = runSelector.selectRuns(params)
plot(run_list, no_show)
