import pytest
import pandas as pd
import numpy as np
import os
import logging
from src.data.data_libs.feature_calculator import FeatureCalculator

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

def test_calculate_all_ok(df_base):
    calc = FeatureCalculator(debug=True)
    features = [
        "ema_fast", "ema_slow", "rsi", "macd_hist", "atr", "bb_width", "return_pct",
        "candle_direction", "volume_relative", "pullback",
        "hammer_pattern", "inverted_hammer_pattern"
    ]
    df_out = calc.calculate_all(df_base, features=features)
    for feat in features:
        assert feat in df_out.columns
        assert df_out.shape[0] == df_base.shape[0]
    meta = calc.get_last_metadata()
    assert sorted(meta["features"]) == sorted(features)

def test_calculate_with_params(df_base):
    calc = FeatureCalculator()
    params = {
        "ema_fast": {"window": 5},
        "pullback": {"window": 5},
        "rsi": {"window": 3},
        "volume_relative": {"window": 3}
    }
    df_out = calc.calculate_all(df_base, features=["ema_fast", "pullback", "rsi", "volume_relative"], params=params)
    assert "ema_fast" in df_out.columns
    assert "pullback" in df_out.columns
    assert "rsi" in df_out.columns
    assert "volume_relative" in df_out.columns

def test_pullback_and_ema_fast_sync(df_base):
    calc = FeatureCalculator()
    params = {"ema_fast": {"window": 8}, "pullback": {"window": 8}}
    df_out = calc.calculate_all(df_base, features=["ema_fast", "pullback"], params=params)
    ema = df_out["ema_fast"]
    pullback = df_out["pullback"]
    expected = (df_base["close"] - ema) / ema
    pd.testing.assert_series_equal(pullback, expected, check_names=False, rtol=1e-10)

def test_missing_column_raises(df_base):
    calc = FeatureCalculator()
    df_wrong = df_base.drop(columns=["close"])
    with pytest.raises(KeyError):
        calc.calculate_all(df_wrong, features=["rsi"])

def test_feature_not_supported(df_base):
    calc = FeatureCalculator()
    df_out = calc.calculate_all(df_base, features=["not_exists", "ema_fast"])
    assert "ema_fast" in df_out.columns
    assert "not_exists" not in df_out.columns

def test_empty_dataframe():
    calc = FeatureCalculator()
    with pytest.raises(ValueError):
        calc.calculate_all(pd.DataFrame(), features=["ema_fast"])

def test_plugin_registration(df_base):
    calc = FeatureCalculator()
    def feat_fake(df, param=1):
        return df["close"] * param
    FeatureCalculator.register_feature("fake", feat_fake)
    df_out = calc.calculate_all(df_base, features=["fake"], params={"fake": {"param": 2}})
    assert "fake" in df_out.columns
    assert all(df_out["fake"] == df_base["close"] * 2)

def test_list_features(df_base):
    calc = FeatureCalculator()
    feats = calc.list_available_features()
    assert isinstance(feats, list)
    assert "rsi" in feats
    assert "ema_fast" in feats
    assert "pullback" in feats
    assert "volume_relative" in feats

