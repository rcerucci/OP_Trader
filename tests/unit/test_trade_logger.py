import pytest
import os
from src.env.env_libs.trade_logger import TradeLogger

@pytest.fixture
def trade_logger(tmp_path):
    # tmp_path é um objeto pathlib.Path criado e limpo pelo pytest
    logger = TradeLogger(symbol="EURUSD", log_dir=str(tmp_path), debug=True)
    yield logger

def test_log_trade(trade_logger):
    trade_logger.log_trade({"action": "buy", "price": 1.105, "size": 1.0, "status": "opened", "trade_id": "uuid1"})
    logs = trade_logger.get_logs()
    assert logs["trade"]
    assert logs["trade"][0]["action"] == "buy"
    assert logs["trade"][0]["status"] == "opened"

def test_log_reward(trade_logger):
    trade_logger.log_reward({"reward": 15.0, "step": 10, "components": {"profit": 17.0, "penalty": -2.0}})
    logs = trade_logger.get_logs()
    assert logs["reward"]
    assert logs["reward"][0]["reward"] == 15.0

def test_log_context(trade_logger):
    trade_logger.log_context({"macro": "long", "regime": "bull"})
    logs = trade_logger.get_logs()
    assert logs["context"]
    assert logs["context"][0]["regime"] == "bull"

def test_save_logs_and_reset(trade_logger):
    # Gerar alguns logs
    trade_logger.log_trade({"action": "buy", "price": 1.1, "size": 1.0, "status": "opened", "trade_id": "t1"})
    trade_logger.log_reward({"reward": 10.0, "step": 5, "components": {"profit": 12.0, "penalty": -2.0}})
    trade_logger.log_context({"macro": "short", "regime": "bear"})
    # Salvar logs
    trade_logger.save_logs()
    # Verificar arquivos
    files = os.listdir(trade_logger.log_dir)
    print("Arquivos na pasta de logs:", files)  # Diagnóstico extra
    assert any("trade" in f and f.endswith(".csv") for f in files)
    assert any("reward" in f and f.endswith(".csv") for f in files)
    assert any("context" in f and f.endswith(".csv") for f in files)
    # Resetar logs
    trade_logger.reset()
    logs = trade_logger.get_logs()
    assert not logs["trade"] and not logs["reward"] and not logs["context"]

def test_event_malformed(trade_logger):
    # Falta campos obrigatórios
    trade_logger.log_trade({"price": 1.2, "size": 0.5})  # sem action/status
    logs = trade_logger.get_logs()
    assert logs["trade"][-1]["price"] == 1.2  # Ainda assim loga, mas com warning
