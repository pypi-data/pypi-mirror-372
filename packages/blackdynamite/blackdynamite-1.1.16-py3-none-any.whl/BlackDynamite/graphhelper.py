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
from . import runselector
from . import bdparser
################################################################
import re
import sys
import numpy as np
################################################################


class GraphHelper:

    def getMeasures(self, run_list):
        myresults = []
        add_req = []
        if self.frequency:
            add_req += ["step %% {0} = 0".format(self.frequency)]
        if self.start:
            add_req += ["step > {0}".format(self.start)]
        if self.end:
            add_req += ["step < {0}".format(self.end)]

        for r, j in run_list:
            res = r.getScalarQuantities(self.quantities, add_req)
            if res is None:
                continue
            for key, step, value in res:
                if value is None:
                    del res[key]
            myresults.append([r, j, res])
        return myresults

    def selectGraphs(self):
        run_list = self.runSelector.selectRuns(self.constraints,
                                               self.sort_by)
        results = self.getMeasures(run_list)
        return results

    def show(self):
        import matplotlib.pyplot as plt
        plt.show()

    def makeGraphs(self, fig=None, axe=None, **kwargs):
        results = self.selectGraphs()
        for r, j, data in results:
            # print(r.id, data)
            if data:
                fig, axe = self.makeCurve(data, fig=fig, axe=axe,
                                          myrun=r, myjob=j, **kwargs)
        return fig, axe

    def replaceRunAndJobsParameters(self, name, myrun, myjob):

        res = name
        # print (res)
        codes = [["%r." + key, myrun[key]] for key in myrun.entries.keys()]
        codes += [["%j." + key, myjob[key]] for key in myjob.entries.keys()]
        for code, val in codes:
            res = res.replace(code, str(val))
        return res

    def generateLabels(self, results, myrun, myjob):
        labels = []
        names = [r[0] for r in results]
        for i in range(0, len(results)):
            name = results[i][0]
            # print(self.legend)
            if (not self.legend or i >= len(self.legend) or
                    not self.legend[i]):
                labels.append(
                    self.replaceRunAndJobsParameters(name, myrun, myjob)
                )
                continue
            head_legend = self.legend[i].replace("{", "{{")
            head_legend = head_legend.replace("}", "}}")
            head_legend = re.sub(r"(%)([0-9]+)", r'{\2}', head_legend).format(
                *names)
            # print (head_legend)
            head_legend = self.replaceRunAndJobsParameters(
                head_legend, myrun, myjob)
            # print(head_legend)
            # if (not head_legend.find("%") == -1):
            # print("unknown variable name. Possible variables are:")
            # print "\n".join([c[0] for c in codes])
            # sys.exit(-1)

            # print (head_legend)
            labels.append(head_legend)
        return labels

    def makeComposedQuantity(self, results, myrun, myjob):
        vecs = [np.column_stack((r[1], r[2])) for r in results]
        names = [r[0] for r in results]
        # print (vecs[0].shape)
        new_results = []

        for comp in self.using:
            exprs = comp.split(":")
            res = []
            for i in [0, 1]:
                e = re.sub(r"(%)([0-9]+)\.(x)", r"vecs[\2][:,0]", exprs[i])
                e = re.sub(r"(%)([0-9]+)\.(y)", r"vecs[\2][:,1]", e)
                e = self.replaceRunAndJobsParameters(e, myrun, myjob)

                try:
                    res.append(eval(e))
                except Exception as ex:
                    print("invalid expression: '" + exprs[i] + "'")
                    print("invalid expression: '" + e + "'")
                    print(ex)
                    i = 1
                    for v in vecs:
                        print('quantity {0}/{1} shape: {2}'.format(
                            i, len(vecs), v.shape))
                        i += 1
                    sys.exit(-1)

            name = re.sub(r"(%)([0-9]+)\.([x|y])", r'(" + str(names[\2]) + ")',
                          exprs[1])
            name = "\"" + name + "\""
            name = eval(name)
            new_results.append([name, res[0], res[1]])
        return new_results

    def decorateGraph(self, fig, axe, myrun, myjob, results):
        if not results:
            return None

        if fig is None:
            import matplotlib.pyplot as plt
            fig = plt.figure()
            axe = fig.add_subplot(1, 1, 1)

        if self.xrange:
            axe.set_xlim(self.xrange)
        if self.yrange:
            axe.set_ylim(self.yrange)

        if self.xlabel:
            axe.set_xlabel(self.xlabel)

        if self.ylabel:
            axe.set_ylabel(self.ylabel)

        if self.title:
            t = self.replaceRunAndJobsParameters(self.title, myrun, myjob)
            axe.set_title(t)

        axe.grid(True, linewidth=0.1)
        if self.using:
            results = self.makeComposedQuantity(results, myrun, myjob)

        labels = self.generateLabels(results, myrun, myjob)
        # print (labels)
        return fig, axe, results, labels

    def makeCurve(self, results, myrun=None, myjob=None,
                  fig=None, axe=None, **kwargs):
        fig, axe, results, labels = self.decorateGraph(
            fig, axe, myrun, myjob, results)

        for count, result in enumerate(results):
            # name = result[0]
            step = result[1]
            vec = result[2]
            label = labels[count]

            # print (self.quantities)
            # print (name)
            style = dict()

            if self.marker is not None:
                style["marker"] = self.marker
            if self.blackwhite:
                width_index = self.cycle_index/len(self.linestyle_cycle)
                style_index = self.cycle_index % len(self.linestyle_cycle)
                self.cycle_index += 1
                style["linewidth"] = self.linewidth_cycle[width_index]
                style["linestyle"] = self.linestyle_cycle[style_index]
                style["color"] = 'k'
            axe.plot(step/self.xscale, vec/self.yscale,
                     label=label, **style)
            axe.legend(loc='best')

        if self.fileout:
            fig.savefig(self.fileout)

        return fig, axe

    def setConstraints(self, **params):
        self.constraints = []
        if "constraints" in params:
            self.constraints = params["constraints"]

    def setBinaryOperator(self, **params):
        self.binary_operator = 'and'
        if ("binary_operator" in params):
            self.binary_operator = params["binary_operator"]

    def setQuantity(self, **params):

        if "quantity" in params:
            self.quantities = params["quantity"]
        else:
            print("quantity should be provided using option --quantity")
            self.quantities = "__BLACKDYNAMITE_ERROR__"

    def __init__(self, base, **params):

        self.setConstraints(**params)
        self.setQuantity(**params)
        self.base = base
        self.runSelector = runselector.RunSelector(self.base)

        self.fig = None
        self.xrange = None
        self.yrange = None
        self.xlabel = None
        self.ylabel = None
        self.xscale = None
        self.yscale = None
        self.fileout = None
        self.title = None
        self.using = None
        self.frequency = None
        self.start = None
        self.end = None
        self.figsize = None
        self.blackwhite = None
        self.legend = None
        self.sort_by = None
        self.marker = None

        # set the members if keys are present in params
        members = set(self.__dict__.keys())
        p = set(params.keys())
        for key in members & p:
            setattr(self, key, params[key])

        if params["list_quantities"] is True:
            myrun = base.Run()
            print("list of possible quantities:\n")
            print("\n".join(myrun.listQuantities()))
            sys.exit(0)

        if params["list_parameters"] is True:
            self.base.getPossibleParameters()
            sys.exit(0)

        self.linewidth_cycle = [1, 2, 4]
        self.linestyle_cycle = ['-', '--', '-.']
        self.cycle_index = 0

