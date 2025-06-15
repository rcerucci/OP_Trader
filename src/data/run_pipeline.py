#!/usr/bin/env python3
"""
src/data/run_pipeline.py

Runner Op_Trader: carrega .env do root, resolve e tipa todos os parâmetros,
monta dicionários robustos para cada etapa e injeta explicitamente no DataPipeline.

Nunca usa print — só logger.
100% robusto para produção/CI/CD.

Autor: Equipe Op_Trader
Data: 2025-06-14
"""

import argparse
import configparser
import os
import sys

from pathlib import Path
from dotenv import load_dotenv
from typing import Tuple, List, Dict, Any
from src.utils.path_setup import ensure_project_root
from src.utils.logging_utils import get_logger
from src.data.data_pipeline import DataPipeline

def parse_args():
    parser = argparse.ArgumentParser(
        description="Op_Trader Data Pipeline: coleta, limpeza, correção, features e normalização."
    )
    parser.add_argument("--config", "-c", help="Caminho para o arquivo config.ini", default="config.ini")
    parser.add_argument("--debug", action="store_true", help="Ativa logs DEBUG gerais")
    parser.add_argument("--diagnosis-log-level", help="Nível de log (NONE, ERROR, WARNING, INFO, DEBUG)")
    parser.add_argument("--diagnosis-debug-level", help="Nível detalhado de debug")
    parser.add_argument("--diagnosis-max-log-size", help="Tamanho máximo do arquivo de log")
    parser.add_argument("--diagnosis-backup-count", type=int, help="Qtd. de arquivos de backup de log")
    return parser.parse_args()

def load_config(path: str) -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(path, encoding='utf-8')
    return {sec: dict(cfg[sec]) for sec in cfg.sections()}

def merge_diagnosis_overrides(config: dict, args: argparse.Namespace):
    mapping = {
        "diagnosis_log_level": "log_level",
        "diagnosis_debug_level": "debug_level",
        "diagnosis_max_log_size": "max_log_size",
        "diagnosis_backup_count": "backup_count"
    }
    if "DIAGNOSIS" not in config:
        config["DIAGNOSIS"] = {}
    for cli_arg, ini_key in mapping.items():
        val = getattr(args, cli_arg, None)
        if val is not None:
            config["DIAGNOSIS"][ini_key] = str(val)

def parse_feature_params(feature_cfg: dict, logger=None) -> Tuple[List[str], Dict[str, Any]]:
    """
    Extrai e tipa features e parâmetros do bloco FEATURE_ENGINEER.
    Retorna:
        - features_lista: lista de features
        - features_params: dict {feature: {param: valor, ...}}
    """
    features_lista = [f.strip() for f in feature_cfg.get("features", "").split(",") if f.strip()]
    features_params = {}
    for k, v in feature_cfg.items():
        if k == "features":
            continue
        # Parse genérico: tenta extrair o nome da feature e do parâmetro por convenção
        # Ex: ema_fast_window -> feature=ema_fast, param=window
        try:
            if "_" in k:
                tokens = k.split("_")
                # Parâmetros mais comuns em features de finanças
                if tokens[-1] in {
                    "window", "lag", "method", "short", "long", "signal", "lookback", "bins",
                    "format", "mode", "threshold", "span", "n", "states", "pip_size", "min_hold"
                }:
                    feature = "_".join(tokens[:-1])
                    param = tokens[-1]
                else:
                    feature = k
                    param = "value"
            else:
                feature = k
                param = "value"

            # Conversão de tipo segura
            if v.lower() in {"true", "false"}:
                val_conv = v.lower() == "true"
            else:
                try:
                    val_conv = int(v)
                except Exception:
                    try:
                        val_conv = float(v)
                    except Exception:
                        val_conv = v  # mantém como string se não for número

            if feature not in features_params:
                features_params[feature] = {}
            features_params[feature][param] = val_conv
        except Exception as e:
            if logger:
                logger.warning(f"[feature_param_parse] Ignorando parâmetro '{k}' (valor '{v}'): {str(e)}")
            continue
    return features_lista, features_params

def parse_params(config_section: dict, exclude_keys=None, logger=None):
    """
    Extração e tipagem robusta para qualquer seção de parâmetros simples.
    Retorna dict no formato {chave: valor tipado}
    """
    result = {}
    exclude_keys = set(exclude_keys or [])
    for k, v in config_section.items():
        if k in exclude_keys:
            continue
        try:
            if v.lower() in {"true", "false"}:
                val_conv = v.lower() == "true"
            else:
                try:
                    val_conv = int(v)
                except Exception:
                    try:
                        val_conv = float(v)
                    except Exception:
                        val_conv = v
            result[k] = val_conv
        except Exception as e:
            if logger:
                logger.warning(f"[param_parse] Ignorando parâmetro '{k}' (valor '{v}'): {str(e)}")
    return result

