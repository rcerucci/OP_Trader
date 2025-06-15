# src/utils/file_saver.py

"""
file_saver.py

Utilitários para geração de nomes de arquivos padronizados (com tags: broker, corretora, etc.) 
e salvamento seguro de DataFrames, JSON, Pickle e modelos, seguindo o padrão Op_Trader.
Pronto para expansão: uso futuro em pipelines de treino, tuning, logs e artefatos de CI/CD.

Autor: Equipe Op_Trader
Data: 2025-06-11
"""

import os
import json
import pickle
from datetime import datetime
from typing import Optional, Any, Dict

import pandas as pd

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)
logger = get_logger("file_saver")

# ======= Funções de utilidade base =======

def get_timestamp() -> str:
    """
    Retorna timestamp padrão YYYYMMDD_HHMMSS para uso em nomes de arquivos.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.debug(f"Timestamp gerado: {ts}")
    return ts

def build_filename(
    prefix: str,
    step: str,
    broker: str,
    corretora: str,
    asset: str,
    timeframe: str,
    period: Optional[str] = "",
    timestamp: Optional[str] = "",
    extension: str = "csv"
) -> str:
    """
    Gera nome de arquivo padronizado, com todas as tags de rastreabilidade.

    Args:
        prefix (str): Diretório base (ex: "data/processed").
        step (str): Etapa do processamento ("features", "raw", "model", etc).
        broker (str): Nome do broker/fonte (ex: "mt5", "binance").
        corretora (str): Nome da corretora/server/provider (ex: "xp", "rico", "n/a").
        asset (str): Símbolo do ativo.
        timeframe (str): Timeframe do ativo.
        period (str, opcional): Período de referência.
        timestamp (str, opcional): Timestamp customizado.
        extension (str, opcional): Extensão do arquivo.

    Returns:
        str: Caminho completo do arquivo.
    """
    required = [prefix, step, broker, corretora, asset, timeframe]
    if not all(required):
        msg = "Campos obrigatórios (prefix, step, broker, corretora, asset, timeframe) não podem ser vazios."
        logger.error(msg)
        raise ValueError(msg)
    elements = [step, broker, corretora, asset, timeframe]
    if period:
        elements.append(period)
    if timestamp:
        elements.append(timestamp)
    filename = "_".join(elements) + f".{extension}"
    fullpath = os.path.join(prefix, filename)
    logger.debug(f"Nome de arquivo construído: {fullpath}")
    return fullpath

# ======= Salvamento de artefatos =======

def save_dataframe(df: pd.DataFrame, filepath: str) -> None:
    """
    Salva DataFrame como CSV, criando diretórios e logando todo o processo.
    """
    directory = os.path.dirname(filepath)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Falha ao criar diretório '{directory}': {e}")
            raise
    if df.empty:
        logger.critical(f"Tentativa de salvar DataFrame vazio em '{filepath}'.")
        raise ValueError("DataFrame fornecido está vazio.")
    try:
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"DataFrame salvo em: {filepath}")
    except Exception as e:
        logger.error(f"Falha ao salvar DataFrame em '{filepath}': {e}")
        raise IOError(f"Erro ao salvar DataFrame: {e}")

def save_json(obj: Any, filepath: str) -> None:
    """
    Salva um objeto (dict, lista, etc) como JSON, criando diretórios e logando.
    """
    directory = os.path.dirname(filepath)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Falha ao criar diretório '{directory}': {e}")
            raise
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=4)
        logger.info(f"Arquivo JSON salvo em: {filepath}")
    except Exception as e:
        logger.error(f"Falha ao salvar JSON em '{filepath}': {e}")
        raise IOError(f"Erro ao salvar JSON: {e}")

def save_pickle(obj: Any, filepath: str) -> None:
    """
    Salva um objeto Python serializável via pickle (útil para scalers, modelos, tuning, etc).
    """
    directory = os.path.dirname(filepath)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Falha ao criar diretório '{directory}': {e}")
            raise
    try:
        with open(filepath, "wb") as f:
            pickle.dump(obj, f)
        logger.info(f"Arquivo pickle salvo em: {filepath}")
    except Exception as e:
        logger.error(f"Falha ao salvar pickle em '{filepath}': {e}")
        raise IOError(f"Erro ao salvar pickle: {e}")

# ======= Salvamento de artefatos de modelo (treino/tuning/checkpoint) =======

def save_model_artifact(obj: Any, filepath: str, artifact_type: str = "model") -> None:
    """
    Salva artefatos de modelos (usando pickle por padrão, mas pode ser adaptado para joblib, etc).
    Útil para modelos RL, tuning, checkpoints, configs.

    Args:
        obj (Any): Objeto serializável.
        filepath (str): Caminho do arquivo.
        artifact_type (str): Tipo ("model", "tuning", "checkpoint", etc).
    """
    # Aqui pode ser expandido para formatos específicos (ex: joblib, torch, h5)
    try:
        save_pickle(obj, filepath)
        logger.info(f"Artefato '{artifact_type}' salvo em: {filepath}")
    except Exception as e:
        logger.error(f"Erro ao salvar artefato de modelo '{artifact_type}': {e}")
        raise

# ======= Função central para salvar dados + metadata =======

def save_dataframe_metadata(
    df: pd.DataFrame,
    step: str,
    broker: str,
    corretora: str,
    asset: str,
    timeframe: str,
    period: str = "",
    meta: Optional[Dict] = None,
    scaler: Any = None,
    output_dir: str = "data/processed",
    timestamp: str = None,
    extension: str = "csv",
    debug: bool = False
) -> Dict[str, str]:
    """
    Salva DataFrame, metadata (JSON) e scaler/modelo (Pickle), tudo versionado e auditável.
    Retorna os caminhos dos arquivos gerados.

    Args:
        df (pd.DataFrame): DataFrame a ser salvo.
        step (str): Etapa do processamento.
        broker (str): Nome do broker/fonte.
        corretora (str): Nome da corretora/server/provider.
        asset (str): Ativo.
        timeframe (str): Timeframe.
        period (str, opcional): Período referenciado.
        meta (dict, opcional): Metadados para salvar como JSON.
        scaler (Any, opcional): Objeto scaler/modelo auxiliar.
        output_dir (str, opcional): Diretório base para saída.
        timestamp (str, opcional): Timestamp customizado.
        extension (str, opcional): Extensão do DataFrame principal.
        debug (bool, opcional): Logging detalhado.

    Returns:
        Dict[str, str]: Mapeamento dos arquivos gerados: data, meta, scaler.
    """
    logger_ = get_logger("file_saver", cli_level="DEBUG" if debug else None)

    if not timestamp:
        timestamp = get_timestamp()

    # Caminhos dos arquivos
    data_path = build_filename(
        prefix=output_dir,
        step=step,
        broker=broker,
        corretora=corretora,
        asset=asset,
        timeframe=timeframe,
        period=period,
        timestamp=timestamp,
        extension=extension
    )
    meta_path = data_path.replace(f".{extension}", "_meta.json")
    scaler_path = data_path.replace(f".{extension}", "_scaler.pkl")

    # 1. Salvar DataFrame
    save_dataframe(df, data_path)

    # 2. Salvar metadados (meta.json)
    if meta is not None:
        try:
            save_json(meta, meta_path)
        except Exception as e:
            logger_.warning(f"Metadados não foram salvos: {e}")

    # 3. Salvar scaler/modelo (opcional)
    scaler_saved = False
    if scaler is not None:
        try:
            save_pickle(scaler, scaler_path)
            scaler_saved = True
        except Exception as e:
            logger_.warning(f"Scaler/modelo não foi salvo: {e}")

    logger_.info(f"Todos arquivos salvos (data: {data_path}, meta: {meta_path}, scaler: {scaler_path if scaler_saved else 'n/a'})")
    return {
        "data": data_path,
        "meta": meta_path if meta is not None else "",
        "scaler": scaler_path if scaler_saved else ""
    }

# ======= Exemplos práticos de uso =======
"""
Exemplo 1: Salvando dados com rastreabilidade máxima
-----------------------------------------------------
from src.utils.file_saver import save_dataframe_metadata

result = save_dataframe_metadata(
    df=df_features,
    step="features",
    broker="mt5",
    corretora="xp",
    asset="EURUSD",
    timeframe="M5",
    period="2024-01-01_2024-12-31",
    meta={
        "broker": "mt5",
        "corretora": "xp",
        "pipeline_version": "2025-06-11",
        "parametros_indicadores": {...}
    },
    scaler=mlp_scaler,
    output_dir="data/processed"
)
print(result)
# -> {'data': ..., 'meta': ..., 'scaler': ...}

Exemplo 2: Salvando apenas DataFrame (raw)
-------------------------------------------
save_dataframe_metadata(
    df=df_raw,
    step="raw",
    broker="binance",
    corretora="main",
    asset="BTCUSDT",
    timeframe="1m"
)
"""

# ======= Possíveis expansões futuras =======
# - save_yaml() para configs avançadas
# - save_joblib() para modelos scikit-learn/tuning
# - load_json(), load_pickle() (leitura robusta, rastreável)
# - Utilitários para exportação incremental (streaming/batch)
# - Compactação automática (zip, tar.gz)
# - Versionamento automático de pipelines (hash, git tag)
# - Logging auditável com ID de execução/pipeline

