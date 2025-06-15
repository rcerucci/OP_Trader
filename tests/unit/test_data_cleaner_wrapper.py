# tests/unit/test_data_cleaner_wrapper.py

import pytest
import pandas as pd
from src.data.data_libs.data_cleaner_wrapper import DataCleanerWrapper

COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'time']

def make_valid_df(n=10):
    return pd.DataFrame({
        "datetime": pd.date_range("2024-01-01", periods=n, freq="min"),
        "open": [1.0 + 0.1*i for i in range(n)],
        "high": [1.1 + 0.1*i for i in range(n)],
        "low": [0.9 + 0.1*i for i in range(n)],
        "close": [1.05 + 0.1*i for i in range(n)],
        "volume": [100 + i for i in range(n)],
        "time": [1704067200 + 60*i for i in range(n)],
    })

def make_invalid_df_missing():
    df = make_valid_df()
    return df.drop(columns=["high"])

def make_invalid_df_nan():
    df = make_valid_df()
    df.loc[0, "close"] = None
    return df

def make_df_extra_col():
    df = make_valid_df()
    df["dummy"] = range(len(df))
    return df

def test_clean_ok_round_and_schema():
    wrapper = DataCleanerWrapper(debug=True)
    df = make_valid_df()
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert list(df_clean.columns) == COLUMNS_REQUIRED
    for col in ["open", "high", "low", "close"]:
        assert all(df_clean[col].apply(lambda x: float(f"{x:.3f}") == x))
    assert pd.api.types.is_datetime64_any_dtype(df_clean["datetime"])
    assert pd.api.types.is_numeric_dtype(df_clean["open"])
    assert pd.api.types.is_numeric_dtype(df_clean["volume"])

def test_schema_missing():
    wrapper = DataCleanerWrapper(debug=True)
    df = make_invalid_df_missing()
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert df_clean.empty

def test_missing_decimals():
    wrapper = DataCleanerWrapper(debug=True)
    df = make_valid_df()
    df_clean = wrapper.clean(df, ohlc_decimals=None)
    assert df_clean.empty

def test_remove_nan():
    wrapper = DataCleanerWrapper(debug=True)
    df = make_invalid_df_nan()
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert len(df_clean) == len(df) - 1

def test_schema_extra_col_discarded():
    wrapper = DataCleanerWrapper(debug=True)
    df = make_df_extra_col()
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert set(df_clean.columns) == set(COLUMNS_REQUIRED)
    assert "dummy" not in df_clean.columns

def test_callback_gap():
    wrapper = DataCleanerWrapper(debug=True, gap_params={"max_gap_seconds": 30})
    gaps = []
    wrapper.on_gap(lambda info: gaps.append(info))
    df = make_valid_df()
    df.loc[5, "datetime"] = df.loc[4, "datetime"] + pd.Timedelta(minutes=5)
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert len(gaps) > 0
    assert "gap" in gaps[0]

def test_callback_outlier():
    wrapper = DataCleanerWrapper(debug=True, outlier_params={"threshold": 1.5})
    outliers = []
    wrapper.on_outlier(lambda info: outliers.append(info))
    df = make_valid_df()
    df.loc[7, "open"] = 2.0
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert any(o["column"] == "open" and o["index"] == 7 for o in outliers)

def test_empty_df():
    wrapper = DataCleanerWrapper(debug=True)
    df = pd.DataFrame()
    df_clean = wrapper.clean(df, ohlc_decimals=3)
    assert df_clean.empty

def test_not_dataframe():
    wrapper = DataCleanerWrapper(debug=True)
    result = wrapper.clean("not a df", ohlc_decimals=3)
    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_streaming_mode_ok():
    wrapper = DataCleanerWrapper(debug=True, mode="streaming")
    df = make_valid_df()
    df_clean = wrapper.clean(df, ohlc_decimals=2)
    assert list(df_clean.columns) == COLUMNS_REQUIRED

def test_batch_mode_ok():
    wrapper = DataCleanerWrapper(debug=True, mode="batch")
    df = make_valid_df()
    df_clean = wrapper.clean(df, ohlc_decimals=2)
    assert list(df_clean.columns) == COLUMNS_REQUIRED