def main():
    # 1. Setup do projeto e logger inicial
    project_root = ensure_project_root(__file__)
    dotenv_path = project_root / ".env"
    logger = get_logger("run_pipeline", cli_level="DEBUG")

    # 2. Carrega variáveis do .env
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        logger.info(f"Variáveis do .env carregadas do root do projeto: {dotenv_path}")
    else:
        logger.warning(f"Arquivo .env NÃO encontrado no root do projeto: {dotenv_path}")

    # 3. Valida credenciais sensíveis (exemplo: MT5)
    credenciais_mt5 = [
        os.environ.get("MT5_LOGIN"),
        os.environ.get("MT5_PASSWORD"),
        os.environ.get("MT5_SERVER")
    ]
    if not all(credenciais_mt5):
        logger.warning("Credenciais MT5 incompletas ou ausentes no .env.")

    # 4. Parse CLI/config, faz merge diagnosis
    args = parse_args()
    config = load_config(args.config)
    merge_diagnosis_overrides(config, args)
    if "META" not in config:
        config["META"] = {}
    config["META"]["raw_cli"] = " ".join(sys.argv[1:])

    # 5. Instancia logger definitivo conforme diagnosis
    log_level = config.get("DIAGNOSIS", {}).get("log_level", "DEBUG")
    logger = get_logger("run_pipeline", cli_level=log_level)
    logger.debug("Logger reconfigurado conforme diagnosis.")
    logger.info("Inicializando DataPipeline Op_Trader.")

    # 6. Resolve TODOS os parâmetros necessários para o DataPipeline
    data_cfg = config.get("DATA", {})
    gap_cfg = config.get("GAP_CORRECTOR", {})
    outlier_cfg = config.get("OUTLIER_CORRECTOR", {})
    scaler_cfg = config.get("SCALER", {})
    feature_cfg = config.get("FEATURE_ENGINEER", {})
    env_cfg = config.get("ENV", {})

    # 7. Parsing seguro dos parâmetros de features e outros dicionários!
    features_lista, features_params = parse_feature_params(feature_cfg, logger=logger)
    gap_params = parse_params(gap_cfg, logger=logger)
    outlier_params = parse_params(outlier_cfg, logger=logger)
    scaler_params = parse_params(scaler_cfg, logger=logger)

    logger.debug(f"Lista de features: {features_lista}")
    logger.debug(f"Dicionário de parâmetros de features: {features_params}")
    logger.debug(f"Parâmetros de gaps: {gap_params}")
    logger.debug(f"Parâmetros de outliers: {outlier_params}")
    logger.debug(f"Parâmetros de scaler: {scaler_params}")

    pipeline_args = {
        "config": config,
        "mode": env_cfg.get("mode", "batch"),
        "pipeline_type": data_cfg.get("pipeline_type", "ppo"),
        "symbol": data_cfg.get("symbols", "EURUSD").split(",")[0].strip(),
        "timeframe": data_cfg.get("timeframes", "M5").split(",")[0].strip(),
        "features": features_lista,
        "features_params": features_params,
        "start_date": data_cfg.get("start_date", ""),
        "end_date": data_cfg.get("end_date", ""),
        "volume_sources": [v.strip() for v in data_cfg.get("volume_sources", "real_volume,tick_volume,volume").split(",") if v.strip()],
        "volume_column": data_cfg.get("volume_column", "").strip(),
        "dirs": {
            "raw": data_cfg.get("raw_dir", "data/raw"),
            "cleaned": data_cfg.get("cleaned_dir", "data/cleaned"),
            "corrected": data_cfg.get("corrected_dir", "data/corrected"),
            "features": data_cfg.get("features_dir", "data/features"),
            "features_normalized": data_cfg.get("features_normalized_dir", "data/features_normalized"),
            "scaler": data_cfg.get("scaler_dir", "data/scaler"),
            "final_ppo": data_cfg.get("final_ppo_dir", "data/final_ppo"),
            "final_mlp": data_cfg.get("final_mlp_dir", "data/final_mlp"),
        },
        "gap_params": gap_params,
        "outlier_params": outlier_params,
        "scaler_params": scaler_params,
        "debug": args.debug,
        "callbacks": None,
    }

    logger.debug(f"Parâmetros finais injetados no DataPipeline: {pipeline_args}")

    # 8. Instancia e executa o pipeline (agora tudo passado explicitamente!)
    pipeline = DataPipeline(**pipeline_args)
    result = pipeline.run()

    logger.info(f"Pipeline finalizado. Etapas executadas: {list(pipeline.outputs.keys())}")

if __name__ == '__main__':
    main()
