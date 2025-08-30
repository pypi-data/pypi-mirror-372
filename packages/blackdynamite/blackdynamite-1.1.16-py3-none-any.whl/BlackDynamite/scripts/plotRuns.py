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
import BlackDynamite as BD
from BlackDynamite.graphhelper import GraphParser
from BlackDynamite.graphhelper import GraphHelper
################################################################


def main(argv=None):

    parser = GraphParser()
    params = parser.parseBDParameters(argv)
    print(params)
    base = BD.Base(**params)
    gH = GraphHelper(base, **params)
    gH.makeGraphs(**params)
    if 'fileout' not in params:
        gH.show()


if __name__ == "__main__":
    main()
