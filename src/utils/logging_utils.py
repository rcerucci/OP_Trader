# src/utils/logging_utils.py

"""
logging_utils.py
----------------
Camada central de logging do projeto Op_Trader.

Propósito:
    - Carregar o nível de log a partir do ``config.ini`` ou via CLI.
    - Criar loggers padronizados, coloridos (usando *colorlog* se disponível), compatíveis com qualquer ambiente.
    - Garantir que não haja duplicidade de handlers.
    - Padrão para toda execução (scripts, notebooks, testes, produção).

Exemplo rápido de uso:
    >>> from src.utils.logging_utils import get_logger
    >>> log = get_logger(__name__, cli_level="DEBUG")
    >>> log.info("Mensagem de teste")

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import configparser
import logging
from pathlib import Path
from typing import Optional, Union

from src.utils.path_setup import ensure_project_root

ROOT_DIR: Path = ensure_project_root(__file__)

LOG_LEVELS: dict[str, int] = {
    "NONE": logging.CRITICAL + 10,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}

def load_log_level_from_config(section: str = "DIAGNOSIS", key: str = "log_level") -> int:
    """
    Carrega o nível de log padrão do projeto, definido em config.ini.

    Args:
        section (str): Seção do config.ini (default: "DIAGNOSIS").
        key (str): Chave dentro da seção (default: "log_level").

    Returns:
        int: Nível numérico compatível com logging (e.g., logging.INFO).

    Example:
        >>> load_log_level_from_config()
        20  # logging.INFO
    """
    config_path = ROOT_DIR / "config.ini"
    parser = configparser.ConfigParser()
    parser.read(config_path, encoding='utf-8')
    if parser.has_section(section):
        level_str = parser.get(section, key, fallback="WARNING").strip().upper()
        return LOG_LEVELS.get(level_str, logging.WARNING)
    return logging.WARNING

def _create_console_handler() -> logging.Handler:
    """
    Cria um handler de console padronizado para o projeto.

    Tenta usar colorlog, caso não exista usa logging padrão.

    Returns:
        logging.Handler: Handler pronto para adicionar ao logger.
    """
    try:
        import colorlog  # type: ignore
        handler: logging.Handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        )
    except ImportError:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    handler.setLevel(logging.NOTSET)
    return handler

def get_logger(name: str, cli_level: Optional[Union[int, str]] = None) -> logging.Logger:
    """
    Obtém um logger padronizado do projeto Op_Trader.

    Args:
        name (str): Nome do logger, geralmente __name__.
        cli_level (int | str | None): Nível passado via CLI ou código.
            Aceita: "DEBUG", "INFO", int do logging, ou None (lê do config.ini).

    Returns:
        logging.Logger: Logger configurado, pronto para uso.

    Example:
        >>> log = get_logger("pipeline", cli_level="DEBUG")
        >>> log.info("Processo iniciado")
    """
    if isinstance(cli_level, int):
        level_num = cli_level
    elif isinstance(cli_level, str):
        level_num = LOG_LEVELS.get(cli_level.strip().upper(), logging.WARNING)
    else:
        level_num = load_log_level_from_config()

    logger = logging.getLogger(name)

    # Remove handlers antigos (evita duplicação em reloads)
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    logger.setLevel(level_num)
    logger.addHandler(_create_console_handler())
    logger.propagate = False

    return logger

# --- Exemplo de integração com tqdm (na docstring, não no código):
"""
Para logs em loops com barra de progresso (tqdm):

    from tqdm import tqdm

    for i in tqdm(range(100)):
        # Use tqdm.write para logs que não quebrem a barra:
        tqdm.write("Mensagem logada")

    # Ou crie um logger extra para logs no loop.
"""

# Não executar demonstração local no import; testes ficam em test_logging_utils.py

