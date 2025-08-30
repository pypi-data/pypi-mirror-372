#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import os

import BlackDynamite as BD
from BlackDynamite.base import find_root_path


def main(argv=None):
    # parse parameters
    parser = BD.bdparser.BDParser(description="createDB")
    params = parser.parseBDParameters(argv)

    if "host" not in params or params["host"] is None:
        try:
            find_root_path(os.path.realpath("./"))
        except Exception:
            os.mkdir("./.bd")
    # Then we can connect to the black dynamite database
    base = BD.base.Base(**params, creation=True)

    # Then you have to define the parametric space (the job pattern)
    myjob_desc = base.Job()
    for param, _type in params["job"].items():
        myjob_desc.types[param] = eval(_type)

    # Then you have to define the run pattern
    myruns_desc = base.Run()

    if "run" not in params or params["run"] is None:
        params["run"] = {}

    for param, _type in params["run"].items():
        myruns_desc.types[param] = eval(_type)

    # Then we request for the creation of the database
    base.createBase(myjob_desc, myruns_desc, **params)


if __name__ == "__main__":
    main()
