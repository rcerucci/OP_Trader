# src/utils/path_setup.py

"""
path_setup.py

Utilitário para garantir que a raiz do projeto esteja no sys.path para imports absolutos,
buscando de forma robusta o root do projeto (onde está o .env ou pyproject.toml),
independente do nível de profundidade de onde o script é executado.

Padrão recomendado para projetos profissionais, pipelines, notebooks e testes.

Exemplo de uso:
    from src.utils.path_setup import ensure_project_root
    ROOT_DIR = ensure_project_root(__file__)

- Sempre preferir imports absolutos em todo o projeto.
- Robustez total: encontra o root mesmo se estrutura de pastas mudar ou for chamado de subdiretório profundo.
- Logging integrado (opcional), seguro para todos os contextos.

Autor: Equipe Op_Trader
Data: 2025-06-10 (versão robusta universal)
"""

import sys
from pathlib import Path
from typing import Union

def ensure_project_root(cur_file: Union[str, Path]) -> Path:
    """
    Garante que a raiz do projeto (onde está o .env ou pyproject.toml) esteja no sys.path
    para permitir imports absolutos em qualquer contexto.

    Sobe diretórios a partir do arquivo até encontrar o root do projeto.

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
    file_path = Path(cur_file).resolve()
    # Marcares possíveis de root: .env, pyproject.toml, .git
    markers = [".env", "pyproject.toml", ".git"]
    for parent in [file_path] + list(file_path.parents):
        if any((parent / marker).exists() for marker in markers):
            if str(parent) not in sys.path:
                sys.path.append(str(parent))
                # Logging opcional (se disponível)
                try:
                    from src.utils.logging_utils import get_logger
                    logger = get_logger("path_setup")
                    logger.debug(f"Raiz do projeto adicionada ao sys.path: {parent}")
                except Exception:
                    pass
            return parent
    raise ValueError(
        f"Raiz do projeto não encontrada a partir de '{cur_file}'. "
        "Certifique-se de que .env, pyproject.toml ou .git estejam no root."
    )
