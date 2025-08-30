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

import argparse
import importlib.util
import os
import pwd
import re
################################################################
import socket
import sys
import traceback
from types import ModuleType

import argcomplete
import yaml

################################################################
from . import __path__ as BD_path
from . import base, bdlogging

################################################################
print = bdlogging.invalidPrint
logger = bdlogging.getLogger(__name__)
################################################################


class BDParser(object):

    def error(self, message=None):
        if self.parser.exit_on_error is True:
            self.parser.original_error(message)
        return ""

    def listPossibleHosts(self):
        logger.debug("in")
        bd_dir = os.path.expanduser("~/.blackdynamite")
        bd_hosts = os.path.join(bd_dir, "hosts")
        hosts = []
        try:
            hosts += [h.strip() for h in open(bd_hosts)]
        except Exception:
            pass
        return hosts

    def listPossibleModules(self, pre_args):
        logger.debug("in")
        paths = []
        if "PYTHONPATH" in os.environ:
            paths = os.environ["PYTHONPATH"].split(":")
        paths += BD_path
        paths += [path + "/coating" for path in BD_path]
        module_list = []
        paths = [p.strip() for p in paths if not p.strip() == ""]
        for p in paths:
            files = os.listdir(p)
            files = [f for f in files if os.path.splitext(f)[1] == ".py"]
            files = [f for f in files if not f[0] == "_"]
            matching_string = ".*blackdynamite.*"
            files = [
                os.path.splitext(f)[0]
                for f in files
                if re.match(
                    matching_string,
                    open(os.path.join(p, f)).read().replace("\n", " "),
                    flags=re.IGNORECASE,
                )
            ]

            module_list += files
        logger.debug("found these files " + str(module_list))

        return module_list

    def updatePossibleHosts(self, new_host):
        logger.debug("in")
        bd_dir = os.path.expanduser("~/.blackdynamite")
        if not os.path.isdir(bd_dir):
            os.mkdir(bd_dir)
        bd_hosts = os.path.join(bd_dir, "hosts")
        hosts = set(self.listPossibleHosts())
        hosts.add(new_host)
        with open(bd_hosts, "w") as f:
            for h in hosts:
                f.write(h + "\n")

    def completer(self, prefix, **kwargs):
        try:
            params = vars(kwargs["parsed_args"])
            if params["logging"] is True:
                bdlogging.activateFileLogging()
            logger.debug("in")
            self.cleanUnsetParams(params)
            logger.debug("prefix " + str(prefix))
            logger.debug("params " + str(params))
            current_key = vars(kwargs["action"])["dest"]
            logger.debug("current_key " + str(current_key) + "\n")

            if current_key == "bdconf":
                return self.listPossibleConf()

            if "bdconf" in params:
                self.readConfFiles(params, params["bdconf"])

            if "host" in params:
                self.readConfFile(params, params["host"] + ".bd")

            for k in params.keys():
                logger.debug("params = " + str(k))

            if current_key == "host":
                return self.listPossibleHosts()
            if current_key == "study":
                params["should_not_check_study"] = True
                mybase = base.Base(**params)
                return mybase.getSchemaList()
            if current_key == "quantity":
                mybase = base.Base(**params)
                myrun = mybase.Run(mybase)
                return myrun.listQuantities()

        except Exception as e:
            logger.debug(traceback.format_exc())
            logger.debug(str(e))

        return []

    def listPossibleConf(self):
        logger.debug("in")
        files = []
        for dir in ["./", os.path.expanduser("~/.blackdynamite")]:
            for filename in os.listdir(dir):
                fileName, fileExtension = os.path.splitext(filename)
                if fileExtension == ".bd":
                    files.append(filename)
        return files

    def readConfFiles(self, read_params, fnames):
        logger.debug("in")
        for f in fnames:
            self.readConfFile(read_params, f)

    def readConfFile(self, params, fname):
        logger.debug("in")
        logger.debug("readConfFileList {0}".format(self.readConfFileList))

        if fname in self.readConfFileList:
            return
        self.readConfFileList.append(fname)

        if isinstance(fname, list):
            raise Exception("cannot use list in that function: " + str(type(fname)))

        for dir in ["./", os.path.expanduser("~/.blackdynamite")]:
            fullpath = os.path.join(dir, fname)
            if os.path.isfile(fullpath):
                fname = fullpath
                break

        with open(fullpath) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
            logger.error(config)
            vars(params).update(config)

        logger.debug("out")

    def parseModuleName(self, module_name):
        return self.loadModule(module_name)

    def loadModule(self, myscript):
        logger.debug("in")
        paths = []
        if "PYTHONPATH" in os.environ:
            paths = os.environ["PYTHONPATH"].split(":")
        paths += BD_path
        paths += [path + "/coating" for path in BD_path]

        mymod = None
        for p in paths:
            try:
                modfile = os.path.join(p, myscript + ".py")
                spec = importlib.util.spec_from_file_location(myscript, modfile)
                mymod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mymod)
                logger.debug("successful loadModule attempt: " + modfile)
                break
            except IOError as io_err:
                logger.debug("failed loadModule attempt: " + str(io_err))
        if mymod is None:
            logger.debug("failed loadModule: {myscript}.py")
        logger.debug("loadModule " + str(mymod))
        if mymod is None:
            logger.debug(
                "cannot find module '" + myscript + "' from paths " + str(paths)
            )
            logger.debug("trace :" + traceback.format_exc() + "\n")
            raise Exception(
                "cannot find module '" + myscript + "' from paths " + str(paths)
            )

        return mymod

    def register_group(self, group_name):
        group = self.parser.add_argument_group(group_name)

        class MyGroup:
            def __init__(self, grp, parser):
                self.group = grp
                self.parser = parser

            def add_argument(self, *args, **kwargs):
                arg = self.group.add_argument(*args, **kwargs)
                arg.completer = self.parser.completer
                return arg

        return MyGroup(group, self)

    def declareArguments(self, add_mandatory=True):
        logger.debug("in")
        general_group = self.register_group("General")
        bd_parser_group = self.register_group("BDParser")

        bd_parser_group.add_argument(
            "--study",
            help="Specify the study from the BlackDynamite database"
            ". This refers to the schemas in PostgreSQL language",
            type=str,
        )

        bd_parser_group.add_argument(
            "--host", type=str, help="Specify data base server address"
        )
        bd_parser_group.add_argument(
            "--port", type=int, help="Specify data base server port"
        )

        bd_parser_group.add_argument(
            "--user",
            type=str,
            default=pwd.getpwuid(os.getuid())[0],
            help="Specify user name to connect to data base server",
        )
        bd_parser_group.add_argument(
            "--password", type=str, help="Provides the password"
        )

        bd_parser_group.add_argument(
            "--bdconf",
            action="append",
            help="Path to a BlackDynamite file(*.bd) " "configuring current options",
        )

        bd_parser_group.add_argument(
            "--truerun",
            action="store_true",
            help=(
                "Set this flag if you want to truly perform the"
                " action on base. If not set all action are mainly dryrun"
            ),
        )

        bd_parser_group.add_argument(
            "--constraints",
            help="This allows to constraint run/job selections by properties",
            type=lambda s: [e.strip() for e in s.split(",")],
            default=None,
        )

        bd_parser_group.add_argument(
            "--binary_operator",
            type=str,
            default="and",
            help="Set the default binary operator to " "make requests to database",
        )

        bd_parser_group.add_argument(
            "--list_parameters",
            action="store_true",
            help=("Request to list the possible job/run parameters"),
        )

        bd_parser_group.add_argument(
            "--yes", action="store_true", help="Answer all questions to yes"
        )

        general_group.add_argument(
            "--logging", action="store_true", help="Activate the file logging system"
        )
        general_group.add_argument(
            "--help", action="store_true", help="Activate the file logging system"
        )

    def addEnvBDArguments(self, parser):
        logger.debug("in")
        pre_args, unknown = parser.parse_known_args(args=self.argv)

        for name, value in os.environ.items():
            m = re.match("BLACKDYNAMITE_(.*)", name)
            if m:
                var = m.group(1).lower()
                logger.error(var + ":" + value)
                admissible_params = [e.dest for e in self.parser._actions]
                added_arg = []
                if var not in pre_args or vars(pre_args)[var] is None:
                    if var in admissible_params:
                        added_arg.append("--" + var)
                        added_arg.append(value)
                self.argv = added_arg + self.argv

    def declareModuleArguments(self, parser):
        logger.debug("in")
        pre_args, unknown = parser.parse_known_args(args=self.argv)
        for param, val in vars(pre_args).items():
            if isinstance(val, ModuleType):
                logger.debug(val.__name__)
                val.register_param(self)

    def createArgumentParser(self, argparser=None):
        # Creates the argument parser
        if self.description is None:
            self.description = "BlackDynamite option parser"
        if argparser is not None:
            self.parser = argparser
        else:
            self.parser = argparse.ArgumentParser(
                description=self.description,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                add_help=False,
            )
        # add arguments
        self.declareArguments(add_mandatory=False)
        self.parser.original_error = self.parser.error
        self.parser.error = lambda message=None: self.error(message)

    def cleanUnsetParams(self, params):
        if isinstance(params, argparse.Namespace):
            params = vars(params)

        unset_params = [e for e, v in params.items() if v is None]

        for u in unset_params:
            del params[u]

    def parseBDParameters(self, argv=None):
        "Parse the BlackDynamite arguments from a provided list (argv)"
        logger.debug("in")
        if argv is None:
            self.argv = list(sys.argv[1:])
        else:
            self.argv = list(argv)

        self.parser.exit_on_error = False
        self.addEnvBDArguments(self.parser)
        self.declareModuleArguments(self.parser)
        pre_args, unknown = self.parser.parse_known_args(args=self.argv)
        self.parser.exit_on_error = True
        self.cleanUnsetParams(pre_args)

        if pre_args.logging:
            bdlogging.activateFileLogging()

        if "bdconf" in pre_args:
            logger.debug("loadBDConfFile\n")
            self.readConfFiles(pre_args, pre_args.bdconf)

        if pre_args.help is True:
            self.parser.print_help()
            self.parser.exit()

        argcomplete.autocomplete(self.parser, exclude=["-h"])
        read_params = self.parser.parse_args(args=self.argv)

        # load parameters from the local config file
        fname = "bd.yaml"
        if os.path.exists(fname):
            with open(fname) as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)
                vars(read_params).update(config)
                read_params.config = os.path.abspath(fname)

        self.cleanUnsetParams(read_params)
        return vars(read_params)

    def __init__(self, argparser=None, description=None):
        logger.debug("in")
        self.readConfFileList = []
        self.argparser = argparser
        self.description = description
        self.createArgumentParser(argparser=argparser)


