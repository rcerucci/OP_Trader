#!/usr/bin/env python3
"""
src/env/environments/base_env.py
Ambiente RL base universal do Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import gymnasium as gym
import numpy as np
from src.utils.logging_utils import get_logger

class BaseEnv(gym.Env):
    """
    Ambiente RL base universal do pipeline Op_Trader.
    Serve como contrato para ambientes específicos (long, short, etc.) e integra macro-contexto, risk, position, reward e logging padronizado.

    Args:
        allowed_actions (list[str]): Ações permitidas (ex: ["buy", "hold"]).
        context_macro (dict, opcional): Dicionário de contexto macro (ex: direção, regime, etc).
        risk_manager (obj, opcional): Gerenciador de risco plugável.
        position_manager (obj, opcional): Gerenciador de posições plugável.
        reward_aggregator (obj, opcional): Agregador de recompensas plugável.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
        kwargs: Opções adicionais.
    """

    metadata = {"render_modes": [], "render_fps": 1}

    def __init__(
        self,
        allowed_actions,
        context_macro=None,
        risk_manager=None,
        position_manager=None,
        reward_aggregator=None,
        logger=None,
        debug: bool = False,
        **kwargs
    ):
        super().__init__()
        self.allowed_actions = allowed_actions
        self.context_macro = context_macro or {}
        self.risk_manager = risk_manager
        self.position_manager = position_manager
        self.reward_aggregator = reward_aggregator
        self.logger = logger or get_logger("BaseEnv", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self.episode = 0
        self._logs = []
        self._current_episode_log = []
        self.action_space = gym.spaces.Discrete(len(allowed_actions))
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)  # Placeholder

        self.logger.info("BaseEnv inicializado. allowed_actions=%s, context_macro=%s", allowed_actions, self.context_macro)

    def reset(self, *, context_macro=None, seed=None, options=None):
        """
        Reinicia o ambiente e atualiza contexto macro.

        Args:
            context_macro (dict, opcional): Novo contexto macro para o episódio.
            seed (int, opcional): Semente do ambiente.
            options (dict, opcional): Parâmetros extras.

        Returns:
            obs, info: Observação inicial, dicionário info.
        """
        self.episode += 1
        if context_macro is not None:
            self.context_macro = context_macro
        self.logger.info(f"Reset (episódio {self.episode}) | context_macro={self.context_macro}")
        # Observação inicial dummy (override nos filhos)
        obs = np.zeros(self.observation_space.shape, dtype=np.float32)
        info = {"context_macro": self.context_macro, "episode": self.episode}
        self._current_episode_log = [{
            "event": "reset",
            "episode": self.episode,
            "context_macro": self.context_macro,
            "seed": seed,
            "info": info
        }]
        self._logs.append(self._current_episode_log)
        return obs, info

    def step(self, action):
        """
        Executa step, valida ação, processa contexto macro e delega componentes.

        Args:
            action: Ação a ser tomada (índice da lista de ações permitidas).

        Returns:
            obs, reward, terminated, truncated, info
        """
        # Validação de ação
        if action not in range(len(self.allowed_actions)):
            self.logger.critical(f"Ação inválida: {action}")
            reward = -1.0  # Penalidade padrão
            terminated = True
            truncated = False
            info = {"error": "Ação não permitida"}
            obs = np.zeros(self.observation_space.shape, dtype=np.float32)
            self._current_episode_log.append({
                "event": "invalid_action",
                "action": action,
                "reward": reward,
                "terminated": terminated,
                "truncated": truncated,
                "info": info
            })
            return obs, reward, terminated, truncated, info

        action_label = self.allowed_actions[action]
        obs = np.zeros(self.observation_space.shape, dtype=np.float32)  # Dummy, sobrescreva nos filhos
        reward = 0.0
        terminated = False
        truncated = False
        info = {"action_label": action_label, "context_macro": self.context_macro}

        # Delegação plugável (filhos devem sobrescrever)
        if self.position_manager:
            try:
                pos_info = self.position_manager.step(action_label)
                info.update({"position": pos_info})
            except Exception as e:
                self.logger.warning(f"Erro no position_manager: {e}")

        if self.risk_manager:
            try:
                risk = self.risk_manager.evaluate(action_label, context=self.context_macro)
                info.update({"risk": risk})
            except Exception as e:
                self.logger.warning(f"Erro no risk_manager: {e}")

        if self.reward_aggregator:
            try:
                reward = self.reward_aggregator.compute_reward(info)
            except Exception as e:
                self.logger.warning(f"Erro no reward_aggregator: {e}")

        self._current_episode_log.append({
            "event": "step",
            "episode": self.episode,
            "action": action,
            "action_label": action_label,
            "reward": reward,
            "terminated": terminated,
            "truncated": truncated,
            "context_macro": self.context_macro,
            "info": info
        })
        self.logger.debug(f"Step: ação={action_label}, reward={reward}, context={self.context_macro}")
        return obs, reward, terminated, truncated, info

    def set_context_macro(self, context_macro: dict):
        """
        Atualiza dinamicamente o contexto macro.

        Args:
            context_macro (dict): Novo contexto macro.
        """
        self.context_macro = context_macro or {}
        self.logger.info(f"Contexto macro atualizado para: {self.context_macro}")

    def get_logs(self) -> dict:
        """
        Retorna todos os logs acumulados do ambiente.

        Returns:
            dict: Logs por episódio.
        """
        return {"episodes": self._logs}

    # Métodos extras para contrato RL
    def render(self, mode='human'):
        """Override nos filhos se desejado."""
        pass

    def close(self):
        """Finaliza recursos, salva logs se necessário."""
        pass
