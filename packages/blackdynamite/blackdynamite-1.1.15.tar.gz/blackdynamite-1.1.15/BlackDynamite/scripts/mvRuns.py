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
from __future__ import print_function
################################################################
import BlackDynamite as BD
import os
import subprocess
import socket
################################################################


def move_run(r,
             machine_src, machine_dst,
             path_src, path_dst):

    if path_src == path_dst and machine_dst == machine_src:
        return

    if not os.path.exists(path_dst):
        os.makedirs(path_dst)

    # print(machine_src, machine_dst)
    # print(path_src, path_dst)

    url_src = machine_src + ':' + path_src
    if url_src[-1] == '/':
        url_src = url_src[:-1]

    print('mv run,job:', r.id, j.id)
    url_dst = path_dst

    if machine_src == machine_dst:
        url_src = path_src
    else:
        url_src = machine_src + ':' + path_src

    if url_src[-1] == '/':
        url_src = url_src[:-1]
    if url_dst[-1] == '/':
        url_dst = url_dst[:-1]

    rsync_command = 'rsync --remove-source-files -auP {0} {1}'.format(
        url_src, url_dst)
    print(rsync_command)
    if params['truerun'] is True:
        ret = subprocess.call(rsync_command, shell=True)
    else:
        ret = True
    if ret:
        return

    r['run_path'] = path_dst
    r['machine_name'] = machine_dst
    r.update()
    if params['truerun'] is True:
        mybase.commit()

################################################################


parser = BD.BDParser()
parser.register_params(
    group="mvRuns",
    params={"path": str},
    mandatory={'path': True},
    help={"path": "Path to the local machine where to store the run outputs"})

params = parser.parseBDParameters()
mybase = BD.Base(**params)


runSelector = BD.RunSelector(mybase)
run_list = runSelector.selectRuns(params, params, quiet=True)
for r, j in run_list:
    machine_dst = socket.gethostname()
    machine_src = r['machine_name']
    path_src = r['run_path']
    if path_src is None:
        continue

    f, p = os.path.split(path_src)
    while p == '':
        f, p = os.path.split(f)
    run_subdir = p

    path_dst = os.path.join(params['path'],
                            "BD-" + params["study"] + "-runs",
                            run_subdir)

    move_run(r, machine_src, machine_dst, path_src, path_dst)
