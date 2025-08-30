#!/usr/bin/env python3

import subprocess
import socket


def _run(cmd):
    print(cmd)
    ret = subprocess.call(cmd, cwd='../example', shell=True)
    assert ret == 0


def test_psql():
    _run('createDB.py --bdconf localhost.bd --study test --truerun --yes')
    _run('createJobs.py --bdconf localhost.bd --study test --truerun --yes')
    _run(
        f'createRuns.py --bdconf localhost.bd --study test --machine_name {socket.gethostname()} --nproc 1 --run_name test --truerun')
    _run('getRunInfo.py --bdconf localhost.bd --study test --truerun')
    _run('launchRuns.py --bdconf localhost.bd --study test --outpath /tmp/ --truerun')
    _run('canYouDigIt.py --bdconf localhost.bd --study test --list_quantities')
    _run('canYouDigIt.py --bdconf localhost.bd --study test --quantity ekin --fileout tmp.pdf')
    _run('post_treatment.py --bdconf localhost.bd --study test')
