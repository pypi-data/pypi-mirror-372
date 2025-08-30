#!/usr/bin/env python3

import subprocess


def _run(cmd):
    print(cmd)
    ret = subprocess.call(cmd, cwd="massive_example", shell=True)
    assert ret == 0


def __test_zeo():
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")
    _run("canYouDigIt init --truerun --yes")
    _run("canYouDigIt jobs create --truerun --yes")
    _run("canYouDigIt runs create --run_name test --truerun")
    _run("canYouDigIt runs info --truerun")
    _run("canYouDigIt runs launch --truerun")
    _run("canYouDigIt full-update --run_name test --truerun")
    _run("canYouDigIt runs plot --list_quantities")
    _run("canYouDigIt runs info --run_id 1")
    _run("canYouDigIt runs exec --run_id 1 ls")
    _run("canYouDigIt info")
    _run("canYouDigIt runs update --truerun nproc = 2")
    _run("canYouDigIt runs plot --quantity ekin --fileout tmp.pdf")
    _run("python post_treatment.py --no_show")
    _run("canYouDigIt server stop")
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")


def __test_server():
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")
    _run("canYouDigIt init --truerun --yes")
    _run("canYouDigIt server start")
    _run("canYouDigIt server status")
    _run("canYouDigIt server stop")
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")


def __test_tcp_server():
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")
    _run("canYouDigIt init --truerun --yes")
    _run("canYouDigIt server stop")
    _run("canYouDigIt --verbose server start --host zeo://localhost:6666")
    _run("canYouDigIt server status")
    _run("canYouDigIt server status --host zeo://localhost:6666")
    _run("canYouDigIt server stop")
    _run("rm -rf .bd bd.log BD-bd_study-runs test.pdf tmp.pdf")
