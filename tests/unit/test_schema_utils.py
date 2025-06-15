# tests/unit/test_schema_utils.py

import pytest
import pandas as pd
import numpy as np

from src.data.data_libs import schema_utils

@pytest.fixture
def mock_feature_schema(tmp_path, monkeypatch):
    """
    Cria um schema fictício em disco para teste (compatível com path do schema_utils).
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    control_path = tmp_path / "feature_schema.json"
    schema_path = config_dir / "schema_v1.json"
    features = ["close", "rsi", "ema_20"]
    # Salva schema real
    schema_path.write_text(
        '{"all_features": ["close", "rsi", "ema_20"]}',
        encoding="utf-8"
    )
    # Salva arquivo de controle
    control_path.write_text(
        '{"schema_file": "schema_v1.json"}',
        encoding="utf-8"
    )
    # Patcha os paths default do módulo para o tmp_path e config_dir
    monkeypatch.setattr(schema_utils, "DEFAULT_SCHEMA_CONTROL", control_path)
    monkeypatch.setattr(schema_utils, "ROOT_DIR", tmp_path)
    yield features, control_path, schema_path

def test_load_feature_list_ok(mock_feature_schema):
    features, control_path, _ = mock_feature_schema
    feats = schema_utils.load_feature_list()
    assert feats == features

def test_align_dataframe_to_schema_ok(mock_feature_schema):
    features, *_ = mock_feature_schema
    # DF bagunçado, tipos variados
    df = pd.DataFrame({
        'rsi': [50, 60],
        'ema_20': [1.11, 1.12],
        'close': [1.2, 1.25],
        'extra': [99, 99], # coluna que não deveria entrar
    })
    aligned = schema_utils.align_dataframe_to_schema(df, features)
    assert list(aligned.columns) == features
    assert aligned.shape == (2, 3)
    assert all(aligned.dtypes == "float64")
    # Deve preencher np.nan se faltar coluna
    df_partial = pd.DataFrame({'rsi': [44, 55]})
    aligned2 = schema_utils.align_dataframe_to_schema(df_partial, features)
    assert set(aligned2.columns) == set(features)
    assert np.isnan(aligned2['close']).all()
    assert np.isnan(aligned2['ema_20']).all()

def test_validate_dataframe_schema_strict_pass(mock_feature_schema):
    features, *_ = mock_feature_schema
    df = pd.DataFrame({
        "close": [1.1, 1.2],
        "rsi": [50.0, 55.0],
        "ema_20": [1.15, 1.16]
    })
    # Força tipos errados só para garantir conversão
    df = df.astype("float64")
    assert schema_utils.validate_dataframe_schema(df, features, strict=True)

def test_validate_dataframe_schema_strict_fail_wrong_order(mock_feature_schema):
    features, *_ = mock_feature_schema
    df = pd.DataFrame({
        "rsi": [50, 55],
        "close": [1.2, 1.3],
        "ema_20": [1.15, 1.18]
    })
    df = df.astype("float64")
    result = schema_utils.validate_dataframe_schema(df, features, strict=True)
    assert result is False

def test_validate_dataframe_schema_strict_fail_dtype(mock_feature_schema):
    features, *_ = mock_feature_schema
    df = pd.DataFrame({
        "close": [1, 2],          # int, deveria ser float64
        "rsi": [50, 51],          # int
        "ema_20": [1.0, 2.0]      # ok
    })
    # Não converte int para float64
    assert not schema_utils.validate_dataframe_schema(df, features, strict=True)

def test_validate_dataframe_schema_non_strict(mock_feature_schema):
    features, *_ = mock_feature_schema
    df = pd.DataFrame({
        "rsi": [50.0, 60.0],
        "ema_20": [1.11, 1.12],
        "close": [1.2, 1.25],
        "col_extra": [99, 88]
    })
    # Ordem diferente, extra, todos float64
    assert not schema_utils.validate_dataframe_schema(df, features, strict=False)  # Falha (extra)
    # Remove a extra, muda dtype
    df2 = df[features].copy()
    df2["close"] = df2["close"].astype("int32")
    assert not schema_utils.validate_dataframe_schema(df2, features, strict=False)  # Falha (dtype)

def test_validate_dataframe_schema_raise_on_error(mock_feature_schema):
    features, *_ = mock_feature_schema
    df = pd.DataFrame({
        "rsi": [50, 60],
        "ema_20": [1.11, 1.12]
        # falta 'close'
    })
    # Alinha, mas falta coluna
    with pytest.raises(ValueError):
        schema_utils.validate_dataframe_schema(df, features, strict=False, raise_on_error=True)
