#!/usr/bin/env python
################################################################
import BlackDynamite as BD
import datetime
import transaction
from BTrees.OOBTree import BTree
################################################################


class Command:

    def __init__(self, cmd):
        self.cmd = cmd

    def __repr__(self):
        return self.cmd()


def make_command(func):
    return Command(func)


@make_command
def commit():
    transaction.commit()
    return ""


################################################################
def check_types(obj, desc):
    for name, e in desc.entries.items():
        if name not in obj.entries:
            raise RuntimeError('missing entry in run')
        _e = obj.entries[name]
        if _e is not None and not isinstance(_e, e):
            raise RuntimeError(
                f'incompatible types {name}: {_e}, {type(_e)} should be {e}')


################################################################
def clean_run_entries(base):
    study = base.root.schemas[base.schema]
    desc = study.run_desc

    for _id, r in study.runs.items():
        check_types(r, desc)

################################################################


def clean_job_entries(base):
    study = base.root.schemas[base.schema]
    desc = study.job_desc

    for _id, r in study.jobs.items():
        check_types(r, desc)

################################################################


def reconstruct_indexes(base):
    study = base.root.schemas[base.schema]
    study['JobsIndex'] = BTree()
    study['RunsIndex'] = BTree()
    for _id, j in study.jobs.items():
        params = j.get_params()
        base.jobs_index[params] = _id
    for _id, r in study.runs.items():
        params = r.get_params()
        base.runs_index[params] = _id


################################################################


def main(argv=None):
    parser = BD.bdparser.BDParser()
    params = parser.parseBDParameters(argv)
    base = BD.Base(**params)
    reconstruct_indexes(base)
    base.commit()
    clean_job_entries(base)
    base.commit()
    clean_run_entries(base)
    base.commit()

################################################################


if __name__ == '__main__':
    main()
