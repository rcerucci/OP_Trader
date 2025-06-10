# src/utils/path_setup.py

"""
path_setup.py

Módulo utilitário para garantir que a raiz do projeto esteja no sys.path.
Essencial para garantir imports absolutos e evitar problemas em execução
de scripts a partir de diferentes diretórios.

Exemplo de uso:
    from src.utils.path_setup import ensure_project_root

    ROOT_DIR = ensure_project_root(__file__)

- Sempre preferir imports absolutos em todos os scripts do projeto.
- Este módulo é fundamental para garantir compatibilidade com a estrutura src/.

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import sys
from pathlib import Path
from typing import Union

def ensure_project_root(cur_file: Union[str, Path]) -> Path:
    """
    Garante que a raiz do projeto esteja no sys.path para permitir imports absolutos.

    Args:
        cur_file (str | Path): Caminho do arquivo atual (__file__).

    Returns:
        Path: Objeto Path apontando para a raiz do projeto.

    Raises:
        ValueError: Se não for possível resolver o caminho esperado da raiz.

    Example:
        >>> from src.utils.path_setup import ensure_project_root
        >>> ROOT_DIR = ensure_project_root(__file__)
    """
    try:
        file_path = Path(cur_file).resolve()
        # A raiz do projeto é 2 níveis acima do arquivo (ajustado à estrutura src/)
        root = file_path.parents[2]
    except Exception as e:
        raise ValueError(
            f"Falha ao identificar raiz do projeto a partir de '{cur_file}': {e}"
        )

    if str(root) not in sys.path:
        sys.path.append(str(root))
        # Logging opcional, se logging_utils já estiver carregado:
        try:
            from src.utils.logging_utils import get_logger
            logger = get_logger("path_setup")
            logger.debug(f"Adicionada raiz do projeto ao sys.path: {root}")
        except Exception:
            # logging_utils pode não estar disponível ainda na inicialização
            pass

    return root
