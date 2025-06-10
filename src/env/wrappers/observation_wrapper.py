#!/usr/bin/env python3
"""
src/env/wrappers/observation_wrapper.py
Wrapper plugável para transformação, filtragem e logging de observações em ambientes RL do Op_Trader.
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

class ObservationWrapper(gym.Wrapper):
    """
    Wrapper para transformação, filtragem e logging de observações no RL Op_Trader.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        obs_fn (callable, opcional): Função customizada de transformação da observação.
        logger (Logger, opcional): Logger estruturado Op_Trader.
        log_dir (str, opcional): Diretório para salvar logs.
        debug (bool): Ativa logs detalhados.
    """

    def __init__(self, env, obs_fn=None, logger=None, log_dir: str = None, debug: bool = False, **kwargs):
        super().__init__(env)
        self.env = env
        self.obs_fn = obs_fn
        self.log_dir = log_dir or "logs/observation"
        os.makedirs(self.log_dir, exist_ok=True)
        self.debug = debug
        self.logger = logger or get_logger("ObservationWrapper", cli_level="DEBUG" if debug else "INFO")
        self._lock = threading.RLock()
        self._logs = []
        self._episode = 0
        self._current_episode_log = []
        self.logger.info("ObservationWrapper inicializado.")

    def reset(self, **kwargs):
        """
        Reinicia o ambiente e aplica obs_fn à observação inicial.

        Returns:
            obs, info: Observação inicial (potencialmente transformada) e info do reset.
        """
        with self._lock:
            self._episode += 1
            obs, info = self.env.reset(**kwargs)
            transformed_obs = self._apply_obs_fn(obs)
            reset_log = {
                "event": "reset",
                "episode": self._episode,
                "original_obs": self._serialize_obs(obs),
                "transformed_obs": self._serialize_obs(transformed_obs),
                "info": info,
                "timestamp": get_timestamp()
            }
            self._current_episode_log = [reset_log]
            self._logs.append(self._current_episode_log)
            self.logger.info(f"Ambiente resetado (episódio {self._episode})")
            return transformed_obs, info

    def step(self, action):
        """
        Executa step, aplica obs_fn à observação e loga transformação.

        Args:
            action: Ação do agente.

        Returns:
            obs, reward, terminated, truncated, info
        """
        with self._lock:
            obs, reward, terminated, truncated, info = self.env.step(action)
            original_obs = obs
            transformed_obs = self._apply_obs_fn(obs)
            log = {
                "event": "step",
                "episode": self._episode,
                "action": self._serialize_action(action),
                "original_obs": self._serialize_obs(original_obs),
                "transformed_obs": self._serialize_obs(transformed_obs),
                "reward": float(reward),
                "terminated": bool(terminated),
                "truncated": bool(truncated),
                "info": info,
                "timestamp": get_timestamp()
            }
            self._current_episode_log.append(log)
            self.logger.debug(f"Observação transformada no step: {self._serialize_obs(original_obs)} -> {self._serialize_obs(transformed_obs)}")
            return transformed_obs, reward, terminated, truncated, info

    def set_obs_fn(self, obs_fn):
        """
        Troca dinâmica da função de transformação de observação.

        Args:
            obs_fn (callable): Nova função de transformação.
        """
        with self._lock:
            self.obs_fn = obs_fn
            self.logger.info("Função de transformação de observação atualizada.")

    def save_logs(self, path: str = None):
        """
        Salva logs de observação em CSV/JSON padronizados.

        Args:
            path (str, opcional): Caminho base dos arquivos.
        """
        with self._lock:
            base_filename = path or build_filename(
                prefix=self.log_dir,
                suffix="observation",
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
                self.logger.info(f"Logs de observação salvos: {csv_path} | {json_path}")
            except Exception as e:
                self.logger.critical(f"Falha ao salvar logs de observação: {e}")

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

    def _apply_obs_fn(self, obs):
        """Aplica obs_fn à observação, com validação e logging de edge case."""
        try:
            if self.obs_fn:
                transformed = self.obs_fn(obs)
                if not self._validate_obs(transformed):
                    self.logger.warning("Obs transformada inválida (NaN, tipo ou shape). Usando obs original.")
                    return obs
                return transformed
            return obs
        except Exception as e:
            self.logger.warning(f"obs_fn lançou exceção: {e}. Usando obs original.")
            return obs

    @staticmethod
    def _validate_obs(obs):
        """Valida se obs é numérica, sem NaN/inf e tem shape compatível."""
        arr = np.asarray(obs)
        if not np.issubdtype(arr.dtype, np.number):
            return False
        if not np.all(np.isfinite(arr)):
            return False
        return True

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
