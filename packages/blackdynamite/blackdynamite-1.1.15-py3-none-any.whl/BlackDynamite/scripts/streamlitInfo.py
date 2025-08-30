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

################################################################
import sys

import pandas as pd

import BlackDynamite as BD
from BlackDynamite import runselector
from BlackDynamite.graphhelper import GraphHelper

################################################################


def write_summary(mybase):

    runSelector = runselector.RunSelector(mybase)
    run_list = runSelector.selectRuns([])

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

    df = []
    for run_name, stat in run_stats.items():
        tot = 0
        for n, count in stat:
            tot += count
        for n, count in stat:
            df.append([run_name, n, count, str(int(100.*count/tot))+' %'])
    df = pd.DataFrame(df, columns=['run_name', 'state', 'count', '%'])
    import st_aggrid
    st_aggrid.AgGrid(
        df, columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_CONTENTS)
################################################################


def write_run_info(run_id, mybase):
    import streamlit as st

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

        if len(job_list) == 0:
            st.write("no job found with id " + myjob.id)
            return
        myjob = job_list[0]
    else:
        myjob = myrun[1]
        myrun = myrun[0]

    st.markdown(f"## Run *{run_id}*")
    params_info, configfile_info, quantity_info = st.tabs(
        ["Run&Job", "Config Files", "Quantities"])

    with params_info:
        import st_aggrid

        st.markdown("#### job info")
        df = pd.DataFrame([(k, v) for k, v in myjob.entries.items()],
                          columns=['param', 'value'])
        st_aggrid.AgGrid(
            df, columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)

        st.markdown("#### run info")
        df = pd.DataFrame([(k, v) for k, v in myrun.entries.items()],
                          columns=['param', 'value'])
        st_aggrid.AgGrid(
            df, columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)

    with configfile_info:
        conffiles = myrun.getConfigFiles()
        for conf in conffiles:
            with st.expander(f'file #{conf.id}: {conf["filename"]}'):
                st.code(conf["file"])

    with quantity_info:
        list_quantities = list(myrun.quantities.keys())
        if len(list_quantities) > 0:
            df = pd.DataFrame(list_quantities, columns=['Quantity Name'])
            st_aggrid.AgGrid(
                df, columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)
        else:
            st.markdown("no registered quantities")
################################################################


def write_runs_tab(params, base):
    import streamlit as st
    selector = st.text_input(
        "Run filter", value="state=FINISHED")
    if selector:
        params['constraints'] = selector.split(',')

    runSelector = BD.RunSelector(base)
    run_list = runSelector.selectRuns(params)
    infos_list = []
    column_names = None

    import streamlit as st
    st.markdown(f'Selected {len(run_list)} runs')
    for r, j in run_list:
        infos = [v for k, v in r.entries.items()]
        column_names = [e for e in r.entries.keys()]
        infos_list.append(infos)

    df = pd.DataFrame(infos_list, columns=column_names)
    cols = list(df.columns.values)
    cols.pop(cols.index('id'))
    cols.pop(cols.index('job_id'))
    cols.pop(cols.index('state'))
    cols.pop(cols.index('run_name'))
    df = df[['id', 'job_id', 'run_name', 'state'] + cols]

    import st_aggrid
    gb = st_aggrid.GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single')
    gridOptions = gb.build()

    table_runs = st_aggrid.AgGrid(
        df, height=400, gridOptions=gridOptions,
        columns_auto_size_mode=st_aggrid.ColumnsAutoSizeMode.FIT_CONTENTS)
    selected_rows = table_runs.selected_rows
    if selected_rows:
        selected_run_id = selected_rows[0]['id']
        write_run_info(selected_run_id, base)
################################################################


def write_jobs_tab(params, base):
    import streamlit as st
    selector = st.text_input(
        "Job filter", value="")
    if selector:
        params['constraints'] = selector.split(',')
    else:
        params['constraints'] = []

    jobSelector = BD.JobSelector(base)
    job_list = jobSelector.selectJobs(params)
    infos_list = []
    column_names = None

    st.markdown(f'Selected {len(job_list)} Jobs')
    for j in job_list:
        infos = [v for k, v in j.entries.items()]
        column_names = j.entries.keys()
        infos_list.append(infos)

    df = pd.DataFrame(infos_list, columns=column_names)
    cols = list(df.columns.values)
    cols.pop(cols.index('id'))
    df = df[['id'] + cols]

    st.dataframe(df, use_container_width=True)

################################################################


def write_graph_tab(params, base):
    import streamlit as st

    col_params, col_figure = st.columns(2)
    with col_params:
        selector = st.text_input(
            "Run filter", key='filter4graphs', value="state=FINISHED")
        if selector:
            params['constraints'] = selector.split(',')

        runSelector = BD.RunSelector(base)
        run_list = runSelector.selectRuns(params)
        st.markdown(f'Selected {len(run_list)} runs')
        st.markdown('---\n')
        study = base.root.schemas[base.schema]
        quantity_x = st.selectbox(
            "Select the X axis", ['step']+sorted(list(study['Quantities'])),
            index=0)
        quantity_y = st.selectbox(
            "Select the Y axis", study['Quantities'])

        legend = st.text_input("Legend", value="Run %j.id")
        marker = st.text_input("Marker", value="")
        line_style = st.text_input("Line Style", value="-")

        params['list_quantities'] = False
        params['quantity'] = [quantity_x, quantity_y]
        if quantity_x == 'step':
            params['quantity'] = [quantity_y]
            params['xlabel'] = 'step'
        else:
            params['quantity'] = [quantity_x, quantity_y]
            params['using'] = ["%0.y:%1.y"]
            params['xlabel'] = quantity_x

        params['xscale'] = 1
        params['yscale'] = 1
        params['legend'] = [legend]
        params['ylabel'] = quantity_y
        params['marker'] = marker
        params['linestyle'] = line_style

    with col_figure:
        if st.button('Generate Plot'):
            with st.spinner("Please wait"):
                gH = GraphHelper(base, **params)
                fig, axe = gH.makeGraphs(**params)
                st.pyplot(fig)


################################################################


def main(argv=None):
    import streamlit as st

    st.set_page_config(layout="wide")

    parser = BD.BDParser(description="streamlitInfo")
    params = parser.parseBDParameters(argv)
    base = BD.Base(**params)

    st.header(f'Study *{params["study"]}*')

    st.markdown(f'- user: {params["user"]}')

    db_tab, runs_tab, jobs_tab, graph_tab = st.tabs(
        ["Database", "Runs", "Jobs", "Graphs"])

    with runs_tab:
        write_runs_tab(params, base)
    with jobs_tab:
        write_jobs_tab(params, base)
    with db_tab:
        write_summary(base)
    with graph_tab:
        write_graph_tab(params, base)
    return


################################################################

if __name__ == "__main__":
    main()
