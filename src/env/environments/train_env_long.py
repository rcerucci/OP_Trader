#!/usr/bin/env python3
"""
src/env/environments/train_env_long.py
Ambiente RL especializado para estratégias long-only (buy/hold), herdando contrato do BaseEnv.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

from src.env.environments.base_env import BaseEnv
from src.utils.logging_utils import get_logger

class TrainEnvLong(BaseEnv):
    """
    Ambiente RL especializado para treinamento de agentes PPO na direção “long” (compra).
    Herdado de BaseEnv. Restringe as ações permitidas a ["buy", "hold"] e executa
    ciclo completo de reset, step, validação e logging para estratégias long-only.

    Args:
        context_macro (dict, opcional): Contexto macro (ex: direção, regime, etc).
        position_manager (obj, opcional): Plug-in de posição.
        risk_manager (obj, opcional): Plug-in de risco.
        reward_aggregator (obj, opcional): Plug-in de recompensa.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Logging detalhado.
        kwargs: Demais parâmetros herdados.
    """

    def __init__(self, context_macro: dict = None, **kwargs):
        super().__init__(
            allowed_actions=["buy", "hold"],
            context_macro=context_macro,
            **kwargs
        )
        # Logger herdado do BaseEnv, apenas reforço se necessário
        self.logger = self.logger or get_logger("TrainEnvLong")

    def step(self, action):
        """
        Executa um passo no ambiente, restrito às ações “buy” e “hold”.

        Args:
            action (int): Índice da ação ("buy"=0, "hold"=1).

        Returns:
            obs, reward, terminated, truncated, info
        """
        if action not in [0, 1]:
            self.logger.critical(f"Ação inválida no TrainEnvLong: {action}")
            reward = -1.0
            terminated = True
            truncated = False
            info = {"error": "Ação não permitida (apenas buy/hold)", "action": action}
            obs = self.observation_space.sample() * 0  # ou np.zeros
            self._current_episode_log.append({
                "event": "invalid_action",
                "action": action,
                "reward": reward,
                "terminated": terminated,
                "truncated": truncated,
                "info": info
            })
            return obs, reward, terminated, truncated, info

        # Chama o step do BaseEnv, que já lida com plugáveis e logging
        return super().step(action)

    def reset(self, *, context_macro=None, seed=None, options=None):
        """
        Reinicia o ambiente, podendo atualizar contexto macro e logando o episódio.

        Returns:
            obs, info: Observação inicial e info.
        """
        if context_macro is not None:
            self.context_macro = context_macro
        return super().reset(context_macro=self.context_macro, seed=seed, options=options)
