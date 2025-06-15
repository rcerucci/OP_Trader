# tests/unit/test_outlier_gap_corrector.py

import pytest
import pandas as pd
import numpy as np
from src.data.data_libs.outlier_gap_corrector import OutlierGapCorrector

@pytest.fixture
def df_5m_gap():
    # Simula série de 5m com 2 gaps
    idx = pd.date_range("2024-01-01", periods=10, freq="5min").delete([3, 7])
    n = len(idx)
    df = pd.DataFrame({
        "datetime": idx,
        "open": np.arange(n) + 1.0,
        "high": np.arange(n) + 2.0,
        "low": np.arange(n) + 0.5,
        "close": np.arange(n) + 1.5,
        "volume": np.arange(n) * 10 + 100
    })
    return df

@pytest.fixture
def df_5m_outlier():
    # Simula série de 5m com outliers claros
    dt = pd.date_range("2024-01-01", periods=10, freq="5min")
    data = np.arange(10) + 1.0
    data[2] = 100  # Outlier em open
    data2 = np.arange(10) + 2.0
    data2[5] = -99  # Outlier em high
    df = pd.DataFrame({
        "datetime": dt,
        "open": data,
        "high": data2,
        "low": np.arange(10) + 0.5,
        "close": np.arange(10) + 1.5,
        "volume": np.arange(10) * 10 + 100
    })
    return df

def test_detect_and_fix_gaps(df_5m_gap):
    corretor = OutlierGapCorrector(freq='5min', debug=True)
    gaps_df = corretor.detect_gaps(df_5m_gap)
    assert not gaps_df.empty
    assert gaps_df.shape[0] == 2  # Dois gaps

    df_corrigido = corretor.fix_gaps(df_5m_gap)
    expected_len = pd.date_range(
        df_5m_gap['datetime'].min(), df_5m_gap['datetime'].max(), freq='5min'
    ).size
    assert df_corrigido.shape[0] == expected_len
    assert df_corrigido['gap_fixed'].sum() >= 2
    assert "gap_fixed" in df_corrigido.columns

def test_detect_and_fix_outliers(df_5m_outlier):
    corretor = OutlierGapCorrector(freq='5min', debug=True)
    outlier_flags = corretor.detect_outliers(df_5m_outlier)
    # Deve marcar True pelo menos nos dois outliers injetados
    assert outlier_flags["open_outlier"].sum() == 1
    assert outlier_flags["high_outlier"].sum() == 1

    # Testa imputação por média
    df_mean = corretor.fix_outliers(df_5m_outlier, strategy="mean")
    assert "open_fixed" in df_mean.columns
    # A média usada deve ser a média dos valores "normais", sem o outlier
    open_sem_outlier = np.delete(df_5m_outlier["open"].values, 2)
    mean_val = open_sem_outlier.mean()
    # Todos os valores corrigidos devem ser igual à média calculada
    for ix in df_mean.index[df_mean["open_fixed"]]:
        assert np.isclose(df_mean.loc[ix, "open"], mean_val, rtol=1e-2)

    # Testa interpolação
    df_interp = corretor.fix_outliers(df_5m_outlier, strategy="interpolate")
    assert not df_interp.isnull().any().any()
    assert "high_fixed" in df_interp.columns

def test_pipeline_5min_and_1h(df_5m_gap, df_5m_outlier):
    # 5min: ffill
    corretor_5m = OutlierGapCorrector(freq='5min', strategies={'all': 'ffill'}, debug=False)
    df_corr_5m = corretor_5m.fix_gaps(df_5m_gap)
    df_corr_5m = corretor_5m.fix_outliers(df_corr_5m)
    assert df_corr_5m.isnull().sum().sum() == 0
    assert "gap_fixed" in df_corr_5m.columns

    # 1h: interpolate
    idx = pd.date_range("2024-01-01", periods=10, freq="1h").delete([2])
    n = len(idx)
    df_1h = pd.DataFrame({
        "datetime": idx,
        "open": np.arange(n) + 1.0,
        "high": np.arange(n) + 2.0,
        "low": np.arange(n) + 0.5,
        "close": np.arange(n) + 1.5,
        "volume": np.arange(n) * 10 + 100
    })
    corretor_1h = OutlierGapCorrector(freq='1h', strategies={'all': 'interpolate'}, debug=False)
    df_corr_1h = corretor_1h.fix_gaps(df_1h)
    df_corr_1h = corretor_1h.fix_outliers(df_corr_1h)
    assert df_corr_1h.isnull().sum().sum() == 0

def test_report(df_5m_gap, df_5m_outlier):
    corretor = OutlierGapCorrector(freq='5min', debug=False)
    corretor.detect_gaps(df_5m_gap)
    corretor.detect_outliers(df_5m_outlier)
    rep = corretor.report()
    assert "gaps_detected" in rep
    assert "outliers_detected" in rep
    assert rep["gaps_detected"] >= 0

def test_stress_10000_linhas_comparativo():
    n = 10_000
    dt = pd.date_range("2024-01-01", periods=n, freq="5min")
    rng = np.random.default_rng(42)
    gaps_idx = rng.choice(n, size=10, replace=False)
    dt_gap = dt.delete(gaps_idx)
    m = len(dt_gap)
    df = pd.DataFrame({
        "datetime": dt_gap,
        "open": np.random.normal(10, 1, m),
        "high": np.random.normal(11, 1, m),
        "low": np.random.normal(9, 1, m),
        "close": np.random.normal(10, 1, m),
        "volume": np.random.randint(90, 110, m)
    })
    outlier_indices = rng.choice(m, size=10, replace=False)
    df.loc[df.index[outlier_indices], "open"] = 1000

    corretor = OutlierGapCorrector(freq="5min", strategies={"all": "interpolate"}, debug=False)
    df_corr = corretor.fix_gaps(df)
    df_corr2 = corretor.fix_outliers(df_corr, strategy="interpolate")

    # Shape antes e depois
    assert df.shape[0] == n - 10
    assert df_corr2.shape[0] == n

    # Verifica que gaps e outliers foram tratados:
    assert not df_corr2.isnull().any().any()
    assert (df_corr2["gap_fixed"].sum() == 10)

    # Linhas inseridas: só as flags gap_fixed==True
    gaps_corrigidos = df_corr2[df_corr2["gap_fixed"]]
    assert gaps_corrigidos.shape[0] == 10

    # Outliers corrigidos (com flag): só as flags open_fixed==True
    if "open_fixed" in df_corr2.columns:
        n_outliers_corrigidos = df_corr2["open_fixed"].sum()
        # Os índices dos outliers não devem estar mais com valor 1000
        open_corrigidos = df_corr2.loc[df_corr2["open_fixed"], "open"]
        assert (open_corrigidos != 1000).all()
        # Verifique que os valores corrigidos são próximos da interpolação (opcional)
        # Exemplo: print os valores antigos/corrigidos (para debug/auditoria)
        print("Valores dos outliers após correção:", open_corrigidos.values)

    # Estatísticas do df original vs corrigido
    print("Mean open (original):", df["open"].mean())
    print("Mean open (corrigido):", df_corr2["open"].mean())
    print("Qtd gaps originais:", 10)
    print("Qtd gaps corrigidos:", gaps_corrigidos.shape[0])
    print("Qtd outliers corrigidos:", int(n_outliers_corrigidos))

    # Exporte os df (opcional, para inspeção visual)
    # df.to_csv("df_original.csv", index=False)
    # df_corr2.to_csv("df_corrigido.csv", index=False)
