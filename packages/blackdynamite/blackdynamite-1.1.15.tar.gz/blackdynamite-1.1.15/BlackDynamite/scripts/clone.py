#!/usr/bin/env python

import os
import subprocess

import BlackDynamite as BD


def main(argv=None):
    parser = BD.bdparser.BDParser()
    group = parser.register_group('clone')
    group.add_argument("remote_URI", help="The remote uri where the BD study is stored (must be a git repository)")
    group.add_argument("dest_dir", help="Directory where to clone")
    group.add_argument("--deep-copy", action='store_true')

    params = parser.parseBDParameters(argv)

    if os.path.exists(params['dest_dir']):
        raise RuntimeError(f"FATAL: cannot clone {params['dest_dir']} as it already exists")

    remote = params['remote_URI']
    if os.path.isdir(remote):
        remote = os.path.abspath(remote)
    command = ["git", "clone", remote, params['dest_dir']]
    p = subprocess.run(command)
    if p.returncode != 0:
        raise RuntimeError("An error occurred while GIT-cloning")

    os.chdir(params['dest_dir'])
    os.mkdir('.bd')
    command = ["rsync", "-au", "--info=progress2",
               os.path.join(remote, '.bd', 'zeo.blob'), ".bd/"]
    p = subprocess.run(command)
    if p.returncode != 0:
        raise RuntimeError("An error occurred while retrieving the database")

    for fname in ['zeo.conf', 'zdaemon.conf']:
        command = ["rsync", "-au", "--info=progress2",
                   os.path.join(remote, '.bd', fname), ".bd/"]
        p = subprocess.run(command)
        if p.returncode != 0:
            raise RuntimeError("An error occurred while retrieving the database configuration")

    if params['deep_copy']:
        command = ["rsync", "-au", "--info=progress2",
                   os.path.join(remote, '.bd') , "."]
        p = subprocess.run(command)
        if p.returncode != 0:
            raise RuntimeError("An error occurred while retrieving the entire database")

        os.remove('.bd/zeo.conf')
        os.system('rm -rf .bd/*.lock')
        os.system('rm -rf .bd/*.socket')

    print(f"{'deep' if params['deep_copy'] else ''} clone of {remote} created in {params['dest_dir']}")


if __name__ == "__main__":
    main()
