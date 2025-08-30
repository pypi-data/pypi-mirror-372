#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
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
################################################################
import sys
################################################################


def getJobInfo(job_id, mybase):
    myjob = mybase.Job()
    myjob["id"] = job_id
    myjob.id = job_id
    job_list = myjob.getMatchedObjectList()

    if (len(job_list) == 0):
        print("no job found with id " + str(job_id))
        sys.exit(1)

    myjob = job_list[0]
    if isinstance(myjob, mybase.Job):
        myjob = mybase.Job()
        myjob.id = job_id
        job_list = myjob.getMatchedObjectList()

        if (len(job_list) == 0):
            print("no job found with id " + myjob.id)
            sys.exit(1)

        myjob = job_list[0]
    else:
        myjob = myjob[1]

    list_entries = myjob.entries.keys()
    print("*"*6 + " job info " + "*"*6)
    for entry in list_entries:
        if (myjob[entry]):
            print(entry + ": " + str(myjob[entry]))

################################################################


def getJobInfos(j, info_names):
    job_infos = []
    for col in info_names:
        key_run = col.replace('%j.', '').strip()
        if key_run in j.entries:
            job_infos.append(j[key_run])
        else:
            raise Exception('Key {0} is not a valid parameter'.format(
                key_run))

    return job_infos
################################################################


def main(argv=None):

    parser = BD.BDParser(description="getJobInfo")
    group = parser.register_group("getJobInfo")
    group.add_argument(
        "--job_id", type=int,
        help="Select a job_id for complete output")
    group.add_argument(
        "--order", type=str,
        default="id",
        help="specify the column which serves to order the lines")
    group.add_argument("--infos", type=str)

    params = parser.parseBDParameters(argv)
    mybase = BD.Base(**params)

    if "job_id" in params:
        getJobInfo(params["job_id"], mybase)
        return

    jobSelector = BD.JobSelector(mybase)
    job_list = jobSelector.selectJobs(params)
    _loader = BD.loader.Loader("Fetching job infos").start()

    if 'infos' in params:
        info_names = params['infos'].split(',')
    elif len(job_list) > 0:
        info_names = [k for k in job_list[0].types.keys()]
    else:
        info_names = []

    infos_list = []
    for j in job_list:

        try:
            infos = getJobInfos(j, info_names)

            def transform_None(x):
                if x is None:
                    return 'None'
                return x

            infos = [transform_None(x) for x in infos]
            infos_list.append(infos)
        except Exception as e:
            print(getJobInfos(j, info_names))
            print(e)

    _loader.stop('Loaded job infos: ✓')
    from tabulate import tabulate
    _loader = BD.loader.Loader("Create table").start()
    tab = tabulate(infos_list, headers=info_names, tablefmt='github')
    _loader.stop('Table create: ✓')
    print("\n", flush=True)
    print(tab, flush=True)


################################################################

if __name__ == "__main__":
    main()
