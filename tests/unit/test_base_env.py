import pytest
import numpy as np
from src.env.environments.base_env import BaseEnv

class DummyRiskManager:
    def evaluate(self, action_label, context):
        return {"risk_score": 0.42, "action": action_label, "context": context}

class DummyPositionManager:
    def step(self, action_label):
        return {"position_status": "opened", "action": action_label}

class DummyRewardAggregator:
    def compute_reward(self, info):
        return 1.23 + (0.1 if "risk" in info else 0.0)

def test_base_env_reset_and_step_basic():
    env = BaseEnv(
        allowed_actions=["buy", "hold"],
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

    obs2, reward, terminated, truncated, info = env.step(0)
    assert isinstance(obs2, np.ndarray)
    assert reward > 1.0
    assert not terminated
    assert "risk" in info and "position" in info

def test_base_env_set_context_macro_and_logging():
    env = BaseEnv(allowed_actions=["buy", "sell"], debug=True)
    env.set_context_macro({"direction": "short", "strength": 5})
    assert env.context_macro["direction"] == "short"
    obs, info = env.reset()
    assert info["context_macro"]["direction"] == "short"

def test_base_env_invalid_action():
    env = BaseEnv(allowed_actions=["buy", "hold"], debug=True)
    obs, info = env.reset()
    obs2, reward, terminated, truncated, info = env.step(999)  # ação inválida
    assert terminated
    assert reward < 0
    assert "error" in info

def test_base_env_logs():
    env = BaseEnv(allowed_actions=["buy", "hold"], debug=True)
    env.reset()
    env.step(0)
    logs = env.get_logs()
    assert isinstance(logs, dict)
    assert "episodes" in logs
    assert len(logs["episodes"]) >= 1
