# tests/unit/test_mt5_connector.py

import os
from pathlib import Path
from dotenv import load_dotenv

import pytest
import pandas as pd
from src.data.data_libs.mt5_connector import MT5Connector
from src.utils.mt5_connection import close_mt5_connection

COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'time']

# Carrega .env robusto
cur_path = Path(__file__).resolve()
for parent in [cur_path] + list(cur_path.parents):
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        break

@pytest.mark.skipif(
    os.environ.get("MT5_LOGIN") is None,
    reason="Credenciais do MT5 não configuradas no ambiente (.env)."
)
def test_connect_and_close():
    conn = MT5Connector(debug=True)
    assert conn.connect() is True
    close_mt5_connection()

@pytest.mark.skipif(
    os.environ.get("MT5_LOGIN") is None,
    reason="Credenciais do MT5 não configuradas no ambiente (.env)."
)
def test_collect_batch_ohlcv():
    conn = MT5Connector(debug=True)
    conn.connect()
    df, decimals = conn.collect(
        symbol="EURUSD",
        timeframe="M5",
        start_date="2023-01-01",
        end_date="2023-01-02",
        data_type="ohlcv"
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(decimals, int) and decimals > 0
    assert list(df.columns) == COLUMNS_REQUIRED
    assert not df.empty
    assert pd.api.types.is_datetime64_any_dtype(df["datetime"])
    assert pd.api.types.is_numeric_dtype(df["open"])
    assert pd.api.types.is_numeric_dtype(df["volume"])
    close_mt5_connection()

@pytest.mark.skipif(
    os.environ.get("MT5_LOGIN") is None,
    reason="Credenciais do MT5 não configuradas no ambiente (.env)."
)
def test_collect_batch_tick():
    conn = MT5Connector(debug=True)
    conn.connect()
    df, decimals = conn.collect(
        symbol="EURUSD",
        timeframe="M1",
        start_date="2023-01-01",
        end_date="2023-01-01",
        data_type="tick"
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(decimals, int) and decimals > 0
    assert list(df.columns) == COLUMNS_REQUIRED
    close_mt5_connection()

def test_streaming_callback_called(monkeypatch):
    # Simula streaming: método público on_new_data + dummy collect
    called = {}
    def fake_connect(self):
        return True
    def fake_collect(self, symbol, timeframe, start_date=None, end_date=None, data_type="ohlcv", **kwargs):
        df = pd.DataFrame({
            "datetime": pd.date_range("2023-01-01", periods=2, freq="5min"),
            "open": [1.0, 1.1], "high": [1.2, 1.3], "low": [0.9, 1.0],
            "close": [1.05, 1.15], "volume": [100, 101], "time": [1672531200, 1672531500]
        })
        if hasattr(self, "_callback") and self._callback:
            self._callback(df)
        return df, 5
    monkeypatch.setattr(MT5Connector, "connect", fake_connect)
    monkeypatch.setattr(MT5Connector, "collect", fake_collect)
    conn = MT5Connector(debug=True, mode="streaming")
    def cb(df):
        assert list(df.columns) == COLUMNS_REQUIRED
        called["ok"] = True
    conn.on_new_data(cb)
    conn.collect("EURUSD", "M1", data_type="ohlcv")
    assert called.get("ok") is True

def test_fallback_volume_sources(monkeypatch):
    # Testa fallback e erro crítico se mais de um campo de volume é válido
    df_mock = pd.DataFrame({
        "datetime": pd.date_range("2023-01-01", periods=2, freq="5min"),
        "open": [1.0, 1.1], "high": [1.2, 1.3], "low": [0.9, 1.0], "close": [1.05, 1.15],
        "tick_volume": [100, 101], "real_volume": [100, 102],  # AMBOS válidos
        "time": [1672531200, 1672531500]
    })
    class FakeMT5:
        @staticmethod
        def symbol_info(symbol):
            class Info: digits = 5
            return Info()
    monkeypatch.setattr("src.data.data_libs.mt5_connector.mt5", FakeMT5())
    conn = MT5Connector(debug=True, volume_sources=['real_volume', 'tick_volume'])
    result = conn._standardize_columns(df_mock)
    assert result.empty

def test_no_valid_volume(monkeypatch):
    df_mock = pd.DataFrame({
        "datetime": pd.date_range("2023-01-01", periods=2, freq="5min"),
        "open": [1.0, 1.1], "high": [1.2, 1.3], "low": [0.9, 1.0], "close": [1.05, 1.15],
        "tick_volume": [0, 0], "real_volume": [0, 0],
        "time": [1672531200, 1672531500]
    })
    class FakeMT5:
        @staticmethod
        def symbol_info(symbol):
            class Info: digits = 5
            return Info()
    monkeypatch.setattr("src.data.data_libs.mt5_connector.mt5", FakeMT5())
    conn = MT5Connector(debug=True, volume_sources=['real_volume', 'tick_volume'])
    result = conn._standardize_columns(df_mock)
    assert result.empty
