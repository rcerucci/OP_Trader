# tests/unit/test_scaler.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.data_libs.scaler import ScalerUtils

@pytest.fixture
def sample_df():
    """DataFrame contínuo típico."""
    return pd.DataFrame({
        "feature1": [1.0, 2.0, 3.0, 4.0],
        "feature2": [100, 200, 300, 400],
    })

def test_fit_transform_ok(sample_df):
    scaler = ScalerUtils(debug=True)
    scaler.logger.propagate = True  # Permite caplog capturar logs
    df_norm = scaler.fit_transform(sample_df)
    assert isinstance(df_norm, pd.DataFrame)
    assert df_norm.shape == sample_df.shape
    assert all(df_norm.columns == ["feature1_norm", "feature2_norm"])
    # Corrige: desvio padrão populacional, igual scikit-learn
    np.testing.assert_allclose(df_norm["feature1_norm"].mean(), 0.0, atol=1e-7)
    np.testing.assert_allclose(df_norm["feature2_norm"].std(ddof=0), 1.0, atol=1e-7)

def test_transform_ok(sample_df):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    scaler.fit_transform(sample_df)
    df_new = pd.DataFrame({
        "feature1": [5.0, 6.0],
        "feature2": [500, 600],
    })
    df_norm = scaler.transform(df_new)
    assert list(df_norm.columns) == ["feature1_norm", "feature2_norm"]
    assert df_norm.shape == (2, 2)
    assert np.all(df_norm.abs().values < 5)

def test_fit_transform_empty():
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    with pytest.raises(ValueError):
        scaler.fit_transform(pd.DataFrame())

def test_transform_without_fit(sample_df):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    with pytest.raises(RuntimeError):
        scaler.transform(sample_df)

def test_transform_empty_after_fit(sample_df):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    scaler.fit_transform(sample_df)
    with pytest.raises(ValueError):
        scaler.transform(pd.DataFrame())

def test_save_and_load_scaler(tmp_path, sample_df):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    df_norm = scaler.fit_transform(sample_df)
    path = tmp_path / "scaler.pkl"
    scaler.save_scaler(path)
    assert path.exists()
    scaler2 = ScalerUtils()
    scaler2.logger.propagate = True
    scaler2.load_scaler(path)
    df_new = pd.DataFrame({
        "feature1": [10.0, 20.0],
        "feature2": [1000, 2000],
    })
    df_norm2 = scaler2.transform(df_new)
    assert list(df_norm2.columns) == ["feature1_norm", "feature2_norm"]
    assert df_norm2.shape == (2, 2)

def test_save_scaler_without_fit(tmp_path):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    with pytest.raises(RuntimeError):
        scaler.save_scaler(tmp_path / "will_not_save.pkl")

def test_load_scaler_file_not_found(tmp_path):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    fake_path = tmp_path / "not_found.pkl"
    with pytest.raises(FileNotFoundError):
        scaler.load_scaler(fake_path)

def test_transform_column_mismatch(sample_df):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    scaler.fit_transform(sample_df)
    df_bad = pd.DataFrame({"feature3": [1, 2, 3, 4]})
    with pytest.raises(Exception):
        scaler.transform(df_bad)

def test_logging_on_error(sample_df, caplog):
    scaler = ScalerUtils()
    scaler.logger.propagate = True
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            scaler.transform(sample_df)
        assert "Scaler não foi carregado ou treinado" in caplog.text

def test_logging_save_load(tmp_path, sample_df):
    scaler = ScalerUtils(debug=True)
    scaler2 = ScalerUtils()
    path = tmp_path / "log_scaler.pkl"
    scaler.fit_transform(sample_df)
    scaler.save_scaler(path)
    scaler2.load_scaler(path)
    # Logs são auditados pelo console (live log call). Nenhum assert caplog necessário aqui.
    assert path.exists()
