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

from __future__ import print_function
################################################################
from . import sqlobject
from . import selector

import re
import os
################################################################
__all__ = ["ConfFile", "addFile"]
################################################################


class ConfFile(sqlobject.SQLObject):
    """
    """

    table_name = "configfiles"

    def addFile(self, filename,
                params=None,
                regex_params=None,
                content=None):

        print("adding file " + filename)
        self.entries["filename"] = os.path.basename(filename)
        if content:
            self.entries["file"] = content
        else:
            self.entries["file"] = open(filename, 'r').read()

        if regex_params:
            for p in params:
                # lowerp = p.lower()
                rp = "(" + regex_params
                rp = rp.replace("%p", ")(" + p)
                rp = rp.replace("%v", ")(.*)")

                rr = "\\1\\2__BLACKDYNAMITE__" + p + "__"
                # print (rp)
                # print (rr)
                self.entries["file"] = re.sub(rp, rr,
                                              self.entries["file"],
                                              flags=re.IGNORECASE)
        # print (self.entries["file"])
        file_select = selector.Selector(self.base)

        filelist = self.base.select(ConfFile, self)
        if (len(filelist) == 0):
            tmp_conffile = ConfFile(self.base)
            tmp_conffile.entries = dict(self.entries)
            del tmp_conffile.entries['filename']
            md5filelist = tmp_conffile.getMatchedObjectList()
            if len(md5filelist) != 0:
                import md5
                for f in md5filelist:
                    raise Exception("""
There is already another file with same content but different name:
this is an impossible situation for BlackDynamite.
The file concerned is '{0}'  md5:{1}

** If you want keep going, please rename the file before insertion **
""".format(f['filename'], md5.new(f['file']).hexdigest()))

            self.base.insert(self)
        elif (len(filelist) == 1):
            self.entries = filelist[0].entries
            self.id = filelist[0].id

    def __init__(self, connection):
        sqlobject.SQLObject.__init__(self, connection)
        self.types["filename"] = str
        self.types["file"] = str


def addFile(filename, base, **kwargs):
    cnffile = ConfFile(base)
    cnffile.addFile(filename, **kwargs)
    return cnffile
