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
from BlackDynamite import runselector
from BlackDynamite import jobselector
################################################################
import sys
import datetime
################################################################


def printSummary(mybase, params):

    jobSelector = jobselector.JobSelector(mybase)
    jobSelector.selectJobs(params)

    runSelector = runselector.RunSelector(mybase)
    run_list = runSelector.selectRuns(params)

    _stats = {}
    for r, j in run_list:
        if (r.run_name, r.state) not in _stats:
            _stats[(r.run_name, r.state)] = 0
        _stats[(r.run_name, r.state)] += 1

    run_stats = {}
    for k, v in _stats.items():
        run_name = k[0]
        state = k[1]
        count = v
        if run_name not in run_stats:
            run_stats[run_name] = []
        run_stats[run_name].append((state, count))

    print('\n---- run states ----')
    for run_name, st in run_stats.items():
        tot = 0
        for n, count in st:
            tot += count
        for n, count in st:
            print("{:20} {:>20} => {:5} ({:>5.1f}%)".format(
                run_name, n, count, 100.*count/tot))
        print("")
    sys.exit(0)

################################################################


def getRunInfo(run_id, mybase):
    myrun = mybase.Run()
    myrun["id"] = run_id
    myrun.id = run_id
    run_list = myrun.getMatchedObjectList()

    if (len(run_list) == 0):
        print("no run found with id " + str(run_id))
        sys.exit(1)

    myrun = run_list[0]
    if isinstance(myrun, mybase.Run):
        myjob = mybase.Job(mybase)
        myjob.id = myrun["job_id"]
        myjob["id"] = myrun["job_id"]
        job_list = myjob.getMatchedObjectList()

        if (len(job_list) == 0):
            print("no job found with id " + myjob.id)
            sys.exit(1)

        myjob = job_list[0]
    else:
        myjob = myrun[1]
        myrun = myrun[0]

    list_entries = myjob.entries.keys()
    print("*"*6 + " job info " + "*"*6)
    for entry in list_entries:
        if (myjob[entry]):
            print(entry + ": " + str(myjob[entry]))

    print("*"*6 + " run info " + "*"*6)
    list_entries = list(myrun.entries.keys())
    regular_run_entries = ("run_name",
                           "job_id",
                           "state",
                           "start_time",
                           "machine_name",
                           "exec",
                           "nproc")

    for entry in regular_run_entries:
        if (myrun[entry]):
            print(entry + ": " + str(myrun[entry]))
        list_entries.remove(entry)

    for entry in list_entries:
        if (myrun[entry]):
            print(entry + ": " + str(myrun[entry]))

    print("*"*6 + " config files " + "*"*6)

    conffiles = myrun.getConfigFiles()
    for conf in conffiles:
        print("file #" + str(conf.id) + ": " + conf["filename"])
        print("*"*6)
        print(conf["file"])

    list_quantities = list(myrun.quantities.keys())
    if len(list_quantities) > 0:
        print("*"*6 + " quantities " + "*"*6)
        for q in list_quantities:
            print(q)
    else:
        print("*"*6 + " no registered quantities " + "*"*6)
################################################################


def getInfoNames(params):
    infos = []
    infos.append("run_name")
    infos.append("id")
    infos.append("job_id")
    if "infos" in params:
        infos += params['infos']
    else:
        infos += ["state", "nproc", "machine_name"]

    infos.append("start_time")
    infos.append("last step")
    infos.append("last update")
    infos.append("Time/step")
    infos.append("Total Time")

    return infos

################################################################


def formatTimeDelta(t):
    if (t < datetime.timedelta(seconds=1)):
        if (t < datetime.timedelta(microseconds=1000)):
            t = str(t.microseconds) + "μs"
        else:
            t = str(1./1000.*t.microseconds) + 'ms'
    else:
        ms = t.microseconds
        t -= datetime.timedelta(microseconds=ms)
        t = str(t)
    return t

################################################################


def getTimeInfos(r):

    step, steptime = r.getLastStep()
    start_time = r['start_time']
    time_perstep = None
    total_time = None

    if (step is not None and steptime and start_time):
        time_perstep = (steptime-start_time)/(step+1)
        total_time = steptime-start_time
        time_perstep = formatTimeDelta(time_perstep)
        total_time = formatTimeDelta(total_time)

    if start_time:
        start_time = start_time.strftime("%H:%M %d/%m/%y")
    if steptime:
        steptime = steptime.strftime("%H:%M %d/%m/%y")

    run_infos = [start_time, step, steptime, time_perstep, total_time]
    return run_infos

################################################################


def getRunInfos(r, j, info_names):
    run_infos = []
    for col in info_names[:-5]:
        key_run = col.replace('%r.', '').strip()
        if not key_run == 'start_time':
            if key_run in r.entries:
                run_infos.append(r[key_run])
            else:
                key_job = col.replace('%j.', '').strip()
                if key_job in j.entries:
                    run_infos.append(j[key_job])
                else:
                    raise Exception('Key {0} is not a valid parameter'.format(
                        key_run))
    run_infos += getTimeInfos(r)

    return run_infos
################################################################


def main(argv=None):

    parser = BD.BDParser(description="getRunInfo")
    group = parser.register_group("getRunInfo")
    group.add_argument(
        "--run_id", type=int,
        help="Select a run_id for complete output")
    group.add_argument(
        "--order", type=str,
        default="id",
        help="specify the column which serves to order the lines")
    group.add_argument(
        "--summary", action='store_true',
        help="Output a summary of the completeness of the study")
    group.add_argument(
        "--infos", type=lambda s: [e.strip() for e in s.split(',')])

    params = parser.parseBDParameters(argv)
    mybase = BD.Base(**params)

    if params["summary"] is True:
        printSummary(mybase, params)

    if "run_id" in params:
        getRunInfo(params["run_id"], mybase)
        return

    info_names = getInfoNames(params)
    runSelector = BD.RunSelector(mybase)
    run_list = runSelector.selectRuns(params,
                                      sort_by="runs." + params["order"])

    _loader = BD.loader.Loader("Fetching run infos").start()

    infos_list = []
    for r, j in run_list:

        try:
            infos = getRunInfos(r, j, info_names)

            def transform_None(x):
                if x is None:
                    return 'None'
                return x

            infos = [transform_None(x) for x in infos]
            infos_list.append(infos)
        except Exception as e:
            print(getRunInfos(r, j, info_names))
            print(e)

    _loader.stop('Loaded run infos: ✓')
    from tabulate import tabulate
    _loader = BD.loader.Loader("Create table").start()
    tab = tabulate(infos_list, headers=info_names, tablefmt='github')
    _loader.stop('Table create: ✓')
    print("\n", flush=True)
    print(tab, flush=True)


################################################################

if __name__ == "__main__":
    main()
