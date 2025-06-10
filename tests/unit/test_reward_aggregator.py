import pytest
from src.env.env_libs.reward_aggregator import RewardAggregator

def profit_reward(state_before, action, state_after):
    return state_after["portfolio_value"] - state_before["portfolio_value"]

def penalty_reward(state_before, action, state_after):
    return -1.0 if action.get("type") == "invalid" else 0.0

@pytest.fixture
def ra():
    return RewardAggregator(
        reward_components=[profit_reward, penalty_reward],
        weights={"profit_reward": 0.7, "penalty_reward": 0.3},
        normalization="none",
        logger=None,
        debug=True
    )

def test_calculate_reward_basic(ra):
    s0 = {"portfolio_value": 100.0}
    a = {"type": "hold"}
    s1 = {"portfolio_value": 110.0}
    r = ra.calculate_reward(s0, a, s1)
    breakdown = ra.get_reward_breakdown()
    assert "profit_reward" in breakdown
    assert "penalty_reward" in breakdown
    assert breakdown["profit_reward"]["value"] == 10.0
    assert breakdown["penalty_reward"]["value"] == 0.0
    assert breakdown["total"] == pytest.approx(7.0)
    assert r == pytest.approx(7.0)

def test_calculate_reward_with_penalty(ra):
    s0 = {"portfolio_value": 100.0}
    a = {"type": "invalid"}
    s1 = {"portfolio_value": 100.0}
    r = ra.calculate_reward(s0, a, s1)
    breakdown = ra.get_reward_breakdown()
    assert breakdown["penalty_reward"]["value"] == -1.0

def test_add_component(ra):
    def custom_comp(s0, a, s1): return 5.0
    ra.add_component("custom", custom_comp, weight=2.0)
    s0, a, s1 = {}, {}, {}
    r = ra.calculate_reward(s0, a, s1)
    breakdown = ra.get_reward_breakdown()
    assert "custom" in breakdown
    assert breakdown["custom"]["weight"] == 2.0

def test_reset(ra):
    ra.reset()
    assert ra._last_breakdown is None
    assert ra._reward_history == []

def test_save_breakdown(tmp_path):
    ra = RewardAggregator(reward_components=[profit_reward])
    s0, a, s1 = {"portfolio_value": 1.0}, {}, {"portfolio_value": 2.0}
    ra.calculate_reward(s0, a, s1)
    ra.save_breakdown(path=str(tmp_path))
    files = list(tmp_path.iterdir())
    assert any("reward_breakdown" in f.name for f in files)
