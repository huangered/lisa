# SPDX-License-Identifier: Apache-2.0
#
# Copyright (C) 2015, ARM Limited and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

""" CPUs Analysis Module """

import pandas as pd

from lisa.utils import memoized
from lisa.analysis.base import AnalysisBase, requires_events


class CpusAnalysis(AnalysisBase):
    """
    Support for CPUs signals analysis
    """

    name = 'cpus'

    def __init__(self, trace):
        super(CpusAnalysis, self).__init__(trace)


###############################################################################
# DataFrame Getter Methods
###############################################################################

    @requires_events(['sched_switch'])
    def df_context_switches(self):
        """
        Compute number of context switches on each CPU.

        :returns: A :class:`pandas.DataFrame` with:

          * A ``context_switch_cnt`` column (the number of context switch per CPU)
        """
        sched_df = self._trace.df_events('sched_switch')
        cpus = list(range(self._trace.cpus_count))
        ctx_sw_df = pd.DataFrame(
            [len(sched_df[sched_df['__cpu'] == cpu]) for cpu in cpus],
            index=cpus,
            columns=['context_switch_cnt']
        )
        ctx_sw_df.index.name = 'cpu'

        return ctx_sw_df

###############################################################################
# Plotting Methods
###############################################################################

    @requires_events(df_context_switches.required_events)
    def plot_context_switch(self, filepath=None):
        """
        Plot histogram of context switches on each CPU.
        """
        fig, axis = self.setup_plot(height=8)

        ctx_sw_df = self.df_context_switches()
        ctx_sw_df["context_switch_cnt"].plot.bar(
            title="Per-CPU Task Context Switches", legend=False, ax=axis)
        axis.grid()

        self.save_plot(fig, filepath)
        return axis

    def plot_orig_capacity(self, axis, cpu):
        """
        Plot the orig capacity of a CPU onto a given axis

        :param axis: The axis
        :type axis: matplotlib.axes.Axes

        :param cpu: The CPU
        :type cpu: int
        """
        if "cpu-capacities" in self._trace.plat_info:
            axis.axhline(self._trace.plat_info["cpu-capacities"][cpu],
                         color=self.get_next_color(axis),
                         linestyle='--', label="orig_capacity")

# vim :set tabstop=4 shiftwidth=4 expandtab textwidth=80
