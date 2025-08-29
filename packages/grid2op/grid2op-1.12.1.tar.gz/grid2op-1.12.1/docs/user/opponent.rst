.. currentmodule:: grid2op.Opponent

Opponent Modeling
===================================

This page is organized as follow:

.. contents:: Table of Contents
    :depth: 3

Objectives
-----------
Power systems are a really important tool today, that can be as resilient as possible to avoid possibly dramatic
consequences.

In grid2op, we chose to enforce this property by implementing an "Opponent", modeled thanks to the :class:`BaseOpponent`
that can take malicious actions to deteriorate the state of the powergrid and make tha Agent (:class:`grid2op.Agent`)
fail. To make the agent "game over" is really easy (for
example it could isolate a load by forcing the disconnection of all the powerline that powers it). This would not be
fair, and that is why the Opponent has some dedicated budget (modeled with the :class:`BaseActionBudget`).

The class :class:`OpponentSpace` has the delicate role to:
- send the necessary information for the Opponent to attack properly.
- make sure the attack performed by the opponent is legal
- compute the cost of such attack
- make sure this cost is not too high for the opponent budget.

Relation with N-1 security
----------------------------

The "opponent" modeling in grid2op is closely related to the N-1 security criterion used
in operation by many TSOs.

Definition of N-1 security
^^^^^^^^^^^^^^^^^^^^^^^^^^

There are different definition of "N-1 security" depending on the TSOs. In this 
part of the documentation we will define it clearly to avoid misunderstanding.

First, a grid is said to be "in security" if no threshold are violate for any equipement on the grid.
In the context of grid2op, this most often means that all powerlines have a flow under a certain
threshold (refer to as "thermal limit" in grid2op).

``̀`
A grid is N-1 safe, if, for any "contingency" (*eg* the disconnection a powerline) from 
a given list (in general this list is "all the lines / transformers on the grid"), the grid would
still be "in security" (define in the above paragraph) after this contingency occurred.
``̀`

N-1 with corrective actions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This security criteria might not be met at all time, but the grid would still be "secure" 100%
of the time.

Indeed, for some actions with a very short "implementation time" (say an action nearly instantaneous, like 
the opening or the closing of a switch), it can be possible to implement this action only in case of
contingency to avoid the grid to go out of security.

This would give the following definition of N-1 security:

``̀`
A grid is N-1 secure (with corrective action), if an only if, for a any contingency (among a given list),
it is possible to find (at least) a corrective action (understand: an action that can be quickly implemented after
the contingency, including the "I do nothing action") that would bring the grid back to security.
``̀`

.. note::
  If a grid is N-1 secure (as described in the above paragraph), it will be "N-1 secure (with corrective action)".

  The opposite is not true.

Extension of the N-1 security, with corrective actions, on a time interval
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Grid2op is especially suited to study how the grid will evolve around a given time interval (say a few hours 
or a few days).

The N-1 criterion can then be "extended" to include the time dependance. The natural definition would be:

``̀`
A grid is N-1 scure accross the time interval [beginning, end] if (and only if), for any contingency 
(among a given list) occurring during this time interval, there exists a list of corrective actions that
can ensure the grid remains in security at any time until the end of this interval".
``̀`

.. note::
  If the grid state is not modified by any action, assessing whether or not the grid is "N-1 secure on a given time interval"
  is equivalent to assess whether or not, for each step within the interval, the grid is "N-1 secure".

  This is not the case if there are "feedback loops" on the grid, such as delayed protection, presence of corrective actions 
  or storage units on the grid, and in general anything that can affect the state of the grid and be "non instantly reversible".

  In this case, it is possible to find examples where grids are "N-1 secure for all step within the inveral", but the 
  grid is not "N-1 secure accross the time interval". For example, imagine the case where a storage unit should be emptied
  as a "corrective measure". In this case, the grid is "N-1 secure" at each step (we assume you can always empty it for one step). 
  But the grid is not safe during the whole interval, if the initial capacity of the storage unit is not sufficient
  to last the whole duration of the contingency.

Translation with the grid2op framework
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Grid2op allows to easily assess if a grid is "N-1 secure, with (or without) corrective action, accross a given time interval".

For the version without corrective actions, you can imagine something like this:

.. code-block:: python

  # let's suppose env is a grid2op environment
  # with the correct data concerning the proper "time interval"
  # env.reset() set the state at the beginning of the time interval
  # and when env.step() is "done"  it is the end of the time
  # interval

  is_secure = np.zeros(len(LIST_OF_ALL_CONTINGENCIES), dtype=bool)
  for c_num, contingency_id in enumerate(LIST_OF_ALL_CONTINGENCIES):
    # reset the environment and disconnect the
    # given contingency_id
    init_obs = env.reset(options={"init state": {"set_line_status": [(contingency_id, -1)]}})
    obs = init_obs
    done = False
    terminated = False
    while not done:
      if (obs.rho >= 1.).any():
        # there is an overflow for this contingency_id for this step 
        # grid is not secure
        is_secure[c_num] = False
        terminated = True
        break

      act = env.action_space() # replace this by a "corrective action" from a agent if needed
      obs, reward, done, info = env.step(act)

      if done and obs.current_step < obs.max_step:
        # episode terminated premarturely
        is_secure[c_num] = False
        terminated = True
        break

    if not terminated:
      is_secure[c_num] = True

  # At this point the grid is N-1 safe for this time interval
  # if and only if:
  assert is_secure.all()

