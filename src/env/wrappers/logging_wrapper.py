#!/usr/bin/env python3
"""
src/env/wrappers/logging_wrapper.py
Wrapper plugável para logging estruturado e detalhado de steps, resets, episódios, ações, rewards e eventos de ambiente RL no Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import gymnasium as gym
from src.utils.logging_utils import get_logger
from src.env.env_libs.trade_logger import TradeLogger
from src.utils.file_saver import build_filename, save_dataframe, get_timestamp
import pandas as pd
import os
import json

class LoggingWrapper(gym.Wrapper):
    """
    Wrapper plugável para logging estruturado de ambientes RL.

    Permite logging detalhado (steps, resets, episódios, ações, rewards, eventos críticos)
    sem poluir o ambiente principal. Integra com logger do projeto, TradeLogger, file_saver.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        logger (Logger, optional): Logger estruturado do projeto.
        trade_logger (TradeLogger, optional): Logger especializado para trades.
        log_level (str): Nível de logging ("DEBUG", "INFO", "AUDIT").
        log_dir (str, optional): Diretório para salvar logs.
        debug (bool): Se True, ativa logging detalhado.
        **kwargs: Argumentos adicionais plugáveis.
    """

    def __init__(self, env, logger=None, trade_logger=None, log_level: str = "INFO", log_dir: str = None, debug: bool = False, **kwargs):
        super().__init__(env)
        self.env = env
        self.log_level = log_level.upper()
        self.log_dir = log_dir or "logs/episodes"
        os.makedirs(self.log_dir, exist_ok=True)
        self.debug = debug
        if logger is not None:
            self.logger = logger
        else:
            cli_lvl = "DEBUG" if debug or self.log_level == "DEBUG" else self.log_level
            self.logger = get_logger("LoggingWrapper", cli_level=cli_lvl)
        self.trade_logger = trade_logger
        self._lock = threading.RLock()
        self._logs = []
        self._episode = 0
        self._current_episode_log = None

    def reset(self, **kwargs):
        """
        Reinicia o ambiente e loga o contexto inicial, seed, episódio.

        Returns:
            obs, info: Observação inicial e info do reset.
        """
        if self._episode == 0:
            init_log = {
                "event": "INIT",
                "episode": 0,
                "data": {"msg": "LoggingWrapper inicializado", "log_level": self.log_level},
                "timestamp": get_timestamp()
            }
            episode_log = [init_log]
        else:
            episode_log = []
        # depois segue normalmente, anexando reset_log...

        with self._lock:
            self._episode += 1
            obs, info = self.env.reset(**kwargs)
            reset_log = {
                "event": "reset",
                "episode": self._episode,
                "obs": self._serialize_obs(obs),
                "info": info,
                "timestamp": get_timestamp(),
                "seed": kwargs.get("seed", None)
            }
            episode_log = [reset_log]
            self._current_episode_log = episode_log
            self._logs.append(self._current_episode_log)
            self.logger.info(f"Ambiente resetado (episódio {self._episode})")
            return obs, info

    def step(self, action):
        """
        Executa step, logando ação, reward, done, contexto antes/depois e exceções.

        Args:
            action: Ação a ser tomada.

        Returns:
            obs, reward, terminated, truncated, info
        """
        with self._lock:
            try:
                obs, reward, terminated, truncated, info = self.env.step(action)
                step_log = {
                    "event": "step",
                    "episode": self._episode,
                    "action": self._serialize_action(action),
                    "obs": self._serialize_obs(obs),
                    "reward": float(reward),
                    "terminated": bool(terminated),
                    "truncated": bool(truncated),
                    "info": info,
                    "timestamp": get_timestamp()
                }
                if self._current_episode_log is None:
                    # Inicia novo episódio se necessário
                    self._current_episode_log = [step_log]
                    self._logs.append(self._current_episode_log)
                else:
                    self._current_episode_log.append(step_log)
                if self.trade_logger:
                    try:
                        self.trade_logger.log_step(step_log)
                    except Exception as e:
                        self.logger.warning(f"Falha ao logar no TradeLogger: {e}")
                self.logger.debug(f"Step registrado: ação={action}, reward={reward}, terminated={terminated}, truncated={truncated}")
                return obs, reward, terminated, truncated, info
            except Exception as e:
                err_log = {
                    "event": "error",
                    "episode": self._episode,
                    "error": str(e),
                    "timestamp": get_timestamp()
                }
                if self._current_episode_log is None:
                    self._current_episode_log = [err_log]
                    self._logs.append(self._current_episode_log)
                else:
                    self._current_episode_log.append(err_log)
                self.logger.error(f"Erro durante step: {e}")
                raise

    def log_event(self, event_type: str, data: dict):
        """
        Loga evento customizado (ex: risco, intervenção, métricas externas).

        Args:
            event_type (str): Tipo do evento.
            data (dict): Dados do evento.

        Returns:
            None
        """
        with self._lock:
            try:
                log = {
                    "event": event_type,
                    "episode": self._episode,
                    "data": data,
                    "timestamp": get_timestamp()
                }
                if self._current_episode_log is None:
                    self._current_episode_log = [log]
                    self._logs.append(self._current_episode_log)
                else:
                    self._current_episode_log.append(log)
                self.logger.info(f"Evento logado: {event_type} | {data}")
            except Exception as e:
                self.logger.warning(f"Evento malformado não logado: {e}")

    def save_logs(self, path: str = None):
        """
        Salva os logs do episódio/ciclo em arquivo CSV e JSON padronizados.

        Args:
            path (str, optional): Caminho do arquivo base de logs.

        Returns:
            None
        """
        with self._lock:
            base_filename = path or build_filename(
                prefix=self.log_dir,
                suffix="logging",
                asset="env",
                timeframe=f"ep{self._episode}",
                period=None,
                timestamp=get_timestamp(),
                extension=None  # Adiciona .csv e .json
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
                self.logger.info(f"Logs salvos: {csv_path} | {json_path}")
            except Exception as e:
                self.logger.critical(f"Falha ao salvar logs: {e}")

    def get_logs(self) -> dict:
        """
        Retorna todos os logs acumulados do wrapper.

        Returns:
            dict: Logs por episódio.
        """
        with self._lock:
            return {"episodes": self._logs}

    def close(self):
        """
        Garante salvamento e flush dos logs pendentes.
        """
        with self._lock:
            try:
                self.save_logs()
            except Exception as e:
                self.logger.critical(f"Falha ao salvar logs no close: {e}")
            if hasattr(self.env, "close"):
                self.env.close()

    def _log_event(self, event_type, data):
        """
        Loga evento interno thread-safe (apenas para inicialização, etc).
        """
        with self._lock:
            log = {
                "event": event_type,
                "episode": self._episode,
                "data": data,
                "timestamp": get_timestamp()
            }
            if self._current_episode_log is None:
                self._current_episode_log = [log]
                self._logs.append(self._current_episode_log)
            else:
                self._current_episode_log.append(log)

    @staticmethod
    def _serialize_obs(obs):
        """Serializa observação para logging seguro."""
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
        """Serializa ação para logging seguro."""
        try:
            if isinstance(action, (int, float, str)):
                return action
            if hasattr(action, "tolist"):
                return action.tolist()
            return str(action)
        except Exception:
            return "unserializable_action"
