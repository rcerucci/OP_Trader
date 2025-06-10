import pytest
import numpy as np
import logging
import os

from src.env.wrappers.action_wrapper import ActionWrapper
from src.env.wrappers.reward_wrapper import RewardWrapper
from src.env.wrappers.normalization_wrapper import NormalizationWrapper
from src.env.wrappers.observation_wrapper import ObservationWrapper
from src.env.wrappers.logging_wrapper import LoggingWrapper

ACTION_MAP = {
    0: "buy",
    1: "hold",
    2: "sell",
    3: "close"
}

class DummyActionSpace:
    dtype = np.int64
    shape = ()
    def contains(self, x):
        try:
            return int(x) in ACTION_MAP
        except Exception:
            return False

class DummyEnvAllCases:
    def __init__(self, terminated_steps=[4, 8], truncated_step=10):
        self.action_space = DummyActionSpace()
        self.observation_space = type("Obs", (), {"shape": (2,)})()
        self.episode_steps = 0
        self.done = False
        self._rewards = [1.0, -1.0, 0.0, 5.0, -5.0]
        self._terminated_steps = terminated_steps
        self._truncated_step = truncated_step

    def reset(self, **kwargs):
        self.episode_steps = 0
        self.done = False
        return np.zeros((2,), dtype=np.float32), {"reset": True, "step": 0}

    def step(self, action):
        action = int(action)
        self.episode_steps += 1
        reward = self._rewards[self.episode_steps % len(self._rewards)]
        action_type = ACTION_MAP.get(action, "unknown")
        info = {
            "step": self.episode_steps,
            "custom_flag": bool(action == 3),
            "action_type": action_type,
            "pnl": float(reward * 100),
            "drawdown": float(-abs(reward * 10)),
            "logs": f"Step {self.episode_steps}, action={action} ({action_type})"
        }
        obs = np.ones((2,), dtype=np.float32) * self.episode_steps
        terminated = self.episode_steps in self._terminated_steps
        truncated = self.episode_steps >= self._truncated_step
        if terminated or truncated:
            self.done = True
        return obs, reward, terminated, truncated, info

    def close(self):
        pass

@pytest.fixture
def logger_full():
    logger = logging.getLogger("FullRLTestLogger")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(h)
    logger.propagate = True
    return logger

def make_wrapped_env(env, logger_full, tmp_path):
    return LoggingWrapper(
        RewardWrapper(
            ObservationWrapper(
                NormalizationWrapper(
                    ActionWrapper(
                        env,
                        action_fn=lambda a: int(a),
                        logger=logger_full,
                        log_dir=str(tmp_path)
                    ),
                    logger=logger_full
                ),
                obs_fn=lambda obs: obs / 10.0,
                logger=logger_full
            ),
            reward_fn=lambda r: r * 2,
            logger=logger_full,
            log_dir=str(tmp_path)
        ),
        logger=logger_full,
        log_level="DEBUG",
        log_dir=str(tmp_path),
    )

def test_pipeline_returns_all_cases(tmp_path, logger_full):
    # Episódio 1: termina por terminated (só após passar por todas as ações)
    env_term = DummyEnvAllCases(terminated_steps=[4], truncated_step=100)
    wrapped_term = make_wrapped_env(env_term, logger_full, tmp_path)

    obs, info = wrapped_term.reset()
    done = False
    steps = 0
    rewards, obs_arrays, terminateds, truncateds, infos, actions_semantics = [], [], [], [], [], []

    while not done and steps < 10:
        action = steps % 4
        obs, reward, terminated, truncated, info = wrapped_term.step(action)
        print(f"[TERM] Step={steps+1} | action={action} ({info['action_type']}) | reward={reward} | term={terminated} | trunc={truncated} | info={info}")
        rewards.append(reward)
        obs_arrays.append(obs)
        terminateds.append(terminated)
        truncateds.append(truncated)
        infos.append(info)
        actions_semantics.append(info["action_type"])
        steps += 1
        done = terminated or truncated

    assert any(terminateds), "Terminated nunca foi True!"
    assert not any(truncateds), "Não deveria truncar nesse episódio."
    assert set(actions_semantics) >= {"buy", "hold", "sell", "close"}

    # Episódio 2: termina por truncated
    env_trunc = DummyEnvAllCases(terminated_steps=[], truncated_step=5)
    wrapped_trunc = make_wrapped_env(env_trunc, logger_full, tmp_path)

    obs, info = wrapped_trunc.reset()
    done = False
    steps = 0
    rewards2, obs_arrays2, terminateds2, truncateds2, infos2, actions_semantics2 = [], [], [], [], [], []

    while not done and steps < 10:
        action = steps % 4
        obs, reward, terminated, truncated, info = wrapped_trunc.step(action)
        print(f"[TRUNC] Step={steps+1} | action={action} ({info['action_type']}) | reward={reward} | term={terminated} | trunc={truncated} | info={info}")
        rewards2.append(reward)
        obs_arrays2.append(obs)
        terminateds2.append(terminated)
        truncateds2.append(truncated)
        infos2.append(info)
        actions_semantics2.append(info["action_type"])
        steps += 1
        done = terminated or truncated

    assert not any(terminateds2), "Não deveria terminar por terminated nesse episódio."
    assert any(truncateds2), "Truncated nunca foi True!"
    assert set(actions_semantics2) >= {"buy", "hold", "sell", "close"}

    # Checagem universal para ambos
    for rewards, obs_arrays, infos in [(rewards, obs_arrays, infos), (rewards2, obs_arrays2, infos2)]:
        assert any(r > 0 for r in rewards)
        assert any(r < 0 for r in rewards)
        assert all(isinstance(o, np.ndarray) for o in obs_arrays)
        for info in infos:
            assert isinstance(info, dict)
            assert "step" in info
            assert "logs" in info
            assert "action_type" in info
            assert info["action_type"] in {"buy", "hold", "sell", "close"}
            assert "pnl" in info
            assert "drawdown" in info

    wrapped_term.save_logs()
    wrapped_trunc.save_logs()
    logs_saved = [f for f in os.listdir(tmp_path) if f.endswith(".csv") or f.endswith(".json")]
    assert logs_saved, "Nenhum log salvo!"
    wrapped_term.close()
    wrapped_trunc.close()
