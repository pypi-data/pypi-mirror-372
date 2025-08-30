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
import copy
import re
import sys

import persistent
import transaction
from ZODB.POSException import ConflictError

################################################################
from . import bdlogging, lowercase_btree

################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
BTree = lowercase_btree._LowerCaseBTree
PBTree = lowercase_btree.PersistentLowerCaseBTree
################################################################


def _transaction(foo):
    def _protected_transation(self, *args, **kwargs):
        saved_state = self.__getstate__()
        max_attempts = 10
        attempts = 0
        while True:
            try:
                foo(self, *args, **kwargs)
            except ConflictError as e:
                # logger.error('***************CONFLICT************')
                transaction.abort()
                new_state = self.__getstate__()
                found_diff = False
                for k, v in saved_state.items():
                    if k in ["types", "quantities"]:
                        continue
                    if k in new_state and v != new_state[k]:
                        logger.error(
                            f"attempt {attempts} diff state for key"
                            f" {k}: {v} != {new_state[k]}"
                        )
                        if k == "configfiles":
                            for f in v:
                                logger.error(f.file)
                            for f in new_state[k]:
                                logger.error(f.file)

                        found_diff = True

                attempts += 1
                if found_diff:
                    raise e
                if attempts == max_attempts:
                    raise e
            else:
                break

    return _protected_transation


class ZEOObject(persistent.Persistent, BTree):
    "The generic object related to entries in the database"

    def commit(self):
        from .base_zeo import BaseZEO

        BaseZEO.singleton_base.commit()

    def __setattr__(self, attr, value):
        BTree.__setattr__(self, attr, value)

    def setFields(self, constraints):
        for cons in constraints:
            _regex = r"(\w*)\s*=\s*(.*)"
            match = re.match(_regex, cons)
            if not match or (not len(match.groups()) == 2):
                raise RuntimeError("malformed assignment: " + cons)
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

    def __init__(self):
        persistent.Persistent.__init__(self)
        BTree.__init__(self)
        super().__init__()
        self.allowNull = {}
        self.types = PBTree()
        self.operators = {}

    def __getstate__(self):
        "Get the state of the object for a pickling operations"
        state = {}

        for k in self.__dict__.keys():
            if k == "base":
                continue
            state[k] = self.__dict__[k]
        return state

    _flag_debug = False

    def __setstate__(self, state):
        for k in state.keys():
            self.__dict__[k] = state[k]
        if self._flag_debug:
            raise

    def copy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        _cp = type(self)()

        for k in self.__dict__.keys():
            if k == "base":
                continue
            _cp.__dict__[k] = copy.deepcopy(self.__dict__[k])
        return _cp

    @_transaction
    def update(self):
        from .base_zeo import BaseZEO

        if isinstance(self, BaseZEO.singleton_base.Job):
            obj_list = BaseZEO.singleton_base._get_jobs()
        elif isinstance(self, BaseZEO.singleton_base.Run):
            obj_list = BaseZEO.singleton_base._get_runs()
        else:
            raise RuntimeError("undefined yet")

        # logger.warning(self.id)
        obj = obj_list[self.id]
        if obj != self:
            logger.error(id(obj))
            logger.error(id(self))
            raise
        # logger.error(self.base)
        # logger.error(obj)

        for key, value in self.entries.items():
            # logger.error(f'update {key}: {obj[key]} -> value')
            obj[key] = value
            BaseZEO.singleton_base.commit()

    def createTableRequest(self):
        self.base.root.schemas[self.base.schema]["default_job"] = self

    def matchConstraint(self, constraint):

        # case it is an object of same type
        if isinstance(constraint, type(self)):
            for key, value in self.items():
                if constraint[key] != value:
                    return False
            return True
        # case it is a list/dict of constraints to evaluate
        else:
            logger.error(type(self))
            logger.error(constraint)
            for key, value in self.items():
                if key not in constraint:
                    continue
                if constraint[key] != value:
                    return False
            return True
        raise RuntimeError("toimplement")

    def getMatchedObjectList(self):
        from .base_zeo import BaseZEO

        if BaseZEO.singleton_base is None:
            raise RuntimeError("singleton was not allocated")
        return BaseZEO.singleton_base.select(self, self)

    def __repr__(self):
        type_prefix = "object:\n"
        entries = self.entries
        keys = set(self.entries.keys())
        keys.remove("id")

        if not len(keys):
            type_prefix = "descriptor:\n"
            entries = self.types
        if not len(entries.keys()):
            return "Empty ZEO object"

        outputs = []
        for k, v in sorted(entries.items()):
            if k == "id" and v is None:
                continue

            outputs += ["  " + k + ": " + str(v)]

        return type(self).__name__ + " " + type_prefix + "\n".join(outputs)

    def get_params(self):
        params = tuple([v for e, v in self.entries.items() if e != "id"])
        return params

    def get_keys(self):
        keys = tuple([e for e, v in self.entries.items() if e != "id"])
        return keys

    def evalFunctorEntries(self):
        keys = self.get_keys()
        for k in keys:
            if callable(self.entries[k]):
                try:
                    self.entries[k] = self.entries[k](self)
                except Exception as e:
                    logger.error(f"Cannot get entry {k}")
                    raise e

    @property
    def base(self):
        from .base_zeo import BaseZEO

        return BaseZEO.singleton_base
