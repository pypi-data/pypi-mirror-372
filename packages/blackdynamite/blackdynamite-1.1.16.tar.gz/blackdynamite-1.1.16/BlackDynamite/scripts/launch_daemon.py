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

import getpass
################################################################
import os
import socket
import time

import psutil

################################################################
import BlackDynamite as BD

from .launchRuns import launch

################################################################


def find_pids(root_dir):
    pids = []
    for p in psutil.process_iter(["pid", "username"]):
        username = p.username()
        if username != getpass.getuser():
            continue
        pid = p.pid
        if p.status() == psutil.STATUS_ZOMBIE:
            p.kill()
            continue
        if "canYouDigIt" not in p.cmdline():
            continue

        if root_dir != p.cwd():
            continue

        cmd = p.cmdline()
        if "launch_daemon" not in cmd:
            continue

        pids.append(pid)
    return pids


################################################################


def main(argv=None):

    parser = BD.BDParser(description="launcher daemon")
    group = parser.register_group("launchDaemon")
    group.add_argument(
        "--wait",
        type=str,
        default=5,
        help="Waiting time between launch of the runs in seconds",
    )
    group.add_argument(
        "--outpath",
        type=str,
        default=os.path.realpath("./"),
        help="Where to store the run output",
    )
    group.add_argument(
        "--generator",
        type=lambda s: parser.parseModuleName(s),
        default="bashCoat",
        help="Set job generator",
    )
    group.add_argument(
        "--nruns",
        type=int,
        default=-1,
        help=("Specify the number of runs to launch at each iteration"),
    )
    group.add_argument("--machine_name", type=str, default=socket.gethostname())

    group.add_argument(
        "--status", action="store_true", help="get status of detached launch daemon"
    )
    group.add_argument("--start", action="store_true", help="start launch daemon")
    group.add_argument("--stop", action="store_true", help="stop launch daemon")

    group.add_argument(
        "--detach",
        "-d",
        action="store_true",
        help="For starting: run in detach/daemon mode with Zdaemon manager",
    )
    params = parser.parseBDParameters(argv)
    mybase = BD.Base(**params)
    bd_dir = mybase.bd_dir
    root_dir = mybase.root_dir
    del mybase

    conf_fname = os.path.join(bd_dir, "launch.conf")

    if params["start"] and not params["detach"]:
        while True:
            params["truerun"] = True
            launch(params)
            time.sleep(params["wait"])

    elif params["start"] and params["detach"]:
        exclude = ["--detach", "-d"]
        clargs = " ".join([a for a in parser.argv if a not in exclude])

        prog = f"canYouDigIt launch_daemon {clargs}"

        zdaemon_conf = f"""
<runner>
 program {prog}
 socket-name {bd_dir}/launch.socket
 transcript {bd_dir}/launch.log
</runner>
"""

        os.makedirs(bd_dir, exist_ok=True)
        with open(conf_fname, "w") as f:
            f.write(zdaemon_conf)

        os.system(f"zdaemon -C {conf_fname} start")
        os.system(f"zdaemon -C {conf_fname} status")

    elif params["status"]:
        print("ZDaemon status:")
        if os.path.exists(conf_fname):
            os.system(f"zdaemon -C {conf_fname} status")
        else:
            print("  Daemon not initialized")
        pids = find_pids(root_dir)
        print(f"Running launchers pids: {pids}")

    elif params["stop"]:
        os.system(f"zdaemon -C {conf_fname} stop")
        pids = find_pids(root_dir)
        if pids:
            print(f"Killing: {pids}")
            pids = [str(e) for e in pids]
            os.system(f"kill -9 {' '.join(pids)}")


if __name__ == "__main__":
    main()
