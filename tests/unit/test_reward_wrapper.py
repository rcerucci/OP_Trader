import pytest
import gymnasium as gym
import numpy as np
from src.env.wrappers.reward_wrapper import RewardWrapper

class DummyEnv(gym.Env):
    """Ambiente RL mock para testes de reward."""
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

def clip_reward(reward):
    return max(min(reward, 1.0), -1.0)

def nan_reward(_):
    return float('nan')

@pytest.fixture
def temp_log_dir(tmp_path):
    log_dir = tmp_path / "reward_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir)

def test_reward_transformation_and_logging(temp_log_dir):
    env = DummyEnv()
    wrapper = RewardWrapper(env, reward_fn=clip_reward, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    done = False
    steps = 0
    while not done:
        obs, reward, terminated, truncated, info = wrapper.step(0)
        assert -1.0 <= reward <= 1.0
        steps += 1
        done = terminated or truncated
    logs = wrapper.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    wrapper.save_logs()
    wrapper.close()

def test_set_reward_fn_dynamic(temp_log_dir):
    env = DummyEnv()
    wrapper = RewardWrapper(env, log_dir=temp_log_dir, debug=True)
    wrapper.set_reward_fn(clip_reward)
    obs, info = wrapper.reset()
    _, reward, _, _, _ = wrapper.step(0)
    assert -1.0 <= reward <= 1.0
    wrapper.set_reward_fn(None)
    _, reward, _, _, _ = wrapper.step(0)
    assert reward > 0.0  # volta ao reward original
    wrapper.close()

def test_invalid_reward_fn_and_nan(temp_log_dir):
    env = DummyEnv()
    wrapper = RewardWrapper(env, reward_fn=nan_reward, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    _, reward, _, _, _ = wrapper.step(0)
    assert reward == 0.0  # reward NaN deve ser corrigido para zero
    wrapper.set_reward_fn(lambda x: 1/0)  # função que lança exceção
    _, reward, _, _, _ = wrapper.step(0)
    assert reward > 0.0  # deve cair para reward original
    wrapper.close()

def test_thread_safety(temp_log_dir):
    import threading
    env = DummyEnv()
    wrapper = RewardWrapper(env, reward_fn=clip_reward, log_dir=temp_log_dir, debug=True)
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
