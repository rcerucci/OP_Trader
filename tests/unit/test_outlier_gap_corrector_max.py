import pytest
import pandas as pd
import numpy as np
from src.data.data_libs.outlier_gap_corrector import OutlierGapCorrector

@pytest.mark.parametrize("freq, mean, std", [
    ("5min", 10, 1),   # PPO (micro)
    ("1h", 100, 10)    # MLP (macro)
])
def test_correto_macro_micro_stress(freq, mean, std):
    n = 10_000
    dt = pd.date_range("2024-01-01", periods=n, freq=freq)
    rng = np.random.default_rng(2024 if freq == "5min" else 2025)
    # 20 gaps aleatórios
    gaps_idx = rng.choice(n, size=20, replace=False)
    dt_gap = dt.delete(gaps_idx)
    m = len(dt_gap)
    # Colunas de preços/volume simuladas
    df = pd.DataFrame({
        "datetime": dt_gap,
        "open": np.random.normal(mean, std, m),
        "high": np.random.normal(mean+1, std, m),
        "low": np.random.normal(mean-1, std, m),
        "close": np.random.normal(mean, std, m),
        "volume": np.random.randint(1000, 2000, m)
    })
    # 20 outliers na coluna 'close'
    outlier_indices = rng.choice(m, size=20, replace=False)
    df.loc[df.index[outlier_indices], "close"] = 1e6  # Valor absurdo

    # Salva df original para comparação
    df_original = df.copy(deep=True)

    corretor = OutlierGapCorrector(freq=freq, strategies={"all": "interpolate"}, debug=False)
    # Corrige gaps
    df_corr = corretor.fix_gaps(df)
    # Corrige outliers
    df_final = corretor.fix_outliers(df_corr, strategy="interpolate")

    # 1. Shape final igual ao número de períodos esperado
    assert df_final.shape[0] == n, f"Shape final {df_final.shape[0]} != {n}"

    # 2. Não há NaN
    assert not df_final.isnull().any().any(), "Ainda há NaN após correção"

    # 3. Todos gaps corrigidos
    assert "gap_fixed" in df_final.columns
    assert df_final["gap_fixed"].sum() == 20, "Nem todos os gaps foram tratados"

    # 4. Todos os outliers corrigidos (valores corrigidos não podem ser mais 1e6)
    assert "close_fixed" in df_final.columns
    n_outliers_corrigidos = df_final["close_fixed"].sum()
    assert n_outliers_corrigidos >= 15, f"Menos outliers tratados do que esperado: {n_outliers_corrigidos}"
    assert (df_final.loc[df_final["close_fixed"], "close"] < 1e5).all(), "Outlier não corrigido"

    # 5. Comparação estatística: a média do final deve estar no range plausível
    final_mean = df_final["close"].mean()
    assert mean - 2*std < final_mean < mean + 2*std, f"Média final fora do esperado: {final_mean}"

    # 6. Auditoria de linhas alteradas
    # Para gaps: checa que linhas inseridas não existem no original
    novos_datetimes = set(df_final.loc[df_final["gap_fixed"], "datetime"])
    antigos_datetimes = set(df_original["datetime"])
    assert novos_datetimes.isdisjoint(antigos_datetimes), "Gaps inseridos colidem com original"
    # Para outliers: os índices corrigidos estavam presentes no original e tinham valor alterado
    for ix in df_final.index[df_final["close_fixed"]]:
        dt_val = df_final.loc[ix, "datetime"]
        if dt_val in antigos_datetimes:
            v_orig = df_original.loc[df_original["datetime"] == dt_val, "close"].values
            v_corr = df_final.loc[ix, "close"]
            if len(v_orig) > 0 and v_orig[0] == 1e6:
                assert v_corr != 1e6, "Valor outlier não corrigido"

    # 7. Logging visual (opcional)
    print(f"Modo: {'PPO/Micro' if freq == '5min' else 'MLP/Macro'}")
    print(f"Shape inicial: {df_original.shape} | Shape final: {df_final.shape}")
    print(f"Gaps corrigidos: {df_final['gap_fixed'].sum()} | Outliers corrigidos: {n_outliers_corrigidos}")
    print(f"Média close final: {final_mean:.3f}")
