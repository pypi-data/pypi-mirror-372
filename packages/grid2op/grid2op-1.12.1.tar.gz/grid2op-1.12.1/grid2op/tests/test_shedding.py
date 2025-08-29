# Copyright (c) 2024, RTE (https://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public License, version 2.0.
# If a copy of the Mozilla Public License, version 2.0 was not distributed with this file,
# you can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of Grid2Op, Grid2Op a testbed platform to model sequential decision making in power systems.

import json
import warnings
import unittest
import numpy as np
import tempfile

import grid2op
from grid2op.dtypes import dt_float
from grid2op.Exceptions import AmbiguousAction
from grid2op.Action import CompleteAction
from grid2op.Backend import PandaPowerBackend
from grid2op.Parameters import Parameters
from grid2op.Action._backendAction import _BackendAction


class _BackendNoDetach(PandaPowerBackend):
    @classmethod
    def set_detachment_is_allowed(cls, detachment_is_allowed: bool) -> None:
        cls.detachment_is_allowed = False
            
    def load_grid(self, path, filename = None):
        self.cannot_handle_detachment()
        return super().load_grid(path, filename)


class TestShedding(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        param = Parameters()
        param.MAX_SUB_CHANGED = 5
        param.ENV_DOES_REDISPATCHING = False  # some tests fail otherwise
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("rte_case5_example",
                                    param=param,
                                    action_class=CompleteAction,
                                    allow_detachment=True,
                                    test=True,
                                    _add_to_name=type(self).__name__)
        obs = self.env.reset(seed=0, options={"time serie id": "00"}) # Reproducibility
        self.load_lookup = {name:i for i,name in enumerate(self.env.name_load)}
        self.gen_lookup = {name:i for i,name in enumerate(self.env.name_gen)}

    def tearDown(self) -> None:
        self.env.close()

    def test_shedding_parameter_is_true(self):
        assert self.env._allow_detachment is True
        assert type(self.env).detachment_is_allowed
        assert type(self.env.backend).detachment_is_allowed
        assert self.env.backend.detachment_is_allowed

    def test_shed_single_load(self):
        # Check that a single load can be shed
        load_idx = self.load_lookup["load_4_2"]
        load_pos = self.env.load_pos_topo_vect[load_idx]
        act = self.env.action_space({
            "set_bus": [(load_pos, -1)]
        })
        obs, _, done, info = self.env.step(act)
        assert not done
        assert info["is_illegal"] is False
        assert obs.topo_vect[load_pos] == -1

    def test_shed_single_generator(self):
        # Check that a single generator can be shed
        gen_idx = self.gen_lookup["gen_0_0"]
        gen_pos = self.env.gen_pos_topo_vect[gen_idx]
        act = self.env.action_space({
            "set_bus": [(gen_pos, -1)]
        })
        obs, _, done, info = self.env.step(act)
        assert not done
        assert info["is_illegal"] is False
        assert obs.topo_vect[gen_pos] == -1

    def test_shed_multiple_loads(self):
        # Check that multiple loads can be shed at the same time
        load_idx1 = self.load_lookup["load_4_2"]
        load_idx2 = self.load_lookup["load_3_1"]
        load_pos1 = self.env.load_pos_topo_vect[load_idx1]
        load_pos2 = self.env.load_pos_topo_vect[load_idx2]
        act = self.env.action_space({
            "set_bus": [(load_pos1, -1), (load_pos2, -1)]
        })
        obs, _, done, info = self.env.step(act)
        assert not done
        assert info["is_illegal"] is False
        assert obs.topo_vect[load_pos1] == -1
        assert obs.topo_vect[load_pos2] == -1

    def test_shed_load_and_generator(self):
        # Check that load and generator can be shed at the same time
                # Check that multiple loads can be shed at the same time
        load_idx = self.load_lookup["load_4_2"]
        gen_idx = self.gen_lookup["gen_0_0"]
        load_pos = self.env.load_pos_topo_vect[load_idx]
        gen_pos = self.env.gen_pos_topo_vect[gen_idx]
        act = self.env.action_space({
            "set_bus": [(load_pos, -1), (gen_pos, -1)]
        })
        obs, _, done, info = self.env.step(act)
        assert not done
        assert info["is_illegal"] is False
        assert obs.topo_vect[load_pos] == -1
        assert obs.topo_vect[gen_pos] == -1

    def test_shedding_persistance(self):
        # Check that components remains disconnected if shed
        load_idx = self.load_lookup["load_4_2"]
        load_pos = self.env.load_pos_topo_vect[load_idx]
        act = self.env.action_space({
            "set_bus": [(load_pos, -1)]
        })
        _ = self.env.step(act)
        obs, _, done, _ = self.env.step(self.env.action_space({}))
        assert not done
        assert obs.topo_vect[load_pos] == -1


class TestSheddingActions(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        p = Parameters()
        p.MAX_SUB_CHANGED = 999999
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage",
                                    param=p,
                                    action_class=CompleteAction,
                                    allow_detachment=True,
                                    test=True,
                                    _add_to_name=type(self).__name__)
        obs = self.env.reset(seed=0, options={"time serie id": 0}) # Reproducibility
        assert type(self.env).detachment_is_allowed
        assert type(obs).detachment_is_allowed
        assert type(self.env.action_space()).detachment_is_allowed
        
    def tearDown(self) -> None:
        self.env.close()
        super().tearDown()
        
    def aux_test_action_property_xxx(self, el_type):
        detach_xxx = f"detach_{el_type}"
        _detach_xxx = f"_detach_{el_type}"
        _modif_detach_xxx = f"_modif_detach_{el_type}"
        n_xxx = getattr(type(self.env), f"n_{el_type}")
        name_xxx = getattr(type(self.env), f"name_{el_type}")
        xxx_change_bus = f"{el_type}_change_bus"
        xxx_set_bus = f"{el_type}_set_bus"
        xxx_to_subid = getattr(type(self.env),f"{el_type}_to_subid")
        
        act1 = self.env.action_space()
        assert detach_xxx in type(act1).authorized_keys, f"{detach_xxx} not in {type(act1).authorized_keys}"
        setattr(act1, detach_xxx, np.ones(n_xxx, dtype=bool))
        assert getattr(act1, _detach_xxx).all()
        assert getattr(act1, _modif_detach_xxx)
        lines_imp, subs_imp = act1.get_topological_impact(_read_from_cache=False)
        assert subs_imp[xxx_to_subid].all()
        assert (~lines_imp).all()
        
        act2 = self.env.action_space()
        setattr(act2, detach_xxx, 1)
        assert getattr(act2, _detach_xxx)[1]
        assert getattr(act2, _modif_detach_xxx)
        lines_imp, subs_imp = act2.get_topological_impact(_read_from_cache=False)
        assert subs_imp[xxx_to_subid[1]].all()
        assert (~lines_imp).all()
        
        act3 = self.env.action_space()
        setattr(act3, detach_xxx, [0, 1])
        assert getattr(act3, _detach_xxx)[0]
        assert getattr(act3, _detach_xxx)[1]
        assert getattr(act3, _modif_detach_xxx)
        lines_imp, subs_imp = act3.get_topological_impact(_read_from_cache=False)
        assert subs_imp[xxx_to_subid[[0, 1]]].all()
        assert (~lines_imp).all()
        
        for el_id, el_nm in enumerate(name_xxx):
            act4 = self.env.action_space()
            setattr(act4, detach_xxx, {el_nm})
            assert getattr(act4, _detach_xxx)[el_id]
            assert getattr(act4, _modif_detach_xxx)
            lines_imp, subs_imp = act4.get_topological_impact(_read_from_cache=False)
            assert subs_imp[xxx_to_subid[el_id]].all()
            assert (~lines_imp).all()
        
        # change and disconnect
        act5 = self.env.action_space()
        setattr(act5, xxx_change_bus, [0])
        setattr(act5, detach_xxx, [0])
        is_amb, exc_ = act5.is_ambiguous()
        assert is_amb, f"error for {el_type}"
        assert isinstance(exc_, AmbiguousAction), f"error for {el_type}"
        
        # set_bus and disconnect
        act6 = self.env.action_space()
        setattr(act6, xxx_set_bus, [(0, 1)])
        setattr(act6, detach_xxx, [0])
        is_amb, exc_ = act6.is_ambiguous()
        assert is_amb, f"error for {el_type}"
        assert isinstance(exc_, AmbiguousAction), f"error for {el_type}"
        
        # flag not set
        act7 = self.env.action_space()
        getattr(act7, _detach_xxx)[0] = True
        act7._cached_is_not_ambiguous = False
        is_amb, exc_ = act7.is_ambiguous()
        assert is_amb, f"error for {el_type}"
        assert isinstance(exc_, AmbiguousAction), f"error for {el_type}"
        
        for el_id in range(n_xxx):
            # test to / from dict
            act8 = self.env.action_space()
            setattr(act8, detach_xxx, [el_id])
            dict_ = act8.as_serializable_dict()  # you can save this dict with the json library
            act8_reloaded = self.env.action_space(dict_)
            assert act8 == act8_reloaded, f"error for {el_type} for id {el_id}"
            
            # test to / from json
            act9 = self.env.action_space()
            setattr(act9, detach_xxx, [el_id])
            dict_ = act9.to_json()
            with tempfile.NamedTemporaryFile() as f_tmp:
                with open(f_tmp.name, "w", encoding="utf-8") as f:
                    json.dump(obj=dict_, fp=f)
                    
                with open(f_tmp.name, "r", encoding="utf-8") as f:
                    dict_reload = json.load(fp=f)
            act9_reloaded = self.env.action_space()
            act9_reloaded.from_json(dict_reload)
            assert act9 == act9_reloaded, f"error for {el_type} for id {el_id}"
            
            # test to / from vect
            act10 = self.env.action_space()
            setattr(act10, detach_xxx, [el_id])
            vect_ = act10.to_vect()        
            act10_reloaded = self.env.action_space()
            act10_reloaded.from_vect(vect_)
            assert act10 == act10_reloaded, f"error for {el_type} for id {el_id}"
    
    def test_action_property_load(self):
        self.aux_test_action_property_xxx("load")
        
    def test_action_property_gen(self):
        self.aux_test_action_property_xxx("gen")
        
    def test_action_property_storage(self):
        self.aux_test_action_property_xxx("storage")

    def test_backend_action(self):
        for load_id in range(self.env.n_load):
            bk_act :_BackendAction = self.env.backend.my_bk_act_class()
            act = self.env.action_space()
            act.detach_load = load_id
            assert act._detach_load[load_id]
            bk_act += act
            (
                active_bus,
                (prod_p, prod_v, load_p, load_q, storage),
                topo__,
                shunts__,
            ) = bk_act()
            assert topo__.changed[self.env.load_pos_topo_vect[load_id]], f"error for load {load_id}"
            assert topo__.values[self.env.load_pos_topo_vect[load_id]] == -1, f"error for load {load_id}"
            assert bk_act.get_load_detached()[load_id], f"error for load {load_id}"
            assert bk_act.get_load_detached().sum() == 1, f"error for load {load_id}"
            
        for gen_id in range(self.env.n_gen):
            bk_act :_BackendAction = self.env.backend.my_bk_act_class()
            act = self.env.action_space()
            act.detach_gen = gen_id
            assert act._detach_gen[gen_id]
            bk_act += act
            (
                active_bus,
                (prod_p, prod_v, load_p, load_q, storage),
                topo__,
                shunts__,
            ) = bk_act()
            assert topo__.changed[self.env.gen_pos_topo_vect[gen_id]], f"error for gen {gen_id}"
            assert topo__.values[self.env.gen_pos_topo_vect[gen_id]] == -1, f"error for gen {gen_id}"
            assert bk_act.get_gen_detached()[gen_id], f"error for gen {gen_id}"
            assert bk_act.get_gen_detached().sum() == 1, f"error for gen {gen_id}"
            
        for sto_id in range(self.env.n_storage):
            bk_act :_BackendAction = self.env.backend.my_bk_act_class()
            act = self.env.action_space()
            act.detach_storage = sto_id
            assert act._detach_storage[sto_id]
            bk_act += act
            (
                active_bus,
                (prod_p, prod_v, load_p, load_q, storage),
                topo__,
                shunts__,
            ) = bk_act()
            assert topo__.changed[self.env.storage_pos_topo_vect[sto_id]], f"error for storage {sto_id}"
            assert topo__.values[self.env.storage_pos_topo_vect[sto_id]] == -1, f"error for storage {sto_id}"
            assert bk_act.get_sto_detached()[sto_id], f"error for storage {sto_id}"
            assert bk_act.get_sto_detached().sum() == 1, f"error for storage {sto_id}"
    
    
class TestSheddingEnv(unittest.TestCase):
    def get_parameters(self):
        params = Parameters()
        params.MAX_SUB_CHANGED = 999999
        params.ENV_DOES_REDISPATCHING = False
        return params
        
    def setUp(self):
        params = self.get_parameters()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage",
                                    param=params,
                                    action_class=CompleteAction,
                                    allow_detachment=True,
                                    test=True,
                                    _add_to_name=type(self).__name__)
        obs = self.env.reset(seed=0, options={"time serie id": 0}) # Reproducibility
        assert type(self.env).detachment_is_allowed
        assert type(obs).detachment_is_allowed
        assert type(self.env.action_space()).detachment_is_allowed
    
    def tearDown(self):
        self.env.close()
        return super().tearDown()
    
    def test_no_shedding(self):
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert (np.abs(self.env._prev_load_p - obs.load_p) <= 1e-7).all()
        assert (np.abs(self.env._prev_load_q - obs.load_q) <= 1e-7).all()
        assert (np.abs(self.env._prev_gen_p - obs.gen_p) <= 1e-7).all()
        # for env
        assert (~self.env._loads_detached).all()
        assert (~self.env._gens_detached).all()
        assert (~self.env._storages_detached).all()
        assert (np.abs(self.env._load_p_detached) <= 1e-7).all()
        assert (np.abs(self.env._load_q_detached) <= 1e-7).all()
        assert (np.abs(self.env._gen_p_detached) <= 1e-7).all()
        assert (np.abs(self.env._storage_p_detached) <= 1e-7).all()
        # for obs
        assert (~obs.load_detached).all()
        assert (~obs.gen_detached).all()
        assert (~obs.storage_detached).all()
        assert (np.abs(obs.load_p_detached) <= 1e-7).all()
        assert (np.abs(obs.load_q_detached) <= 1e-7).all()
        assert (np.abs(obs.gen_p_detached) <= 1e-7).all()
        assert (np.abs(obs.storage_p_detached) <= 1e-7).all()
        
        # slack ok
        assert np.abs(self.env._delta_gen_p.sum() / self.env._gen_activeprod_t.sum()) <= 0.02  # less than 2% losses
        
    def test_shedding_load_step(self):
        # NB warning this test does not pass if STOP_EP_IF_GEN_BREAK_CONSTRAINTS (slack breaks its rampdown !)
        obs, reward, done, info = self.env.step(self.env.action_space({"detach_load": 0}))
        # env converged
        assert not done, info["exception"]
        
        # load properly disconnected
        assert obs.topo_vect[obs.load_pos_topo_vect[0]] == -1
        # 0 in the observation for this load
        assert np.abs(obs.load_p[0]) <= 1e-7
        assert np.abs(obs.load_q[0]) <= 1e-7
        
        # all other loads ok
        assert (np.abs(self.env._prev_load_p[1:] - obs.load_p[1:]) <= 1e-7).all()
        assert (np.abs(self.env._prev_load_q[1:] - obs.load_q[1:]) <= 1e-7).all()
        assert (~self.env._loads_detached[1:]).all()
        assert (np.abs(self.env._load_p_detached[1:]) <= 1e-7).all()
        assert (np.abs(self.env._load_q_detached[1:]) <= 1e-7).all()
        assert (~obs.load_detached[1:]).all()
        assert (np.abs(obs.load_p_detached[1:]) <= 1e-7).all()
        assert (np.abs(obs.load_q_detached[1:]) <= 1e-7).all()
        
        # load properly written as detached
        normal_load_p = dt_float(21.9)
        normal_load_q = dt_float(15.3)
        assert np.abs(self.env._load_p_detached[0] - normal_load_p) <= 1e-7
        assert np.abs(self.env._load_q_detached[0] - normal_load_q) <= 1e-7
        assert np.abs(obs.load_p_detached[0] - normal_load_p) <= 1e-7
        assert np.abs(obs.load_q_detached[0] - normal_load_q) <= 1e-7
        
        # rest is ok
        assert (np.abs(self.env._prev_gen_p - obs.gen_p) <= 1e-7).all()
        assert (~self.env._gens_detached).all()
        assert (~self.env._storages_detached).all()
        assert (np.abs(self.env._gen_p_detached) <= 1e-7).all()
        assert (np.abs(self.env._storage_p_detached) <= 1e-7).all()
        
        assert (~obs.gen_detached).all()
        assert (~obs.storage_detached).all()
        assert (np.abs(obs.gen_p_detached) <= 1e-7).all()
        assert (np.abs(obs.storage_p_detached) <= 1e-7).all()
        
        # slack completely "messed up"
        assert self.env._delta_gen_p.sum() <= -normal_load_p
        assert obs.gen_p_delta.sum() <= -normal_load_p
        
        # another step
        obs, reward, done, info = self.env.step(self.env.action_space())
        # env converged
        assert not done
        # load properly disconnected
        assert obs.topo_vect[obs.load_pos_topo_vect[0]] == -1
        # load properly written as detached
        normal_load_p = dt_float(22.0)
        normal_load_q = dt_float(15.2)
        assert np.abs(self.env._load_p_detached[0] - normal_load_p) <= 1e-7
        assert np.abs(self.env._load_q_detached[0] - normal_load_q) <= 1e-7
        assert self.env._delta_gen_p.sum() <= -normal_load_p
        
        # another step
        obs, reward, done, info = self.env.step(self.env.action_space())
        # env converged
        assert not done
        # load properly disconnected
        assert obs.topo_vect[obs.load_pos_topo_vect[0]] == -1
        # load properly written as detached
        normal_load_p = dt_float(21.6)
        normal_load_q = dt_float(15.1)
        assert np.abs(self.env._load_p_detached[0] - normal_load_p) <= 1e-7
        assert np.abs(self.env._load_q_detached[0] - normal_load_q) <= 1e-7
        assert self.env._delta_gen_p.sum() <= -normal_load_p
        
        # now attached it again
        obs, reward, done, info = self.env.step(self.env.action_space({"set_bus": {"loads_id": [(0, 1)]}}))
        # env converged
        assert not done
        # load properly disconnected
        assert obs.topo_vect[obs.load_pos_topo_vect[0]] == 1
        # load properly written as detached
        assert np.abs(self.env._load_p_detached[0] - 0.) <= 1e-7
        assert np.abs(self.env._load_q_detached[0] - 0.) <= 1e-7
        # slack ok
        assert np.abs(self.env._delta_gen_p.sum() / self.env._gen_activeprod_t.sum()) <= 0.02  # less than 2% losses
        
        
