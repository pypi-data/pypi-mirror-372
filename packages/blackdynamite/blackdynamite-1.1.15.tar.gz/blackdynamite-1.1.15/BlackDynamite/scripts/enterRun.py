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
import subprocess
import os
import sys
import socket
import argparse
################################################################


def print_full_run_info(job, run):
    separator = '-'*30
    print(separator)
    print("JOB INFO")
    print(separator)
    print(job)
    print(separator)
    print("RUN INFO")
    print(separator)
    print(run)
    print(separator)


def main(argv=None):
    parser = BD.BDParser(description='enterRun')
    group = parser.register_group("enterRun")
    group.add_argument("--run_id", type=int,
                       help="Select a run_id to enter context")
    group.add_argument("--order", type=str)
    group.add_argument("command", nargs=argparse.REMAINDER)

    params = parser.parseBDParameters(argv)
    if params['command']:
        params['command'] = ' '.join(params['command']).strip()
    else:
        del params['command']

    mybase = BD.Base(**params)

    if 'run_id' in params:
        params['run_constraints'] = ['id = {0}'.format(params['run_id'])]
        try:
            del params['job_constraints']
        except Exception:
            pass

    runSelector = BD.RunSelector(mybase)
    run_list = runSelector.selectRuns(params, quiet=True)
    mybase.close()

    if len(run_list) == 0:
        print("no run found")
        sys.exit(1)

    run, job = run_list[0]
    run_id = run['id']

    if 'command' not in params:
        print_full_run_info(job, run)
        print(f"LOGGING TO '{run['machine_name']}'")
    else:
        print(
            f"Run #{run.id}: {run['machine_name']}> {params['command']}")

    separator = '-'*30
    print(separator)

    if run['state'] == 'CREATED':
        print("Cannot enter run: not yet started")
        sys.exit(-1)

    bashrc_filename = os.path.join(
        '/tmp', 'bashrc.user{0}.study{1}.run{2}'.format(params['user'],
                                                        mybase.schema,
                                                        run_id))
    bashrc = open(bashrc_filename, 'w')
    bashrc.write('export PS1="\\u@\\h:<{0}|RUN-{1}> $ "\n'.format(
        mybase.schema, run_id))
    bashrc.write('cd {0}\n'.format(run['run_path']))
    bashrc.close()

    command_login = 'bash --rcfile {0} -i'.format(bashrc_filename)
    if 'command' in params:
        command_login += f' -c "{params["command"]}"'

    if ((not run['machine_name'] == socket.gethostname()) and
            (not run['machine_name'] == 'localhost')):
        command1 = 'scp -q {0} {1}:{0}'.format(bashrc_filename,
                                               run['machine_name'])
        subprocess.call(command1, shell=True)

        command_login = 'ssh -X -A -t {0} "{1}"'.format(
            run['machine_name'], command_login)

    # print command_login
    subprocess.call(command_login, shell=True)


if __name__ == "__main__":
    main()
