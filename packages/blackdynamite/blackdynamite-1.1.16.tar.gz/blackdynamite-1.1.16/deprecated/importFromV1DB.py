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
import os
import pwd
import psycopg2
from BlackDynamite import bdparser
import datetime
import numpy as np
from tqdm import tqdm
################################################################


def convert_to_datetime(_time):
    if type(_time) == int:
        return datetime.datetime(_time)
    return _time


def getTypeCode(connection):
    curs = connection.cursor()
    curs.execute("SELECT typname,oid  from pg_type;")
    type_code = {}
    for i in curs:
        # print(f'guessing type: {i[0]}:{i[1]}')
        if i[0] == 'float8':
            type_code[i[1]] = float
        elif i[0] == 'text':
            type_code[i[1]] = str
        elif i[0] == 'int8':
            type_code[i[1]] = int
        elif i[0] == 'int4':
            type_code[i[1]] = int
        elif i[0] == 'bool':
            type_code[i[1]] = bool
        elif i[0] == 'timestamp':
            type_code[i[1]] = convert_to_datetime
        elif i[0] == 'bool':
            type_code[i[1]] = bool
        elif i[0] == '_float8':
            type_code[i[1]] = lambda x: np.array(x, dtype=float)
        elif i[0] == '_int4':
            type_code[i[1]] = lambda x: np.array(x, dtype=int)
        else:
            # print(f'unknown type: {i[0]}:{i[1]}')
            pass

    return type_code


def performRequest(connection, request, params=[]):
    curs = connection.cursor()
    try:
        curs.execute(request, params)
    except psycopg2.ProgrammingError as err:
        raise psycopg2.ProgrammingError(
            ("While trying to execute the query '{0}' with parameters " +
             "'{1}', I caught this: '{2}'").format(request, params, err))
    return curs


def main(argv=None):
    if isinstance(argv, str):
        argv = argv.split()

    ################################################################
    # make connection to old database
    ################################################################
    parser = BD.BDParser()
    parser.register_params(
        group="saveBDStudy.py",
        params={"out_file": str, "verbose": bool, "study": str},
        help={"out_dir": "Specify the dirname where to save the study",
              "verbose": "Activate the verbose mode of pg_dump",
              "study": "specify the study to backup. \
    If none provided all studies are backed up"})

    params = parser.parseBDParameters(argv=argv)
    # print(params)

    psycopg2_params = ["host", "user", "port", "password"]
    connection_params = bdparser.filterParams(psycopg2_params, params)

    connection = psycopg2.connect(**connection_params)
    truerun = params["truerun"]

    ################################################################
    # get the type code
    ################################################################
    type_code = getTypeCode(connection)
    print('connected to old database')

    ################################################################
    # creates the local database
    ################################################################
    del params['host']
    _study = params['study']
    params['study'] = params['study'].replace('_', '')
    params['user'] = pwd.getpwuid(os.getuid())[0]
    mybase = BD.Base(**params, creation=True)
    print('created new database')

    ################################################################
    # fetches the jobs
    ################################################################
    print('fetching jobs')
    sel = f"SELECT * FROM {_study}.jobs"
    job_curs = performRequest(connection, sel)
    myjob_desc = mybase.Job(mybase)
    job_col_names = []
    for desc in job_curs.description:
        _name = desc[0]
        _type = desc[1]
        myjob_desc.types[_name] = type_code[_type]
        job_col_names.append(_name)
    # print([e for e in myjob_desc.types.items()])

    ################################################################
    # fetches the runs
    ################################################################
    print('fetching runs')
    sel = f"SELECT * FROM {_study}.runs"
    run_curs = performRequest(connection, sel)
    myrun_desc = mybase.Run(mybase)
    run_col_names = []
    for desc in run_curs.description:
        _name = desc[0]
        _type = desc[1]
        myrun_desc.types[_name] = type_code[_type]
        run_col_names.append(_name)
    # print([e for e in myrun_desc.types.items()])

    mybase.createBase(myjob_desc, myrun_desc, **params)

    for entries in job_curs:
        for i, _name in enumerate(job_col_names):
            myjob_desc[_name] = myjob_desc.types[_name](entries[i])
        mybase.insert(myjob_desc, keep_state=True)

    for entries in run_curs:
        # print('################################################################')
        for i, _name in enumerate(run_col_names):
            if entries[i] is None:
                continue
            # print(_name, entries[i],
            # myrun_desc.types[_name], type(entries[i]))
            if type(entries[i]) == myrun_desc.types[_name]:
                myrun_desc[_name] = entries[i]
            else:
                myrun_desc[_name] = myrun_desc.types[_name](entries[i])
        mybase.insert(myrun_desc, keep_state=True)

    ################################################################
    # fetches the configfiles
    ################################################################
    print('fetching configfiles')
    sel = f"SELECT * FROM {_study}.configfiles"
    config_files_curs = performRequest(connection, sel)
    config_file_col_names = []

    for desc in config_files_curs.description:
        _name = desc[0]
        _type = desc[1]
        config_file_col_names.append(_name)

    conf_files_by_hash = dict()
    conf_files_by_id = dict()
    for entries in config_files_curs:
        myconfig_file = {}
        for i, _name in enumerate(config_file_col_names):
            myconfig_file[_name] = entries[i]

        _id = myconfig_file['id']
        myconfig_file = mybase.ConfFile(
            myconfig_file['filename'], content=myconfig_file['file'])
        conf_files_by_hash[myconfig_file.id] = myconfig_file
        conf_files_by_id[_id] = myconfig_file

    ################################################################
    # fetches the runconfig(association between runs and files)
    ################################################################
    print('fetching runconfig')
    sel = f"SELECT * FROM {_study}.runconfig"
    run_config_curs = performRequest(connection, sel)
    run_config_col_names = []
    for desc in run_config_curs.description:
        _name = desc[0]
        _type = desc[1]
        run_config_col_names.append(_name)

    run_container = mybase._get_runs()
    for entries in run_config_curs:
        runconfig_file = {}
        for i, _name in enumerate(run_config_col_names):
            runconfig_file[_name] = entries[i]

        # print(runconfig_file)
        run = run_container[runconfig_file['run_id']]
        conf_file = conf_files_by_id[runconfig_file['configfile_id']]
        run.configfiles[conf_file.id] = conf_file

    ################################################################
    # fetches the quantities
    ################################################################
    print('fetching quantities')
    sel = f"SELECT * FROM {_study}.quantities"

    quantity_curs = performRequest(connection, sel)
    quantity_col_names = []
    quantity_col_type = []
    for desc in quantity_curs.description:
        _name = desc[0]
        _type = desc[1]
        quantity_col_names.append(_name)
        quantity_col_type.append(type_code[_type])

    # print(quantity_col_names)
    # print(quantity_col_type)

    quantities = {}
    for entries in quantity_curs:
        quantity = {}
        for i, _name in enumerate(quantity_col_names):
            quantity[_name] = entries[i]
        quantities[quantity['id']] = quantity
        mybase.quantities.add(quantity['name'])

    if truerun:
        mybase.commit()
    else:
        import transaction
        transaction.abort()

    ################################################################
    # fetches the data per quantity
    ################################################################
    print('fetching data')

    runs = [i for i in run_container]
    for i in tqdm(runs):
        e = run_container[i]

        fetch_data_quantity_for_run(
            e, connection, _study, 'scalar_real',
            type_code, quantities, truerun)
        fetch_data_quantity_for_run(
            e, connection, _study, 'scalar_integer',
            type_code, quantities, truerun)
        fetch_data_quantity_for_run(
            e, connection, _study, 'vector_real',
            type_code, quantities, truerun)
        fetch_data_quantity_for_run(
            e, connection, _study, 'vector_integer',
            type_code, quantities, truerun)

        if truerun:
            mybase.commit()
        else:
            import transaction
            transaction.abort()

    ################################################################
    # fetches the timestamps
    ################################################################
    print('fetching timestamps')

    runs = [i for i in run_container]
    for i in tqdm(runs):
        e = run_container[i]

        request = f"""
SELECT max(b.max),max(b.time) from (
SELECT max(step) as max,max(computed_at) as time
from {_study}.scalar_integer where run_id = {e.id}
union
SELECT max(step) as max,max(computed_at)
as time from {_study}.scalar_real where run_id = {e.id}
union
SELECT max(step) as max,max(computed_at)
as time from {_study}.vector_integer where run_id = {e.id}
union
SELECT max(step) as max,max(computed_at) as time
from {_study}.vector_real where run_id = {e.id}) as b
"""
        curs = performRequest(connection, request)
        item = curs.fetchone()
        if (item is not None):
            e.last_step, e.last_step_time = item[0], item[1]

        if truerun:
            mybase.commit()
        else:
            import transaction
            transaction.abort()

    ################################################################
    # commit to new database
    ################################################################
    print('commit to new database')

    if truerun:
        mybase.commit()
    else:
        import transaction
        transaction.abort()