################################################################


class GraphParser(bdparser.BDParser):
    """
    """

    def __init__(self):
        bdparser.BDParser.__init__(self)

    def declareArguments(self, add_mandatory=True):
        bdparser.BDParser.declareArguments(self, add_mandatory)
        graph_helper_group = self.register_group("GraphHelper")
        graph_helper_group.add_argument(
            "--quantity", type=lambda s: [e.strip() for e in s.split(',')],
            help="Specify the quantity to be outputed")
        graph_helper_group.add_argument(
            "--xrange", type=lambda s: [float(e) for e in s.split(',')],
            help="Specify range of values in the X direction. e.g: -1, 1")
        graph_helper_group.add_argument(
            "--yrange", type=lambda s: [float(e) for e in s.split(',')],
            help="Specify range of values in the Y direction")
        graph_helper_group.add_argument(
            "--sort_by", type=lambda s: [e.strip() for e in s.split(',')],
            help="Specify a study parameter to be used in sorting the curves")
        graph_helper_group.add_argument(
            "--xlabel", type=str, help="Specify the label for the X axis")
        graph_helper_group.add_argument(
            "--ylabel", type=str, help="Specify the label for the Y axis")
        graph_helper_group.add_argument(
            "--xscale", type=float, default=1.,
            help="Specify a scale factor for the X axis")
        graph_helper_group.add_argument(
            "--yscale", type=float, default=1.,
            help="Specify a scale factor for the Y axis")
        graph_helper_group.add_argument("--title", type=str,
                                        help="Specify title for the graph")
        graph_helper_group.add_argument(
            "--legend", type=lambda s: [e.strip() for e in s.split(',')],
            help=(
                "Specify a legend for the curves."
                " The syntax can use %%j.param or %%r.param to use"
                " get job and run values"), default=None)
        graph_helper_group.add_argument("--using", action='append', help=(
            "Allow to combine several quantities. "
            "The syntax uses python syntax where "
            "%%quantity1.column1:%%quantity2.column2 is the python "
            "numpy vector provided by quantity number (provided using the "
            "--quantities option) and column number (x or y). "
            "The sytax is comparable to the GNUPlot one in using the ':' "
            "to separate X from Y axis"))
        graph_helper_group.add_argument(
            "--list_quantities", action='store_true',
            help="Request to list the possible quantities to be plotted")
        graph_helper_group.add_argument(
            "--frequency", type=int, default=1, help=(
                "Set a frequency at which the quantity values "
                "should be retreived "
                "(helpful when the amount of data is very large)"))
        graph_helper_group.add_argument(
            "--start", type=float,
            help="Set the start X value for the graph")
        graph_helper_group.add_argument(
            "--end", type=int,
            help="Set the end X value for the graph")
        graph_helper_group.add_argument("--figsize", action='append')
        graph_helper_group.add_argument(
            "--blackwhite", action='store_true',
            help="Request a black and white graph generation")
        graph_helper_group.add_argument(
            "--marker", type=str,
            help="Request a specific marker (matplotlib option)")
        graph_helper_group.add_argument(
            "--fileout", type=str,
            help='Request to write a PDF file'
            ' (given its name) containing the graph')


################################################################
__all__ = ["GraphHelper", "GraphParser"]
################################################################
