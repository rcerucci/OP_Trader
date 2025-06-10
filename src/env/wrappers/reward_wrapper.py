#!/usr/bin/env python3
"""
src/env/wrappers/reward_wrapper.py
Wrapper plugável para pós-processamento, transformação e logging de recompensas em ambientes RL do Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import gymnasium as gym
from src.utils.logging_utils import get_logger
from src.utils.file_saver import build_filename, save_dataframe, get_timestamp
import pandas as pd
import os
import json
import numpy as np

class RewardWrapper(gym.Wrapper):
    """
    Wrapper para modificação, pós-processamento e logging de recompensas no RL Op_Trader.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        reward_fn (callable, opcional): Função customizada para transformação da reward.
        logger (Logger, opcional): Logger estruturado Op_Trader.
        log_dir (str, opcional): Diretório para salvar logs.
        debug (bool): Ativa logs detalhados.
    """

    def __init__(self, env, reward_fn=None, logger=None, log_dir: str = None, debug: bool = False, **kwargs):
        super().__init__(env)
        self.env = env
        self.reward_fn = reward_fn
        self.log_dir = log_dir or "logs/reward"
        os.makedirs(self.log_dir, exist_ok=True)
        self.debug = debug
        self.logger = logger or get_logger("RewardWrapper", cli_level="DEBUG" if debug else "INFO")
        self._lock = threading.RLock()
        self._logs = []
        self._episode = 0
        self._current_episode_log = []
        self.logger.info("RewardWrapper inicializado.")

    def reset(self, **kwargs):
        """
        Reinicia o ambiente e os logs de reward.

        Returns:
            obs, info: Observação inicial e info do reset.
        """
        with self._lock:
            self._episode += 1
            obs, info = self.env.reset(**kwargs)
            reset_log = {
                "event": "reset",
                "episode": self._episode,
                "obs": self._serialize_obs(obs),
                "info": info,
                "timestamp": get_timestamp()
            }
            self._current_episode_log = [reset_log]
            self._logs.append(self._current_episode_log)
            self.logger.info(f"Ambiente resetado (episódio {self._episode})")
            return obs, info

    def step(self, action):
        """
        Executa step, aplica reward_fn e loga transformação.

        Args:
            action: Ação do agente.

        Returns:
            obs, reward, terminated, truncated, info
        """
        with self._lock:
            obs, reward, terminated, truncated, info = self.env.step(action)
            original_reward = reward
            transformed = False

            try:
                if self.reward_fn:
                    reward = self.reward_fn(reward)
                    transformed = True
            except Exception as e:
                self.logger.warning(f"reward_fn lançou exceção: {e}. Usando reward original.")
                reward = original_reward

            # Corrige NaN, inf ou tipo não numérico
            if not np.isscalar(reward) or not np.isfinite(reward):
                self.logger.warning(f"Reward inválida detectada ({reward}), corrigida para zero.")
                reward = 0.0

            log = {
                "event": "step",
                "episode": self._episode,
                "action": self._serialize_action(action),
                "original_reward": float(original_reward),
                "transformed_reward": float(reward),
                "transformed": transformed,
                "terminated": bool(terminated),
                "truncated": bool(truncated),
                "info": info,
                "timestamp": get_timestamp()
            }
            self._current_episode_log.append(log)
            self.logger.debug(f"Reward transformada: {original_reward} -> {reward}, ação={action}")
            return obs, reward, terminated, truncated, info

    def set_reward_fn(self, reward_fn):
        """
        Troca dinâmica da função de transformação de reward.

        Args:
            reward_fn (callable): Nova função de transformação.
        """
        with self._lock:
            self.reward_fn = reward_fn
            self.logger.info("Função de transformação de reward atualizada.")

    def save_logs(self, path: str = None):
        """
        Salva logs do episódio/ciclo em CSV/JSON padronizados.

        Args:
            path (str, opcional): Caminho base dos arquivos.
        """
        with self._lock:
            base_filename = path or build_filename(
                prefix=self.log_dir,
                suffix="reward",
                asset="env",
                timeframe=f"ep{self._episode}",
                period=None,
                timestamp=get_timestamp(),
                extension=None
            )
            csv_path = f"{base_filename}.csv"
            json_path = f"{base_filename}.json"

            flat_logs = []
            for ep in self._logs:
                for entry in ep:
                    flat_logs.append(entry)

            try:
                df = pd.DataFrame(flat_logs)
                save_dataframe(df, csv_path)
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(flat_logs, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Logs de reward salvos: {csv_path} | {json_path}")
            except Exception as e:
                self.logger.critical(f"Falha ao salvar logs de reward: {e}")

    def get_logs(self) -> dict:
        """
        Retorna todos os logs acumulados.

        Returns:
            dict: Logs por episódio.
        """
        with self._lock:
            return {"episodes": self._logs}

    def close(self):
        """
        Garante salvamento/flush dos logs pendentes.
        """
        with self._lock:
            try:
                self.save_logs()
            except Exception as e:
                self.logger.critical(f"Falha ao salvar logs no close: {e}")
            if hasattr(self.env, "close"):
                self.env.close()

    @staticmethod
    def _serialize_obs(obs):
        try:
            if isinstance(obs, (int, float, str)):
                return obs
            if hasattr(obs, "tolist"):
                return obs.tolist()
            return str(obs)
        except Exception:
            return "unserializable_obs"

    @staticmethod
    def _serialize_action(action):
        try:
            if isinstance(action, (int, float, str)):
                return action
            if hasattr(action, "tolist"):
                return action.tolist()
            return str(action)
        except Exception:
            return "unserializable_action"
