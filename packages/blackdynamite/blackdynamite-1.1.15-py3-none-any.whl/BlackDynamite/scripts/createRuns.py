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

# First we need to set the python headers
# and to import the blackdynamite modules
import BlackDynamite as BD
import tqdm

################################################################


def main(argv=None):

    # import a runparser (instead of a generic BD parser)
    parser = BD.RunParser(description="createRuns")
    params = parser.parseBDParameters(argv)

    # Then we can connect to the black dynamite database
    base = BD.Base(**params)

    # create a run object
    myrun = base.Run()

    # set the run parameters from the parsed entries
    myrun.setEntries(params)

    # add a configuration file
    for f in params["config_files"]:
        myrun.addConfigFiles(f)

    # set the entry point (executable) file
    myrun.setExecFile(params["exec_file"])

    # create a job selector
    jobSelector = BD.JobSelector(base)

    # select the jobs that should be associated with the
    # runs about to be created
    job_list = jobSelector.selectJobs(params, quiet=False)
    print(f"Attaching runs to {len(job_list)} jobs")
    # create the runs
    for i, j in enumerate(tqdm.tqdm(job_list)):
        for param, v in params["run_space"].items():
            if isinstance(v, str) and myrun.types[param] != str:
                v = eval(v)
                if callable(v):
                    v = v(j)
            myrun[param] = myrun.types[param](v)
        # toto = myrun.getMatchedObjectList()
        myrun.attachToJob(j)

        if i % 1000 == 0:
            # if truerun, commit the changes to the base
            if params["truerun"] is True:
                base.commit()

    # if truerun, commit the changes to the base
    if params["truerun"] is True:
        base.commit()


if __name__ == "__main__":
    main()
