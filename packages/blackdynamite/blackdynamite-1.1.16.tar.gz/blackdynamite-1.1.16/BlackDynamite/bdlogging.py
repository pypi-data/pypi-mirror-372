#!/usr/bin/env python
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

import logging
import os
import sys
import traceback

from . import __name__ as global_name

# Base level logger
root_logger = logging.getLogger(global_name)
root_logger.setLevel(logging.DEBUG)  # Avoid hard-filtering

# Logging format
BD_FORMAT = "%(levelname)s:%(funcName)s [%(filename)s:%(lineno)d]: %(message)s"

sh = logging.StreamHandler(sys.stderr)
sh.setLevel(logging.INFO)  # Only show warnings to screen
sh.setFormatter(logging.Formatter(BD_FORMAT))

root_logger.addHandler(sh)


class ExtraContext:
    """Adds some context to logging"""
    _wire = {
        'foo': lambda x: x.foo(),
        'l': lambda x: x.lololo(),
        'f': lambda x: x.fname()
    }

    @staticmethod
    def getTr():
        return traceback.extract_stack(limit=20)[11]

    def fname(self):
        return os.path.basename(self.getTr()[0])

    def lololo(self):
        return self.getTr()[1]

    def foo(self):
        return self.getTr()[2]

    def __getitem__(self, name):
        return self._wire[name](self)

    def __iter__(self):
        d = {k: self._wire[k](self) for k in self._wire}
        return iter(d)


def invalidPrint(x):
    raise Exception('print should not be used in that class: '
                    'use the logging system instead: "{0}"'.format(x))


def activateFileLogging():
    """Activate logging to file (if not already enabled)"""
    # formatter =
    # logging.Formatter(fmt='%(levelname)s:%(foo)50s:%(f)15s:%(l)s:'
    #                               + ' '*10 + '%(message)s')
    formatter = logging.Formatter(BD_FORMAT)

    # Handler for file
    bd_file_handler = logging.FileHandler('bd.log', mode='a+')
    bd_file_handler.setFormatter(formatter)
    bd_file_handler.setLevel(logging.DEBUG)  # Log everything to file
    if '_has_file_handler' not in globals() \
       or not globals()['_has_file_handler']:
        logger = logging.getLogger(global_name)
        logger.debug("Activating logging to file")
        logger.addHandler(bd_file_handler)

        # This should be the first line logged in file
        logger.debug("Activated logging to file")
        globals()['_has_file_handler'] = True


def getLogger(name):
    logger = logging.getLogger(name)
    logger.propagate = True
    return logger