You can, almost as easily (if you use an agent that is able to take some "corrective actions") assess
if the grid is "N-1 secure for a given time interval with corrective actions" by having an 
agent take corrective actions (replace `act` variable above).

.. note::
  If you do that, you must also make sure that the agent cannot reconnect the contingency
  (*eg* the disconnected powerline) for the entire duration of the episode.


Reformulation with an opponent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Evaluating if a grid is N-1 secure for a given time interval can be reformulated as evaluating
if a grid is secure against an opponent that will try to disconnect a powerline, for a certain duration,
preventing its reconnection.
And you "run" this opponent for each contingency that you need to simulate.

And if an agent manages to find a "correct list of actions" for all of these contingencies, then you 
can say that this agent "makes the grid secure".

Informatically, this reformulation "hides" the 
`init_obs = env.reset(options={"init state": {"set_line_status": [(contingency_id, -1)]}})`
inside the opponent which "lives" inside the environment.

The sketch of the above code would look like:

.. code-block:: python

  is_secure = np.zeros(len(LIST_OF_ALL_CONTINGENCIES), dtype=bool)
  for c_num, contingency_id in enumerate(LIST_OF_ALL_CONTINGENCIES):
    env.set_opponent(Opponent_Attack_Line(contingency_id))  
    # NB: this `set_opponent` is not implemented, it's an illustration of the equivalence
    # NB: the Opponent_Attack_Line(contingency_id) does not exists either
    init_obs = env.reset()
    # init_obs has the proper "attack", which is "disconnection of the line contingency_id"

    ... # rest is unchanged

And now, to limit computation time (for example in training) you can imagine having an opponent that would
always find the worst possible line to disconnect (="attack" in grid2op formulation) for a given agent (for 
example by simulating the previous for loop 'in its head' before actually disconnecting the line). If such
an opponent exists, it is sufficient to ensure that "if the agent manages to overcome the single attack of this
'oracle opponent', then the agent makes the grid N-1 secure for the entire episode with curative actions."

Of course, in practice this 'oracle opponent' is really hard to find. So we decided to target the
"worst possible line to disconnect" for a given agent, with a heuristic. This lead to the different
opponent present in grid2op today.

How to create an opponent in any environment
---------------------------------------------

This section is a work in progress, it will only cover how to set up one type of opponent, and supposes
that you already know which lines you want to attack, at which frequency etc.

More detailed information about the opponent will be provide in the future.

The set up for the opponent in the "l2rpn_neurips_track1" has the following configuration.

.. code-block:: python

    lines_attacked = ["62_58_180", "62_63_160", "48_50_136", "48_53_141", "41_48_131", "39_41_121",
                  "43_44_125", "44_45_126", "34_35_110", "54_58_154"]
    rho_normalization = [0.45, 0.45, 0.6, 0.35, 0.3, 0.2,
                         0.55, 0.3, 0.45, 0.55]
    opponent_attack_cooldown = 12*24  # 24 hours, 1 hour being 12 time steps
    opponent_attack_duration = 12*4  # 4 hours
    opponent_budget_per_ts = 0.16667  # opponent_attack_duration / opponent_attack_cooldown + epsilon
    opponent_init_budget = 144.  # no need to attack straightfully, it can attack starting at midday the first day
    config = {
        "opponent_attack_cooldown": opponent_attack_cooldown,
        "opponent_attack_duration": opponent_attack_duration,
        "opponent_budget_per_ts": opponent_budget_per_ts,
        "opponent_init_budget": opponent_init_budget,
        "opponent_action_class": PowerlineSetAction,
        "opponent_class": WeightedRandomOpponent,
        "opponent_budget_class": BaseActionBudget,
        'kwargs_opponent': {"lines_attacked": lines_attacked,
                            "rho_normalization": rho_normalization,
                            "attack_period": opponent_attack_cooldown}
    }

To create the same type of opponent on the **case14** grid you can do:

.. code-block:: python

    import grid2op
    from grid2op.Action import PowerlineSetAction
    from grid2op.Opponent import RandomLineOpponent, BaseActionBudget
    env_name = "l2rpn_case14_sandbox"

    env_with_opponent = grid2op.make(env_name,
                                     opponent_attack_cooldown=12*24,
                                     opponent_attack_duration=12*4,
                                     opponent_budget_per_ts=0.5,
                                     opponent_init_budget=0.,
                                     opponent_action_class=PowerlineSetAction,
                                     opponent_class=RandomLineOpponent,
                                     opponent_budget_class=BaseActionBudget,
                                     kwargs_opponent={"lines_attacked":
                                          ["1_3_3", "1_4_4", "3_6_15", "9_10_12", "11_12_13", "12_13_14"]}
                                     )
    # and now you have an opponent on the l2rpn_case14_sandbox
    # you can for example
    obs = env_with_opponent.reset()

    act = ...  # chose an action here
    obs, reward, done, info = env_with_opponent.step(act)


