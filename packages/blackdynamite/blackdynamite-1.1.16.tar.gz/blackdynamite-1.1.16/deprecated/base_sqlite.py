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
################################################################
import os
import sqlite3
import sys
################################################################
__all__ = ["BaseSQLite"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class BaseSQLite(base.BaseSQL):
    """
    """

    def __init__(self, truerun=False, creation=False, **kwargs):
        sqlite_params = ["host"]
        connection_params = bdparser.filterParams(sqlite_params, kwargs)
        logger.info('connection arguments: {0}'.format(connection_params))
        self.filename = connection_params['host']
        try:
            connection = sqlite3.connect(self.filename)
            logger.debug('connected to base')
        except Exception as e:
            logger.error(
                "Connection failed: check your connection settings:\n" +
                str(e))
            sys.exit(-1)
        assert(isinstance(connection, sqlite3.Connection))

        self.dbhost = (kwargs["host"]
                       if "host" in kwargs.keys()
                       else "localhost")

        super().__init__(connection=connection, truerun=truerun,
                         creation=creation, **kwargs)

    def performRequest(self, request, params=[]):
        curs = self.connection.cursor()
        # logger.debug (request)
        # logger.debug (params)
        try:
            curs.execute(request, params)
        except psycopg2.ProgrammingError as err:
            raise psycopg2.ProgrammingError(
                ("While trying to execute the query '{0}' with parameters " +
                 "'{1}', I caught this: '{2}'").format(request, params, err))
        return curs

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

    def createTypeCodes(self):
        pass

    def createSchema(self, params={"yes": False}):
        # create the schema of the simulation
        curs = self.connection.cursor()
        basename = os.path.splitext(self.filename)[0]
        schema_filename = basename + "_" + self.schema + '.sql'
        if os.path.exists(schema_filename):
            validated = bdparser.validate_question(
                "Are you sure you want to drop the schema named '" +
                self.schema + "'", params, False)
            if validated is True:
                os.unlink(schema_filename)
            else:
                logger.debug("creation canceled: exit program")
                sys.exit(-1)

        curs.execute(f'ATTACH DATABASE "{schema_filename}" AS {self.schema}')

################################################################
