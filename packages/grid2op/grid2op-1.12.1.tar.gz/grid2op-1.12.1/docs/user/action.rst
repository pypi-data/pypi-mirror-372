.. currentmodule:: grid2op.Action

.. _n_gen: ./space.html#grid2op.Space.GridObjects.n_gen
.. _n_load: ./space.html#grid2op.Space.GridObjects.n_load
.. _n_line: ./space.html#grid2op.Space.GridObjects.n_line
.. _n_sub: ./space.html#grid2op.Space.GridObjects.n_sub
.. _n_storage: ./space.html#grid2op.Space.GridObjects.n_storage
.. _dim_topo: ./space.html#grid2op.Space.GridObjects.dim_topo
.. _set_bus: ./action.html#grid2op.Action.BaseAction.set_bus
.. _line_or_set_bus: ./action.html#grid2op.Action.BaseAction.line_or_set_bus
.. _line_ex_set_bus: ./action.html#grid2op.Action.BaseAction.line_ex_set_bus
.. _load_set_bus: ./action.html#grid2op.Action.BaseAction.load_set_bus
.. _gen_set_bus: ./action.html#grid2op.Action.BaseAction.gen_set_bus
.. _storage_set_bus: ./action.html#grid2op.Action.BaseAction.storage_set_bus
.. _change_bus: ./action.html#grid2op.Action.BaseAction.change_bus
.. _line_or_change_bus: ./action.html#grid2op.Action.BaseAction.line_or_change_bus
.. _line_ex_change_bus: ./action.html#grid2op.Action.BaseAction.line_ex_change_bus
.. _load_change_bus: ./action.html#grid2op.Action.BaseAction.load_change_bus
.. _gen_change_bus: ./action.html#grid2op.Action.BaseAction.gen_change_bus
.. _storage_change_bus: ./action.html#grid2op.Action.BaseAction.storage_change_bus
.. _line_set_status: ./action.html#grid2op.Action.BaseAction._line_set_status
.. _line_change_status: ./action.html#grid2op.Action.BaseAction._line_change_status
.. _redispatch: ./action.html#grid2op.Action.BaseAction.redispatch
.. _storage_p: ./action.html#grid2op.Action.BaseAction.storage_p
.. _curtail: ./action.html#grid2op.Action.BaseAction.curtail

.. _action-module:

Action
===================================

This page is organized as follow:

.. contents:: Table of Contents
    :depth: 3
    
Objectives
----------
The "Action" module lets you define some actions on the underlying power _grid.
These actions are either made by an agent, or by the environment.

For now, the actions can act on:

  - the "injections" and allows you to change:

    - the generators active power production setpoint
    - the generators voltage magnitude setpoint
    - the loads active power consumption
    - the loads reactive power consumption

  - the status of the powerlines (connected/disconnected)
  - the configuration at substations eg setting different objects to different buses for example
  - changing the power produced / absorbed by storage units
  - redispatch some controllable generators (asking them to deviate their active production setpoint 
    from their initial setpoint - *ie* the setpoint they have in the environment)
  - curtail some renewable generators (asking them to produce less than what they could)
  
More actions are added depdending on user requests. If you want grid2op to support another type of action, 
it's often not difficult (the hardest part is to properly define *what* this new type of action consist and 
what is needed to keep the "grid2op problem" a (PO)-MDP) once the "functional specifications" are well established.

If you want to use some grid2op features that are not coded in grid2op, please consult the 
section :ref:`action-module-backend_callbacks` of this documentation which give a possible way to do this.


The BaseAction class is abstract. You can implement it the way you want. If you decide to extend it, make sure
that the :class:`grid2op.Backend` class will be able to understand it. If you don't, your extension will
not affect the
underlying powergrid. Indeed a :class:`grid2op.Backend` will call the :func:`BaseAction.__call__` method
and should
understands its return type.


The :class:`BaseAction` and all its derivatives also offer some useful inspection utilities:

  - :func:`BaseAction.__str__` prints the action in a format that gives useful information on how it will
    affect the powergrid
  - :func:`BaseAction.effect_on` returns a dictionary that gives information about its effect.

From :class:`BaseAction` inherit in particular the :class:`PlayableAction`, the base class of all action that
players are allowed to play.

