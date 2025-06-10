import pytest
from src.env.env_libs.position_manager import PositionManager

class DummyRiskManager:
    def validate_order(self, symbol, action, size, price, context=None):
        if size > 2.0:
            return {"status": "rejected", "reason": "Size too large"}
        return {"status": "approved"}
    def update_risk_metrics(self, trade_result):
        pass

@pytest.fixture
def pm():
    return PositionManager(symbol="EURUSD", risk_manager=DummyRiskManager(), logger=None, debug=True)

def test_open_and_close(pm):
    res = pm.open_position("buy", 1.10, 1.0)
    assert res["status"] == "opened"
    assert pm.get_current_position() is not None
    res2 = pm.close_position(1.15)
    assert res2["status"] == "closed"
    assert pm.get_current_position() is None

def test_open_with_existing_position(pm):
    pm.open_position("buy", 1.10, 1.0)
    res = pm.open_position("buy", 1.12, 1.0)
    assert res["status"] == "rejected"

def test_open_invalid_params(pm):
    with pytest.raises(ValueError):
        pm.open_position("", 1.10, 1.0)
    with pytest.raises(ValueError):
        pm.open_position("buy", 0, 1.0)
    with pytest.raises(ValueError):
        pm.open_position("buy", 1.10, -2.0)

def test_close_without_position(pm):
    res = pm.close_position(1.10)
    assert res["status"] == "no_position"

def test_risk_manager_reject(pm):
    res = pm.open_position("buy", 1.10, 5.0)
    assert res["status"] == "rejected"

def test_reset(pm):
    pm.open_position("buy", 1.10, 1.0)
    pm.close_position(1.12)
    pm.reset()
    assert pm.get_current_position() is None
    assert pm.history == []

def test_save_snapshot(tmp_path):
    pm = PositionManager(symbol="EURUSD", logger=None)
    pm.open_position("buy", 1.10, 1.0)
    pm.close_position(1.13)
    pm.save_snapshot(path=str(tmp_path))
    import os
    files = os.listdir(tmp_path)
    assert any("position_snapshot" in f for f in files)
