from overcooked import Action, Overcooked
import numpy as np


def test_overcooked_attributes():
    env = Overcooked.from_layout("simple_o")
    height, width = env._mdp.shape
    assert env.n_agents == 2
    assert env.n_actions == Action.NUM_ACTIONS
    assert env.observation_shape == (25, height, width)
    assert env.reward_space.shape == (1,)
    assert env.extras_shape == (2,)
    assert not env.is_multi_objective


def test_overcooked_obs_state():
    HORIZON = 100
    env = Overcooked.from_layout("coordination_ring", horizon=HORIZON)
    height, width = env._mdp.shape
    obs, state = env.reset()
    for i in range(HORIZON):
        assert obs.data.dtype == np.float32
        assert state.data.dtype == np.float32
        assert obs.extras.dtype == np.float32
        assert state.extras.dtype == np.float32
        assert obs.shape == (25, height, width)
        assert obs.extras_shape == (2,)
        assert state.shape == (25, height, width)
        assert state.extras_shape == (2,)

        assert np.all(obs.extras[:, 0] == i / HORIZON)
        assert np.all(state.extras[0] == i / HORIZON)

        step = env.random_step()
        obs = step.obs
        state = step.state
        if i < HORIZON - 1:
            assert not step.done
        else:
            assert step.done


def test_overcooked_shaping():
    UP = 0
    RIGHT = 2
    STAY = 4
    INTERACT = 5
    grid = [
        ["X", "X", "X", "D", "X"],
        ["X", "O", "S", "2", "X"],
        ["X", "1", "P", " ", "X"],
        ["X", "T", "S", " ", "X"],
        ["X", "X", "X", "X", "X"],
    ]

    env = Overcooked.from_grid(grid)
    env.reset()
    actions_rewards = [
        ([UP, STAY], False),
        ([INTERACT, STAY], False),
        ([RIGHT, STAY], False),
        ([INTERACT, STAY], True),
    ]

    for action, expected_reward in actions_rewards:
        step = env.step(action)
        if expected_reward:
            assert step.reward.item() > 0


def test_overcooked_name():
    grid = [
        ["X", "X", "X", "D", "X"],
        ["X", "O", "S", "2", "X"],
        ["X", "1", "P", " ", "X"],
        ["X", "T", "S", " ", "X"],
        ["X", "X", "X", "X", "X"],
    ]

    env = Overcooked.from_grid(grid)
    assert env.name == "Overcooked-custom-layout"

    env = Overcooked.from_grid(grid, layout_name="my incredible grid")
    assert env.name == "Overcooked-my incredible grid"

    env = Overcooked.from_layout("asymmetric_advantages")
    assert env.name == "Overcooked-asymmetric_advantages"


def test_render():
    env = Overcooked.from_layout("simple_o")
    img = env.get_image()
    assert img is not None
