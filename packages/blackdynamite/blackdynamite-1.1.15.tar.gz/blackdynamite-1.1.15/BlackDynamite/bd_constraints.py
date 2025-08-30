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
from . import bdlogging
################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class BDconstraints(object):

    ""

    def __iadd__(self, constraints):
        if not isinstance(constraints, BDconstraints):
            # print('cons2', constraints)
            constraints = BDconstraints(self.base, constraints)

        self.constraints += constraints.constraints
        return self

    def __init__(self, base, constraints):
        # print('cons', constraints)
        self.constraints = constraints
        self.base = base
        self.conditions = None

        if isinstance(constraints, BDconstraints):
            self.constraints = constraints.constraints

        elif isinstance(constraints, dict):

            if "constraints" in constraints:
                self.constraints = constraints["constraints"]
            elif "run_id" in constraints:
                self.constraints = [
                    'runs.id = {0}'.format(constraints['run_id'])]
            elif "job_id" in constraints:
                self.constraints = [
                    'jobs.id = {0}'.format(constraints['job_id'])]
            else:
                self.constraints = []

        if not isinstance(self.constraints, list):
            self.constraints = [self.constraints]


################################################################
