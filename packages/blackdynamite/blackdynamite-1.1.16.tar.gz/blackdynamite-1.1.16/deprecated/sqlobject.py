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
from __future__ import print_function
################################################################
import copy
import datetime
import psycopg2
import re
import sys
################################################################


class LowerCaseDict(object):

    def __init__(self):
        self.entries = {}

    def __getattr__(self, attr):
        if 'entries' not in self.__dict__:
            raise AttributeError(attr)
        key = attr.lower()
        if key in self.entries:
            return self.entries[key]
        else:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        key = attr.lower()
        if key == 'entries':
            object.__setattr__(self, key, value)

        entries = self.entries
        if key in entries:
            self.__setitem__(attr, value)
        else:
            object.__setattr__(self, attr, value)

    def __getitem__(self, index):
        return self.entries[index.lower()]

    def keys(self):
        return self.entries.keys()

    def __iter__(self):
        return self.entries.__iter__()

    def __setitem__(self, index, value):
        self.entries[index.lower()] = value

    def items(self):
        return self.entries.items()

    def copy(self):
        cp = LowerCaseDict()
        cp.entries = self.entries
        return cp

    def setEntries(self, params):
        for p, val in params.items():
            if p in self.types:
                self.entries[p] = val

################################################################


class SQLObject(LowerCaseDict):
    " The generic object related to entries in the database "

    def __str__(self):
        keys = set(self.entries.keys())
        if 'id' in self.entries:
            keys.remove('id')
        keys = list(keys)
        if 'id' in self.entries:
            keys = ['id'] + keys
        outputs = []
        for k in keys:
            v = self.entries[k]
            outputs += [k + ": " + str(v)]
        return "\n".join(outputs)

    def commit(self):
        self.base.connection.commit()

    def setFields(self, constraints):
        for cons in constraints:
            _regex = "(\w*)\s*=\s*(.*)"
            match = re.match(_regex, cons)
            if (not match or (not len(match.groups()) == 2)):
                print("malformed assignment: " + cons)
                sys.exit(-1)
            key = match.group(1).lower().strip()
            val = match.group(2)
            if key not in self.types:
                print("unknown key '{0}'".format(key))
                print("possible keys are:")
                for k in self.types.keys():
                    print("\t" + k)
                sys.exit(-1)
            val = self.types[key](val)
            self.entries[key] = val

    def __init__(self, base):
        LowerCaseDict.__init__(self)
        self.foreign_keys = {}
        self.allowNull = {}
        self.types = LowerCaseDict()
        self.base = base
        self.operators = {}
        self._prepare()

    def __deepcopy__(self, memo):
        _cp = type(self)(self.base)
        _cp.types = copy.deepcopy(self.types.copy(), memo)
        _cp.entries = copy.deepcopy(self.entries.copy(), memo)
        # _cp.id = self.id
        _cp.foreign_keys = copy.deepcopy(self.foreign_keys, memo)
        _cp.allowNull = copy.deepcopy(self.foreign_keys, memo)
        _cp.connection = self.base
        return _cp

    def _prepare(self):
        try:
            self.base.setObjectItemTypes(self)
        except psycopg2.ProgrammingError:
            self.base.connection.rollback()

    def insert(self):
        params = list()
        # print (self.types)

        ex_msg = ""
        for key, value in self.types.items():
            if key == "id":
                continue
            if ((key not in self.entries) and (key not in self.allowNull)):
                ex_msg += (
                    "key '" + key +
                    "' must be given a value before proceeding insertion\n")
        if (not ex_msg == ""):
            raise Exception("\n****************\n"+ex_msg+"****************\n")

        for key, value in self.entries.items():
            # print (key)
            # print (self.types[key])
            # print (value)
            params.append(self.types[key.lower()](value))

        request = """
INSERT INTO {0}.{1} ({2}) VALUES  ({3}) RETURNING id
""".format(self.base.schema, self.table_name,
           ','.join(self.entries.keys()),
           ','.join(["%s" for item in params])), params
        return request

    def delete(self):
        request, params = "DELETE FROM {0}.{1} WHERE id={2}".format(
            self.base.schema,
            self.table_name,
            self.id), []
        self.base.performRequest(request, params)

    def update(self):
        params = list()
        keys = list()
        for key, value in self.entries.items():
            if (value is None):
                continue
            _type = self.types[key]
            # print (_type)
            # print (key)
            # print (type(value))
            if (_type == datetime.datetime):
                continue
            # _type = str
            keys.append(key)
            params.append(_type(value))

        request = "UPDATE {0}.{1} SET ({2}) = ({3}) WHERE id = {4}".format(
            self.base.schema,
            self.table_name,
            ','.join(keys),
            ','.join(["%s" for item in params]), self.id)

        self.base.performRequest(request, params)

    def getquoted(self):
        raise RuntimeError('code needs review')
        # objs = [sql_adapt(member) for member in self._sql_members()]
        # for obj in objs:
        #     if hasattr(obj, 'prepare'):
        #         obj.prepare(self._conn)
        # quoted_objs = [obj.getquoted() for obj in objs]
        # return '(' + ', '.join(quoted_objs) + ')'

    def createTableRequest(self):
        query_string = "CREATE TABLE {0}.{1} ( id SERIAL PRIMARY KEY,".format(
            self.base.schema, self.table_name)

        for key, value in self.types.items():
            if key == 'id':
                continue
            if (value == float):
                type_string = "DOUBLE PRECISION"
            elif (value == int):
                type_string = "INTEGER"
            elif (value == str):
                type_string = "TEXT"
            elif (value == bool):
                type_string = "BOOLEAN"
            elif (value == datetime.datetime):
                type_string = "TIMESTAMP"

            else:
                print(value)
                raise Exception("type '{0}' not handled".format(value))

            query_string += "{0} {1} ".format(key, type_string)
            if (key not in self.allowNull):
                query_string += " NOT NULL"
            query_string += ","

        for key, value in self.foreign_keys.items():
            query_string += "FOREIGN KEY ({0}) REFERENCES {1}.{2},".format(
                key, self.base.schema, value)

        return query_string[:-1] + ");"

    def getMatchedObjectList(self):
        from . import selector
        sel = selector.Selector(self.base)
        return self.base.select(self, self)
