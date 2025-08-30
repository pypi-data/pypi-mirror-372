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

from __future__ import print_function

from . import job

import numpy as np


class BDStat(object):
    """
    """

    def average(self, quantities, run_list, entries_to_average,
                functor=None, quiet=True):
        cpt = dict()
        results = dict()

        run_counter = 0
        entries_to_average.append("id")
        entries_to_consider = []

        if len(run_list) > 0:
            for e in run_list[0][1].entries:
                if e not in entries_to_average:
                    entries_to_consider.append(e)

        entries_to_consider = sorted(entries_to_consider)

        if functor is None:
            def _identity_functor(*x):
                return dict([(quantities[i], e) for i, e in enumerate(x)])

            functor = _identity_functor

        for r, j in run_list:
            run_counter += 1

            entries_values = [j[i] for i in entries_to_consider]
            entries_values = tuple(entries_values)

            scalar_quantities = r.getScalarQuantities(quantities)
            if scalar_quantities is None:
                continue
            scalar_quantities = [
                np.array(q[1:]).T for q in scalar_quantities if q is not None]
            to_average = functor(*scalar_quantities)

            if entries_values not in results.keys():
                results[entries_values] = dict()
                cpt[entries_values] = 0

            result = results[entries_values]
            for quantity_name, value in to_average.items():
                if quantity_name not in result.keys():
                    result[quantity_name] = np.zeros((value.shape[0], 3))

                # print(value.shape)
                sz1 = value.shape[0]
                sz2 = result[quantity_name].shape[0]

                if (sz1 > sz2):
                    value = value[:sz2, :]
                elif (sz2 > sz1):
                    result[quantity_name] = result[quantity_name][:sz1, :]

                # print(result[ent].shape, value.shape)
                result[quantity_name][:, 0] += value[:, 0]
                result[quantity_name][:, 1] += value[:, 1]
                result[quantity_name][:, 2] += value[:, 1]**2
            cpt[entries_values] += 1

        # after summation, performs the average
        for entries_values, result in results.items():
            myjob = self.base.Job()
            for i, entry in enumerate(entries_to_consider):
                myjob.entries[entry] = entries_values[i]

            for q in result.keys():
                result[q] /= cpt[entries_values]
                result[q][:, 2] -= result[q][:, 1]**2
                result[q][:, 2] = np.maximum(
                    np.zeros(result[q][:, 2].shape[0]),
                    result[q][:, 2])
                result[q][:, 2] = np.sqrt(result[q][:, 2])

            results[entries_values] = {"ref_job": myjob,
                                       "averaged_number": cpt[entries_values],
                                       "data": result
                                       }

        return results

    def averageVector(self, quantity, run_list, entries_to_average):
        result = dict()
        all_steps = dict()
        run_info = dict()
        cpt = dict()
        run_counter = 0
        nb_runs = len(run_list)

        entries_to_average.append("id")
        entries_to_consider = []

        if (run_list is not []):
            for e in run_list[0][1].entries:
                if e not in entries_to_average:
                    entries_to_consider.append(e)

        for r, j in run_list:
            steps, data = r.getAllVectorQuantity(quantity)
            run_counter += 1

            if (data is None):
                continue

            print("{0:<5} {1:<15} {2:>5}/{3:<5} {4:.1f}%".format(
                r.id, data.shape, run_counter, nb_runs,
                1.*run_counter/nb_runs*100))
            ent = [j[i] for i in entries_to_consider]
            ent = tuple(ent)
            if (ent not in result.keys()):
                #                print (ent)
                result[ent] = np.zeros([data.shape[0], data.shape[1], 2])
                all_steps[ent] = steps
                cpt[ent] = 0
            # print (result[ent].shape)
            # print (q.shape)
            sz1 = data.shape[0]
            sz2 = result[ent].shape[0]
            if (sz1 > sz2):
                data = data[:sz2]
                steps = steps[:sz2]
            elif (sz2 > sz1):
                result[ent] = result[ent][:sz1]
                all_steps[ent] = all_steps[ent][:sz1]

            result[ent][:, :, 0] += data[:, :]
            result[ent][:, :, 1] += data[:, :]**2
            cpt[ent] += 1

        for ent in result.keys():
            #            print (ent)
            myjob = self.base.Job(self.base)
            for i in range(0, len(entries_to_consider)):
                myjob.entries[entries_to_consider[i]] = ent[i]

            result[ent] /= cpt[ent]
            result[ent][:, :, 1] -= result[ent][:, :, 0]**2
            result[ent][:, :, 1] = np.sqrt(result[ent][:, :, 1])
            result[ent] = {"ref_job": myjob,
                           "averaged_number": cpt[ent],
                           "steps": all_steps[ent],
                           "data": result[ent]}

        return result

    def __init__(self, base, **params):
        self.base = base

################################################################


__all__ = ["BDStat"]