Finally, :class:`BaseAction` class define some strict behavior to follow if reimplementing them.
The correctness of each
instances of BaseAction is assessed both when calling :func:`BaseAction.update` or with a call to
:func:`BaseAction._check_for_ambiguity` performed for example by the Backend when it must implement
its effect on the
powergrid through a call to :func:`BaseAction.__call__`

Constructing an action in grid2op is made in the following manner:

.. code-block:: python

    import grid2op
    env = grid2op.make("l2rpn_case14_sandbox")
    dictionary_describing_the_action = {...}  # se bellow
    my_action = env.action_space(dictionary_describing_the_action)
    print(my_action)

On the above code, `dictionary_describing_the_action` should be a dictionary that describe what action
you want to perform on the grid. For more information you can consult the help of the :func:`BaseAction.update`.

To avoid extremely verbose things, as of grid2op 1.5.0, we introduced some convenience functions to allow
easier action construction. You can now do `act.load_set_bus = ...` instead of the previously way
more verbose `act.update({"set_bus": {"loads_id": ...}})`

.. _action-module-examples:

Main action "properties"
---------------------------
In the table below, we present the main properties that you can use to code, using the grid2op framework, the
action that you want to perform on the grid.

=============================================================================    =========  ============
Name(s)                                                                          Type       Size (each)
=============================================================================    =========  ============
`set_bus`_                                                                       int        `dim_topo`_
`gen_set_bus`_                                                                   int        `n_gen`_
`load_set_bus`_                                                                  int        `n_load`_
`line_or_set_bus`_                                                               int        `n_line`_
`line_ex_set_bus`_                                                               int        `n_line`_
`storage_set_bus`_                                                               int        `n_storage`_
`change_bus`_                                                                    bool       `dim_topo`_
`gen_change_bus`_                                                                bool       `n_gen`_
`load_change_bus`_                                                               bool       `n_load`_
`line_or_change_bus`_                                                            bool       `n_line`_
`line_ex_change_bus`_                                                            bool       `n_line`_
`storage_change_bus`_                                                            bool       `n_storage`_
`line_set_status`_                                                               int        `n_line`_
`line_change_status`_                                                            bool       `n_line`_
`redispatch`_                                                                    float      `n_gen`_
`storage_p`_                                                                     float      `n_storage`_
`curtail`_                                                                       float      `n_gen`_
=============================================================================    =========  ============

All the attributes above are "properties", you don't have to use parenthesis to access them:

.. code-block:: python

    # valid code
    gen_buses = act.gen_change_bus

    # do not run
    # invalid code, it will "crash", do not run
    gen_buses = act.gen_change_bus()
    # end do not run

And neither should you uses parenthesis to modify them:

.. code-block:: python

    # valid code
    act.load_set_bus = [(1, 2) , (2, 1), (3, 1)]

    # invalid code, it will crash, do not run
    act.load_set_bus([(1, 2) , (2, 1), (3, 1)])
    # end do not run

Property cannot be set "directly", you have to use the `act.XXX = ..` syntax. For example:

.. code-block:: python

    # valid code
    act.line_change_status = [1, 3, 4]

    # invalid code, it will raise an error, and even if it did not it would have not effect
    # do not run
    act.line_change_status[1] = True
    # end do not run

Usage Examples
--------------
In this section, we describe how to implement some action types. For further information about the
impact of the action implemented, please consult the appropriate getting_started notebook.

Set bus
++++++++
The "properties" concerned by this sections are: `set_bus`_, `gen_set_bus`_, `load_set_bus`_, `line_or_set_bus`_,
`line_ex_set_bus`_ and `storage_set_bus`_. They all work in the same fashion, a detailed explanation is provided in
the  `gen_set_bus`_ help page.

Concretely, to perform a "set_bus" action you need to provide 2 elements: the id of the object you want to modify, and
where you want to place it.

For example, if you want to change the element (regardless of its type) 5, and set it to busbar 2:

.. code-block:: python

    act = env.action_space()  # create an action
    act.set_bus = [(5, 2)]  # perform the desired modification

You can modify as many elements as you want:

.. code-block:: python

    act = env.action_space()  # create an action
    act.set_bus = [(5, 2), (6, 1)]
    # equivalent to:
    act2 = env.action_space()  # create an action
    act2.set_bus = [(5, 2)]
    act2.set_bus = [(6, 1)]

