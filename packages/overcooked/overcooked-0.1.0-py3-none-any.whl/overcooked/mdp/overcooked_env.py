import copy
from typing import Callable

import cv2
import gymnasium
import numpy as np
import pygame

from overcooked.mdp.actions import Action
from overcooked.mdp.overcooked_mdp import (
    EVENT_TYPES,
    OvercookedGridworld,
)
from overcooked.planning.planners import (
    NO_COUNTERS_PARAMS,
    MediumLevelActionManager,
    MotionPlanner,
)
from overcooked.visualization.state_visualizer import StateVisualizer


MAX_HORIZON = int(1e10)


class OvercookedEnv(object):
    """
    An environment wrapper for the OvercookedGridworld Markov Decision Process.

    The environment keeps track of the current state of the agent, updates
    it as the agent takes actions, and provides rewards to the agent.

    E.g. of how to instantiate OvercookedEnv:
    > mdp = OvercookedGridworld(...)
    > env = OvercookedEnv.from_mdp(mdp, horizon=400)
    """

    def __init__(
        self,
        mdp_generator_fn: Callable[..., OvercookedGridworld],
        start_state_fn=None,
        horizon=MAX_HORIZON,
        mlam_params=NO_COUNTERS_PARAMS,
        info_level=0,
        num_mdp=1,
        initial_info={},
    ):
        """
        mdp_generator_fn (callable):    A no-argument function that returns a OvercookedGridworld instance
        start_state_fn (callable):      Function that returns start state for the MDP, called at each environment reset
        horizon (int):                  Number of steps before the environment returns done=True
        mlam_params (dict):             params for MediumLevelActionManager
        info_level (int):               Change amount of logging
        num_mdp (int):                  the number of mdp if we are using a list of mdps
        initial_info (dict):            the initial outside information feed into the generator function

        TODO: Potentially make changes based on this discussion
        https://github.com/HumanCompatibleAI/overcooked_ai/pull/22#discussion_r416786847
        """
        assert callable(mdp_generator_fn), (
            "OvercookedEnv takes in a OvercookedGridworld generator function. "
            "If trying to instantiate directly from a OvercookedGridworld "
            "instance, use the OvercookedEnv.from_mdp method"
        )
        self.num_mdp = num_mdp
        self.variable_mdp = num_mdp > 1
        self.mdp_generator_fn = mdp_generator_fn
        self.horizon = horizon
        self._mlam = None
        self._mp = None
        self.mlam_params = mlam_params
        self.start_state_fn = start_state_fn
        self.info_level = info_level
        self.reset(outside_info=initial_info)
        if self.horizon >= MAX_HORIZON and self.info_level > 0:
            print(
                "Environment has (near-)infinite horizon and no terminal states. \
                Reduce info level of OvercookedEnv to not see this message."
            )

    @property
    def mlam(self):
        if self._mlam is None:
            if self.info_level > 0:
                print("Computing MediumLevelActionManager")
            self._mlam = MediumLevelActionManager.from_pickle_or_compute(self.mdp, self.mlam_params, force_compute=False)
        return self._mlam

    @property
    def mp(self):
        if self._mp is None:
            if self._mlam is not None:
                self._mp = self.mlam.motion_planner
            else:
                if self.info_level > 0:
                    print("Computing MotionPlanner")
                self._mp = MotionPlanner.from_pickle_or_compute(
                    self.mdp,
                    self.mlam_params["counter_goals"],
                    force_compute=False,
                )
        return self._mp

    @staticmethod
    def from_mdp(
        mdp: OvercookedGridworld,
        start_state_fn=None,
        horizon=MAX_HORIZON,
        mlam_params=NO_COUNTERS_PARAMS,
        info_level=1,
        num_mdp=None,
    ):
        """
        Create an OvercookedEnv directly from a OvercookedGridworld mdp
        rather than a mdp generating function.
        """
        if num_mdp is not None:
            assert num_mdp == 1

        def mdp_generator_fn(*args, **kwargs):
            return mdp

        return OvercookedEnv(
            mdp_generator_fn=mdp_generator_fn,
            start_state_fn=start_state_fn,
            horizon=horizon,
            mlam_params=mlam_params,
            info_level=info_level,
            num_mdp=1,
        )

    @property
    def env_params(self):
        """
        Env params should be thought of as all of the params of an env WITHOUT the mdp.
        Alone, env_params is not sufficent to recreate a copy of the Env instance, but it is
        together with mdp_params (which is sufficient to build a copy of the Mdp instance).
        """
        return {
            "start_state_fn": self.start_state_fn,
            "horizon": self.horizon,
            "info_level": self.info_level,
            "num_mdp": self.num_mdp,
        }

    def copy(self):
        # TODO: Add testing for checking that these util methods are up to date?
        return OvercookedEnv(
            mdp_generator_fn=self.mdp_generator_fn,
            start_state_fn=self.start_state_fn,
            horizon=self.horizon,
            info_level=self.info_level,
            num_mdp=self.num_mdp,
        )

    def __repr__(self):
        """
        Standard way to view the state of an environment programatically
        is just to print the Env object
        """
        return self.mdp.state_string(self.state)

    def step(self, joint_action, joint_agent_action_info=None, display_phi=False):
        """Performs a joint action, updating the environment state
        and providing a reward.

        On being done, stats about the episode are added to info:
            ep_sparse_r: the environment sparse reward, given only at soup delivery
            ep_shaped_r: the component of the reward that is due to reward shaped (excluding sparse rewards)
            ep_length: length of rollout
        """
        assert not self.is_done()
        if joint_agent_action_info is None:
            joint_agent_action_info = [{}, {}]
        next_state, mdp_infos = self.mdp.get_state_transition(self.state, joint_action, display_phi, self.mp)

        # Update game_stats
        self._update_game_stats(mdp_infos)

        # Update state and done
        self.state = next_state
        done = self.is_done()
        env_info = self._prepare_info_dict(joint_agent_action_info, mdp_infos)

        if done:
            self._add_episode_info(env_info)

        timestep_sparse_reward = sum(mdp_infos["sparse_reward_by_agent"])
        return (next_state, timestep_sparse_reward, done, env_info)

    def lossless_state_encoding_mdp(self, state):
        """
        Wrapper of the mdp's lossless_encoding
        """
        return self.mdp.lossless_state_encoding(state, self.horizon)

    def featurize_state_mdp(self, state, num_pots=2):
        """
        Wrapper of the mdp's featurize_state
        """
        return self.mdp.featurize_state(state, self.mlam, num_pots=num_pots)

    def reset(self, regen_mdp=True, outside_info={}):
        """
        Resets the environment. Does NOT reset the agent.
        Args:
            regen_mdp (bool): gives the option of not re-generating mdp on the reset,
                                which is particularly helpful with reproducing results on variable mdp
            outside_info (dict): the outside information that will be fed into the scheduling_fn (if used), which will
                                 in turn generate a new set of mdp_params that is used to regenerate mdp.
                                 Please note that, if you intend to use this arguments throughout the run,
                                 you need to have a "initial_info" dictionary with the same keys in the "env_params"
        """
        if regen_mdp:
            self.mdp = self.mdp_generator_fn(outside_info)
            self._mlam = None
            self._mp = None
        if self.start_state_fn is None:
            self.state = self.mdp.get_standard_start_state()
        else:
            self.state = self.start_state_fn()

        events_dict = {k: [[] for _ in range(self.mdp.num_players)] for k in EVENT_TYPES}
        rewards_dict = {
            "cumulative_sparse_rewards_by_agent": np.array([0] * self.mdp.num_players),
            "cumulative_shaped_rewards_by_agent": np.array([0] * self.mdp.num_players),
        }
        self.game_stats = {**events_dict, **rewards_dict}

    def is_done(self):
        """Whether the episode is over."""
        return self.state.timestep >= self.horizon or self.mdp.is_terminal(self.state)

    def potential(self, mlam, state=None, gamma=0.99):
        """
        Return the potential of the environment's current state, if no state is provided
        Otherwise return the potential of `state`
        args:
            mlam (MediumLevelActionManager): the mlam of self.mdp
            state (OvercookedState): the current state we are evaluating the potential on
            gamma (float): discount rate
        """
        state = state if state else self.state
        return self.mdp.potential_function(state, mp=self.mp, gamma=gamma)

    def _prepare_info_dict(self, joint_agent_action_info, mdp_infos):
        """
        The normal timestep info dict will contain infos specifc to each agent's action taken,
        and reward shaping information.
        """
        # Get the agent action info, that could contain info about action probs, or other
        # custom user defined information
        env_info: dict = {"agent_infos": [joint_agent_action_info[agent_idx] for agent_idx in range(self.mdp.num_players)]}
        # TODO: This can be further simplified by having all the mdp_infos copied over to the env_infos automatically
        env_info["sparse_r_by_agent"] = mdp_infos["sparse_reward_by_agent"]
        env_info["shaped_r_by_agent"] = mdp_infos["shaped_reward_by_agent"]
        env_info["phi_s"] = mdp_infos["phi_s"] if "phi_s" in mdp_infos else None
        env_info["phi_s_prime"] = mdp_infos["phi_s_prime"] if "phi_s_prime" in mdp_infos else None
        return env_info

    def _add_episode_info(self, env_info):
        env_info["episode"] = {
            "ep_game_stats": self.game_stats,
            "ep_sparse_r": sum(self.game_stats["cumulative_sparse_rewards_by_agent"]),
            "ep_shaped_r": sum(self.game_stats["cumulative_shaped_rewards_by_agent"]),
            "ep_sparse_r_by_agent": self.game_stats["cumulative_sparse_rewards_by_agent"],
            "ep_shaped_r_by_agent": self.game_stats["cumulative_shaped_rewards_by_agent"],
            "ep_length": self.state.timestep,
        }
        return env_info

    def _update_game_stats(self, infos):
        """
        Update the game stats dict based on the events of the current step
        NOTE: the timer ticks after events are logged, so there can be events from time 0 to time self.horizon - 1
        """
        self.game_stats["cumulative_sparse_rewards_by_agent"] += np.array(infos["sparse_reward_by_agent"])
        self.game_stats["cumulative_shaped_rewards_by_agent"] += np.array(infos["shaped_reward_by_agent"])

        for event_type, bool_list_by_agent in infos["event_infos"].items():
            # For each event type, store the timestep if it occurred
            event_occurred_by_idx = [int(x) for x in bool_list_by_agent]
            for idx, event_by_agent in enumerate(event_occurred_by_idx):
                if event_by_agent:
                    self.game_stats[event_type][idx].append(self.state.timestep)

    ####################
    # TRAJECTORY LOGIC #
    ####################

    def execute_plan(self, start_state, joint_action_plan, display=False):
        """Executes action_plan (a list of joint actions) from a start
        state in the mdp and returns the resulting state."""
        self.state = start_state
        done = False
        if display:
            print("Starting state\n{}".format(self))
        for joint_action in joint_action_plan:
            self.step(joint_action)
            done = self.is_done()
            if display:
                print(self)
            if done:
                break
        successor_state = self.state
        self.reset(False)
        return successor_state, done


