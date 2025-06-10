"""
src/utils/vecnorm_loader.py
Utilitário para salvar e restaurar objetos VecNormalize do PPO de forma segura, garantindo compatibilidade com o pipeline Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-07
"""

import os
from typing import Optional
from stable_baselines3.common.vec_env import VecNormalize, VecEnv
from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

logger = get_logger(__name__)


def save_vecnormalize(env: VecNormalize, path: str) -> None:
    """
    Salva o estado atual de um objeto VecNormalize.

    Args:
        env (VecNormalize): Ambiente com normalização ativa.
        path (str): Caminho de destino para salvar o arquivo .pkl.

    Raises:
        ValueError: Se o ambiente não for uma instância de VecNormalize.
        IOError: Em caso de falha de escrita no disco.

    Example:
        >>> save_vecnormalize(env, "models/buy/vecnormalize.pkl")
    """
    if not isinstance(env, VecNormalize):
        raise ValueError("O ambiente fornecido não é uma instância de VecNormalize.")

    try:
        env.save(path)
        logger.info(f"VecNormalize salvo com sucesso em: {path}")
    except Exception as e:
        logger.error(f"Erro ao salvar VecNormalize: {e}")
        raise IOError(f"Falha ao salvar VecNormalize em {path}: {e}")


def load_vecnormalize(path: str, env: VecEnv) -> VecNormalize:
    """
    Carrega um objeto VecNormalize previamente salvo e o aplica ao ambiente fornecido.

    Args:
        path (str): Caminho do arquivo .pkl salvo.
        env (VecEnv): Ambiente base que será envolvido pela normalização carregada.

    Returns:
        VecNormalize: Ambiente com normalização restaurada.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        ValueError: Se o arquivo não contiver um VecNormalize válido.

    Example:
        >>> env = DummyVecEnv([...])
        >>> env = load_vecnormalize("models/buy/vecnormalize.pkl", env)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo VecNormalize não encontrado: {path}")

    try:
        env_norm = VecNormalize.load(path, env)
        logger.info(f"VecNormalize carregado de: {path}")
        return env_norm
    except Exception as e:
        logger.error(f"Erro ao carregar VecNormalize: {e}")
        raise ValueError(f"Falha ao carregar VecNormalize: {e}")
