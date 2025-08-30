#!/usr/bin/env python

import os
import subprocess

import git

import BlackDynamite as BD
from BlackDynamite.base import find_root_path


def main(argv=None):
    parser = BD.bdparser.BDParser()
    group = parser.register_group('pull')
    group.add_argument("--fetch_runs_data", action='store_true')
    group.add_argument("--remote", type=str, default=None)

    root_path = find_root_path(path="./")
    root_path = os.path.abspath(root_path)
    print('RootPath: ', root_path)
    os.chdir(root_path)
    params = parser.parseBDParameters(argv)
    mybase = BD.Base(**params)

    if 'remote' not in params:
        params['remote'] = None

    print('BD study: ', mybase.schema)
    repo = git.Repo('.')
    remotes = repo.remotes

    print('Remotes: ', [e.name for e in remotes])

    if not remotes:
        raise RuntimeError("Cannot pull as there is no (git) remote defined")
    elif len(remotes) > 1 and params['remote'] is None:
        raise RuntimeError(f"You have to choose a remote from {[e.name for e in remotes]}")
    elif params['remote'] in [e.name for e in remotes]:
        remote = [e for e in remotes if e.name == params['remote']][0]
    elif len(remotes) == 1:
        remote = remotes[0]
    else:
        raise RuntimeError("should not happen")

    print(f'Pulling: from {remote.name}:{remote.url}')

    command = ["rsync", "-au", "--info=progress2",
               os.path.join(remote.url, '.bd', 'zeo.blob'), ".bd/"]
    p = subprocess.run(command)
    if p.returncode != 0:
        raise RuntimeError("An error occurred while retrieving the database")

    for fname in ['zeo.conf', 'zdaemon.conf']:
        command = ["rsync", "-au", "--info=progress2",
                   os.path.join(remote.url, '.bd', fname), ".bd/"]
        p = subprocess.run(command)
        if p.returncode != 0:
            raise RuntimeError("An error occurred while retrieving the database configuration")

    if params['fetch_runs_data']:
        raise RuntimeError("FATAL: Fetching runs data is not yet a working feature")
        command = ["rsync", "-au", "--info=progress2",
                   "BD-", "."]
        p = subprocess.run(command, cwd=params['dest_dir'])
        if p.returncode != 0:
            raise RuntimeError("An error occurred while retrieving the database")


if __name__ == "__main__":
    main()