################################################################


def fetch_data_quantity_for_run(myrun, connection, _study,
                                type_quantity,
                                type_code, quantities,
                                truerun=False):

    run_id = myrun.id
    if type_quantity == 'scalar_real':
        array_type = float
    if type_quantity == 'scalar_integer':
        array_type = int
    if type_quantity == 'vector_real':
        array_type = float
    if type_quantity == 'vector_integer':
        array_type = int

    # print(f'fetching quantities: {_type}')
    # counting the entries
    sel = (f"SELECT * FROM {_study}.{type_quantity}"
           f" WHERE run_id = {run_id} ORDER BY step")
    data_curs = performRequest(connection, sel)
    data_col_names = []
    data_col_type = []
    for desc in data_curs.description:
        _name = desc[0]
        _type = desc[1]
        # print(_name, _type)
        data_col_names.append(_name)
        data_col_type.append(type_code[_type])

    data_per_quantity = {}
    step_per_quantity = {}
    for entries in data_curs:
        data = {}
        for i, _name in enumerate(data_col_names):
            data[_name] = data_col_type[i](entries[i])

        quantity = quantities[data['quantity_id']]
        if quantity['name'] not in data_per_quantity:
            data_per_quantity[quantity['name']] = []
            step_per_quantity[quantity['name']] = []

        _val = data_per_quantity[quantity['name']]
        _step = step_per_quantity[quantity['name']]

        _val.append(data['measurement'])
        _step.append(data['step'])

    for q, data in data_per_quantity.items():
        steps = step_per_quantity[q]
        if (type_quantity == 'vector_real' or
                type_quantity == 'vector_integer'):
            data = np.array([np.array(d, dtype=array_type)
                             for d in data], dtype=object)
        else:
            data = np.array(data, dtype=array_type)
        if truerun:
            myrun.saveQuantityArrayToBlob(q, steps, data)
            myrun.commit()
        else:
            import transaction
            transaction.abort()


################################################################


if __name__ == '__main__':
    main()
