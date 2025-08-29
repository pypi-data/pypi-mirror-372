# Copyright (c) 2019-2024, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

from typing import Dict, Union, Literal

import grid2op
from grid2op.Exceptions import EnvError, ChronicsError
from grid2op.Chronics import ChangeNothing


class _ObsCH(ChangeNothing):
    """
    INTERNAL

    .. warning:: /!\\\\ Internal, do not use unless you know what you are doing /!\\\\

    This class is reserved to internal use. Do not attempt to do anything with it.
    """
    
    # properties that should not be accessed
    @property
    def chronicsClass(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `chronicsClass`")
    
    @property
    def path(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `path`")
    
    @property
    def _real_data(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_real_data`")
    
    @property
    def kwargs(self):
        return {}

    @kwargs.setter
    def kwargs(self, new_value):
        raise ChronicsError('Impossible to set the "kwargs" attribute')
    
    @property
    def _kwargs(self):
        return {}

    # functions overriden from the ChronicsHandler class
    def forecasts(self):
        return []
    
    def get_name(self):
        return ""
    
    def next_time_step(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `next_time_step`")
    
    def max_episode_duration(self):
        return 0
    
    def seed(self, seed):
        """.. warning:: This function is part of the public API of ChronicsHandler but should not do anything here"""
        pass
    
    def cleanup_action_space(self):
        """.. warning:: This function is part of the public API of ChronicsHandler but should not do anything here"""
        pass
    
    # methods overriden from the ChronicsHandler class (__getattr__) so forwarded to the Chronics class
    @property
    def gridvalueClass(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `gridvalueClass`")
    
    @property
    def data(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `data`")
    
    @property
    def sep(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `sep`")
    
    @property
    def subpaths(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `subpaths`")
    
    @property
    def _order(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_order`")
    
    @property
    def chunk_size(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `chunk_size`")
    
    @property
    def _order_backend_loads(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_order_backend_loads`")
    
    @property
    def _order_backend_prods(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_order_backend_prods`")
    
    @property
    def _order_backend_lines(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_order_backend_lines`")
    
    @property
    def _order_backend_subs(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_order_backend_subs`")
    
    @property
    def _names_chronics_to_backend(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_names_chronics_to_backend`")
    
    @property
    def _filter(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_filter`")
    
    @property
    def _prev_cache_id(self):
        raise EnvError("There are no time series in the observation from `obs.simulate`, so no `_prev_cache_id`")
    