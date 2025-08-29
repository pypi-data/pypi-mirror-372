# Copyright (c) 2024, RTE (https://www.rte-france.com)
# See AUTHORS.txt and https://github.com/Grid2Op/grid2op/pull/319
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import unittest
import grid2op
import tempfile
import numpy as np
import re
import os
import json
import warnings

from grid2op.Chronics import (MultifolderWithCache,
                              GridStateFromFileWithForecastsWithMaintenance,
                              FromHandlers)
from grid2op.Chronics.handlers import (CSVHandler,
                                       NoisyForecastHandler,
                                       LoadQFromPHandler,
                                       JSONMaintenanceHandler)

from grid2op.Runner import Runner


class Issue616Tester(unittest.TestCase):
    def setUp(self):
        self.env_name = "l2rpn_case14_sandbox"
        # create first env
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make(self.env_name,
                               test=True)
        
        # hack for adding maintenance
        dict_maint = {
            "maintenance_starting_hour":  1,
            "maintenance_ending_hour": 2,
            "line_to_maintenance": ["1_2_2", "1_4_4", "9_10_12", "12_13_14"],
            "daily_proba_per_month_maintenance": [0.7 for _  in range(12)],
            "max_daily_number_per_month_maintenance": [1 for _  in range(12)],
            "maintenance_day_of_week": list(range(7))
            }
        self.tmp_files = [os.path.join(env.get_path_env(),
                                       "chronics", "0000", "maintenance_meta.json"),
                          os.path.join(env.get_path_env(),
                                       "chronics", "0001", "maintenance_meta.json"),
                          os.path.join(env.get_path_env(),
                                       "chronics", "0000", "maintenance_meta.json"),
        ]
        for path in self.tmp_files:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(fp=f, obj=dict_maint)
        env.close()
        # create the env with the maintenance
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env_bug = grid2op.make(self.env_name, 
                                    chronics_class=MultifolderWithCache,
                                    data_feeding_kwargs={"gridvalueClass": GridStateFromFileWithForecastsWithMaintenance},
                                    test=True
                                   )
        self.env_bug.chronics_handler.reset()
        
        # store the normal maintenance schedule:
        self.maint_ref = (np.array([  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  
                                     11, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 
                                     298, 299]) + 12,
                          np.array([4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 2, 2, 2, 2, 2, 
                                    2, 2, 2, 2, 2, 2]))
    
    def tearDown(self) -> None:
        self.env_bug.close()
        for el in self.tmp_files:
            if os.path.exists(el):
                os.remove(el)
        return super().tearDown()
    
    def test_reset(self):
        """test that the seed is used correctly in env.reset"""
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_ref = 1. * self.env_bug.chronics_handler.real_data.data.maintenance
        
        obs = self.env_bug.reset(seed=1, options={"time serie id": 0})
        maint_1 = 1. * self.env_bug.chronics_handler.real_data.data.maintenance
        
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_0 = 1. * self.env_bug.chronics_handler.real_data.data.maintenance
        
        assert (maint_ref == maint_0).all()
        assert (maint_ref != maint_1).any()
        assert (maint_ref.nonzero()[0] == self.maint_ref[0]).all()
        assert (maint_ref.nonzero()[1] == self.maint_ref[1]).all()
        
    def test_runner(self):
        """test the runner behaves correctly"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            runner = Runner(**self.env_bug.get_params_for_runner())
        res = runner.run(nb_episode=3,
                         env_seeds=[0, 1, 0], 
                         max_iter=5,
                         add_detailed_output=True)
        
        maint_ref = np.array([ -1,  -1, 300,  -1,  12,  -1,  -1,  -1,  -1,  -1,  
                              -1,  -1,  -1, -1,  -1,  -1,  -1,  -1,  -1,  -1],
                             dtype=np.int32)
        assert (res[0][-1].observations[0].time_next_maintenance == maint_ref).all()
        assert (res[0][-1].observations[0].time_next_maintenance != res[1][-1].observations[0].time_next_maintenance).any()
        assert (res[0][-1].observations[0].time_next_maintenance == res[2][-1].observations[0].time_next_maintenance).all()
        
    def test_chronics_handler_twice_reset(self):
        """test the same results is obtained if the chronics handler is reset twice"""
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_ref = 1. * self.env_bug.chronics_handler.real_data.data.maintenance
        assert (maint_ref.nonzero()[0] == self.maint_ref[0]).all()
        assert (maint_ref.nonzero()[1] == self.maint_ref[1]).all()
        
        self.env_bug.chronics_handler.reset()
        maint_ref = 1. * self.env_bug.chronics_handler.real_data.data.maintenance
        assert (maint_ref.nonzero()[0] == self.maint_ref[0]).all()
        assert (maint_ref.nonzero()[1] == self.maint_ref[1]).all()


class Issue616WithHandlerTester(unittest.TestCase):
    def setUp(self):
        self.env_name = "l2rpn_case14_sandbox"
        hs_ = [5*(i+1) for i in range(12)]
        
        # create first env
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make(self.env_name,
                               test=True)
        
        # hack for adding maintenance
        dict_maint = {
            "maintenance_starting_hour":  1,
            "maintenance_ending_hour": 2,
            "line_to_maintenance": ["1_2_2", "1_4_4", "9_10_12", "12_13_14"],
            "daily_proba_per_month_maintenance": [0.7 for _  in range(12)],
            "max_daily_number_per_month_maintenance": [1 for _  in range(12)],
            "maintenance_day_of_week": list(range(7))
            }
        self.tmp_json = tempfile.NamedTemporaryFile(dir=os.path.join(env.get_path_env(), "chronics", "0000"),
                                    prefix="maintenance_meta",
                                    suffix=".json")
        with open(self.tmp_json.name, "w", encoding="utf-8") as f:
            json.dump(fp=f, obj=dict_maint)
        
        # uses the default noise: sqrt(horizon) * 0.01 : error of 8% 1h ahead
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env_bug = grid2op.make(self.env_name,
                                        chronics_class=MultifolderWithCache,
                            data_feeding_kwargs={"gridvalueClass": FromHandlers,
                                                    "gen_p_handler": CSVHandler("prod_p"),
                                                    "load_p_handler": CSVHandler("load_p"),
                                                    "gen_v_handler": CSVHandler("prod_v"),
                                                    "load_q_handler": LoadQFromPHandler("load_q"),
                                                    "h_forecast": hs_,
                                                    "maintenance_handler": JSONMaintenanceHandler(json_file_name=self.tmp_json.name),
                                                    "gen_p_for_handler": NoisyForecastHandler("prod_p_forecasted"),
                                                    "load_p_for_handler": NoisyForecastHandler("load_p_forecasted"),
                                                    "load_q_for_handler": NoisyForecastHandler("load_q_forecasted"),
                                                },
                            test=True
                                )  
            self.env_bug.chronics_handler.reset()
        
        # store the normal maintenance schedule:
        self.maint_ref = (np.array([  12,   13,   14,   15,   16,   17,   18,   19,   20,   21,   22,
         23,  300,  301,  302,  303,  304,  305,  306,  307,  308,  309,
        310,  311]),
        np.array([12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14,
       14, 14, 14, 14, 14, 14, 14]))
        
        self.load_p_ref = np.array([[22.        , 87.        , 45.79999924,  7.        , 12.        ,
        28.20000076,  8.69999981,  3.5       ,  5.5       , 12.69999981,
        14.80000019],
       [22.44357109, 90.38361359, 46.61357117,  7.00726891, 12.49121857,
        28.84151268,  8.93680668,  3.45285726,  5.58550406, 13.10054588,
        15.43630219],
       [22.48419762, 89.22782135, 45.57607269,  6.98833132, 12.35618019,
        28.45972633,  9.01393414,  3.44352579,  5.57040882, 12.96386147,
        15.2933054 ],
       [21.85004234, 86.51035309, 44.29330063,  6.82195902, 11.86427689,
        28.2765255 ,  8.79933834,  3.36154509,  5.33892441, 12.65522861,
        14.92921543],
       [21.61282349, 86.64777374, 44.50276947,  6.68032742, 11.88705349,
        27.90019035,  8.84160995,  3.34016371,  5.30496597, 12.57473373,
        14.63777542],
       [23.22621727, 92.27429962, 47.29320145,  7.25162458, 12.71661758,
        30.16255379,  9.24844837,  3.57326436,  5.57008839, 13.34719276,
        15.97459316],
       [20.23793983, 81.04374695, 42.03972244,  6.25536346, 10.85489559,
        26.03334999,  8.0951767 ,  3.12768173,  5.05948496, 11.49882984,
        13.89058685],
       [19.92967606, 81.96430206, 41.73068237,  6.54965878, 11.13441944,
        26.10506821,  8.04672432,  3.08769631,  4.95902777, 11.50868607,
        13.94141674],
       [20.64870644, 83.94567871, 42.16581726,  6.56127167, 11.38573551,
        27.0170002 ,  8.39456749,  3.1841464 ,  5.21042156, 11.96467113,
        14.37690353],
       [19.72007751, 79.25064087, 40.82889175,  6.11044645, 10.83215523,
        25.83052444,  7.77693176,  3.05522323,  4.814291  , 11.5728159 ,
        13.9799614 ],
       [21.79347801, 87.17391205, 42.77978897,  6.76001358, 11.70390511,
        28.14990807,  8.67703247,  3.32955885,  5.24657774, 12.30927849,
        14.83167171],
       [19.81615639, 78.61643982, 40.09531021,  6.11152506, 10.64886951,
        25.27948952,  7.87090397,  2.96316385,  4.72254229, 11.20446301,
        13.88982964],
       [19.3391819 , 77.26506805, 39.22829056,  6.04922247, 10.44865608,
        24.83847427,  7.8823204 ,  2.93295646,  4.76605368, 11.18189621,
        13.19830322]])
        
        self.load_q_ref = np.array([15.4      , 60.899998 , 32.059998 ,  4.9      ,  8.4      ,
       19.74     ,  6.0899997,  2.45     ,  3.85     ,  8.889999 ,
       10.36     ], dtype=np.float32)

    def tearDown(self) -> None:
        self.env_bug.close()
        self.tmp_json.close()
        return super().tearDown()
    
    def test_reset(self):
        """test that the seed is used correctly in env.reset"""
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_ref = 1. * self.env_bug.chronics_handler.real_data.data.maintenance_handler.maintenance
        load_q_ref = 1. * obs.load_q
        load_p_ref = 1. * obs.get_forecast_arrays()[0]
        
        obs = self.env_bug.reset(seed=1, options={"time serie id": 0})
        maint_1 = 1. * self.env_bug.chronics_handler.real_data.data.maintenance_handler.maintenance
        load_q_1 = 1. * obs.load_q
        load_p_1= 1. * obs.get_forecast_arrays()[0]
        
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_0 = 1. * self.env_bug.chronics_handler.real_data.data.maintenance_handler.maintenance
        load_q_0 = 1. * obs.load_q
        load_p_0 = 1. * obs.get_forecast_arrays()[0]
        
        # maintenance, so JSONMaintenanceHandler
        assert (maint_ref == maint_0).all()
        assert (maint_ref != maint_1).any()
        assert (maint_ref.nonzero()[0] == self.maint_ref[0]).all()
        assert (maint_ref.nonzero()[1] == self.maint_ref[1]).all()
        
        # load_q, so LoadQFromPHandler
        assert (load_q_ref == load_q_0).all()
        # assert (load_q_ref != load_q_1).any()  # it's normal it works as this is not random !
        assert (load_q_ref == self.load_q_ref).all()
        
        # load_p_forecasted, so NoisyForecastHandler
        assert (load_p_ref == load_p_0).all()
        assert (load_p_ref != load_p_1).any()
        assert (np.abs(load_p_ref - self.load_p_ref) <= 1e-6).all()
        
    def test_runner(self):
        """test the runner behaves correctly"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            runner = Runner(**self.env_bug.get_params_for_runner())
            res = runner.run(nb_episode=3,
                            env_seeds=[0, 1, 0], 
                            max_iter=5,
                            add_detailed_output=True)
        obs = res[0][-1].observations[0]
        maint_ref = 1. * obs.time_next_maintenance
        load_q_ref = 1. * obs.load_q
        # load_p_ref = 1. * obs.get_forecast_arrays()[0] not present in episodeData
        
        obs = res[1][-1].observations[0]
        maint_1 = 1. * obs.time_next_maintenance
        load_q_1 = 1. * obs.load_q
        # load_p_1 = 1. * obs.get_forecast_arrays()[0] not present in episodeData
        
        obs = res[2][-1].observations[0]
        maint_0 = 1. * obs.time_next_maintenance
        load_q_0 = 1. * obs.load_q
        # load_p_0 = 1. * obs.get_forecast_arrays()[0] not present in episodeData
        
        # maintenance, so JSONMaintenanceHandler
        assert (maint_ref == maint_0).all()
        assert (maint_ref != maint_1).any()
        # TODO test against a reference data stored in the file
        
        # load_q, so LoadQFromPHandler
        assert (load_q_ref == load_q_0).all()
        # assert (load_q_ref != load_q_1).any()  # it's normal it works as this is not random !
        assert (load_q_ref == self.load_q_ref).all()
        
        # load_p_forecasted, so NoisyForecastHandler
        # assert (load_p_ref == load_p_0).all()
        # assert (load_p_ref != load_p_1).any()
        # TODO test that with an agent
        
    def test_chronics_handler_twice_reset(self):
        """test the same results is obtained if the chronics handler is reset twice"""
        obs = self.env_bug.reset(seed=0, options={"time serie id": 0})
        maint_ref = 1. * obs.time_next_maintenance
        load_q_ref = 1. * obs.load_q
        load_p_ref = 1. * obs.get_forecast_arrays()[0]
        
        self.env_bug.chronics_handler.reset()
        maint_1 = 1. * obs.time_next_maintenance
        load_q_1 = 1. * obs.load_q
        load_p_1 = 1. * obs.get_forecast_arrays()[0]
        
        assert (np.abs(maint_ref - maint_1) <= 1e-6).all()
        assert (np.abs(load_q_ref - load_q_1) <= 1e-6).all()
        assert (np.abs(load_p_ref - load_p_1) <= 1e-6).all()
    
    
if __name__ == "__main__":
    unittest.main()
