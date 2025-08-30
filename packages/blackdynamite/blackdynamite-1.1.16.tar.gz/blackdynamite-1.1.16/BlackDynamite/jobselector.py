#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- py-which-shell: "python"; -*-
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
from . import selector
from . import loader
################################################################


class JobSelector(selector.Selector):
    """
    """

    def selectJobs(self, constraints=None, sort_by=None, quiet=False):

        if quiet is False:
            _loader = loader.Loader("Loading jobs").start()

        job_list = self.base.select(self.base.Job, constraints=constraints,
                                    sort_by=sort_by)

        if quiet is False:
            _loader.stop(f'Loaded {len(job_list)} jobs: ✓')

        return job_list

    def __init__(self, base):
        selector.Selector.__init__(self, base)

################################################################


__all__ = ["JobSelector"]
