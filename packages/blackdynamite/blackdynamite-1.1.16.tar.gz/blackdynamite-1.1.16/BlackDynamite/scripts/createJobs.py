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
import importlib.util
import os
import numpy as np

################################################################


def main(argv=None):
    # parsing parameters
    parser = BD.bdparser.BDParser(description="createJobs")
    params = parser.parseBDParameters(argv)

    # Then we can connect to the black dynamite database
    base = BD.base.Base(**params)

    # create of job object
    job = base.Job()

    job_space = params["job_space"]

    if isinstance(job_space, str):
        myscript, ext = os.path.splitext(job_space)
        if ext == ".py":
            print("executing: ", job_space)
            modfile = job_space
            spec = importlib.util.spec_from_file_location(myscript, modfile)
            if spec is None:
                raise RuntimeError(f"unknown job script type {job_space}")

            mymod = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                raise RuntimeError(f"unknown job script type {job_space}")

            spec.loader.exec_module(mymod)
            _loader = BD.loader.Loader(f"Creating jobs from script {myscript}").start()

            n_insertion = mymod.createJobs(base)
        else:
            raise RuntimeError(f"unknown job script type {job_space}")
    else:
        # specify a range of jobs
        _loader = BD.loader.Loader(
            f"Evaluate job space from script {params['config']}"
        ).start()

        for param, space in job_space.items():
            if isinstance(space, str) and job.types[param] != str:
                space = eval(space)

            if isinstance(space, np.ndarray):
                space = list(space)

            if isinstance(space, list):
                space = [job.types[param](e) for e in space]

            job[param] = space

        _loader.stop("Job space defined: ✓")

        # creation of the jobs on the database
        print(f"Creating jobs from config {params['config']}")

        n_insertion = base.createParameterSpace(
            job, progress_report=True, params=params
        )

        # _loader.stop("Job creation: ✓")
    print(f"Inserted {n_insertion} new jobs ✓")


if __name__ == "__main__":
    main()
