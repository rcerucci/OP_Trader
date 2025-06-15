import pytest
import numpy as np
import pandas as pd
import os
from src.data.data_libs.feature_calculator import FeatureCalculator

@pytest.fixture(scope="module")
def df_big():
    """Gera um DataFrame simulado grande (10.000 linhas) para teste massivo."""
    N = 10_000
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=N, freq="min")
    price_base = 100 + np.cumsum(np.random.normal(0, 0.05, size=N))
    df = pd.DataFrame({
        "datetime": dates,
        "open": price_base + np.random.uniform(-0.03, 0.03, size=N),
        "high": price_base + np.random.uniform(0, 0.07, size=N),
        "low": price_base - np.random.uniform(0, 0.07, size=N),
        "close": price_base + np.random.uniform(-0.03, 0.03, size=N),
        "volume": np.random.randint(1000, 5000, size=N),
        "time": np.arange(1700000000, 1700000000 + N),
    })
    return df

def test_feature_calculator_bigdata(df_big, tmp_path, caplog):
    """
    Testa o FeatureCalculator em um DataFrame grande (10.000 candles).
    Valida:
    - Execução sem erro
    - Todas as features presentes
    - Shape correto
    - Sem NaN indevidos após warmup das janelas
    - Salva CSV para auditoria
    - Logging detalhado
    """
    features = [
        "ema_fast", "ema_slow", "rsi", "macd_hist", "atr", "bb_width", "return_pct",
        "candle_direction", "volume_relative", "pullback",
        "hammer_pattern", "inverted_hammer_pattern"
    ]
    caplog.set_level("DEBUG", logger="op_trader.feature_calculator")
    calc = FeatureCalculator(debug=True)
    df_out = calc.calculate_all(df_big, features=features)

    # Check shape
    assert df_out.shape[0] == df_big.shape[0]
    for feat in features:
        assert feat in df_out.columns

    # Após o warmup (window máximo: 50), os NaNs devem ser só nas primeiras linhas
    warmup = 60
    df_valid = df_out.iloc[warmup:]
    for feat in features:
        # Aceita NaN apenas se rolling exige, e só no começo
        nan_count = df_valid[feat].isna().sum()
        assert nan_count < 2, f"{feat} tem {nan_count} NaNs após warmup"

    # Estatísticas rápidas (pode customizar ou comentar se desejar)
    print(df_out[features].describe().T)

    # Salva output para auditoria
    output_path = tmp_path / "feature_calculator_bigdata_output.csv"
    df_out.to_csv(output_path, index=False)
    print(f"\nArquivo de output salvo: {output_path}")

    # Logging: deve haver pelo menos um log de cálculo por feature
    for feat in features:
        assert f"Cálculo '{feat}'" in caplog.text, f"Sem log para '{feat}'"

    # Verificação extra: logging de conclusão
    assert "Features calculadas" in caplog.text

    # Opcional: print das primeiras e últimas linhas
    print("Primeiras linhas calculadas:\n", df_out.head(5)[features])
    print("Últimas linhas calculadas:\n", df_out.tail(5)[features])

