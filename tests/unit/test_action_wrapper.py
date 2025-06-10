# tests/unit/test_action_wrapper.py

import pytest
import numpy as np
import gymnasium as gym
from src.env.wrappers.action_wrapper import ActionWrapper

class DummyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        self.last_action = None
    def step(self, action):
        self.last_action = action
        obs = np.zeros((2,), dtype=np.float32)
        reward = 1.0
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info
    def reset(self, **kwargs):
        return np.zeros((2,), dtype=np.float32), {}

def test_action_transformation_and_logging(tmp_path):
    env = DummyEnv()
    def clipper(a): return np.clip(a, -0.5, 0.5)
    wrapper = ActionWrapper(env, action_fn=clipper, log_dir=str(tmp_path))
    obs, info = wrapper.reset()
    action = np.array([1.0, -1.0])
    obs, reward, terminated, truncated, info = wrapper.step(action)
    np.testing.assert_array_almost_equal(env.last_action, [0.5, -0.5])
    logs = wrapper.get_logs()
    assert logs[-1]["original_action"] == [1.0, -1.0]
    assert logs[-1]["transformed_action"] == [0.5, -0.5]

def test_action_fn_exception_fallback():
    env = DummyEnv()
    def bad_fn(a): raise RuntimeError("fail")
    wrapper = ActionWrapper(env, action_fn=bad_fn)
    obs, info = wrapper.reset()
    action = np.array([0.3, 0.7])
    obs, reward, terminated, truncated, info = wrapper.step(action)
    np.testing.assert_allclose(np.array(env.last_action, dtype=np.float32),
                              np.array([0.3, 0.7], dtype=np.float32),
                              rtol=1e-5, atol=1e-7)
    logs = wrapper.get_logs()
    np.testing.assert_allclose(np.array(logs[-1]["transformed_action"], dtype=np.float32),
                              np.array([0.3, 0.7], dtype=np.float32),
                              rtol=1e-5, atol=1e-7)

def test_set_action_fn_dynamic():
    env = DummyEnv()
    wrapper = ActionWrapper(env)
    def double(a): return a * 2
    wrapper.set_action_fn(double)
    obs, info = wrapper.reset()
    action = np.array([0.6, 0.7])  # multiplica por 2 => [1.2, 1.4] fora do espaço!
    with pytest.raises(ValueError):
        wrapper.step(action)

def test_nan_action_auto_fix():
    env = DummyEnv()
    def nan_fn(a): return np.array([np.nan, 1.0])
    wrapper = ActionWrapper(env, action_fn=nan_fn)
    obs, info = wrapper.reset()
    obs, reward, terminated, truncated, info = wrapper.step([0.5, 0.5])
    np.testing.assert_array_equal(env.last_action, [0.0, 1.0])

def test_save_logs_creates_file(tmp_path):
    env = DummyEnv()
    wrapper = ActionWrapper(env, log_dir=str(tmp_path))
    obs, info = wrapper.reset()
    wrapper.step([0.1, 0.2])
    wrapper.save_logs()
    import os
    files = [f for f in os.listdir(tmp_path) if "action_logs" in f]
    assert files, "Arquivo de logs não foi criado!"
