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

import hashlib
import os
################################################################
import re

################################################################
from . import bdlogging

################################################################
__all__ = ["ConfFile", "addFile"]
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class ConfFile:
    """
    Class storing file information
    """

    table_name = "configfiles"

    def __init__(self, filename,
                 params=None,
                 regex_params=None,
                 content=None):
        self.filename = os.path.basename(filename)
        if content:
            self.file = content
        else:
            self.file = open(filename, 'r').read()

        self.id = hashlib.md5(self.file.encode()).hexdigest()
        logger.debug("adding file " + filename + ": " + self.id)

        if regex_params:
            for p in params:
                # lowerp = p.lower()
                rp = "(" + regex_params
                rp = rp.replace("%p", ")(" + p)
                rp = rp.replace("%v", ")(.*)")

                rr = "\\1\\2__BLACKDYNAMITE__" + p + "__"
                # print (rp)
                # print (rr)
                self.file = re.sub(rp, rr,
                                   self.file,
                                   flags=re.IGNORECASE)

    def __getitem__(self, index):
        return getattr(self, index)

    def __setitem__(self, index, value):
        return setattr(self, index, value)


def addFile(filename, **kwargs):
    cnffile = ConfFile(filename, **kwargs)
    return cnffile
