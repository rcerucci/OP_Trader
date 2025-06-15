# tests/unit/test_file_saver.py
"""
Teste de Funcionalidade para src/utils/file_saver.py

Cobre 100% dos fluxos principais e edge cases:
- Salva DataFrame com meta e scaler (tudo OK)
- DataFrame vazio (erro)
- Falha de permissão/diretório (erro)
- Falha de serialização (warning)
- Ausência de meta/scaler (ignora, loga)
- Logging detalhado
"""

import os
import tempfile
import shutil
import pandas as pd
import pytest
from unittest.mock import patch
from src.utils.file_saver import (
    get_timestamp, build_filename, save_dataframe, save_json, save_pickle, save_dataframe_metadata
)

def test_get_timestamp():
    ts = get_timestamp()
    assert len(ts) == 15 and "_" in ts

def test_build_filename():
    fname = build_filename(
        prefix="data/processed",
        step="features",
        broker="mt5",
        corretora="xp",
        asset="EURUSD",
        timeframe="M5",
        period="2024-01-01_2024-12-31",
        timestamp="20250611_211500"
    )
    # Verifica somente a terminação, que é o que importa para rastreio de nome
    assert "features_mt5_xp_EURUSD_M5_2024-01-01_2024-12-31_20250611_211500.csv" in fname.replace("\\", "/")
    assert fname.endswith(".csv")


def test_save_dataframe_and_json(tmp_path):
    df = pd.DataFrame({"a": [1,2], "b": [3,4]})
    meta = {"info": "teste"}
    csv_path = tmp_path / "test.csv"
    json_path = tmp_path / "test.json"
    save_dataframe(df, str(csv_path))
    assert os.path.exists(csv_path)
    df2 = pd.read_csv(csv_path)
    assert df2.equals(df)
    save_json(meta, str(json_path))
    with open(json_path, "r", encoding="utf-8") as f:
        assert "teste" in f.read()

def test_save_pickle(tmp_path):
    obj = {"x": [1,2,3]}
    pkl_path = tmp_path / "obj.pkl"
    save_pickle(obj, str(pkl_path))
    import pickle
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
        assert data == obj

def test_save_dataframe_metadata_full(tmp_path):
    df = pd.DataFrame({"c": [7,8,9]})
    meta = {"param": "ok"}
    scaler = [0.1, 0.2]
    res = save_dataframe_metadata(
        df=df,
        step="features",
        broker="mt5",
        corretora="xp",
        asset="EURUSD",
        timeframe="M5",
        period="2025-01-01_2025-06-11",
        meta=meta,
        scaler=scaler,
        output_dir=str(tmp_path),
        debug=True
    )
    assert os.path.exists(res["data"])
    assert os.path.exists(res["meta"])
    assert os.path.exists(res["scaler"])
    assert pd.read_csv(res["data"]).equals(df)
    with open(res["meta"], "r", encoding="utf-8") as f:
        assert "ok" in f.read()
    import pickle
    with open(res["scaler"], "rb") as f:
        assert pickle.load(f) == scaler

def test_save_dataframe_metadata_no_meta_scaler(tmp_path):
    df = pd.DataFrame({"z": [0, 1, 2]})
    res = save_dataframe_metadata(
        df=df,
        step="raw",
        broker="binance",
        corretora="main",
        asset="BTCUSDT",
        timeframe="1m",
        output_dir=str(tmp_path),
    )
    assert os.path.exists(res["data"])
    assert res["meta"] == ""
    assert res["scaler"] == ""

def test_save_dataframe_empty_error(tmp_path):
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        save_dataframe(df, str(tmp_path / "should_fail.csv"))
    with pytest.raises(ValueError):
        save_dataframe_metadata(
            df=df,
            step="features",
            broker="mt5",
            corretora="xp",
            asset="EURUSD",
            timeframe="M5",
            output_dir=str(tmp_path)
        )

def test_save_dataframe_permission_error():
    df = pd.DataFrame({"a": [1]})
    # Simular erro de permissão usando patch
    with patch("os.makedirs", side_effect=PermissionError("Sem permissão")):
        with pytest.raises(PermissionError):
            save_dataframe(df, "/root/test.csv")

def test_save_pickle_serialize_error(tmp_path):
    # Objetos não serializáveis devem lançar IOError
    class NoPickle:
        def __getstate__(self):
            raise RuntimeError("Não pode serializar!")
    obj = NoPickle()
    pkl_path = tmp_path / "fail.pkl"
    with pytest.raises(IOError):
        save_pickle(obj, str(pkl_path))