class TestSheddingActionsNoShedding(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        p = Parameters()
        p.MAX_SUB_CHANGED = 999999
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage",
                                    param=p,
                                    action_class=CompleteAction,
                                    allow_detachment=False,
                                    test=True,
                                    _add_to_name=type(self).__name__)
        obs = self.env.reset(seed=0, options={"time serie id": 0}) # Reproducibility
        
    def tearDown(self) -> None:
        self.env.close()
        super().tearDown()        
        
    def test_load(self):
        obs = self.env.reset()
        assert not type(self.env).detachment_is_allowed
        assert (~obs.load_detached).all()
        
        with self.assertRaises(UserWarning):
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                self.env.action_space({"detach_load": 0})
        
        obs, reward, done, info = self.env.step(self.env.action_space({"set_bus": {"loads_id": [(0, -1)]}}))
        assert done
        
    def test_gen(self):
        obs = self.env.reset()
        assert not type(self.env).detachment_is_allowed
        assert (~obs.gen_detached).all()
        
        with self.assertRaises(UserWarning):
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                self.env.action_space({"detach_gen": 0})
        
        obs, reward, done, info = self.env.step(self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}}))
        assert done
        
    def test_storage(self):
        obs = self.env.reset()
        assert not type(self.env).detachment_is_allowed
        assert (~obs.storage_detached).all()
        
        with self.assertRaises(UserWarning):
            with warnings.catch_warnings():
                warnings.filterwarnings("error")
                self.env.action_space({"detach_storage": 0})
        
        obs, reward, done, info = self.env.step(self.env.action_space({"set_bus": {"storages_id": [(0, -1)]}, "set_storage": [(0, 1.)]}))
        assert done