def test_all_features_math_validation_with_logs(df_base, caplog):
    """
    Valida matematicamente todos os cálculos do FeatureCalculator com pandas/numpy puro,
    garante emissão dos logs DEBUG/INFO do cálculo, imprime e salva o DataFrame calculado.
    """
    # Ativa o caplog corretamente para o logger do projeto!
    with caplog.at_level("DEBUG", logger="op_trader.feature_calculator"):
        calc = FeatureCalculator(debug=True)
        features = [
            "ema_fast", "ema_slow", "rsi", "macd_hist", "atr", "bb_width", "return_pct",
            "candle_direction", "volume_relative", "pullback",
            "hammer_pattern", "inverted_hammer_pattern"
        ]
        df_out = calc.calculate_all(df_base, features=features)
        # Checagem dos logs principais
        for feat in features:
            assert f"Cálculo '{feat}'" in caplog.text, f"Sem log para '{feat}'"
        assert "Features calculadas:" in caplog.text

        print("\nDataFrame calculado pelo FeatureCalculator:")
        print(df_out)

        os.makedirs("logs", exist_ok=True)
        df_out.to_csv("logs/feature_calculator_output.csv", index=False)

        ema_fast = df_base["close"].ewm(span=20, adjust=False).mean()
        np.testing.assert_allclose(df_out["ema_fast"].fillna(0), ema_fast.fillna(0), atol=1e-8, err_msg="ema_fast inválido")

        ema_slow = df_base["close"].ewm(span=50, adjust=False).mean()
        np.testing.assert_allclose(df_out["ema_slow"].fillna(0), ema_slow.fillna(0), atol=1e-8, err_msg="ema_slow inválido")

        window = 14
        delta = df_base["close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        np.testing.assert_allclose(df_out["rsi"].dropna(), rsi.dropna(), rtol=1e-8, err_msg="rsi inválido")

        ema_12 = df_base["close"].ewm(span=12, adjust=False).mean()
        ema_26 = df_base["close"].ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line
        np.testing.assert_allclose(df_out["macd_hist"].dropna(), macd_hist.dropna(), rtol=1e-8, err_msg="macd_hist inválido")

        window = 14
        high = df_base["high"]
        low = df_base["low"]
        close_prev = df_base["close"].shift(1)
        tr1 = high - low
        tr2 = (high - close_prev).abs()
        tr3 = (low - close_prev).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=window, min_periods=window).mean()
        np.testing.assert_allclose(df_out["atr"].dropna(), atr.dropna(), rtol=1e-8, err_msg="atr inválido")

        window = 20
        sma = df_base["close"].rolling(window=window, min_periods=window).mean()
        std = df_base["close"].rolling(window=window, min_periods=window).std()
        upper = sma + 2 * std
        lower = sma - 2 * std
        bb_width = upper - lower
        np.testing.assert_allclose(df_out["bb_width"].fillna(0), bb_width.fillna(0), rtol=1e-8, err_msg="bb_width inválido")

        returns = df_base["close"].pct_change()
        np.testing.assert_allclose(df_out["return_pct"].fillna(0), returns.fillna(0), rtol=1e-8, err_msg="return_pct inválido")

        diff = df_base["close"] - df_base["open"]
        expected_direction = diff.apply(lambda x: 1.0 if x > 0 else (-1.0 if x < 0 else 0.0))
        assert all(df_out["candle_direction"] == expected_direction), "candle_direction inválido"

        window = 5
        vol = df_base["volume"]
        ma = vol.rolling(window=window, min_periods=window).mean()
        std = vol.rolling(window=window, min_periods=window).std()
        vol_rel = (vol - ma) / std.replace(0, np.nan)
        np.testing.assert_allclose(df_out["volume_relative"].fillna(0), vol_rel.fillna(0), rtol=1e-8, err_msg="volume_relative inválido")

        ema = df_base["close"].ewm(span=20, adjust=False).mean()
        pullback = (df_base["close"] - ema) / ema
        np.testing.assert_allclose(df_out["pullback"].fillna(0), pullback.fillna(0), rtol=1e-8, err_msg="pullback inválido")

        body = (df_base["close"] - df_base["open"]).abs()
        lower_shadow = np.where(
            df_base["close"] > df_base["open"],
            df_base["open"] - df_base["low"],
            df_base["close"] - df_base["low"],
        )
        total_range = df_base["high"] - df_base["low"]
        is_hammer = (lower_shadow >= 2 * body) & (body <= 0.3 * total_range)
        hammer_expected = is_hammer.astype(float)
        assert all(df_out["hammer_pattern"] == hammer_expected), "hammer_pattern inválido"

        body = (df_base["close"] - df_base["open"]).abs()
        upper_shadow = np.where(
            df_base["open"] > df_base["close"],
            df_base["high"] - df_base["open"],
            df_base["high"] - df_base["close"],
        )
        total_range = df_base["high"] - df_base["low"]
        is_inverted = (upper_shadow >= 2 * body) & (body <= 0.3 * total_range)
        inv_hammer_expected = is_inverted.astype(float)
        assert all(df_out["inverted_hammer_pattern"] == inv_hammer_expected), "inverted_hammer_pattern inválido"
