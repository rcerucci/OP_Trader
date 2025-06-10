# src/utils/mt5_connection.py

"""
mt5_connection.py

Módulo utilitário para conectar e desconectar do MetaTrader5 usando variáveis definidas no .env.
Permite log detalhado e controle seguro para integração do pipeline Op_Trader com o MT5.

- Carrega credenciais do .env
- Usa logger padronizado do projeto
- Decide log_level via CLI ou config.ini
- Logging informativo para todas as etapas
- Raise e logging explícito para variáveis ausentes, erro de inicialização e encerramento

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import MetaTrader5 as mt5
from dotenv import load_dotenv

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)

def load_log_level_from_config(section: str = "DIAGNOSIS", key: str = "log_level") -> Optional[str]:
    """
    Lê log_level do config.ini (fallback se CLI não informar).

    Args:
        section (str, optional): Seção do config.ini. Default 'DIAGNOSIS'.
        key (str, optional): Chave do nível de log. Default 'log_level'.

    Returns:
        Optional[str]: String do nível (ex: 'DEBUG', 'INFO'), ou None.
    """
    import configparser

    parser = configparser.ConfigParser()
    config_path = ROOT_DIR / "config.ini"
    parser.read(config_path)
    if parser.has_section(section):
        return parser.get(section, key, fallback=None).strip().upper()
    return None

def connect_to_mt5(cli_level: Optional[str] = None) -> bool:
    """
    Inicializa conexão com MetaTrader5, logando cada etapa.
    Carrega credenciais do .env localizado na raiz do projeto.

    Args:
        cli_level (Optional[str]): Nível de log para o logger ('DEBUG', 'INFO', etc).

    Returns:
        bool: True se conexão bem sucedida, False caso contrário.

    Raises:
        RuntimeError: Se variáveis obrigatórias não forem encontradas.

    Example:
        >>> ok = connect_to_mt5(cli_level='DEBUG')
        >>> if not ok:
        ...     raise RuntimeError("Falha ao conectar ao MT5")
    """
    env_path = ROOT_DIR / ".env"
    load_dotenv(dotenv_path=env_path)

    if cli_level is None:
        cli_level = load_log_level_from_config()

    logger = get_logger("mt5_connection", cli_level=cli_level)

    try:
        login = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")

        if not login or not password or not server:
            msg = "Uma ou mais variáveis MT5_LOGIN, MT5_PASSWORD ou MT5_SERVER não foram encontradas no ambiente."
            logger.error(msg)
            raise RuntimeError(msg)
        login = int(login)
    except Exception as e:
        logger.error("Erro ao carregar as variáveis do arquivo .env para MT5.")
        logger.debug(f"Detalhes: {e}")
        return False

    logger.debug(f"Tentando inicializar MT5 com login={login}, server={server}")
    try:
        if not mt5.initialize(login=login, password=password, server=server):
            code, msg = mt5.last_error()
            logger.error(f"Falha ao inicializar MT5: {code} - {msg}")
            return False
    except Exception as e:
        logger.error(f"Exceção ao tentar inicializar MT5: {e}")
        return False

    version = mt5.version()
    logger.info(f"Conectado ao MT5 (versão {version}).")
    return True

def close_mt5_connection(cli_level: Optional[str] = None) -> None:
    """
    Encerra conexão com MetaTrader5, registrando log da operação.

    Args:
        cli_level (Optional[str]): Nível de log.

    Raises:
        RuntimeError: Se falhar ao encerrar conexão.

    Example:
        >>> close_mt5_connection(cli_level="INFO")
    """
    if cli_level is None:
        cli_level = load_log_level_from_config()

    logger = get_logger("mt5_connection", cli_level=cli_level)
    try:
        mt5.shutdown()
        logger.info("Conexão com MT5 encerrada.")
    except Exception as e:
        logger.error(f"Falha ao encerrar conexão com MT5: {e}")
        raise RuntimeError(f"Falha ao encerrar conexão com MT5: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teste de conexão ao MetaTrader5 (MT5).")
    parser.add_argument(
        "--log-level", type=str, help="Nível de log: DEBUG, INFO, WARNING, ERROR ou NONE (fallback: config.ini)."
    )
    args = parser.parse_args()
    cli_level = args.log_level if args.log_level else load_log_level_from_config()

    success = connect_to_mt5(cli_level=cli_level)
    if not success:
        sys.exit(1)
    close_mt5_connection(cli_level=cli_level)