class Overcooked(gymnasium.Env):
    """
    Wrapper for the Env class above that is SOMEWHAT compatible with the standard gym API.
    Why only somewhat? Because we need to flatten a multi-agent env to be a single-agent env (as gym requires).

    NOTE: Observations returned are in a dictionary format with various information that is
     necessary to be able to handle the multi-agent nature of the environment. There are probably
     better ways to handle this, but we found this to work with minor modifications to OpenAI Baselines.

    NOTE: The index of the main agent (as gym envs are 'single-agent') in the mdp is randomized at each reset
     of the environment, and is kept track of by the self.agent_idx attribute. This means that it is necessary
     to pass on this information in the output to know for which agent index featurizations should be made for
     other agents.

    For example, say one is training A0 paired with A1, and A1 takes a custom state featurization.
    Then in the runner.py loop in OpenAI Baselines, we will get the lossless encodings of the state,
    and the true Overcooked state. When we encode the true state to feed to A1, we also need to know
    what agent index it has in the environment (as encodings will be index dependent).
    """

    env_name = "Overcooked-v0"

    # gym checks for the action space and obs space while initializing the env and throws an error if none exists
    # custom_init after __init__ no longer works
    # might as well move all the initilization into the actual __init__
    def __init__(self, base_env, featurize_fn, baselines_reproducible=False):
        """
        base_env: OvercookedEnv
        featurize_fn(mdp, state): fn used to featurize states returned in the 'both_agent_obs' field

        Example creating a gym env:

        mdp = OvercookedGridworld.from_layout_name("asymmetric_advantages")
        base_env = OvercookedEnv.from_mdp(mdp, horizon=500)
        env = gymnasium.make("Overcooked-v0",base_env = base_env, featurize_fn =base_env.featurize_state_mdp)
        """
        if baselines_reproducible:
            # NOTE:
            # This will cause all agent indices to be chosen in sync across simulation
            # envs (for each update, all envs will have index 0 or index 1).
            # This is to prevent the randomness of choosing agent indexes
            # from leaking when using subprocess-vec-env in baselines (which
            # seeding does not reach) i.e. having different results for different
            # runs with the same seed.
            # The effect of this should be negligible, as all other randomness is
            # controlled by the actual run seeds
            np.random.seed(0)
        self.base_env = base_env
        self.featurize_fn = featurize_fn
        self.observation_space = self._setup_observation_space()
        self.action_space = gymnasium.spaces.Discrete(len(Action.ALL_ACTIONS))
        self.reset()
        self.visualizer = StateVisualizer()

    def _setup_observation_space(self):
        dummy_mdp = self.base_env.mdp
        dummy_state = dummy_mdp.get_standard_start_state()
        obs_shape = self.featurize_fn(dummy_state)[0].shape
        high = np.ones(obs_shape, dtype=np.float32) * float("inf")
        low = np.zeros(obs_shape, dtype=np.float32)
        return gymnasium.spaces.Box(low, high, dtype=np.float32)

    def step(self, action):
        """
        action:
            (agent with index self.agent_idx action, other agent action)
            is a tuple with the joint action of the primary and secondary agents in index format

        returns:
            observation: formatted to be standard input for self.agent_idx's policy
        """
        assert all(self.action_space.contains(a) for a in action), "%r (%s) invalid" % (
            action,
            type(action),
        )
        agent_action, other_agent_action = [Action.INDEX_TO_ACTION[a] for a in action]

        if self.agent_idx == 0:
            joint_action = (agent_action, other_agent_action)
        else:
            joint_action = (other_agent_action, agent_action)

        next_state, reward, done, env_info = self.base_env.step(joint_action)
        ob_p0, ob_p1 = self.featurize_fn(next_state)
        if self.agent_idx == 0:
            both_agents_ob = (ob_p0, ob_p1)
        else:
            both_agents_ob = (ob_p1, ob_p0)

        env_info["policy_agent_idx"] = self.agent_idx

        if "episode" in env_info.keys():
            env_info["episode"]["policy_agent_idx"] = self.agent_idx

        obs = {
            "both_agent_obs": both_agents_ob,
            "overcooked_state": next_state,
            "other_agent_env_idx": 1 - self.agent_idx,
        }
        return obs, reward, done, env_info

    def reset(self):
        """
        When training on individual maps, we want to randomize which agent is assigned to which
        starting location, in order to make sure that the agents are trained to be able to
        complete the task starting at either of the hardcoded positions.

        NOTE: a nicer way to do this would be to just randomize starting positions, and not
        have to deal with randomizing indices.
        """
        self.base_env.reset()
        self.mdp = self.base_env.mdp
        self.agent_idx = np.random.choice([0, 1])
        ob_p0, ob_p1 = self.featurize_fn(self.base_env.state)

        if self.agent_idx == 0:
            both_agents_ob = (ob_p0, ob_p1)
        else:
            both_agents_ob = (ob_p1, ob_p0)
        return {
            "both_agent_obs": both_agents_ob,
            "overcooked_state": self.base_env.state,
            "other_agent_env_idx": 1 - self.agent_idx,
        }

    def render(self):
        rewards_dict = {}  # dictionary of details you want rendered in the UI
        for key, value in self.base_env.game_stats.items():
            if key in [
                "cumulative_shaped_rewards_by_agent",
                "cumulative_sparse_rewards_by_agent",
            ]:
                rewards_dict[key] = value

        image = self.visualizer.render_state(
            state=self.base_env.state,
            grid=self.base_env.mdp.terrain_mtx,
            hud_data=StateVisualizer.default_hud_data(self.base_env.state, **rewards_dict),
        )

        buffer = pygame.surfarray.array3d(image)
        image = copy.deepcopy(buffer)
        image = np.flip(np.rot90(image, 3), 1)
        image = cv2.resize(image, (2 * 528, 2 * 464))
        return image
