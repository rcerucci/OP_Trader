import pytest
import numpy as np
from src.env.environments.train_env_short import TrainEnvShort

class DummyRiskManager:
    def evaluate(self, action_label, context):
        return {"risk_score": 1.0 if action_label == "sell" else 0.0}

class DummyPositionManager:
    def step(self, action_label):
        return {"position_status": "opened" if action_label == "sell" else "hold"}

class DummyRewardAggregator:
    def compute_reward(self, info):
        return 2.0 if info.get("action_label") == "sell" else 1.0

def test_train_env_short_reset_and_step_basic():
    env = TrainEnvShort(
        context_macro={"direction": "short"},
        risk_manager=DummyRiskManager(),
        position_manager=DummyPositionManager(),
        reward_aggregator=DummyRewardAggregator(),
        debug=True
    )
    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    assert "context_macro" in info
    assert env.context_macro["direction"] == "short"

    obs2, reward, terminated, truncated, info = env.step(0)  # sell
    assert isinstance(obs2, np.ndarray)
    assert reward == 2.0
    assert not terminated
    assert info["action_label"] == "sell"
    assert "risk" in info and "position" in info

    obs3, reward, terminated, truncated, info = env.step(1)  # hold
    assert reward == 1.0
    assert not terminated
    assert info["action_label"] == "hold"

def test_train_env_short_invalid_action():
    env = TrainEnvShort(debug=True)
    env.reset()
    obs, reward, terminated, truncated, info = env.step(5)  # ação inválida
    assert terminated
    assert reward < 0
    assert "error" in info
    assert info["error"].startswith("Ação não permitida")

def test_train_env_short_logs():
    env = TrainEnvShort(debug=True)
    env.reset()
    env.step(0)
    logs = env.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    assert len(logs["episodes"]) >= 1

def test_train_env_short_context_macro_update():
    env = TrainEnvShort(debug=True)
    env.reset(context_macro={"direction": "short", "regime": "bear"})
    assert env.context_macro["regime"] == "bear"
    obs, info = env.reset()
    assert "regime" in info["context_macro"]
