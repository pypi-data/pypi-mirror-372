# Copyright (c) 2019-2020, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

from typing import Tuple

from grid2op.typing_variables import STEP_INFO_TYPING

import grid2op.Observation
from grid2op.Action import BaseAction
from grid2op.Environment.environment import Environment


class ForecastEnv(Environment):
    """Type of environment that increments the `highres_simulator` when it calls the env.step method.
    
    It is the returned value of :func:`grid2op.Observation.BaseObservation.get_forecast_env`.
    """
    def __init__(self,**kwargs):
        if "_update_obs_after_reward" not in kwargs:
            kwargs["_update_obs_after_reward"] = False
        super().__init__(**kwargs)
        self._do_not_erase_local_dir_cls = True
        
    def step(self, action: BaseAction) -> Tuple["grid2op.Observation.BaseObservation",
                                                float,
                                                bool,
                                                STEP_INFO_TYPING]:
        self._highres_sim_counter += 1
        return super().step(action)