################################################################


def validate_question(question, params, default_validated=True):
    logger.debug("in")
    if default_validated:
        default_str = "(Y/n)"
    else:
        default_str = "(y/N)"

    if params["yes"] is False:
        validated = input("{0}? {1} ".format(question, default_str))
        # print (validated)
        if validated == "\n" or validated == "":
            validated = default_validated
        elif validated == "Y" or validated == "y":
            validated = True
        else:
            validated = False
    else:
        logger.debug("{0}? {1} Forced Y".format(question, default_str))
        validated = True

    return validated


################################################################


def filterParams(sub_list, total_list):
    logger.debug("in")
    new_list = {}
    for p in sub_list:
        if p in total_list and total_list[p] is not False:
            new_list[p] = total_list[p]
    return new_list


################################################################


class RunParser(BDParser):
    """
    Specific parser for runs
    """

    def parseBDParameters(self, argv=None):
        logger.debug("in")
        params = BDParser.parseBDParameters(self, argv)
        params["run_name"], nb_subs = re.subn(r"\s", "_", params["run_name"])
        return params

    def declareArguments(self, add_mandatory=True):
        logger.debug("in")
        BDParser.declareArguments(self, add_mandatory)
        run_group = self.register_group("RunParser")

        run_group.add_argument(
            "--machine_name",
            type=str,
            help=("Specify the name of the machine where" " the job is to be launched"),
            default=socket.gethostname(),
        )
        run_group.add_argument(
            "--nproc",
            type=int,
            help=(
                "Specify the number of processors onto which"
                " this run is supposed to be launched"
            ),
            default=1,
        )
        run_group.add_argument(
            "--run_name",
            type=str,
            required=True,
            help=(
                "User friendly name given to this run."
                " This is usually helpful to recall a run kind"
            ),
        )

    def __init__(self, **kwargs):
        logger.debug("in")
        BDParser.__init__(self, **kwargs)


################################################################

__all__ = ["BDParser", "RunParser"]