And if you want to modify everything on the same action, you can do:

.. code-block:: python

    act = env.action_space()  # create an action
    act_vect = ...  # for example `act_vect = np.random.choice([-1, 1, 2], size=act.dim_topo)`
    act.set_bus = act_vect

In the example above, `act_vect` can, for example, come from a neural network that is able to predict a "good"
state of the grid, the one that it "wants".

.. note:: In the example above, `act_vect` should be a vector of integer.

Change bus
++++++++++
The "properties" concerned by this sections are: `change_bus`_, `gen_change_bus`_, `load_change_bus`_,
`line_or_change_bus`_,
`line_ex_change_bus`_ and `storage_change_bus`_. They all work in the same fashion, a detailed explanation is provided
in the `gen_change_bus`_ help page.

Concretely, to perform a "change_bus" action you need to provide 1 element: the id of the element you want
to change.

For example, if you want to change the element (regardless of its type) 5, and change the busbar on which it is connected:

.. code-block:: python

    act = env.action_space()  # create an action
    act.set_bus = [5]  # perform the desired modification

You can modify as many elements as you want:

.. code-block:: python

    act = env.action_space()  # create an action
    act.change_bus = [5, 6]
    # equivalent to:
    act2 = env.action_space()  # create an action
    act2.change_bus = [5]
    act2.change_bus = [6]

And if you want to modify everything on the same action, you can do:

.. code-block:: python

    act = env.action_space()  # create an action
    act_vect = ...  # for example `act_vect = np.random.choice([0, 1], size=act.dim_topo).astype(bool)`
    act.change_bus = act_vect

In the example above, `act_vect` can, for example, come from a neural network that is able to predict a "good"
state of the grid, the one that it "wants".

.. note:: In the example above, `act_vect` should be a vector of boolean.

.. note:: If an element is disconnected, performing a "change_bus" action on this element will have not effect.

.. note:: Aside from reconnecting elements, which can be done only using the "set_bus" actions, the
    "change_bus" and "set_bus" leads to equivalent grid states. For each state `obs_t`,
    for each "change_bus" action `a_change`, there exists a "set_bus" action `a_set` such that `env.step(a_change)`
    has exactly the same impact as `env.step(a_set)` (note that the `a_set` equivalent to `a_change` depends on the
    current state of the environment, of course).

    We introduced in grid2op the two (equivalent) representation not to limit agent. If we make the
    parallel with oter RL environment, "change_bus" can be thought as "*turn left*" or "*turn right*" whereas "set_bus"
    is more "*go at position (x,y)*".

Set status
+++++++++++
TODO

Change status
++++++++++++++
TODO

Redispatching
++++++++++++++
TODO

Storage power setpoint
+++++++++++++++++++++++

TODO

Getting the resulting topology after an action
------------------------------------------------
Unfortunately, it is sometimes relatively difficult to understand what will be the exact effect of a given
action on a powergrid.

This mainly caused by the fact that the modeled environment embed some complexity of a real powergrid.

To ease the process of estimating the impact of an action on a environment, tow main functions have been
developed and are available:

- `obs.simulate(act, time_step=0)` which will "apply" the action on the known state and do "as if" a step
  has been made. This is called "simulate", it is rather accurate (up to the "we don't know the future" part)
  in the sense that is does check for illegal actions, ambiguous actions, reconnect properly the powerlines
  if needed etc. and performs simulation of "cascading failures" and other things. Of course it takes
  a lot of time to carry out all these computation.
- `impact = obs + act` (since grid2op 1.5.0). On the other hand, the "+" operator of the observation is
  much faster. It can be use to rapidly estimate the state of the grid (especially the topology)
  after the application of an action for example. This is to ease the process of studying what does
  an action exactly.

The difference in computation time, for an action of type "topology set" is shown in the table below:

================================  ================================  =============  =======================
method                             env name                         backend used    time to perform (ms)
================================  ================================  =============  =======================
`obs + act`                        l2rpn_case14_sandbox             pandapower      0.21
`obs.simulate(act, time_step=0)`   l2rpn_case14_sandbox             pandapower      17.3
`obs + act`                        l2rpn_case14_sandbox             lightsim2grid   0.21
`obs.simulate(act, time_step=0)`   l2rpn_case14_sandbox             lightsim2grid   1.56
`obs + act`                        l2rpn_neurips_2020_track2_small  pandapower      0.22
`obs.simulate(act, time_step=0)`   l2rpn_neurips_2020_track2_small  pandapower      33.4
`obs + act`                        l2rpn_neurips_2020_track2_small  lightsim2grid   0.22
`obs.simulate(act, time_step=0)`   l2rpn_neurips_2020_track2_small  lightsim2grid   2.03
================================  ================================  =============  =======================

(results were obtained with grid2op version 1.5.0 on a "Intel(R) Core(TM) i7-4790K CPU @ 4.00GHz" using
"Python 3.8.5 (default, Jul 28 2020, 12:59:40) [GCC 9.3.0] on linux" on ubuntu 20.04.1
"20.04.1-Ubuntu SMP Tue Jan 12 16:39:47 UTC 2021" using linux kernel "5.8.0-38-generic")

As you can see, the `obs + act` method is always approximately 10 times faster than the
`obs.simulate(act, time_step=0)` [of course providing much less information] and can be up
to 150 faster on larger grid (IEEE 118) using the default pandapower backend.

We can also note that, as it doesn't require the use of any simulation, the time to do the `obs + act` is
more or less independent of the grid size (0.21 ms for a grid counting 14 substations and
0.22ms for a grid with 118 substations) while the `obs.simulate` is not.

Now to retrieve a "graph like" object, you can :

.. code-block:: python

    # method 1
    sim_obs, *_ = obs.simulate(act)

    # method 2
    obs_add = obs + add

And refer to the page :ref:`gridgraph-module` or the section :ref:`observation_module_graph` to retrieve a graph
structure from these observations.

For example:

.. code-block:: python

    bus_bus_mat = obs_add.bus_connectivity_matrix()  # alternatively  `sim_obs.bus_connectivity_matrix()`
    # or
    connect_mat = obs_add.connectivity_matrix()  # alternatively  `sim_obs.connectivity_matrix()`



.. _Illegal-vs-Ambiguous:

Illegal vs Ambiguous
---------------------
Manipulating a powergrid is more complex than asking "pacman" to move "left" / "down" / "right" or "up". Computing
a correct action can be a tedious process.

An action can be incorrect because of two main factors:

- ``ambiguous``: this will be the case when an action is performed on 17 objects whereas the given substations counts
  only 16 of them, this will be the case when you ask to reconnect powerline 999 while there are only 20 powerlines
  on the grid etc. This is raised when the action **cannot** be understood as a correct action. Grid2op does not
  know how to interpret your action. If we take the "PacMan" game an ambiguous action would translate in moving
  "up" **and** "down" at the same time.
- ``illegal``: (see :class:`grid2op.Rules.BaseRules` and :class:`grid2op.Parameters.Parameters` for more information).
  An action can be legal or illegal depending on the rules of the game. For example, we could forbid to reconnect
  powerline 7 between time steps 123 and 159 (this would corresponds to a "maintenance" of the powerline, you can
  imagine people painting the tower for example). But that does not mean reconnecting powerline 7 is forbidden at
  other times steps. In this case we say the action is "illegal". Still my overall favorite game, in PacMan this
  would be the equivalent to moving left while there are a wall on the left.

Ambiguous or Illegal, the action will be replaced by a "do nothing" without any other incidents on the game.

.. _action_powerline_status:

