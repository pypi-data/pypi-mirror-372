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
from . import zeoobject
from . import bdlogging
from .bd_constraints import BDconstraints
################################################################
import pyparsing as pp
################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class UnknownVariable(RuntimeError):
    pass

################################################################


class ZEOconstraints(BDconstraints):

    ""

    def __init__(self, base, constraints):
        super().__init__(base, constraints)
        self.constraint_parser = ZEOconstraintsParser(self.base)

    def pushConditionFromZEOObject(self, _cstr):
        zeo_obj = _cstr

        def _matching_functor(*objs):
            obj = objs[0]
            # case it is an object of same type
            for key, value in obj.items():
                if (key in zeo_obj and
                        zeo_obj[key] is not None and
                        zeo_obj[key] != value):
                    logger.debug(
                        f'excluded because of {key} {zeo_obj[key]} != {value}')
                    return False
            return True

        self._condition_functors.append(_matching_functor)

    def getMatchingCondition(self):

        # logger.error(self.constraints)
        self._condition_functors = []
        for _cstr in self.constraints:
            if isinstance(_cstr, str):
                # logger.error(_cstr)
                self.pushConditionFromString(_cstr)

            if isinstance(_cstr, zeoobject.ZEOObject):
                self.pushConditionFromZEOObject(_cstr)

        def _full_condition_functor(objs):
            for _f in self._condition_functors:
                # logger.error(_f)
                val_test = bool(_f(*objs))
                if val_test is False:
                    return False
            return True
        return _full_condition_functor

    def pushConditionFromString(self, _cstr):
        _condition_functor = self.constraint_parser.parse(_cstr)
        self._condition_functors += _condition_functor

################################################################


class ZEOconstraintsParser(object):

    def __init__(self, base):

        self.base = base
        self._params = []
        self.ref_run = base.Run()
        self.ref_job = base.Job()

        # rule for entry in the zeoobject

        var = pp.Word(pp.alphanums+'_')
        prefix = (pp.Literal('runs') | pp.Literal('jobs')) + pp.Literal('.')
        entry = pp.Optional(prefix) + var

        def check_varname(tokens):
            # logger.error(tokens)

            if len(tokens) == 3:
                obj_type = tokens[0]
                var_name = tokens[2].lower()
            else:
                obj_type = None
                var_name = tokens[0].lower()

            res = pp.ParseResults(var_name)
            res['obj_type'] = obj_type

            if obj_type is None:
                job_var = var_name in self.ref_job.types
                run_var = var_name in self.ref_run.types
                # logger.error(obj_type)
                if job_var and run_var and obj_type is None:
                    raise RuntimeError(
                        'ambiguous variable: {} (try {} or {})\n{}'
                        .format(
                            var_name, f'jobs.{var_name}', f'runs.{var_name}',
                            self.base.getPossibleParameters()))

                if job_var:
                    res['obj_type'] = 'jobs'
                elif run_var:
                    res['obj_type'] = 'runs'
                else:
                    raise UnknownVariable(
                        'unknown variable: {0}\n{1}'.format(
                            res[0], self.base.getPossibleParameters()))
            if res.obj_type == 'runs':
                res['ref_obj'] = self.ref_run
            elif res.obj_type == 'jobs':
                res['ref_obj'] = self.ref_job

            if var_name not in res.ref_obj.types:
                raise RuntimeError(
                    'unknown variable: "{0}"\n{1}'.format(
                        var_name, res.ref_obj.types))

            res['type'] = res.ref_obj.types[var_name]
            # logger.error(res)
            # logger.error(res.ref_obj)
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

        constraint = pp.Group(entry + ops + pp.Word(pp.alphanums+'._-'))

        def make_functor(key, op, val):
            if op == '<':
                return lambda *objs: key(*objs) < val(*objs)
            if op == '>':
                return lambda *objs: key(*objs) > val(*objs)
            if op == '<=':
                return lambda *objs: key(*objs) <= val(*objs)
            if op == '>=':
                return lambda *objs: key(*objs) >= val(*objs)
            if op == '=':
                return lambda *objs: key(*objs) == val(*objs)
            if op == '!=':
                return lambda *objs: key(*objs) != val(*objs)
            if op == '~':
                raise
            if op == '~*':
                raise
            if op == '!~':
                raise
            if op == '!~*':
                raise

        def make_key_functor(key):
            def _f(*objs):
                if not hasattr(key, "ref_obj"):
                    return key

                # logger.error(key.ref_obj)
                for o in objs:
                    if isinstance(o, key.ref_obj.__class__):
                        return getattr(o, key[0])

                raise RuntimeError(
                    f"could not find an object of type {key.ref_obj.__class__}"
                    f" in \n{objs}")
            return _f

        def regroup_constraints(tokens):
            # logger.error(tokens)
            # expected_type = tokens[0].type
            parsed_key = tokens[0]
            key = parsed_key[0]
            obj_type = parsed_key.obj_type
            if obj_type:
                key = obj_type + '.' + key
            # logger.error(key)
            # logger.error(type(key))
            op = tokens[0][1]
            val = tokens[0][2]

            key = entry.parseString(key)
            try:
                val = entry.parseString(val)
            except UnknownVariable:
                val = key.type(val)

            res = make_functor(
                make_key_functor(key), op, make_key_functor(val))
            return res

        constraint = constraint.setParseAction(regroup_constraints)

        separator = (pp.Literal(',').setParseAction(
            lambda tokens: 'and') | pp.Literal('and'))

        self.constraints = (constraint + pp.Optional(
            pp.OneOrMore(separator + constraint)))

    def parse(self, _str):
        # logger.error(_str)
        try:
            res = self.constraints.parseString(_str)
        except pp.ParseException:
            raise RuntimeError("cannot parse expression: '" + _str + "'")

        res = [e for e in res]
        return res
