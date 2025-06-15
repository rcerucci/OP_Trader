import json
from pathlib import Path
import pandas as pd
import pytest

from src.data.data_pipeline import DataPipeline
from src.data.data_collector import DataCollector
from src.data.data_libs.feature_engineer import FeatureEngineer
from src.data.data_libs.schema_utils import align_dataframe_to_schema, validate_dataframe_schema


def make_config(tmp_path):
    raw_dir = tmp_path / "raw"
    feat_dir = tmp_path / "features"
    ppo_dir = tmp_path / "ppo"
    # Cria diretórios de saída
    for d in (raw_dir, feat_dir, ppo_dir):
        d.mkdir(parents=True, exist_ok=True)

    return {
        "DATA": {
            "pipeline_type": "ppo",
            "broker": "mt5",
            "symbols": "EURUSD",
            "timeframes": "M5",
            "start_date": "2020-01-01",
            "end_date": "2020-01-02",
            "raw_dir": str(raw_dir),
            "features_dir": str(feat_dir),
            "final_ppo_dir": str(ppo_dir),
            "volume_sources": "",
            "volume_column": None
        },
        "ENV": {"mode": "batch"},
        "FEATURE_ENGINEER": {"features": "feature_a,feature_b"},
        "GAP_CORRECTOR": {},
        "OUTLIER_CORRECTOR": {},
        "SCALER": {}
    }


def test_data_pipeline_functional_ppp(tmp_path, monkeypatch):
    # Mock DataCollector.collect para retornar df_raw
    df_raw = pd.DataFrame({
        "open": [1.0, 1.1],
        "high": [1.2, 1.3],
        "low": [0.9, 1.0],
        "close": [1.05, 1.15],
        "tick_volume": [100, 110]
    })
    monkeypatch.setattr(DataCollector, "collect", lambda self, **kwargs: df_raw)

    # Mock FeatureEngineer.transform para adicionar colunas de features
    df_features = pd.DataFrame({
        "feature_a": [10, 11],
        "feature_b": [20, 21]
    })
    monkeypatch.setattr(FeatureEngineer, "transform", lambda self, df: df_features)

    # SchemaUtils deve apenas retornar df_features
    monkeypatch.setattr(align_dataframe_to_schema, "__call__", lambda df, schema: df_features)
    monkeypatch.setattr(validate_dataframe_schema, "__call__", lambda df, schema, strict: None)

    config = make_config(tmp_path)
    pipeline = DataPipeline(config=config, mode="batch", pipeline_type="ppo", debug=True)
    result_df = pipeline.run()

    # Valida retorno
    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), df_features)

    # Verifica arquivos gerados e metadados
    raw_path = Path(pipeline.outputs["raw"])
    features_path = Path(pipeline.outputs["features"])
    final_path = Path(pipeline.outputs["final_ppo"])
    assert raw_path.exists(), f"Arquivo raw não encontrado: {raw_path}"
    assert features_path.exists(), f"Arquivo features não encontrado: {features_path}"
    assert final_path.exists(), f"Arquivo final_ppo não encontrado: {final_path}"

    # Metadados
    meta_path = raw_path.with_name(raw_path.stem + "_meta.json")
    assert meta_path.exists(), f"Meta JSON não encontrado: {meta_path}"
    meta = json.loads(meta_path.read_text())
    assert meta["etapa"] == "raw"
    assert meta["pipeline_type"] == "ppo"
    assert meta["broker"] == config["DATA"]["broker"]
    assert "config_hash" in meta
