"""
Op_Trader – schema_utils.py (💎 Refatoração 2025‑06‑12)
------------------------------------------------------
Módulo centralizado para *schema governance* do DataPipeline.

**Motivações da refatoração**
================================
* Corrigir o *bug* detectado no `align_dataframe_to_schema` ("Passing a dict as an indexer …")
  causado por elementos não‑*string* no arquivo JSON de schema.
* Endurecer a validação de entradas para evitar erros silenciosos.
* Fornecer API mais flexível (`drop_extra`, `strict`) sem quebrar contratos
  existentes.
* Melhorar *logging* e cobertura de *edge cases*.

Este arquivo **substitui completamente** a versão anterior.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from pandas.api import types as pdt

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)
LOGGER = get_logger("schema_utils")

# Caminho padrão do controle de schema
DEFAULT_SCHEMA_CONTROL = ROOT_DIR / "config" / "feature_schema.json"

# ---------------------------------------------------------------------------
#  Utils internos
# ---------------------------------------------------------------------------

def _ensure_str_columns(cols: Iterable) -> List[str]:
    """Valida elementos do schema e garante `List[str]`.

    Args:
        cols: Sequência original lida do JSON.
    Returns:
        Lista limpa apenas com `str`.
    Raises:
        TypeError: Se encontrar elemento não‑string.
    """
    cleaned: List[str] = []
    for i, col in enumerate(cols):
        if isinstance(col, str):
            cleaned.append(col)
        else:
            #  Fail‑fast  →  se o JSON estiver mal‑formado o dev fica sabendo.
            LOGGER.critical(
                "Coluna não‑string detectada no schema (idx=%d, type=%s): %s",
                i,
                type(col).__name__,
                col,
            )
            raise TypeError(
                "feature_schema contém elemento não‑string. Veja logs para detalhes."  # noqa: E501
            )
    return cleaned

# ---------------------------------------------------------------------------
#  API pública
# ---------------------------------------------------------------------------

def load_feature_list(schema_control_path: Optional[str | Path] = None) -> List[str]:
    """Carrega `all_features` do JSON de schema.

    Args:
        schema_control_path: Caminho opcional para um `feature_schema.json` custom.
    Returns:
        Lista de nomes de colunas (strings) **em ordem**.
    """
    control_path = Path(schema_control_path) if schema_control_path else DEFAULT_SCHEMA_CONTROL
    LOGGER.debug("[schema_utils] Controle de schema: %s", control_path)

    if not control_path.exists():
        raise FileNotFoundError(f"feature_schema.json não encontrado: {control_path}")

    with control_path.open("r", encoding="utf‑8") as fp:
        control = json.load(fp)

    schema_file = control.get("schema_file")
    if not schema_file:
        raise KeyError("Campo 'schema_file' ausente em feature_schema.json")

    schema_path = ROOT_DIR / "config" / schema_file
    LOGGER.debug("[schema_utils] Lendo arquivo de schema: %s", schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Arquivo de schema não encontrado: {schema_path}")

    with schema_path.open("r", encoding="utf‑8") as fp:
        schema = json.load(fp)

    features_raw = schema.get("all_features", [])
    features = _ensure_str_columns(features_raw)

    LOGGER.info("%d features carregadas do schema (%s)", len(features), schema_file)
    return features


def align_dataframe_to_schema(
    df: pd.DataFrame,
    schema_cols: Sequence[str],
    *,
    strict: bool = False,
    drop_extra: bool = True,
) -> pd.DataFrame:
    """Alinha `df` às colunas definidas no schema, preservando o tipo de datetime e evitando conversão indevida."""
    if df.empty:
        raise ValueError("DataFrame de entrada está vazio.")

    schema_cols = _ensure_str_columns(schema_cols)
    LOGGER.debug("[schema_utils] Alinhando DF para %d colunas do schema", len(schema_cols))

    # 1) Garante ordem & presença (preenche faltantes com NaN)
    aligned = pd.DataFrame(index=df.index, columns=schema_cols)
    common = [c for c in df.columns if c in schema_cols]
    if common:
        aligned.loc[:, common] = df[common]

    # 2) Anexa colunas extras, se permitido
    if not drop_extra:
        extras = [c for c in df.columns if c not in schema_cols]
        if extras:
            LOGGER.warning("Colunas extra fora do schema serão mantidas: %s", extras)
            aligned = pd.concat([aligned, df[extras]], axis=1)

    # 3) Conversão de tipos, PRESERVANDO 'datetime'
    non_float = [c for c in aligned.columns if c != "datetime" and not pdt.is_float_dtype(aligned[c])]
    if non_float:
        LOGGER.info("Convertendo %d colunas para float64: %s", len(non_float), non_float)
        aligned[non_float] = aligned[non_float].apply(pd.to_numeric, errors="coerce")

    # 4) Converte 'datetime' para string, se existir
    if "datetime" in aligned.columns:
        aligned["datetime"] = pd.to_datetime(aligned["datetime"], errors="coerce").dt.strftime('%Y-%m-%d %H:%M:%S')

    # 5) Validação estrita opcional
    if strict and aligned.isna().any().any():
        na_cols = aligned.columns[aligned.isna().any()].tolist()
        raise ValueError(
            f"Valores NaN introduzidos em conversão estrita: {na_cols} » verifique o dataset"
        )

    LOGGER.info("DataFrame alinhado – shape final: %s", aligned.shape)
    return aligned


def validate_dataframe_schema(
    df: pd.DataFrame, schema_cols: Sequence[str], *, strict: bool = True
) -> bool:
    """Valida se *df* cumpre o schema.

    Args:
        df: DataFrame já alinhado.
        schema_cols: Colunas esperadas.
        strict: Se ``True`` exige correspondência exata (nome, ordem, dtype=float64).
    Returns:
        ``True`` se válido; caso contrário gera *logs* de erro e retorna ``False``.
    """
    schema_cols = _ensure_str_columns(schema_cols)

    ok = True
    if list(df.columns) != list(schema_cols):
        LOGGER.error("Colunas fora de ordem ou divergentes do schema.")
        ok = False

    if strict:
        wrong_dtype = [c for c in df.columns if not pdt.is_float_dtype(df[c])]
        if wrong_dtype:
            LOGGER.error("Dtype != float64 detectado em: %s", wrong_dtype)
            ok = False

    if ok:
        LOGGER.info("Schema VALIDADO com sucesso (%d colunas).", len(schema_cols))
    else:
        LOGGER.critical("Falha na validação de schema. Veja erros acima.")

    return ok
