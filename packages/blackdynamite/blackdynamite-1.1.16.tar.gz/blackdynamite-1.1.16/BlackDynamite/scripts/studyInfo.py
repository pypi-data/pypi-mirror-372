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

from __future__ import print_function
################################################################
import BlackDynamite as BD
################################################################


def printDataBaseInfo(base, params):
    curs = base.connection.cursor()
    curs.execute("select current_database()")
    datname = curs.fetchone()[0]
    curs.execute("""
select d.datname,
pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname))
from pg_catalog.pg_database d where (d.datname) = ('{0}')
""".format(datname))
    datsize = curs.fetchone()[1]
    print("Database:", datname, datsize)


def printUserInfo(base, params):
    users = base.getUserList()
    print('registered Users: {0}'.format(', '.join(users)))


def printStudyInfo(base, study, params):
    study_size = base.getStudySize(study)

    owner = base.getStudyOwner(study)
    granted_users = base.getGrantedUsers(study)

    print('{0}'.format(study))
    print('     Owner:{:>30}  '.format(owner))
    print('     #jobs:{:>30}  '.format(study_size['njobs']))
    print('     #runs:{:>30}  '.format(study_size['nruns']))
    print('     size:  {:>30}'.format(study_size['size']))
    print('     grants: {0}'.format(','.join(granted_users)))


def fetchInfo(base, params):

    printUserInfo(base, params)

    if "study" not in params:
        study_list = base.getSchemaList(filter_names=False)
    else:
        study_list = [base.schema]

    printDataBaseInfo(base, params)
    for s in study_list:
        printStudyInfo(base, s, params)


def fetchStudy(base, params):
    runSelector = BD.RunSelector(base)
    run_list = runSelector.selectRuns(params, params, quiet=True)
    print(run_list)


def main(argv=None):
    if (type(argv) == str):
        argv = argv.split()

    parser = BD.BDParser()
    parser.register_params(
        group="studyInfo.py",
        params={"full": bool, "study": str,
                "grant": str, "revoke": str,
                "fetch": bool},
        help={"full": "Say that you want details (can be costful)",
              "study": "specify a study to analyse",
              "grant": "specify an user to grant read permission",
              "revoke": "specify an user to revoke read permission",
              "fetch": "fetch the specified study as one of yours"})

    params = parser.parseBDParameters(argv=argv)
    params["should_not_check_study"] = True
    mybase = BD.Base(**params)

    if 'grant' in params:
        mybase.grantAccess(params['study'], params['grant'])
    if 'revoke' in params:
        mybase.revokeAccess(params['study'], params['revoke'])
    if params['fetch'] is True:
        fetchStudy(mybase, params)

    fetchInfo(mybase, params)


if __name__ == '__main__':
        main()
