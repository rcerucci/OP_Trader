# src/utils/data_shape_utils.py

"""
data_shape_utils.py

Funções utilitárias para alinhamento de DataFrames a schemas de features e carregamento de lista de features
a partir de arquivos de controle. Essencial para garantir consistência entre pipeline de engenharia de features
e modelos no Op_Trader.

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import json
from typing import List, Sequence

import numpy as np
import pandas as pd

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)
logger = get_logger("data_shape_utils")

FEATURE_SCHEMA_CONTROL = ROOT_DIR / "config" / "feature_schema.json"

def load_feature_list() -> List[str]:
    """
    Lê o arquivo de controle (feature_schema.json) e retorna a lista "all_features" do schema ativo.

    Returns:
        List[str]: Lista de nomes de features do schema atual.

    Raises:
        FileNotFoundError: Se arquivos necessários não existirem.
        KeyError: Se campos obrigatórios estiverem ausentes.

    Example:
        >>> features = load_feature_list()
        >>> print(features)
        ['close', 'rsi', 'ema_20', ...]
    """
    logger.debug(f"Lendo controle de schema em: {FEATURE_SCHEMA_CONTROL}")
    if not FEATURE_SCHEMA_CONTROL.exists():
        logger.error(f"Arquivo de controle não encontrado: {FEATURE_SCHEMA_CONTROL}")
        raise FileNotFoundError(f"Arquivo não encontrado: {FEATURE_SCHEMA_CONTROL}")

    with open(FEATURE_SCHEMA_CONTROL, "r", encoding="utf-8") as f:
        control = json.load(f)

    schema_file = control.get("schema_file")
    if not schema_file:
        logger.error("Campo 'schema_file' não encontrado em feature_schema.json.")
        raise KeyError("Campo 'schema_file' ausente no controle de schema.")

    schema_path = ROOT_DIR / "config" / schema_file
    logger.debug(f"Lendo schema de features em: {schema_path}")
    if not schema_path.exists():
        logger.error(f"Arquivo de schema não encontrado: {schema_path}")
        raise FileNotFoundError(f"Arquivo não encontrado: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as sf:
        schema = json.load(sf)

    features = schema.get("all_features", [])
    if not features:
        logger.warning("Nenhuma feature encontrada em 'all_features' do schema.")
    logger.info(f"{len(features)} features carregadas do schema.")
    return features

def align_dataframe_to_schema(
    df: pd.DataFrame, schema_cols: Sequence[str]
) -> pd.DataFrame:
    """
    Alinha o DataFrame às colunas do schema, preservando ordem e tipos.
    Preenche colunas ausentes com np.nan, garante dtype float64 para todas as colunas.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        schema_cols (Sequence[str]): Lista ou tupla de nomes das colunas-alvo.

    Returns:
        pd.DataFrame: DataFrame alinhado ao schema.

    Example:
        >>> aligned = align_dataframe_to_schema(df, features)
        >>> aligned.dtypes.unique()
        [dtype('float64')]
    """
    logger.debug(f"Alinhando DataFrame para schema com {len(schema_cols)} colunas.")
    base = pd.DataFrame(index=df.index, columns=schema_cols, dtype="float64")
    out = base.assign(**df)
    wrong_dtypes = [c for c in out.columns if out[c].dtype != "float64"]
    if wrong_dtypes:
        out[wrong_dtypes] = out[wrong_dtypes].astype("float64")
        logger.info(f"Convertidas {len(wrong_dtypes)} colunas para float64: {wrong_dtypes}")
    logger.info(f"DataFrame alinhado: shape final = {out.shape}")
    return out
