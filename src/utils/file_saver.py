# src/utils/file_saver.py

"""
file_saver.py

Utilitários para geração de nomes de arquivos padronizados (com timestamp) e salvamento seguro de DataFrames.
Usado em todo pipeline Op_Trader para garantir rastreabilidade de dados, modelos e logs.

Exemplo de uso:
    from src.utils.file_saver import get_timestamp, build_filename, save_dataframe

    ts = get_timestamp()
    fname = build_filename(
        prefix="data/processed",
        suffix="features",
        asset="EURUSD",
        timeframe="M5",
        period="2024-01-01_2024-12-31",
        timestamp=ts
    )
    save_dataframe(df, fname)

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)
logger = get_logger("file_saver")

def get_timestamp() -> str:
    """
    Retorna timestamp padrão YYYYMMDD_HHMMSS para uso em nomes de arquivos.

    Returns:
        str: Timestamp formatado.

    Example:
        >>> get_timestamp()
        '20250606_213154'
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.debug(f"Timestamp gerado: {ts}")
    return ts

def build_filename(
    prefix: str,
    suffix: str,
    asset: str,
    timeframe: str,
    period: Optional[str] = "",
    timestamp: Optional[str] = "",
    extension: str = "csv"
) -> str:
    """
    Gera nome de arquivo padronizado do projeto, com sufixos opcionais.

    Args:
        prefix (str): Diretório base (ex: "data/processed").
        suffix (str): Prefixo do arquivo (ex: "market", "features").
        asset (str): Símbolo do ativo (ex: "EURUSD").
        timeframe (str): Timeframe do ativo (ex: "M5").
        period (str, optional): String opcional de período (ex: "2024-01-01_2024-12-31").
        timestamp (str, optional): Timestamp opcional (ex: get_timestamp()).
        extension (str, optional): Extensão, default "csv".

    Returns:
        str: Caminho completo do arquivo.

    Raises:
        ValueError: Se algum campo obrigatório estiver vazio.

    Example:
        >>> build_filename("data/raw", "market", "EURUSD", "M5", "2024-01-01_2024-12-31", "20250606_213154")
        'data/raw/market_EURUSD_M5_2024-01-01_2024-12-31_20250606_213154.csv'
    """
    required = [prefix, suffix, asset, timeframe]
    if not all(required):
        msg = "Campos obrigatórios (prefix, suffix, asset, timeframe) não podem ser vazios."
        logger.error(msg)
        raise ValueError(msg)

    elements = [suffix, asset, timeframe]
    if period:
        elements.append(period)
    if timestamp:
        elements.append(timestamp)
    filename = "_".join(elements) + f".{extension}"
    fullpath = os.path.join(prefix, filename)
    logger.debug(f"Nome de arquivo construído: {fullpath}")
    return fullpath

def save_dataframe(df: pd.DataFrame, filepath: str) -> None:
    """
    Salva DataFrame como CSV no caminho fornecido, criando diretórios quando necessário.

    Args:
        df (pd.DataFrame): DataFrame a ser salvo.
        filepath (str): Caminho completo do arquivo de saída.

    Raises:
        IOError: Se falhar ao salvar o arquivo.

    Example:
        >>> save_dataframe(df, "data/processed/features_EURUSD_M5_2024-...csv")
    """
    directory = os.path.dirname(filepath)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Falha ao criar diretório '{directory}': {e}")
            raise

    try:
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"DataFrame salvo em: {filepath}")
    except Exception as e:
        logger.error(f"Falha ao salvar DataFrame em '{filepath}': {e}")
        raise IOError(f"Erro ao salvar DataFrame: {e}")

