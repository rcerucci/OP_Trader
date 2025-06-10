#!/usr/bin/env python3
"""
src/env/wrappers/normalization_wrapper.py
Wrapper plugável para normalização online/reversível de observações e recompensas em ambientes RL Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import gymnasium as gym
import numpy as np
from src.utils.logging_utils import get_logger
from src.utils.vecnorm_loader import save_vecnormalize, load_vecnormalize
import os

class NormalizationWrapper(gym.Wrapper):
    """
    Wrapper plugável para normalização de observações e recompensas em ambientes RL do Op_Trader.

    Suporta múltiplas estratégias (vecnorm, z_score, minmax, none), persistência do estado, auditoria e logging detalhado.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        norm_type (str): Estratégia de normalização ("vecnorm", "z_score", "minmax", "none").
        obs_stats (dict, opcional): Parâmetros prévios de normalização de observações.
        reward_stats (dict, opcional): Parâmetros prévios de normalização de recompensas.
        logger (Logger, opcional): Logger estruturado.
        save_path (str, opcional): Caminho padrão para persistência.
        debug (bool): Ativa logs detalhados.
    """
    def __init__(self, env, norm_type: str = "vecnorm", obs_stats: dict = None, reward_stats: dict = None, logger=None, save_path: str = None, debug: bool = False, **kwargs):
        super().__init__(env)
        self.env = env
        self.norm_type = norm_type.lower()
        self.obs_stats = obs_stats or {}
        self.reward_stats = reward_stats or {}
        self.save_path = save_path
        self.debug = debug
        self.logger = logger or get_logger("NormalizationWrapper", cli_level="DEBUG" if debug else "INFO")
        self._lock = threading.RLock()

        # Estruturas internas para estatísticas
        self._obs_running_mean = None
        self._obs_running_std = None
        self._rew_running_mean = None
        self._rew_running_std = None
        self._obs_min = None
        self._obs_max = None
        self._n_steps = 0
        self._initialized = False

        self._init_stats()
        self.logger.info(f"NormalizationWrapper inicializado com norm_type={self.norm_type}")

    def _init_stats(self):
        """Inicializa ou restaura as estatísticas de normalização."""
        with self._lock:
            self._n_steps = 0
            self._initialized = False
            self._obs_running_mean = None
            self._obs_running_std = None
            self._rew_running_mean = None
            self._rew_running_std = None
            self._obs_min = None
            self._obs_max = None

    def reset(self, **kwargs):
        """
        Reinicia o ambiente e estatísticas de normalização.

        Returns:
            obs, info: Observação inicial normalizada e info.
        """
        with self._lock:
            obs, info = self.env.reset(**kwargs)
            self._n_steps = 0
            if self.norm_type == "vecnorm" and self.save_path and os.path.exists(self.save_path):
                try:
                    # Carrega normalização existente via utilitário oficial
                    self.env = load_vecnormalize(self.save_path, self.env)
                    self.logger.info(f"Normalização VecNormalize carregada de {self.save_path} no reset.")
                except Exception as e:
                    self.logger.warning(f"Falha ao carregar estado de normalização: {e}")
            # Recalcula stats se necessário
            obs = self._normalize_obs(obs)
            self._initialized = True
            return obs, info

    def step(self, action):
        """
        Executa step, normalizando observação e recompensa.

        Args:
            action: Ação do agente.

        Returns:
            obs, reward, terminated, truncated, info
        """
        with self._lock:
            obs, reward, terminated, truncated, info = self.env.step(action)
            self._n_steps += 1
            obs = self._normalize_obs(obs)
            reward = self._normalize_reward(reward)
            return obs, reward, terminated, truncated, info

    def _normalize_obs(self, obs):
        """Aplica normalização configurada na observação."""
        try:
            arr = np.asarray(obs, dtype=np.float32)
            if self.norm_type == "z_score":
                if self._obs_running_mean is None:
                    self._obs_running_mean = arr.copy()
                    self._obs_running_std = np.ones_like(arr)
                else:
                    # running mean/std
                    alpha = 0.01
                    self._obs_running_mean = (1 - alpha) * self._obs_running_mean + alpha * arr
                    self._obs_running_std = (1 - alpha) * self._obs_running_std + alpha * np.abs(arr - self._obs_running_mean)
                normalized = (arr - self._obs_running_mean) / (self._obs_running_std + 1e-8)
                return normalized
            elif self.norm_type == "minmax":
                if self._obs_min is None or self._obs_max is None:
                    self._obs_min = arr.copy()
                    self._obs_max = arr.copy()
                else:
                    self._obs_min = np.minimum(self._obs_min, arr)
                    self._obs_max = np.maximum(self._obs_max, arr)
                normalized = (arr - self._obs_min) / (self._obs_max - self._obs_min + 1e-8)
                return normalized
            elif self.norm_type == "vecnorm":
                # Se env já é VecNormalize, delega
                return arr
            else:  # "none"
                return arr
        except Exception as e:
            self.logger.warning(f"Falha ao normalizar observação: {e}")
            return obs

    def _normalize_reward(self, reward):
        """Aplica normalização configurada na recompensa."""
        try:
            arr = np.asarray(reward, dtype=np.float32)
            if self.norm_type == "z_score":
                if self._rew_running_mean is None:
                    self._rew_running_mean = arr.copy()
                    self._rew_running_std = np.ones_like(arr)
                else:
                    alpha = 0.01
                    self._rew_running_mean = (1 - alpha) * self._rew_running_mean + alpha * arr
                    self._rew_running_std = (1 - alpha) * self._rew_running_std + alpha * np.abs(arr - self._rew_running_mean)
                normalized = (arr - self._rew_running_mean) / (self._rew_running_std + 1e-8)
                return normalized
            elif self.norm_type == "minmax":
                if self._rew_running_mean is None or self._rew_running_std is None:
                    self._rew_running_mean = arr.copy()
                    self._rew_running_std = arr.copy()
                else:
                    self._rew_running_mean = np.minimum(self._rew_running_mean, arr)
                    self._rew_running_std = np.maximum(self._rew_running_std, arr)
                normalized = (arr - self._rew_running_mean) / (self._rew_running_std - self._rew_running_mean + 1e-8)
                return normalized
            elif self.norm_type == "vecnorm":
                # Se env já é VecNormalize, delega
                return arr
            else:
                return arr
        except Exception as e:
            self.logger.warning(f"Falha ao normalizar reward: {e}")
            return reward

    def save_norm_state(self, path: str = None):
        """
        Persiste o estado atual de normalização (VecNormalize).

        Args:
            path (str, opcional): Caminho do arquivo destino.
        """
        with self._lock:
            if self.norm_type == "vecnorm":
                p = path or self.save_path
                if p:
                    try:
                        save_vecnormalize(self.env, p)
                        self.logger.info(f"Estado de normalização salvo em {p}")
                    except Exception as e:
                        self.logger.error(f"Erro ao salvar estado de normalização: {e}")
                else:
                    self.logger.warning("Nenhum caminho para salvar estado de normalização foi definido.")

    def load_norm_state(self, path: str = None):
        """
        Restaura estado de normalização salvo.

        Args:
            path (str, opcional): Caminho do arquivo salvo.
        """
        with self._lock:
            if self.norm_type == "vecnorm":
                p = path or self.save_path
                if p and os.path.exists(p):
                    try:
                        self.env = load_vecnormalize(p, self.env)
                        self.logger.info(f"Estado de normalização restaurado de {p}")
                    except Exception as e:
                        self.logger.error(f"Erro ao restaurar estado de normalização: {e}")
                else:
                    self.logger.warning("Arquivo de estado de normalização não encontrado.")

    def get_norm_params(self) -> dict:
        """
        Retorna snapshot dos parâmetros/estatísticas de normalização.

        Returns:
            dict: Estatísticas atuais de normalização.
        """
        with self._lock:
            return {
                "norm_type": self.norm_type,
                "obs_mean": None if self._obs_running_mean is None else self._obs_running_mean.tolist(),
                "obs_std": None if self._obs_running_std is None else self._obs_running_std.tolist(),
                "rew_mean": None if self._rew_running_mean is None else self._rew_running_mean.tolist(),
                "rew_std": None if self._rew_running_std is None else self._rew_running_std.tolist(),
                "obs_min": None if self._obs_min is None else self._obs_min.tolist(),
                "obs_max": None if self._obs_max is None else self._obs_max.tolist(),
                "n_steps": self._n_steps
            }

    def close(self):
        """
        Garante salvamento/flush final do estado de normalização.
        """
        with self._lock:
            try:
                self.save_norm_state()
            except Exception as e:
                self.logger.critical(f"Falha ao salvar estado de normalização no close: {e}")
            if hasattr(self.env, "close"):
                self.env.close()
