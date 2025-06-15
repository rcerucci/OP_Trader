# tests/unit/test_feature_engineer.py

import pytest
import pandas as pd
import numpy as np
import os

from src.data.data_libs.feature_engineer import FeatureEngineer

@pytest.fixture
def df_base():
    return pd.DataFrame({
        "datetime": pd.date_range("2024-01-01", periods=10, freq="D"),
        "open": np.linspace(1.10, 1.19, 10),
        "high": np.linspace(1.11, 1.21, 10),
        "low": np.linspace(1.09, 1.17, 10),
        "close": np.linspace(1.11, 1.18, 10),
        "volume": np.arange(1000, 1010),
        "time": np.arange(1700000000, 1700000010),
    })

def test_transform_ok_default_params(df_base):
    feats = [
        "ema_fast", "ema_slow", "rsi", "macd_hist", "atr", "bb_width", "return_pct",
        "candle_direction", "volume_relative", "pullback",
        "hammer_pattern", "inverted_hammer_pattern"
    ]
    eng = FeatureEngineer(features=feats, debug=True)
    df_out = eng.transform(df_base)
    for feat in feats:
        assert feat in df_out.columns
        assert df_out.shape[0] == df_base.shape[0]
    meta = eng.get_metadata()
    assert sorted(meta["features"]) == sorted(feats)
    assert "calculator_meta" in meta
    assert isinstance(meta["time_sec"], float)

def test_transform_explicit_params(df_base):
    params = {
        "ema_fast": {"window": 5},
        "pullback": {"window": 5},
        "rsi": {"window": 3},
        "volume_relative": {"window": 3}
    }
    feats = ["ema_fast", "pullback", "rsi", "volume_relative"]
    eng = FeatureEngineer(features=feats, params=params)
    df_out = eng.transform(df_base)
    for feat in feats:
        assert feat in df_out.columns

def test_transform_config_fallback(df_base):
    feats = ["ema_fast"]
    config = {"ema_fast": {"window": 3}}
    eng = FeatureEngineer(features=feats, config=config)
    df_out = eng.transform(df_base)
    assert "ema_fast" in df_out.columns

def test_transform_hierarquia_params(df_base):
    feats = ["ema_fast"]
    params = {"ema_fast": {"window": 5}}
    config = {"ema_fast": {"window": 10}}
    eng = FeatureEngineer(features=feats, params=params, config=config)
    df_out = eng.transform(df_base)
    # window=5 deve prevalecer (params > config)
    assert "ema_fast" in df_out.columns
    # Checa que o valor está diferente do default
    assert not np.allclose(df_out["ema_fast"], df_base["close"].ewm(span=20, adjust=False).mean())

def test_transform_empty_dataframe():
    eng = FeatureEngineer(features=["ema_fast"])
    with pytest.raises(ValueError):
        eng.transform(pd.DataFrame())

def test_transform_missing_feature(df_base):
    feats = ["ema_fast", "not_exists"]
    eng = FeatureEngineer(features=feats)
    df_out = eng.transform(df_base)
    assert "ema_fast" in df_out.columns
    assert "not_exists" not in df_out.columns

def test_metadata_content(df_base):
    feats = ["ema_fast", "rsi"]
    params = {"rsi": {"window": 2}}
    eng = FeatureEngineer(features=feats, params=params)
    df_out = eng.transform(df_base)
    meta = eng.get_metadata()
    assert meta["features"] == feats
    assert "calculator_meta" in meta
    assert "params" in meta
    assert meta["params"]["rsi"]["window"] == 2

def test_logging_param_sources(df_base, caplog):
    feats = ["ema_fast", "rsi"]
    params = {"ema_fast": {"window": 5}}
    config = {"rsi": {"window": 3}}
    eng = FeatureEngineer(features=feats, params=params, config=config, debug=True)
    eng._logger.propagate = True
    with caplog.at_level("DEBUG"):
        eng.transform(df_base)
        assert "Parâmetro explícito usado para 'ema_fast'" in caplog.text
        assert "Parâmetro do config dict usado para 'rsi'" in caplog.text
        assert "Usando default embutido" not in caplog.text
        
def test_preserva_colunas_originais(df_base):
    feats = ["ema_fast", "rsi"]
    eng = FeatureEngineer(features=feats)
    df_out = eng.transform(df_base)
    for col in ["open", "high", "low", "close", "volume", "datetime", "time"]:
        assert col in df_out.columns

def test_all_features_math_validation_with_logs(df_base, caplog):
    feats = [
        "ema_fast", "ema_slow", "rsi", "macd_hist", "atr", "bb_width", "return_pct",
        "candle_direction", "volume_relative", "pullback",
        "hammer_pattern", "inverted_hammer_pattern"
    ]
    eng = FeatureEngineer(features=feats, debug=True)
    eng._logger.propagate = True
    with caplog.at_level("DEBUG"):
        df_out = eng.transform(df_base)
        for feat in feats:
            assert feat in df_out.columns
        assert "Execução concluída" in caplog.text
        assert "Features solicitadas" in caplog.text
        assert "Parâmetros efetivos" in caplog.text
        
def test_integration_bigdata(tmp_path):
    """Smoke test com DataFrame grande para batch/real-time."""
    N = 2000
    np.random.seed(42)
    df = pd.DataFrame({
        "datetime": pd.date_range("2024-01-01", periods=N, freq="min"),
        "open": np.random.rand(N) + 1,
        "high": np.random.rand(N) + 1.1,
        "low":  np.random.rand(N) + 0.9,
        "close": np.random.rand(N) + 1,
        "volume": np.random.randint(50, 200, size=N),
        "time": np.arange(1700000000, 1700000000 + N),
    })
    feats = ["ema_fast", "rsi", "macd_hist", "candle_direction", "pullback"]
    eng = FeatureEngineer(features=feats, debug=True)
    df_out = eng.transform(df)
    assert df_out.shape[0] == N
    for feat in feats:
        assert feat in df_out.columns
    # Auditoria: salva csv para CI/CD
    out_path = tmp_path / "feature_engineer_bigdata_output.csv"
    df_out.to_csv(out_path, index=False)
    assert out_path.exists()