class TestDetachmentRedisp(unittest.TestCase):
    def setUp(self):
        super().setUp()
        param = Parameters()
        param.MAX_SUB_CHANGED = 999999
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage",
                                    param=param,
                                    action_class=CompleteAction,
                                    allow_detachment=True,
                                    test=True,
                                    _add_to_name=type(self).__name__)
            # assign new limits not to get limited by it
            new_vals = 3. * np.array([140., 120., 70., 70., 40., 100.])
            li_all_cls = [type(self.env),
                          type(self.env.action_space),
                          self.env.action_space.actionClass]
            for this_cls in li_all_cls:
                this_cls.gen_pmax = new_vals
                this_cls.gen_max_ramp_down = new_vals
                this_cls.gen_max_ramp_up = new_vals
            self.tol_redisp = max(self.env._epsilon_poly, 1e-5)
        obs = self.env.reset(seed=0, options={"time serie id": 0}) # Reproducibility
        return super().setUp()
    
    def tearDown(self):
        self.env.close()
        return super().tearDown()
    
    def test_no_redisp_no_detach(self, tol=1e-5):
        # just a basic test to get the values not modified
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.gen_p[0] - 83.6) <= tol, f'{obs.gen_p[0]} vs 83.6'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.gen_p[0] - 83.4) <= tol, f'{obs.gen_p[0]} vs 83.4'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.gen_p[0] - 83.9) <= tol, f'{obs.gen_p[0]} vs 83.9'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.gen_p[0] - 81.5) <= tol, f'{obs.gen_p[0]} vs 81.5'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.gen_p[0] - 82.9) <= tol, f'{obs.gen_p[0]} vs 82.9'
        
    def test_detached_no_redisp_0(self):
        # first test: apply redispatch, then disco, same gen detached and redisp
        amount_redisp = 10.
        act = self.env.action_space({"redispatch": [(0, amount_redisp)]})
        obs, reward, done, info = self.env.step(act)
        assert not done
        assert not info["exception"], info["exception"]
        assert np.abs(obs.actual_dispatch[0] - amount_redisp) <= 1e-8, f"{obs.actual_dispatch[0]} vs {amount_redisp}"
        assert np.abs(obs.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 0."

        act2 = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        obs2, r2, done2, info2 = self.env.step(act2)
        assert not done2, info2["exception"]
        assert np.abs(obs2.gen_p[0] - 0.) <= 1e-8, f"{obs2.gen_p[0]} vs 0."
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.4 MW (base)
        assert np.abs(obs2.actual_dispatch.sum() - (83.4)) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs {(83.4)}"

        act3 = self.env.action_space()
        obs3, r3, done3, info3 = self.env.step(act3)
        assert not done3, info3["exception"]
        assert np.abs(obs3.gen_p[0] - 0.) <= 1e-8, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch[0]) <= 1e-8, f"{obs3.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs3.actual_dispatch.sum() - (83.9 )) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs {(83.9)}"
        
        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.gen_p[0] - 0.) <= 1e-8, f"{obs4.gen_p[0]} vs 0."
        assert np.abs(obs4.actual_dispatch[0]) <= 1e-8, f"{obs4.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs4.actual_dispatch.sum() - (81.5 )) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {(81.5)}"
        
        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.gen_p[0] - 0.) <= 1e-8, f"{obs5.gen_p[0]} vs 0."
        assert np.abs(obs5.actual_dispatch[0]) <= 1e-8, f"{obs5.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs5.actual_dispatch.sum() - (82.9 )) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {(82.9)}" 
        
    def test_detached_no_redisp_1(self):
        # second test: apply disconnect, then redispatch, same gen
        act_redisp = self.env.action_space({"redispatch": [(0, 1.)]})
        act_disc = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        obs, reward, done, info = self.env.step(act_disc)
        assert not done
        assert np.abs(obs.actual_dispatch[0] - 0.) <= 1e-8, f"{obs.actual_dispatch[0]} vs 0."
        assert np.abs(obs.actual_dispatch.sum() - 83.6) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 83.6"
        assert np.abs(obs.gen_p[0] - 0.) <= 1e-8, f"{obs.gen_p[0]} vs 0."
        
        obs2, r2, done2, info2 = self.env.step(act_redisp)
        assert not done2, info2["exception"]
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        assert np.abs(obs2.actual_dispatch.sum() - 83.4) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs 83.4"
        
        obs3, r3, done3, info3 = self.env.step(self.env.action_space())
        assert not done3, info3["exception"]
        assert np.abs(obs3.actual_dispatch[0]) <= 1e-8, f"{obs3.actual_dispatch[0]} vs 0."
        assert abs(obs3.gen_p[0]) <= 1e-8, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch.sum() - 83.9) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs 83.9"
        
        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.gen_p[0] - 0.) <= 1e-8, f"{obs4.gen_p[0]} vs 0."
        assert np.abs(obs4.actual_dispatch[0]) <= 1e-8, f"{obs4.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs4.actual_dispatch.sum() - (81.5 )) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {(81.5)}"

        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.gen_p[0] - 0.) <= 1e-8, f"{obs5.gen_p[0]} vs 0."
        assert np.abs(obs5.actual_dispatch[0]) <= 1e-8, f"{obs5.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs5.actual_dispatch.sum() - (82.9 )) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {(82.9)}" 
            
    def test_detached_no_redisp_2(self):
        # first test: apply redispatch, then disco, different gen redisp and disco
        amount_redisp = 10.
        act = self.env.action_space({"redispatch": [(1, amount_redisp)]})
        # act = self.env.action_space()
        obs, reward, done, info = self.env.step(act)
        assert not done
        assert not info["exception"], info["exception"]
        assert np.abs(obs.actual_dispatch[1] - amount_redisp) <= 1e-8, f"{obs.actual_dispatch[1]} vs {amount_redisp}"
        assert np.abs(obs.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 0."

        act2 = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        obs2, r2, done2, info2 = self.env.step(act2)
        assert not done2, info2["exception"]
        assert np.abs(obs2.gen_p[0] - 0.) <= 1e-8, f"{obs2.gen_p[0]} vs 0."
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.4 MW (base)
        assert np.abs(obs2.actual_dispatch.sum() - (83.4)) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs {(83.4)}"

        act3 = self.env.action_space()
        obs3, r3, done3, info3 = self.env.step(act3)
        assert not done3, info3["exception"]
        assert np.abs(obs3.gen_p[0] - 0.) <= 1e-8, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch[0]) <= 1e-8, f"{obs3.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs3.actual_dispatch.sum() - (83.9 )) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs {(83.9)}"

        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.gen_p[0] - 0.) <= 1e-8, f"{obs4.gen_p[0]} vs 0."
        assert np.abs(obs4.actual_dispatch[0]) <= 1e-8, f"{obs4.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs4.actual_dispatch.sum() - (81.5 )) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {(81.5)}"

        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.gen_p[0] - 0.) <= 1e-8, f"{obs5.gen_p[0]} vs 0."
        assert np.abs(obs5.actual_dispatch[0]) <= 1e-8, f"{obs5.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs5.actual_dispatch.sum() - (82.9 )) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {(82.9)}" 
          
    def test_detached_no_redisp_3(self):
        # second test: apply disconnect, then redispatch, different gen redisp and detached
        act_redisp = self.env.action_space({"redispatch": [(1, 1.)]})
        act_disc = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        obs, reward, done, info = self.env.step(act_disc)
        assert not done
        assert np.abs(obs.actual_dispatch[0] - 0.) <= 1e-8, f"{obs.actual_dispatch[0]} vs 0."
        assert np.abs(obs.actual_dispatch.sum() - 83.6) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 83.6"
        assert np.abs(obs.gen_p[0] - 0.) <= 1e-8, f"{obs.gen_p[0]} vs 0."
        
        obs2, r2, done2, info2 = self.env.step(act_redisp)
        assert not done2, info2["exception"]
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        # assert np.abs(obs2.actual_dispatch[1] - 1.) <= self.tol_redisp, f"{obs2.actual_dispatch[1]} vs 1."
        assert np.abs(obs2.actual_dispatch.sum() - 83.4) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs 83.4"
        
        obs3, r3, done3, info3 = self.env.step(self.env.action_space())
        assert not done3, info3["exception"]
        assert np.abs(obs3.actual_dispatch[0]) <= 1e-8, f"{obs3.actual_dispatch[0]} vs 0."
        assert abs(obs3.gen_p[0]) <= 1e-8, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch.sum() - 83.9) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs 83.9"
        
        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.gen_p[0] - 0.) <= 1e-8, f"{obs4.gen_p[0]} vs 0."
        assert np.abs(obs4.actual_dispatch[0]) <= 1e-8, f"{obs4.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs4.actual_dispatch.sum() - (81.5 )) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {(81.5)}"

        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.gen_p[0] - 0.) <= 1e-8, f"{obs5.gen_p[0]} vs 0."
        assert np.abs(obs5.actual_dispatch[0]) <= 1e-8, f"{obs5.actual_dispatch[0]} vs 0."
        # dispatch should compensate the 83.9 MW (base)
        assert np.abs(obs5.actual_dispatch.sum() - (82.9 )) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {(82.9)}" 
               
    def test_detached_reattached(self):
        # second test: apply redisp, then disco, then reco, same gen redisp and deco
        act_redisp = self.env.action_space({"redispatch": [(0, 1.)]})
        act_disc = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        act_reco = self.env.action_space({"set_bus": {"generators_id": [(0, 1)]}})
        obs, reward, done, info = self.env.step(act_redisp)
        assert not done
        assert np.abs(obs.actual_dispatch[0] - 1.) <= 1e-8, f"{obs.actual_dispatch[0]} vs 0."
        assert np.abs(obs.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 0."

        obs2, r2, done2, info2 = self.env.step(act_disc)
        assert not done2, info2["exception"]
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        assert np.abs(obs2.actual_dispatch.sum() - 83.4) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs 83.4"
        
        obs3, r3, done3, info3 = self.env.step(self.env.action_space())
        assert not done3, info3["exception"]
        assert np.abs(obs3.actual_dispatch[0] - 0.) <= self.tol_redisp, f"{obs3.actual_dispatch[0]} vs 0."
        assert abs(obs3.gen_p[0] - 0.) <= self.tol_redisp, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch.sum() - (83.9)) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs 83.9"
        
        obs4, r4, done4, info4 = self.env.step(act_reco)
        assert np.abs(obs4.actual_dispatch[0] - 1.) <= self.tol_redisp, f"{obs4.actual_dispatch[0]} vs 1."
        assert abs(obs4.gen_p[0] - (81.5 + 1.) ) <= self.tol_redisp, f"{obs4.gen_p[0]} vs 81.5"
        assert np.abs(obs4.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs 0."

        obs5, r5, done5, info5 = self.env.step(self.env.action_space())
        assert np.abs(obs5.actual_dispatch[0] - 1.) <= self.tol_redisp, f"{obs5.actual_dispatch[0]} vs 1."
        assert abs(obs5.gen_p[0] - (82.9 + 1.) ) <= self.tol_redisp, f"{obs5.gen_p[0]} vs 82.9"
        assert np.abs(obs5.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs 0."
        
    def test_detached_reattached_1(self):
        # second test: apply redisp, then disco, then reco, different gen redisp and deco
        act_redisp = self.env.action_space({"redispatch": [(1, 1.)]})
        act_disc = self.env.action_space({"set_bus": {"generators_id": [(0, -1)]}})
        act_reco = self.env.action_space({"set_bus": {"generators_id": [(0, 1)]}})
        obs, reward, done, info = self.env.step(act_redisp)
        assert not done
        assert np.abs(obs.actual_dispatch[1] - 1.) <= 1e-8, f"{obs.actual_dispatch[1]} vs 0."
        assert np.abs(obs.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs 0."

        obs2, r2, done2, info2 = self.env.step(act_disc)
        assert not done2, info2["exception"]
        assert np.abs(obs2.actual_dispatch[0]) <= 1e-8, f"{obs2.actual_dispatch[0]} vs 0."
        assert np.abs(obs2.actual_dispatch.sum() - 83.4) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs 83.4"
        
        obs3, r3, done3, info3 = self.env.step(self.env.action_space())
        assert not done3, info3["exception"]
        assert np.abs(obs3.actual_dispatch[0] - 0.) <= self.tol_redisp, f"{obs3.actual_dispatch[0]} vs 0."
        assert abs(obs3.gen_p[0] - 0.) <= self.tol_redisp, f"{obs3.gen_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch.sum() - (83.9)) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs 83.9"
        
        obs4, r4, done4, info4 = self.env.step(act_reco)
        assert np.abs(obs4.actual_dispatch[1] - 1.) <= self.tol_redisp, f"{obs4.actual_dispatch[0]} vs 1."
        assert abs(obs4.gen_p[0]) > self.tol_redisp, f"{obs4.gen_p[0]} vs 81.5 (+ redisp)"
        assert np.abs(obs4.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs 0."

        obs5, r5, done5, info5 = self.env.step(self.env.action_space())
        assert np.abs(obs5.actual_dispatch[1] - 1.) <= self.tol_redisp, f"{obs5.actual_dispatch[0]} vs 1."
        assert abs(obs5.gen_p[0]) > self.tol_redisp, f"{obs5.gen_p[0]} vs 82.9 (+ redisp)"
        assert np.abs(obs5.actual_dispatch.sum() - 0.) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs 0."
        

class TestSheddingcorrectlySet(unittest.TestCase):
    def test_shedding_env1_bk1(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make("educ_case14_storage",
                               action_class=CompleteAction,
                               allow_detachment=True,
                               test=True,
                               _add_to_name=type(self).__name__+"test_shedding_env1_bk1")
        assert type(env).detachment_is_allowed
        
    def test_shedding_env0_bk1(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make("educ_case14_storage",
                               action_class=CompleteAction,
                               allow_detachment=False,
                               test=True,
                               _add_to_name=type(self).__name__+"test_shedding_env0_bk1")
        assert not type(env).detachment_is_allowed
        
    def test_shedding_env1_bk0(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make("educ_case14_storage",
                               action_class=CompleteAction,
                               allow_detachment=True,
                               test=True,
                               backend=_BackendNoDetach(),
                               _add_to_name=type(self).__name__+"test_shedding_env1_bk1")
        assert not type(env).detachment_is_allowed
        
    def test_shedding_env0_bk0(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            env = grid2op.make("educ_case14_storage",
                               action_class=CompleteAction,
                               allow_detachment=False,
                               test=True,
                               backend=_BackendNoDetach(),
                               _add_to_name=type(self).__name__+"test_shedding_env0_bk1")
        assert not type(env).detachment_is_allowed
        

class TestDetachmentLoad(unittest.TestCase):
    def setUp(self):
        super().setUp()
        param = Parameters()
        param.MAX_SUB_CHANGED = 999999
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.env = grid2op.make("educ_case14_storage",
                                    param=param,
                                    action_class=CompleteAction,
                                    allow_detachment=True,
                                    test=True,
                                    _add_to_name=type(self).__name__)
            # assign new limits not to get limited by it
            new_vals = 3. * np.array([140., 120., 70., 70., 40., 100.])
            li_all_cls = [type(self.env),
                          type(self.env.action_space),
                          self.env.action_space.actionClass]
            for this_cls in li_all_cls:
                this_cls.gen_pmax = new_vals
                this_cls.gen_max_ramp_down = new_vals
                this_cls.gen_max_ramp_up = new_vals
            self.tol_redisp = max(self.env._epsilon_poly, 1e-5)
        obs = self.env.reset(seed=0, options={"time serie id": 0}) # Reproducibility
        return super().setUp()
    
    def tearDown(self):
        self.env.close()
        return super().tearDown()
    
    def test_no_redisp_no_detach(self, tol=1e-5):
        # just a basic test to get the values not modified
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.load_p[0] - 21.9) <= tol, f'{obs.load_p[0]} vs 21.9'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.load_p[0] - 22.0) <= tol, f'{obs.load_p[0]} vs 22.0'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.load_p[0] - 21.6) <= tol, f'{obs.load_p[0]} vs 21.6'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.load_p[0] - 21.6) <= tol, f'{obs.load_p[0]} vs 21.5'
        obs, reward, done, info = self.env.step(self.env.action_space())
        assert abs(obs.load_p[0] - 21.5) <= tol, f'{obs.load_p[0]} vs 21.5'
        
    def test_detached_load(self):
        "do nothing then detached"
        act = self.env.action_space()
        obs, reward, done, info = self.env.step(act)
        assert not done
        assert not info["exception"], info["exception"]
        assert abs(obs.load_p[0] - 21.9) <= self.tol_redisp, f'{obs.load_p[0]} vs 21.9'
        
        act2 = self.env.action_space({"set_bus": {"loads_id": [(0, -1)]}})
        obs2, r2, done2, info2 = self.env.step(act2)
        assert not done2, info2["exception"]
        assert np.abs(obs2.load_p[0] - 0.) <= 1e-8, f"{obs2.load_p[0]} vs 0."
        assert np.abs(obs2.load_q[0] - 0.) <= 1e-8, f"{obs2.load_q[0]} vs 0."
        # dispatch should compensate the 22.0 MW (base)
        assert np.abs(obs2.actual_dispatch.sum() + (22.0)) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs {(22.0)}"
        # does not work, env chronics are not precise (even without redisp it's 2.9 MW or something)
        # assert abs(obs2.gen_p_delta.sum() - 0.) <= 1., f"{obs2.gen_p_delta.sum()}"  # gen_p delta should be bellow 1 MW
        
        act3 = self.env.action_space()
        obs3, r3, done3, info3 = self.env.step(act3)
        assert not done3, info3["exception"]
        assert np.abs(obs3.load_p[0] - 0.) <= 1e-8, f"{obs3.load_p[0]} vs 0."
        assert np.abs(obs3.load_q[0] - 0.) <= 1e-8, f"{obs3.load_q[0]} vs 0."
        # dispatch should compensate the 21.6 MW
        assert np.abs(obs3.actual_dispatch.sum() + (21.6)) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs {(21.6)}"
        # does not work, env chronics are not precise (even without redisp it's 2.9 MW or something)
        
        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.load_p[0] - 0.) <= 1e-8, f"{obs4.load_p[0]} vs 0."
        assert np.abs(obs4.load_q[0] - 0.) <= 1e-8, f"{obs4.load_q[0]} vs 0."
        # dispatch should compensate the 21.6 MW
        assert np.abs(obs4.actual_dispatch.sum() + (21.6)) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {(21.6)}"
        # does not work, env chronics are not precise (even without redisp it's 2.9 MW or something)
        
        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.load_p[0] - 0.) <= 1e-8, f"{obs5.load_p[0]} vs 0."
        assert np.abs(obs5.load_q[0] - 0.) <= 1e-8, f"{obs5.load_q[0]} vs 0."
        # dispatch should compensate the 21.6 MW
        assert np.abs(obs5.actual_dispatch.sum() + (21.5)) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {(21.6)}"
        # does not work, env chronics are not precise (even without redisp it's 2.9 MW or something)
        
    def test_detached_reattached(self):
        "detach, wait and reattach and wait"
        act = self.env.action_space({"set_bus": {"loads_id": [(0, -1)]}})
        obs, reward, done, info = self.env.step(act)
        assert not done
        assert not info["exception"], info["exception"]
        assert np.abs(obs.load_p[0] - 0.) <= self.tol_redisp, f"{obs.load_p[0]} vs 0."
        assert np.abs(obs.load_q[0] - 0.) <= 1e-8, f"{obs.load_q[0]} vs 0."
        assert np.abs(obs.actual_dispatch.sum() + (21.9)) <= self.tol_redisp, f"{obs.actual_dispatch.sum()} vs {(21.6)}"
        
        act2 = self.env.action_space()
        obs2, r2, done2, info2 = self.env.step(act2)
        assert not done2, info2["exception"]
        assert np.abs(obs2.load_p[0] - 0.) <= self.tol_redisp, f"{obs2.load_p[0]} vs 0."
        assert np.abs(obs2.actual_dispatch.sum() + (22.0)) <= self.tol_redisp, f"{obs2.actual_dispatch.sum()} vs {(22.0)}"

        act3 = self.env.action_space({"set_bus": {"loads_id": [(0, 1)]}})
        obs3, r3, done3, info3 = self.env.step(act3)
        assert not done3, info3["exception"]
        assert np.abs(obs3.load_p[0] - 21.6) <= self.tol_redisp, f"{obs3.load_p[0]} vs 0."
        assert np.abs(obs3.actual_dispatch.sum() + 0) <= self.tol_redisp, f"{obs3.actual_dispatch.sum()} vs {0.}"

        act4 = self.env.action_space()
        obs4, r4, done4, info4 = self.env.step(act4)
        assert not done4, info4["exception"]
        assert np.abs(obs4.load_p[0] - 21.6) <= self.tol_redisp, f"{obs4.load_p[0]} vs 0."
        assert np.abs(obs4.actual_dispatch.sum() + (0.)) <= self.tol_redisp, f"{obs4.actual_dispatch.sum()} vs {0.}"
        
        act5 = self.env.action_space()
        obs5, r5, done5, info5 = self.env.step(act5)
        assert not done5, info5["exception"]
        assert np.abs(obs5.load_p[0] - 21.5) <= self.tol_redisp, f"{obs5.load_p[0]} vs 0."
        assert np.abs(obs5.actual_dispatch.sum() + (0.)) <= self.tol_redisp, f"{obs5.actual_dispatch.sum()} vs {0.}"

# TODO with the env parameters STOP_EP_IF_GEN_BREAK_CONSTRAINTS and ENV_DOES_REDISPATCHING

# TODO shedding in simulate
# TODO shedding in Simulator !

# TODO Shedding: Runner

# TODO Shedding: environment copied
# TODO Shedding: MultiMix environment
# TODO Shedding: TimedOutEnvironment
# TODO Shedding: MaskedEnvironment

if __name__ == "__main__":
    unittest.main()
