import pytest
import gymnasium as gym
import numpy as np
from src.env.wrappers.observation_wrapper import ObservationWrapper

class DummyEnv(gym.Env):
    """Ambiente RL mock para teste de observação."""
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

def mask_obs(obs):
    arr = np.array(obs, copy=True)
    arr[0] = 0.0
    return arr

def nan_obs(_):
    return np.array([np.nan, np.nan])

@pytest.fixture
def temp_log_dir(tmp_path):
    log_dir = tmp_path / "observation_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir)

def test_observation_transformation_and_logging(temp_log_dir):
    env = DummyEnv()
    wrapper = ObservationWrapper(env, obs_fn=mask_obs, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    assert obs[0] == 0.0
    done = False
    while not done:
        obs, reward, terminated, truncated, info = wrapper.step(0)
        assert obs[0] == 0.0
        done = terminated or truncated
    logs = wrapper.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    wrapper.save_logs()
    wrapper.close()

def test_set_obs_fn_dynamic(temp_log_dir):
    env = DummyEnv()
    wrapper = ObservationWrapper(env, log_dir=temp_log_dir, debug=True)
    wrapper.set_obs_fn(mask_obs)
    obs, info = wrapper.reset()
    assert obs[0] == 0.0
    wrapper.set_obs_fn(None)
    obs, info = wrapper.reset()
    assert obs[0] != 0.0
    wrapper.close()

def test_invalid_obs_fn_and_nan(temp_log_dir):
    env = DummyEnv()
    wrapper = ObservationWrapper(env, obs_fn=nan_obs, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    # Deve usar obs original por causa do NaN
    assert obs[0] == 0.5
    wrapper.set_obs_fn(lambda x: 1/0)  # função que lança exceção
    obs, info = wrapper.reset()
    assert obs[0] == 0.5
    wrapper.close()

def test_thread_safety(temp_log_dir):
    import threading
    env = DummyEnv()
    wrapper = ObservationWrapper(env, obs_fn=mask_obs, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    def worker():
        for _ in range(2):
            wrapper.step(0)
    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    logs = wrapper.get_logs()
    assert len(logs["episodes"][0]) >= 7
    wrapper.close()
