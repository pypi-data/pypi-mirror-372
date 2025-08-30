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
from . import bdparser
from . import bdlogging
from . import base
from . import job
from . import run_sql
from . import runselector
from .constraints_psql import PSQLconstraints
################################################################
import psycopg2
import sys
import getpass
import atexit
import datetime
import copy
import re
import os
################################################################
__all__ = ["BasePSQL"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class BasePSQL(base.AbstractBase):
    """
    """

    @property
    def Job(self):
        return job.JobSQL

    @property
    def Run(self):
        return run_sql.RunSQL

    def launchRuns(self, run_list, params):
        raise RuntimeError('broken')

    def pack(self):
        raise RuntimeError('broken')

    def __init__(self, truerun=False, creation=False, **kwargs):

        self.BDconstraints = PSQLconstraints

        psycopg2_params = ["host", "user", "port", "password"]
        connection_params = bdparser.filterParams(psycopg2_params, kwargs)

        connection_params['dbname'] = 'blackdynamite'
        if ("password" in connection_params and
                connection_params["password"] == 'ask'):
            connection_params["password"] = getpass.getpass()
        logger.debug('connection arguments: {0}'.format(connection_params))
        try:
            connection = psycopg2.connect(**connection_params)
            logger.debug('connected to base')
        except Exception as e:
            logger.error(
                "Connection failed: check your connection settings:\n" +
                str(e))
            sys.exit(-1)
        assert(isinstance(connection, psycopg2._psycopg.connection))

        self.dbhost = (kwargs["host"]
                       if "host" in kwargs.keys()
                       else "localhost")

        super().__init__(connection=connection, truerun=truerun,
                         creation=creation, **kwargs)

        self.createTypeCodes()
        # We should avoid using __del__ to close DB

        def close_db():
            self.close()

        atexit.register(close_db)

    def performRequest(self, request, params=[]):
        curs = self.connection.cursor()
        logger.debug(request)
        logger.debug(params)
        try:
            curs.execute(request, params)
        except psycopg2.ProgrammingError as err:
            raise psycopg2.ProgrammingError(
                ("While trying to execute the query '{0}' with parameters " +
                 "'{1}', I caught this: '{2}'").format(request, params, err))
        return curs

    def pushQuantity(self, name, type_code, description=None):
        """ implemented type_codes: "int" "float" "int.vector" "float.vector"
        """

        if ((type_code == "int") or (type_code == int)):
            is_integer = True
            is_vector = False
        elif (type_code == "int.vector"):
            is_integer = True
            is_vector = True
        elif ((type_code == "float") or (type_code == float)):
            is_integer = False
            is_vector = False
        elif (type_code == "float.vector"):
            is_integer = False
            is_vector = True
        else:
            raise Exception(
                "invalid type '{0}' for a quantity".format(type_code))

        curs = self.connection.cursor()
        curs.execute("""
INSERT INTO {0}.quantities (name, is_integer, is_vector, description)
VALUES  (%s , %s , %s, %s) RETURNING id
""".format(self.schema), (name, is_integer, is_vector, description))
        item = curs.fetchone()
        if (item is None):
            raise Exception("Counld not create quantity \"" + name + "\"")
        return item[0]

    def getUserList(self):
        curs = self.connection.cursor()
        curs.execute("""
select tableowner from pg_tables where tablename = 'runs';
""")
        users = [desc[0] for desc in curs]
        users = list(set(users))
        return users

    def grantAccess(self, study, user):
        curs = self.connection.cursor()
        curs.execute("""
grant SELECT on ALL tables in schema {0} to {1};
grant USAGE on SCHEMA {0} to {1};
""".format(study, user))
        self.commit()

    def revokeAccess(self, study, user):
        curs = self.connection.cursor()
        curs.execute("""
revoke SELECT on ALL tables in schema {0} from {1};
revoke USAGE on SCHEMA {0} from {1};
""".format(study, user))
        self.commit()

    def getStudyOwner(self, schema):
        curs = self.connection.cursor()
        curs.execute("""
select grantor from information_schema.table_privileges
where (table_name,table_schema,privilege_type)
= ('runs','{0}','SELECT');
""".format(schema))
        owners = [desc[0] for desc in curs]
        return owners[0]

    def createTypeCodes(self):
        curs = self.connection.cursor()
        curs.execute("SELECT typname,oid  from pg_type;")
        self.type_code = {}
        for i in curs:
            if i[0] == 'float8':
                self.type_code[i[1]] = float
            if i[0] == 'text':
                self.type_code[i[1]] = str
            if i[0] == 'int8':
                self.type_code[i[1]] = int
            if i[0] == 'int4':
                self.type_code[i[1]] = int
            if i[0] == 'bool':
                self.type_code[i[1]] = bool
            if i[0] == 'timestamp':
                self.type_code[i[1]] = datetime.datetime

    def getSchemaList(self, filter_names=True):
        curs = self.connection.cursor()

        curs.execute("""
SELECT distinct(table_schema) from information_schema.tables
where table_name='runs'
""")
        schemas = [desc[0] for desc in curs]
        filtered_schemas = []
        if filter_names is True:
            for s in schemas:
                m = re.match('{0}_(.+)'.format(self.user), s)
                if m:
                    s = m.group(1)
                filtered_schemas.append(s)
        else:
            filtered_schemas = schemas
        return filtered_schemas

    def getStudySize(self, study):
        curs = self.connection.cursor()
        try:
            logger.info(study)
            curs.execute("""
select sz from (SELECT SUM(pg_total_relation_size(quote_ident(schemaname)
|| '.' || quote_ident(tablename)))::BIGINT
FROM pg_tables WHERE schemaname = '{0}') as sz
""".format(study))

            size = curs.fetchone()[0]
            curs.execute("""
            select pg_size_pretty(cast({0} as bigint))
            """.format(size))
            size = curs.fetchone()[0]

            curs.execute("""
select count({0}.runs.id) from {0}.runs
""".format(study))
            nruns = curs.fetchone()[0]
            curs.execute("""
select count({0}.jobs.id) from {0}.jobs
""".format(study))
            njobs = curs.fetchone()[0]

        except psycopg2.ProgrammingError:
            self.connection.rollback()
            size = '????'

        return {'size': size, 'nruns': nruns, 'njobs': njobs}

    def createBase(self, job_desc, run_desc, quantities={}, **kwargs):
        # logger.debug(quantities)
        self.createSchema(kwargs)
        self.createTable(job_desc)
        self.createTable(run_desc)
        self.createGenericTables()

        for qname, type in quantities.items():
            self.pushQuantity(qname, type)

        if self.truerun:
            self.commit()

    def createSchema(self, params={"yes": False}):
        # create the schema of the simulation
        curs = self.connection.cursor()
        curs.execute(("SELECT schema_name FROM information_schema.schemata"
                      f" WHERE schema_name = '{self.schema.lower()}'"))

        if curs.rowcount:
            validated = bdparser.validate_question(
                "Are you sure you want to drop the schema named '" +
                self.schema + "'", params, False)
            if validated is True:
                curs.execute("DROP SCHEMA {0} cascade".format(self.schema))
            else:
                logger.debug("creation canceled: exit program")
                sys.exit(-1)

        curs.execute("CREATE SCHEMA {0}".format(self.schema))

    def createTable(self, obj):
        request = obj.createTableRequest()
        curs = self.connection.cursor()
        logger.debug(request)
        curs.execute(request)

    def getColumnProperties(self, sqlobject):
        curs = self.connection.cursor()
        try:
            curs.execute("SELECT * FROM {0}.{1} LIMIT 0".format(
                self.schema, sqlobject.table_name))
            column_names = [desc[0] for desc in curs.description]
            column_type = [desc[1] for desc in curs.description]
            return list(zip(column_names, column_type))
        except psycopg2.errors.UndefinedTable:
            self.connection.rollback()
            return []
        return []

    def setObjectItemTypes(self, sqlobject):
        col_info = self.getColumnProperties(sqlobject)
        for i, j in col_info:
            sqlobject.types[i] = self.type_code[j]
            # logger.debug (str(i) + " " + str(self.type_code[j]))

    def select(self, _types, constraints=None, sort_by=None):

        if (sort_by is not None) and (not isinstance(sort_by, str)):
            raise RuntimeError(
                'sort_by argument is not correct: {0}'.format(sort_by))

        const = PSQLconstraints(self, constraints)
        condition, params = const.getMatchingCondition()

        if not isinstance(_types, list):
            _types = [_types]

        selected_tables = ['{0}.{1}'.format(self.schema, t.table_name)
                           for t in _types]
        selected_tables = ','.join(selected_tables)

        request = "SELECT * FROM {0}".format(selected_tables)

        if condition:
            request += " WHERE " + condition

        # print (sort_by)
        if sort_by:
            request += " ORDER BY " + sort_by

        logger.debug(request)
        logger.debug(params)
        curs = self.performRequest(request, params)

        obj_list = self.buildList(curs, _types)

        return obj_list

    def buildList(self, curs, sqlobjs):

        logger.debug(sqlobjs)
        if not isinstance(sqlobjs, list):
            sqlobjs = [sqlobjs]

        col_infos = []

        sqlobjs2 = []
        for sqlobj in sqlobjs:
            if isinstance(sqlobj, type):
                sqlobj = sqlobj(self)
            sqlobjs2.append(sqlobj)
            col_infos.append(self.getColumnProperties(sqlobj))

        sqlobjs = sqlobjs2

        list_objects = []
        for entries in curs:
            # print(entries)
            objs = []
            offset = 0
            logger.debug(sqlobjs)
            for index, sqlobj in enumerate(sqlobjs):
                obj = copy.deepcopy(sqlobj)
                for col_name, size in col_infos[index]:
                    logger.debug((col_name, entries[offset]))
                    obj[col_name] = entries[offset]
                    offset += 1
                objs.append(obj)
            if len(objs) == 1:
                list_objects.append(objs[0])
            else:
                list_objects.append(tuple(objs))

        return list_objects

    def insert(self, sqlobject):
        curs = self.performRequest(*(sqlobject.insert()))
        sqlobject.id = curs.fetchone()[0]

    def commit(self):
        logger.debug("commiting changes to base")
        self.connection.commit()

    def close(self):
        if 'connection' in self.__dict__:
            logger.debug('closing database session')
            self.connection.close()
            del (self.__dict__['connection'])

    def get_state_summary(self, params=[]):
        runSelector = runselector.RunSelector(self)
        run_list = runSelector.selectRuns(params, quiet=True)
        request = "SELECT run_name,state,count(state) from {0}.runs ".format(
            self.schema)
        if (len(run_list) > 0):
            request += "where id in (" + ",".join(
                [str(r.id) for r, j in run_list]) + ")"
        request += " group by state,run_name order by run_name,state"
        # print (request)
        curs = self.performRequest(request, [])
        stats = {}
        for i in curs:
            if i[0] not in stats:
                stats[i[0]] = []
            stats[i[0]].append([i[1], int(i[2])])
        return stats

    def getObject(self, sqlobject):
        curs = self.connection.cursor()
        curs.execute("SELECT * FROM {0}.{1} WHERE id = {2}".format(
            self.schema, sqlobject.table_name, sqlobject.id))

        col_info = self.getColumnProperties(sqlobject)
        line = curs.fetchone()
        for i in range(0, len(col_info)):
            col_name = col_info[i][0]
            sqlobject[col_name] = line[i]

    def createGenericTables(self,):
        sql_script_name = os.path.join(os.path.dirname(__file__),
                                       "build_tables.sql")
        curs = self.connection.cursor()
        # create generic tables
        query_list = list()
        with open(sql_script_name, "r") as fh:
            for line in fh:
                query_list.append(re.sub("SCHEMAS_IDENTIFIER",
                                         self.schema, line))

        curs.execute("\n".join(query_list))

    def getGrantedUsers(self, schema):
        curs = self.connection.cursor()
        curs.execute("""
select grantee from information_schema.table_privileges
where (table_name,table_schema,privilege_type)
= ('runs','{0}','SELECT');
""".format(schema))
        granted_users = [desc[0] for desc in curs]
        return granted_users

    def retreiveSchemaName(self, creation=False, **kwargs):
        # Need this because getSchemaList strips prefix
        match = re.match('(.+)_(.+)', kwargs["study"])
        if match:
            self.schema = kwargs["study"]
            study_name = match.group(2)
        else:
            self.schema = kwargs["user"] + '_' + kwargs["study"]
            study_name = kwargs["study"]

        # logger.error(self.schema)
        if ((creation is not True) and
                (study_name not in self.getSchemaList())):
            logger.error(study_name)
            raise RuntimeError(
                f"Study name '{study_name}' invalid: "
                f"possibilities are {self.getSchemaList()}")


################################################################
