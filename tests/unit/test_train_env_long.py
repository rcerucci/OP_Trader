import pytest
import numpy as np
from src.env.environments.train_env_long import TrainEnvLong

class DummyRiskManager:
    def evaluate(self, action_label, context):
        return {"risk_score": 1.0 if action_label == "buy" else 0.0}

class DummyPositionManager:
    def step(self, action_label):
        return {"position_status": "opened" if action_label == "buy" else "hold"}

class DummyRewardAggregator:
    def compute_reward(self, info):
        return 2.0 if info.get("action_label") == "buy" else 1.0

def test_train_env_long_reset_and_step_basic():
    env = TrainEnvLong(
        context_macro={"direction": "long"},
        risk_manager=DummyRiskManager(),
        position_manager=DummyPositionManager(),
        reward_aggregator=DummyRewardAggregator(),
        debug=True
    )
    obs, info = env.reset()
    assert isinstance(obs, np.ndarray)
    assert "context_macro" in info
    assert env.context_macro["direction"] == "long"

    obs2, reward, terminated, truncated, info = env.step(0)  # buy
    assert isinstance(obs2, np.ndarray)
    assert reward == 2.0
    assert not terminated
    assert info["action_label"] == "buy"
    assert "risk" in info and "position" in info

    obs3, reward, terminated, truncated, info = env.step(1)  # hold
    assert reward == 1.0
    assert not terminated
    assert info["action_label"] == "hold"

def test_train_env_long_invalid_action():
    env = TrainEnvLong(debug=True)
    env.reset()
    obs, reward, terminated, truncated, info = env.step(5)  # ação inválida
    assert terminated
    assert reward < 0
    assert "error" in info
    assert info["error"].startswith("Ação não permitida")

def test_train_env_long_logs():
    env = TrainEnvLong(debug=True)
    env.reset()
    env.step(0)
    logs = env.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    assert len(logs["episodes"]) >= 1

def test_train_env_long_context_macro_update():
    env = TrainEnvLong(debug=True)
    env.reset(context_macro={"direction": "long", "regime": "bull"})
    assert env.context_macro["regime"] == "bull"
    obs, info = env.reset()
    assert "regime" in info["context_macro"]
