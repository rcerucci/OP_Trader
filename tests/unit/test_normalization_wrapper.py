import pytest
import gymnasium as gym
import numpy as np
import tempfile
import os
from src.env.wrappers.normalization_wrapper import NormalizationWrapper

class DummyEnv(gym.Env):
    """Ambiente RL simples e determinístico."""
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(2)
        self._step = 0

    def reset(self, **kwargs):
        self._step = 0
        return np.array([0.5, 0.2], dtype=np.float32), {"reset": True}

    def step(self, action):
        self._step += 1
        obs = np.array([0.5 + 0.1 * self._step, 0.2 + 0.05 * self._step], dtype=np.float32)
        reward = float(self._step)
        terminated = self._step >= 3
        truncated = False
        info = {"custom": self._step}
        return obs, reward, terminated, truncated, info

    def close(self):
        pass

@pytest.fixture
def temp_norm_path(tmp_path):
    return str(tmp_path / "vecnorm.pkl")

def test_z_score_normalization(temp_norm_path):
    env = DummyEnv()
    norm_env = NormalizationWrapper(env, norm_type="z_score", save_path=temp_norm_path, debug=True)
    obs, info = norm_env.reset()
    assert isinstance(obs, np.ndarray)
    obs2, reward, terminated, truncated, info = norm_env.step(1)
    assert obs2.shape == (2,)
    _ = norm_env.step(1)
    _ = norm_env.step(1)
    norm_env.save_norm_state()
    norm_params = norm_env.get_norm_params()
    assert norm_params["norm_type"] == "z_score"
    assert norm_params["n_steps"] > 0
    norm_env.close()

def test_minmax_normalization():
    env = DummyEnv()
    norm_env = NormalizationWrapper(env, norm_type="minmax", debug=True)
    obs, info = norm_env.reset()
    for _ in range(3):
        obs, reward, terminated, truncated, info = norm_env.step(1)
    params = norm_env.get_norm_params()
    assert params["norm_type"] == "minmax"
    assert params["obs_min"] is not None and params["obs_max"] is not None
    norm_env.close()

def test_vecnorm_state_persistence(temp_norm_path):
    # Apenas testa persistência da chamada dos métodos (não depende do VecNormalize real)
    env = DummyEnv()
    norm_env = NormalizationWrapper(env, norm_type="vecnorm", save_path=temp_norm_path, debug=True)
    obs, info = norm_env.reset()
    for _ in range(2):
        obs, reward, terminated, truncated, info = norm_env.step(1)
    norm_env.save_norm_state()
    # Simula recarregamento (não falha se o arquivo não existir)
    norm_env.load_norm_state()
    norm_env.close()

def test_thread_safety(temp_norm_path):
    import threading
    env = DummyEnv()
    norm_env = NormalizationWrapper(env, norm_type="z_score", save_path=temp_norm_path, debug=True)
    obs, info = norm_env.reset()

    def worker():
        for _ in range(2):
            norm_env.step(1)
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    params = norm_env.get_norm_params()
    assert params["n_steps"] >= 6
    norm_env.close()
