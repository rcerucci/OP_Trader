import pytest
from src.env.env_libs.risk_manager import RiskManager

@pytest.fixture
def risk_manager(tmp_path):
    return RiskManager(config_path=None, logger=None, debug=True)

def test_validate_order_limits(risk_manager):
    # Exposição acima do limite
    result = risk_manager.validate_order("EURUSD", "buy", 10.0, 1.0)
    assert result["status"] == "rejected"
    assert "Exposição" in result["reason"]

def test_validate_order_risk(risk_manager):
    # Risco acima do permitido
    result = risk_manager.validate_order("EURUSD", "buy", 1.0, 10000.0, context={"portfolio_value": 1000})
    assert result["status"] == "rejected"
    assert "Risco" in result["reason"]

def test_validate_order_drawdown(risk_manager):
    # Drawdown acima do permitido
    result = risk_manager.validate_order("EURUSD", "buy", 1.0, 1.0, context={"drawdown": 1.0})
    assert result["status"] == "rejected"
    assert "Drawdown" in result["reason"]

def test_validate_order_sl_tp_invalid(risk_manager):
    # SL/TP inválido
    result = risk_manager.validate_order("EURUSD", "buy", 1.0, 1.0, context={"stop_loss": -5})
    assert result["status"] == "rejected"
    result2 = risk_manager.validate_order("EURUSD", "buy", 1.0, 1.0, context={"take_profit": -10})
    assert result2["status"] == "rejected"

def test_check_risk_limits(risk_manager):
    alerts = risk_manager.check_risk_limits({"drawdown": 0.5, "exposure": 6.0})
    assert "drawdown" in alerts
    assert "exposure" in alerts

def test_calculate_position_size(risk_manager):
    size = risk_manager.calculate_position_size("EURUSD", 0.01, 10000, context={"stop_loss": 50})
    assert size > 0

def test_update_and_get_metrics(risk_manager):
    risk_manager.update_risk_metrics({"pnl": 100, "drawdown": 0.2})
    snap = risk_manager.get_current_limits()
    assert snap["metrics"]["cum_pnl"] == 100.0
    assert snap["metrics"]["drawdown"] == 0.2

def test_reset(risk_manager):
    risk_manager.update_risk_metrics({"pnl": 100, "drawdown": 0.2})
    risk_manager.reset()
    snap = risk_manager.get_current_limits()
    assert snap["metrics"]["cum_pnl"] == 0.0
    assert snap["metrics"]["drawdown"] == 0.0

def test_save_snapshot(tmp_path):
    import os
    rm = RiskManager()
    rm.update_risk_metrics({"pnl": 100, "drawdown": 0.3})
    rm.save_snapshot(path=str(tmp_path))
    files = os.listdir(tmp_path)
    assert any("risk_snapshot" in f for f in files)