Note on powerline status
------------------------
As of grid2op version 1.2.0, we attempted to clean and rationalize the API concerning the change of
powerline status (see explanatory notebook `getting_started/3_Action_GridManipulation` for more detailed
explanation.

The powerline status (connected / disconnected) can now be affected in two different ways:

- by `setting` / `changing` its status directly (using the "set_line_status" or "change_line_status" keyword).
- [NEW] by modifying the bus on any of the end (origin or extremity) of a powerline

In that later case, the behavior is:

- if the bus of a powerline end (origin or extremity) is "set" to -1 and not modified at the other and if the powerline
  was connected, it will disconnect this powerline
- if the bus of a powerline end (origin or extremity) is "set" to 1 or 2 at one end and not modified at the other and
  if the powerline was connected, it will reconnect the powerline
- if the bus of a powerline end (origin or extremity) is "set" to -1 at one end and set to 1 or 2 at its other end the
  action is **ambiguous**.

The way to compute the impact of the action has also been adjusted to reflect these changes.

In the table below we try to summarize all the possible actions and their impact on the powerline.
This table is made considering that "`LINE_ID`" is an id of a powerline and "`SUB_OR`" is the id of the origin of the
substation. If a status is 0 it means the powerlines is disconnected, if the status is 1 it means it is connected.

=============================================  ================  ============   ====================   ====================
action                                         original status   final status   substations affected   line status affected
=============================================  ================  ============   ====================   ====================
{"set_line_status": [(LINE_ID, -1)]}           1                 0              None                    LINE_ID
{"set_line_status": [(LINE_ID, +1)]}           1                 1              None                    LINE_ID
{"set_line_status": [(LINE_ID, -1)]}           0                 0              None                    LINE_ID
{"set_line_status": [(LINE_ID, +1)]}           0                 1              None                    LINE_ID
{"change_line_status": [LINE_ID]}              1                 0              None                    LINE_ID
{"change_line_status": [LINE_ID]}              0                 1              None                    LINE_ID
{"set_bus": {"lines_or_id": [(LINE_ID, -1)]}}  1                 0              None                    INE_ID
{"set_bus": {"lines_or_id": [(LINE_ID, -1)]}}  0                 0              SUB_OR                  None
{"set_bus": {"lines_or_id": [(LINE_ID, 2)]}}   1                 1              SUB_OR                  None
{"set_bus": {"lines_or_id": [(LINE_ID, 2)]}}   0                 1              None                    LINE_ID
{"change_bus": {"lines_or_id": [LINE_ID]}}     1                 1              SUB_OR                  None
{"change_bus": {"lines_or_id": [LINE_ID]}}     0                 0              SUB_OR                  None
=============================================  ================  ============   ====================   ====================

This has other impacts. In grid2op there is a convention that if an object is disconnected,
then it is assigned to bus "-1". For a powerline this entails that a status changed affects the bus of

As we explained in the previous paragraph, some action on one end of a powerline can reconnect a
powerline or disconnect it. This means they modify the bus of **both** the extremity of the powerline.

Here is a table summarizing how the buses are impacted. We denoted by "`PREVIOUS_OR`" the last bus at which
the origin side of the powerline was connected and "`PREVIOUS_EX`" the last bus at which the extremity side of the
powerline was connected. Note that for clarity when something is not modified by the action we decided to write on
the table "not modified" (this entails that after this action, if the powerline is connected then "new origin bus" is
"`PREVIOUS_OR`" and "new extremity bus" is "`PREVIOUS_EX`"). We remind the reader that "-1" encode for a
disconnected object.

=============================================  ================  ============   ==============  ========================
action                                         original status   final status   new origin bus  new extremity bus
=============================================  ================  ============   ==============  ========================
{"set_line_status": [(LINE_ID, -1)]}           1                 0              -1              -1
{"set_line_status": [(LINE_ID, +1)]}           1                 1              Not modified    Not modified
{"set_line_status": [(LINE_ID, -1)]}           0                 0              Not modified    Not modified
{"set_line_status": [(LINE_ID, +1)]}           0                 1              PREVIOUS_OR     PREVIOUS_EX
{"change_line_status": [LINE_ID]}              1                 0              -1              -1
{"change_line_status": [LINE_ID]}              0                 1              PREVIOUS_OR     PREVIOUS_EX
{"set_bus": {"lines_or_id": [(LINE_ID, -1)]}}  1                 0              -1              -1
{"set_bus": {"lines_or_id": [(LINE_ID, -1)]}}  0                 0              Not modified    Not modified
{"set_bus": {"lines_or_id": [(LINE_ID, 2)]}}   1                 1              2               Not modified
{"set_bus": {"lines_or_id": [(LINE_ID, 2)]}}   0                 1              2               PREVIOUS_EX
{"change_bus": {"lines_or_id": [LINE_ID]}}     1                 1              \*              Not modified
{"change_bus": {"lines_or_id": [LINE_ID]}}     0                 0              Not modified    Not modified
=============================================  ================  ============   ==============  ========================

\* means that this bus is affected: if it was on bus 1 it moves on bus 2 and vice versa.

Note on random actions
------------------------
Sampling a "non ambiguous" legal action is a difficult task.

TODO

.. _action-module-converter:

Easier actions manipulation
----------------------------
The action class presented here can be quite complex to apprehend, especially for a machine learning algorithm.

Grid2op offers some more "convient" manipulation of the powergrid by transforming this rather "descriptive"
action formulation to "action_space" that are compatible with Farama Fundation Gymnasium package (
package that was formerly "openAI gym").

This includes:

- :class:`grid2op.gym_compat.GymActionSpace` which "represents" actions as a gymnasium 
  `Dict <https://gymnasium.farama.org/api/spaces/composite/#dict>`_
- :class:`grid2op.gym_compat.BoxGymActSpace` which represents actions as gymnasium 
  `Box <https://gymnasium.farama.org/api/spaces/fundamental/#box>`_ 
  (actions are numpy arrays). This is especially suited for continuous attributes
  such as redispatching, storage or curtailment.
- :class:`grid2op.gym_compat.DiscreteActSpace` which represents actions as gymnasium 
  `Discrete <https://gymnasium.farama.org/api/spaces/fundamental/#discrete>`_
  (actions are integer). This is especially suited for discrete actions such as 
  setting line status or topologies at substation.
- :class:`grid2op.gym_compat.MultiDiscreteActSpace` which represents actions as gymnasium 
  `MultiDiscrete <https://gymnasium.farama.org/api/spaces/fundamental/#multidiscrete>`_
  (actions are integer). This is also especially suited for discrete actions such as 
  setting line status or topologies at substation.

.. note::
  The main difference between :class:`grid2op.gym_compat.DiscreteActSpace` and 
  :class:`grid2op.gym_compat.MultiDiscreteActSpace` is that Discrete actions will 
  allow the agent to perform only one type of action at each step (either it performs
  redispatching on one generator OR on another generator OR it set the status of a powerline
  OR it set the substation at one substation etc. but it cannot "peform redispatching on 
  2 or more generators" nor can it "perform redispatching on one generator AND disconnect a powerline")
  which can be rather limited for some applications.


.. _action-module-backend_callbacks:

Backend callbacks: implementation of action not handled by grid2op
---------------------------------------------------------------------

.. versionadded:: 1.12.1

  This feature has been added in grid2op 1.12.1. Upgrade to a supported grid2op version
  if you want to benefit from it.


Goal
++++++

If you want to use a feature not available in grid2op, the best thing to do would be to
write a github issue or a start a discussion about this feature. And then to develop (or have some 
develop) it in general, so that everyone can benefit from it.

Doing so might be not feasible in practice or take too much time and resources.

To circumvent this limitation of grid2op, in version 1.12.1 we decided to add a feature, directly 
accessible in the action to allow the agent to use function that are not directly availble
in grid2op but are available in the backend they are using.


Limitation
+++++++++++

This function is then backend dependant. If an agent uses this function and decides to change the 
backend, then it will have to recode these "callbacks".

This function can break "grid2op time handling". This means that grid2op has absolutely no control what is 
done, how long it will last, whether it breaks some "rules" etc.

.. danger::
  This function is totally generic and no check at all are made by grid2op. Use with extreme care.

For example, some "callbacks" might break some "rules" of game, allowing to reconnect a powerline that is
under maintenance for example, or to increase the production of a non controllable generator.

Some "callbacks" might have "long lasting" effects, even after the environment is reset (which is guaranteed
not to happen if using grid2op-only actions).

If such an action is done at some point, the agent (or "something" outside of the agent) is responsible to 
"undo" it when needed, for example at the end of an episode, or after the use of "obs.simulate(...)". 

.. warning::
  This is why we do not recommend to use this feature combined with "obs.simulate"

As grid2op has no way of "controlling" what is done in these callbacks, it is possible to 
have grid2op generate a "wrong" observation. For example it would be easy with the "PandaPowerBackend"
to "move" a load from one substation to another (which would be equivalent to physcally move a city from
one side of the country to another...) 

It is also possible to create elements on the grid. Even if such elements are "modeled" by grid2op, 
they will not appear in the observation, which might break the Kirchhoff Current Laws (as seen by grid2op).
This is for example the case if you create a load, such load will not appear on the "obs.load_p" 
vector.

You can also use it to "hack" the environment and allow the agent to observe things that are not
normally observable.

Finally, this feature is applied BEFORE any changes made by "real" grid2op entities (environment, agent, etc.).
This means that you can modify things using this feature, but these modifications might be silently (because
grid2op does not check anything) overriden by other grid2op instructions.

Recommended Usage
++++++++++++++++++

We recommend to use this feature if:

- you want to perform actions not currently modeled in grid2op on elements modeled
  by grid2op (at time of writing, you might want to change the tap ratio of a transformer 
  or a phase shifting transformer)
- you want to peform actions on element not modeled in grid2Op (at time of writing this 
  includes actions on HVDCs for example)

In any case, it's best to let us know so that we can either help you integrate this feature in 
grid2op (the hard part is to have the "functional specs", actually coding in grid2op is 
relatively easy).


Practical Usage
++++++++++++++++
So, how to use it then...

The `action.backend_dependant_callback` is an attribute of 
the action from grid2op 1.12.1. 

.. warning::
  This attribute is ignored on earlier grid2op versions !

This attribute is a "callable" (think of it as a function) that 
takes as input the content of `env.backend._grid` and modifies
it in place.

.. warning::
  Its return value is ignored.

You can use it like this for example:

.. code-block:: python
    
    import grid2op
    from grid2op.Action import BaseAction
    env_name = "educ_case14_storage"  # or any other name
    env = grid2op.make(env_name, test=True)
    obs = env.reset(seed=0, options={"time serie id": 0})

    act = env.action_space()
    
    def change_whatever(grid):
        # this needs to modify "grid"
        # argument in place
        # Any return values if ignored
        ...
        
    act.backend_dependant_callback = change_whatever
    obs, reward, done, info = env.step(act)
  
The code in the :func:`grid2op.Environment.BaseEnv.step` function for this feature is
equivalent to:

.. code-block:: python

  action.backend_dependant_callback(self.backend._grid)

You then need to make sure that the function you pass to `action.backend_dependant_callback` takes only
one argument (which is of type `env.backend._grid`) and returns nothing.


Equivalent implementation
++++++++++++++++++++++++++

Concretely, this function is added to the "env.step" method, BEFORE 
the rest of the modifications are performed.

This modifies the grid before the rest of the action of the agent,
before the change of the environment (new load or generator) and
before the opponent (if any) acts.

If there is an error during the call to `action.backend_dependant_callback(self.backend._grid)`,
then the action is declared `ambiguous`, an :class:`grid2op.Exceptions.InvalidBackendCallback` is added
to the `info["exceptions"]` returned value.

In this case, the whole action is replaced by a "do nothing" action and nothing is done
to the backend.

.. danger::
  About this last statement, grid2op does not control anything regarding this callback. 

  This means that, if env.backend._grid is "half modified" before an exception is raised 
  in the application of `action.backend_dependant_callback` then "half of the modifications"
  will be performed and not removed, and half of them will be ignored.

  In this last case, all other "part" of the actions will be ignored as well.

  For example, if your call back is like this:

  .. code-block:: python
    
    def my_callback(grid):
        grid.something_ok
        grid.some_other_thing_ok
        grid.A_CRITICAL_FAILURE
        # -> suppose an exception is raised here
        grid.a_last_thing_ok
  
  Then in this case, `something_ok` and `some_other_thing_ok` will be implemented
  on the grid. The critical failure will not and neither will `a_last_thing_ok`.

  And because you apply a "callback", grid2op has no way to know, in general, how to undo your changes
  so even if your action is ambiguous, it will not be strictly equivalent to 
  the "do nothing" action: the grid will be modified.

  This breaks the "ACID" (https://en.wikipedia.org/wiki/ACID) "implementation" of the action. In particular
  the action will not be "atomic" anymore (some part might be implemented and not other) nor will it
  be "consistent" (the fact that there is a critical failure in the example might lead the grid to be
  in an inconsistent state from which the grid2op environment might never, even after a `env.reset()`
  recover).

  "With a great power, come great responsibility" ...


Diving even more into the customization
++++++++++++++++++++++++++++++++++++++++

Detailed Documentation by class
-------------------------------

.. automodule:: grid2op.Action
    :members:
    :private-members:
    :special-members:
    :autosummary:


.. include:: final.rst

