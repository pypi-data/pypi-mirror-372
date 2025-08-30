#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from . import sqlobject
from . import bdlogging
from .bd_constraints import BDconstraints
################################################################
import pyparsing as pp
################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class PSQLconstraints(BDconstraints):

    ""

    def __init__(self, base, constraints):
        super().__init__(base, constraints)
        self.constraint_parser = PSQLconstraintsParser(self.base)

    def pushConditionFromSQLObject(self, _cstr):
        _cond = []
        _params = []
        sql_obj = _cstr
        for k, v in sql_obj.entries.items():
            _cond.append('({0}.{1} = %s)'.format(
                sql_obj.table_name, k))
            _params.append(v)
        _cond = ' and '.join(_cond)

        self._pushCondition(_cond, _params)

    def _pushCondition(self, _cond, _params):
        if self.conditions != '':
            self.conditions += ' and '
        self.conditions += _cond
        self.params += _params

    def pushConditionFromString(self, _cstr):
        _cond, _params = self.constraint_parser.parse(_cstr)
        self._pushCondition(_cond, _params)

    def getMatchingCondition(self):

        self.conditions = ""
        self.params = []

        for _cstr in self.constraints:
            if isinstance(_cstr, str):
                self.pushConditionFromString(_cstr)

            if isinstance(_cstr, sqlobject.SQLObject):
                self.pushConditionFromSQLObject(_cstr)

        logger.debug(self.conditions)
        logger.debug(self.params)
        return self.conditions, self.params

################################################################


class PSQLconstraintsParser(object):

    def __init__(self, base):

        self.base = base
        self._params = []
        self.ref_run = base.Run(self.base)
        self.ref_job = base.Job(self.base)

        # rule for entry in the sqlobject

        var = pp.Word(pp.alphanums+'_')
        prefix = (pp.Literal('runs') | pp.Literal('jobs')) + pp.Literal('.')
        entry = pp.Optional(prefix) + var

        def check_varname(tokens):
            # print(tokens)
            res = pp.ParseResults(''.join(tokens))
            logger.debug(res)

            if len(tokens) == 3:
                obj_type = tokens[0]
                var_name = tokens[2].lower()
            else:
                obj_type = None
                var_name = tokens[0].lower()

            if obj_type is None:
                job_var = var_name in self.ref_job.types
                run_var = var_name in self.ref_run.types

                if job_var and run_var:
                    raise RuntimeError(
                        'ambiguous variable: {} (try {} or {})\n{}'
                        .format(
                            res,
                            ', '.join(['jobs.' + _var for _var in res]),
                            ', '.join(['runs.' + _var for _var in res]),
                            self.base.getPossibleParameters()))

                if job_var:
                    res.type = self.ref_job.types[var_name]
                elif run_var:
                    res.type = self.ref_run.types[var_name]
                else:
                    raise RuntimeError(
                        'unknown variable: {0}\n{1}'.format(
                            res[0], self.base.getPossibleParameters()))
            else:
                if obj_type == 'runs':
                    ref_obj = self.ref_run
                elif obj_type == 'jobs':
                    ref_obj = self.ref_job

                if var_name not in ref_obj.types:
                    raise RuntimeError(
                        'unknown variable: "{0}"\n{1}'.format(
                            var_name, ref_obj.types))

                res.type = ref_obj.types[var_name]

            return res

        entry = entry.setParseAction(check_varname)

        # rule to parse the operators
        operators = [
            # '+',   # addition   2 + 3   5
            # '-',   # subtraction        2 - 3   -1
            # '*',   # multiplication     2 * 3   6
            # '/',   # division (integer division truncates the result)
            # '%',   # modulo (remainder)         5 % 4   1
            # '^',   # exponentiation     2.0 ^ 3.0       8
            '<',   # less than
            '>',   # greater than
            '<=',  # less than or equal to
            '>=',  # greater than or equal to
            '=',   # equal
            '!=',  # not equal
            '~',   # Matches regular expression, case sensitive
            '~*',  # Matches regular expression, case insensitive
            '!~',  # Does not match regular expression, case sensitive
            '!~*'  # Does not match regular expression, case insensitive
        ]
        ops = pp.Literal(operators[0])
        for o in operators[1:]:
            ops |= pp.Literal(o)

        # parse a constraint of the form 'var operator value' and flatten it

        constraint = pp.Group(entry + ops + pp.Word(pp.alphanums+'._'))

        def regroup_constraints(tokens):
            expected_type = tokens[0].type
            key = tokens[0][0]
            op = tokens[0][1]
            val = tokens[0][2]

            try:
                parse_res = entry.parseString(val)
                if parse_res.type != expected_type:
                    raise RuntimeError('no the correct type')
                val = parse_res[0]
            except Exception:
                self._params.append(val)
                val = '%s'

            res = ('(' +
                   ' '.join([str(key), str(op), str(val)]) + ')')
            return res

        constraint = constraint.setParseAction(regroup_constraints)

        separator = (pp.Literal(',').setParseAction(
            lambda tokens: 'and') | pp.Literal('and'))

        self.constraints = (constraint + pp.Optional(
            pp.OneOrMore(separator + constraint))).setParseAction(
                lambda tokens: ' '.join(tokens))

    def parse(self, _str):
        self._params = []
        logger.debug(_str)
        try:
            res = self.constraints.parseString(_str)
        except pp.ParseException:
            raise RuntimeError("cannot parse expression: '" + _str + "'")
        res = ' '.join(res)
        return res, self._params
