import json
from pathlib import Path
import pandas as pd
import pytest

from src.data.data_pipeline import DataPipeline
from src.data.data_libs.schema_utils import load_feature_list


def make_dirs(tmp_path, dirs):
    for d in dirs:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)


def make_config(tmp_path, pipeline_type):
    # Diretórios para etapas
    dirs = {
        "raw_dir": "raw",
        "features_dir": "features",
        "features_normalized_dir": "norm",
        "final_ppo_dir": "final_ppo",
        "final_mlp_dir": "final_mlp",
    }
    make_dirs(tmp_path, dirs.values())

    cfg = {
        "DATA": {
            "pipeline_type": pipeline_type,
            "broker": "mt5",
            "symbols": "EURUSD",
            "timeframes": "M5",
            "start_date": "2020-01-01",
            "end_date": "2020-01-02",
            # Caminhos
            **{key: str(tmp_path / path) for key, path in dirs.items()},
            "volume_sources": "",
            "volume_column": None
        },
        "ENV": {"mode": "batch"},
        "FEATURE_ENGINEER": {"features": ",".join(load_feature_list())},
        "GAP_CORRECTOR": {},
        "OUTLIER_CORRECTOR": {},
        "SCALER": {"scaler_columns": "open,high,low,close,volume"}
    }
    return cfg


@pytest.mark.integration
@pytest.mark.parametrize("pipeline_type", ["ppo", "mlp", "ambos"])
def test_data_pipeline_full_flow(tmp_path, pipeline_type):
    """
    Teste funcional: verifica pipeline completa em dados reais via MT5.
    """
    config = make_config(tmp_path, pipeline_type)
    pipeline = DataPipeline(config=config, mode="batch", pipeline_type=pipeline_type, debug=True)

    # Executa pipeline completo
    result_df = pipeline.run()

    # Verifica retorno
    assert isinstance(result_df, pd.DataFrame), "Resultado deve ser um DataFrame"
    assert not result_df.empty, "DataFrame não deve estar vazio"

    # Verifica artefatos e metadados
    for etapa in ["raw", "features"]:
        path = Path(pipeline.outputs[etapa])
        assert path.exists(), f"Arquivo {etapa} não encontrado: {path}"
        meta_path = path.with_name(path.stem + "_meta.json")
        assert meta_path.exists(), f"Meta JSON não encontrado: {meta_path}"
        meta = json.loads(meta_path.read_text())
        assert meta["etapa"] == etapa
        assert meta["pipeline_type"] == pipeline_type

    # Verifica fluxo condicional
    if pipeline_type in ("mlp", "ambos"):
        norm_path = Path(pipeline.outputs.get("features_normalized"))
        assert norm_path and norm_path.exists(), "Features normalizadas não salvas"

    if pipeline_type in ("ppo", "ambos"):
        final_ppo = Path(pipeline.outputs.get("final_ppo"))
        assert final_ppo and final_ppo.exists(), "Final PPO não salvo"
        # Valida schema final
        schema_cols = set(load_feature_list())
        df_cols = set(result_df.columns)
        assert schema_cols.issubset(df_cols), "Colunas de schema ausentes no resultado"
