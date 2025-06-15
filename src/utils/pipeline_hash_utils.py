#!/usr/bin/env python3
"""
src/utils/pipeline_hash_utils.py

Utilitários para criação, atualização e leitura do JSON centralizador de rastreabilidade dos pipelines de dados/treinamento do Op_Trader.

Autor: Equipe Op_Trader
Data: 2025-06-14
"""

import json
import os
from typing import Dict, Any, Optional

def save_pipeline_hash_json(
    hash_path: str,
    config_hash: str,
    timestamp: str,
    config: Dict[str, Any],
    paths: Dict[str, Optional[str]],
    features: list,
    corretora: str,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    status: Dict[str, str] = None,
    log_path: str = None,
    update_only: bool = False,
    extra: Dict[str, Any] = None,
) -> None:
    """
    Cria ou atualiza o JSON centralizador de rastreio de pipeline.

    Args:
        hash_path (str): Caminho do arquivo hash_ppo_...json.
        config_hash (str): Hash da configuração.
        timestamp (str): Timestamp do pipeline.
        config (Dict): Configuração completa do pipeline.
        paths (Dict): Caminhos dos arquivos gerados (raw, cleaned, features, etc).
        features (list): Lista de features utilizadas.
        corretora (str): Nome da corretora.
        symbol (str): Ativo (ex: EURUSD).
        timeframe (str): Timeframe (ex: M5).
        start_date (str): Data inicial.
        end_date (str): Data final.
        status (Dict): Status de cada etapa (opcional).
        log_path (str): Caminho do log de execução (opcional).
        update_only (bool): Se True, apenas atualiza campos do JSON existente.
        extra (Dict): Campos extras para atualizar/incluir.

    Raises:
        Exception: Qualquer erro na escrita ou atualização do JSON.
    """
    data = {}

    if update_only and os.path.exists(hash_path):
        # Carrega o JSON existente para atualização incremental
        with open(hash_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # Campos obrigatórios (apenas sobrescreve se update_only=False)
    if not update_only:
        data["hash"] = config_hash
        data["timestamp"] = timestamp
        data["config"] = config
        data["paths"] = paths
        data["features_used"] = features
        data["corretora"] = corretora
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["status"] = status or {k: "ok" if v else "pending" for k, v in paths.items()}
        if log_path:
            data["log"] = log_path
    else:
        # Atualização incremental: só sobrescreve campos informados
        if paths:
            data.setdefault("paths", {}).update(paths)
        if status:
            data.setdefault("status", {}).update(status)
        if extra:
            data.update(extra)
        if log_path:
            data["log"] = log_path

    # Permite campos extras sempre (ex: métricas, artefatos de modelo)
    if extra:
        data.update(extra)

    # Salva de forma segura
    with open(hash_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
