# tests/unit/test_registry.py

from src.data.data_libs.registry import BROKER_CONNECTORS
from src.data.data_libs.mt5_connector import MT5Connector

def test_mt5_connector_registry():
    assert "mt5" in BROKER_CONNECTORS
    assert BROKER_CONNECTORS["mt5"] == MT5Connector

# Simule registro de novo broker (exemplo, para demonstrar extensão)
def test_add_fake_broker(monkeypatch):
    class FakeBrokerConnector:
        pass
    BROKER_CONNECTORS["fake"] = FakeBrokerConnector
    assert "fake" in BROKER_CONNECTORS
    assert BROKER_CONNECTORS["fake"] == FakeBrokerConnector