And for the track2 of neurips, if you want to make it even more complicated, you can add an opponent
in the same fashion:

.. code-block:: python

    import grid2op
    from grid2op.Action import PowerlineSetAction
    from grid2op.Opponent import RandomLineOpponent, BaseActionBudget
    env_name = "l2rpn_neurips_2020_track2_small"

    env_with_opponent = grid2op.make(env_name,
                                     opponent_attack_cooldown=12*24,
                                     opponent_attack_duration=12*4,
                                     opponent_budget_per_ts=0.5,
                                     opponent_init_budget=0.,
                                     opponent_action_class=PowerlineSetAction,
                                     opponent_class=RandomLineOpponent,
                                     opponent_budget_class=BaseActionBudget,
                                     kwargs_opponent={"lines_attacked":
                                                         ["26_31_106",
                                                          "21_22_93",
                                                          "17_18_88",
                                                          "4_10_162",
                                                          "12_14_68",
                                                          "14_32_108",
                                                          "62_58_180",
                                                          "62_63_160",
                                                          "48_50_136",
                                                          "48_53_141",
                                                          "41_48_131",
                                                          "39_41_121",
                                                          "43_44_125",
                                                          "44_45_126",
                                                          "34_35_110",
                                                          "54_58_154",
                                                          "74_117_81",
                                                          "80_79_175",
                                                          "93_95_43",
                                                          "88_91_33",
                                                          "91_92_37",
                                                          "99_105_62",
                                                          "102_104_61"]}
                                     )
    # and now you have an opponent on the l2rpn_case14_sandbox
    # you can for example
    obs = env_with_opponent.reset()

    act = ...  # chose an action here
    obs, reward, done, info = env_with_opponent.step(act)

To summarize what is going on here:

- `opponent_attack_cooldown`: give the minimum number of time between two attacks (here 1 attack per day)
- `opponent_attack_duration`: duration for each attack (when a line is attacked, it will not be possible to reconnect
  it for that many steps). In the example it's 4h (so 48 steps)
- `opponent_action_class`: type of the action the opponent will perform (in this case `PowerlineSetAction`)
- `opponent_class`: type of the opponent. Change it at your own risk.
- `opponent_budget_class`: Each attack will cost some budget to the opponent. If no budget, the opponent cannot
  attack. This specifies how the budget are computed. Do not change it.
- `opponent_budget_per_ts`: increase of the budget of the opponent per step. The higher this number, the faster the
  the opponent will regenerate its budget.
- `opponent_init_budget`: initial opponent budget. It is set to 0 to "give" the agent a bit of time before the opponent
  is triggered.
- `kwargs_opponent`: additional information for the opponent. In this case we provide for each grid the powerline it
  can attack.

.. note::

    This is only valid for the `RandomLineOpponent` that disconnect powerlines randomly (but not uniformly!). For other
    type of Opponent, we don't provide any information in the documentation at this stage. Feel free to submit
    a github issue if this is an issue for you.

How to deactivate an opponent in an environment
--------------------------------------------------

If you come accross an environment with an "opponent" already present but for some reasons you want to
deactivate it, you can do this by customization the call to "grid2op.make" like this:

.. code-block:: python

  import grid2op
  from grid2op.Action import DontAct
  from grid2op.Opponent import BaseOpponent, NeverAttackBudget
  env_name = ...

        
  # if you want to disable the opponent you can do (grid2op >= 1.9.4)
  kwargs_no_opp = grid2op.Opponent.get_kwargs_no_opponent()
  env_no_opp = grid2op.make(env_name, **kwargs_no_opp)
  # and there the opponent is disabled

  # or, in a more complex fashion (or for older grid2op version <= 1.9.3)
  env_without_opponent = grid2op.make(env_name,
                                      opponent_attack_cooldown=999999,
                                      opponent_attack_duration=0,
                                      opponent_budget_per_ts=0,
                                      opponent_init_budget=0,
                                      opponent_action_class=DontAct,
                                      opponent_class=BaseOpponent,
                                      opponent_budget_class=NeverAttackBudget,
                                      ...  # other arguments pass to the "make" function
                                      )
                            

.. note:: 
  Currently it's not possible to deactivate an opponent once the environment is created.

  If you want this feature, you can comment the issue https://github.com/Grid2Op/grid2op/issues/426


Detailed Documentation by class
--------------------------------
.. automodule:: grid2op.Opponent
    :members:
    :autosummary:

.. include:: final.rst