# Copyright (c) 2023, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of LightSim2grid, LightSim2grid implements a c++ backend targeting the Grid2Op platform.

import unittest
import warnings

import grid2op
from grid2op.Action import CompleteAction


class DetachmentBackendOutputTester(unittest.TestCase):
    """issue is still not replicated and these tests pass"""
    def setUp(self) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage", 
                                     test=True,
                                     allow_detachment=True,
                                     action_class=CompleteAction)
        parameters = self.env.parameters
        parameters.ENV_DOES_REDISPATCHING = False
        self.env.change_parameters(parameters)
        self.env.change_forecast_parameters(parameters)
        # values are hard coded for time serie id = 1, do not modify
        self.obs = self.env.reset(seed=0, options={"time serie id": 1})
        return super().setUp()
    
    def tearDown(self) -> None:
        self.env.close()
        return super().tearDown()
    
    def test_disco_gen(self):
        """test i can disconnect a gen"""
        gen_id = 0
        obs, reward, done, info = self.env.step(self.env.action_space(
            {
                "set_bus": {"generators_id": [(gen_id, -1)]}
            }
        ))
        assert not done, info["exception"]
        assert not info["exception"]
        assert obs.gen_detached[gen_id]
        assert obs.gen_p[gen_id] == 0.
        assert obs.gen_v[gen_id] == 0.
        assert obs.gen_q[gen_id] == 0.
        assert obs.gen_theta[gen_id] == 0., f"{obs.gen_theta[gen_id]} vs 0."
        assert abs(obs.gen_p_detached[gen_id] - 79.8) <= 1e-5, f"{obs.gen_p_detached[gen_id]} vs {79.8}"
        
        obs1, _, done, info = self.env.step(self.env.action_space({}))
        assert not done, info["exception"]
        assert not info["exception"]
        assert obs.gen_detached[gen_id]
        assert obs1.gen_p[gen_id] == 0.
        assert obs1.gen_v[gen_id] == 0.
        assert obs1.gen_q[gen_id] == 0.
        assert obs1.gen_theta[gen_id] == 0., f"{obs1.gen_theta[gen_id]} vs 0."
        assert abs(obs1.gen_p_detached[gen_id] - 80.5) <= 1e-5, f"{obs.gen_p_detached[gen_id]} vs {80.5}"
        
        obs2, _, done, info = self.env.step(self.env.action_space({}))
        assert not done, info["exception"]
        assert not info["exception"]
        assert obs.gen_detached[gen_id]
        assert obs2.gen_p[gen_id] == 0.
        assert obs2.gen_v[gen_id] == 0.
        assert obs2.gen_q[gen_id] == 0.
        assert obs2.gen_theta[gen_id] == 0., f"{obs2.gen_theta[gen_id]} vs 0."
        assert abs(obs2.gen_p_detached[gen_id] - 80.5) <= 1e-5, f"{obs.gen_p_detached[gen_id]} vs {80.5}"
        
    def test_disco_load(self):
        """test i can disconnect a load"""
        load_id = 0
        obs, reward, done, info = self.env.step(self.env.action_space(
            {
                "set_bus": {"loads_id": [(load_id, -1)]}
            }
        ))
        assert not done
        assert obs.load_detached[load_id]
        assert obs.load_p[load_id] == 0., f"{obs.load_p[load_id]} vs 0."
        assert obs.load_q[load_id] == 0., f"{obs.load_q[load_id]} vs 0."
        assert obs.load_v[load_id] == 0., f"{obs.load_v[load_id]} vs 0."
        assert obs.load_theta[load_id] == 0., f"{obs.load_theta[load_id]} vs 0."
        assert abs(obs.load_p_detached[load_id] - 21.9) <= 1e-5
        
        obs1, _, done, info = self.env.step(self.env.action_space({}))
        assert not done
        assert obs1.load_detached[load_id]
        assert obs1.load_p[load_id] == 0., f"{obs1.load_p[load_id]} vs 0."
        assert obs1.load_q[load_id] == 0., f"{obs1.load_q[load_id]} vs 0."
        assert obs1.load_v[load_id] == 0., f"{obs1.load_v[load_id]} vs 0."
        assert obs1.load_theta[load_id] == 0., f"{obs1.load_theta[load_id]} vs 0."
        assert abs(obs1.load_p_detached[load_id] - 21.7) <= 1e-5
        
        obs2, _, done, info = self.env.step(self.env.action_space({}))
        assert not done
        assert obs2.load_detached[load_id]
        assert obs2.load_p[load_id] == 0., f"{obs2.load_p[load_id]} vs 0."
        assert obs2.load_q[load_id] == 0., f"{obs2.load_q[load_id]} vs 0."
        assert obs2.load_v[load_id] == 0., f"{obs2.load_v[load_id]} vs 0."
        assert obs2.load_theta[load_id] == 0., f"{obs2.load_theta[load_id]} vs 0."
        assert abs(obs2.load_p_detached[load_id] - 21.6) <= 1e-5
    
    def test_disco_storage(self):
        """test i can disconnect a storage unit"""
        sto_id = 0
        obs, reward, done, info = self.env.step(self.env.action_space(
            {
                "set_bus": {"storages_id": [(sto_id, -1)]},
                "set_storage": [(0, 1.)]
            }
        ))
        assert not done
        assert obs.storage_detached[sto_id]
        assert obs.storage_power[sto_id] == 0., f"{obs.storage_power[sto_id]} vs 0."
        assert abs(obs.storage_p_detached[sto_id] - 1.) <= 1e-5, f"{obs.storage_p_detached[sto_id]} vs 1."
        
        obs1, _, done, info = self.env.step(self.env.action_space({}))
        assert not done
        assert obs1.storage_detached[sto_id]
        assert obs1.storage_power[sto_id] == 0., f"{obs1.storage_power[sto_id]} vs 0."
        
        obs2, _, done, info = self.env.step(self.env.action_space({}))
        assert not done
        assert obs2.storage_detached[sto_id]
        assert obs2.storage_power[sto_id] == 0., f"{obs2.storage_power[sto_id]} vs 0."
    
    def test_min_uptime_downtime_updated(self):
        # test it's update normally
        assert (self.env._gen_uptime == [ 0,  0,  0, -1, -1,  0]).all()
        assert (self.env._gen_downtime == [-1, -1, -1,  0,  0, -1]).all()
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert (self.env._gen_uptime == [ 1,  1,  1, -1, -1,  1]).all()
        assert (self.env._gen_downtime == [-1, -1, -1,  1,  1, -1]).all()
        
        # now test the detachment of a gen updates it correctly
        obs, reward, done, info = self.env.step(self.env.action_space(
            {
                "set_bus": {"generators_id": [(0, -1)]}
            }
        ))
        assert self.env._gen_uptime[0] == -1, f"{self.env._gen_uptime[0]} vs -1"  # gen is disconnected
        assert self.env._gen_downtime[0] == 0, f"{self.env._gen_downtime[0]} vs 0"
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert self.env._gen_uptime[0] == -1, f"{self.env._gen_uptime[0]} vs -1"  # gen is disconnected
        assert self.env._gen_downtime[0] == 1, f"{self.env._gen_downtime[0]} vs 1"
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert self.env._gen_uptime[0] == -1, f"{self.env._gen_uptime[0]} vs -1"  # gen is disconnected
        assert self.env._gen_downtime[0] == 2, f"{self.env._gen_downtime[0]} vs 2"
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert self.env._gen_uptime[0] == -1, f"{self.env._gen_uptime[0]} vs -1"  # gen is disconnected
        assert self.env._gen_downtime[0] == 3, f"{self.env._gen_downtime[0]} vs 3"
        
        # now re attached the gen and make sure it works
        obs, reward, done, info = self.env.step(self.env.action_space(
            {
                "set_bus": {"generators_id": [(0, 1)]}
            }
        ))
        assert not done
        assert not info["exception"], f'{info["exception"]}'
        assert not info["is_illegal"]
        assert self.env._gen_uptime[0] == 0, f"{self.env._gen_uptime[0]} vs 0" 
        assert self.env._gen_downtime[0] == -1, f"{self.env._gen_downtime[0]} vs -1"
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert self.env._gen_uptime[0] == 1, f"{self.env._gen_uptime[0]} vs 1" 
        assert self.env._gen_downtime[0] == -1, f"{self.env._gen_downtime[0]} vs -1"
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert self.env._gen_uptime[0] == 2, f"{self.env._gen_uptime[0]} vs 2" 
        assert self.env._gen_downtime[0] == -1, f"{self.env._gen_downtime[0]} vs -1"
        
        
if __name__ == "__main__":
    unittest.main()
        