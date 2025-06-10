import pytest
import gymnasium as gym
import os
from src.env.wrappers.logging_wrapper import LoggingWrapper

class DummyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Discrete(2)
        self.action_space = gym.spaces.Discrete(2)
        self._step = 0

    def reset(self, **kwargs):
        self._step = 0
        return 0, {"reset": True}

    def step(self, action):
        self._step += 1
        obs = self._step % 2
        reward = 1.0
        terminated = self._step >= 3
        truncated = False
        info = {"custom": self._step}
        return obs, reward, terminated, truncated, info

    def close(self):
        pass

@pytest.fixture
def temp_log_dir(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir)

def test_logging_wrapper_step_and_reset(temp_log_dir):
    env = DummyEnv()
    wrapper = LoggingWrapper(env, log_level="DEBUG", log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    done = False
    steps = 0
    while not done:
        action = 1
        obs, reward, terminated, truncated, info = wrapper.step(action)
        done = terminated or truncated
        steps += 1
    assert steps == 3
    logs = wrapper.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    assert len(logs["episodes"]) >= 1
    wrapper.save_logs()
    files = os.listdir(temp_log_dir)
    assert any(f.endswith(".csv") for f in files)
    assert any(f.endswith(".json") for f in files)
    wrapper.close()

def test_log_event_and_error_handling(temp_log_dir):
    env = DummyEnv()
    wrapper = LoggingWrapper(env, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()
    wrapper.log_event("custom_event", {"msg": "Teste de evento"})
    logs = wrapper.get_logs()
    assert any(entry["event"] == "custom_event" for entry in logs["episodes"][0])
    wrapper.log_event("bad_event", None)  # Evento malformado, loga warning, não deve quebrar
    wrapper.close()

def test_thread_safety(temp_log_dir):
    import threading
    env = DummyEnv()
    wrapper = LoggingWrapper(env, log_dir=temp_log_dir, debug=True)
    obs, info = wrapper.reset()

    def worker():
        for _ in range(2):
            wrapper.step(1)
            wrapper.log_event("parallel", {"ok": True})

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logs = wrapper.get_logs()
    assert len(logs["episodes"][0]) >= 6
    wrapper.close()
