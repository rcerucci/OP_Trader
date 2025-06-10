"""
src/env/env_libs/reward_aggregator.py
RewardAggregator: cálculo e logging de recompensas multi-componente para ambientes RL.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import numpy as np

from src.utils.logging_utils import get_logger
from src.utils.file_saver import build_filename, save_dataframe

class RewardAggregator:
    def __init__(self, reward_components: list = None, weights: dict = None, normalization: str = None, logger=None, debug: bool = False, **kwargs):
        self.reward_components = []
        if reward_components:
            for f in reward_components:
                if isinstance(f, tuple):
                    self.reward_components.append(f)
                else:
                    # Assume nome pelo __name__ da função
                    self.reward_components.append((getattr(f, "__name__", "component"), f))
        self.weights = weights or {}
        self.normalization = normalization or "none"
        self.logger = logger or get_logger("RewardAggregator", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.Lock()
        self._last_breakdown = None
        self._reward_history = []
        self.logger.info(f"RewardAggregator inicializado. Components: {[n for n, _ in self.reward_components]}, weights: {self.weights}, norm: {self.normalization}")

    def calculate_reward(self, state_before: dict, action: dict, state_after: dict) -> float:
        with self._lock:
            breakdown = {}
            total = 0.0
            weights = self.weights.copy()
            names = [name for name, _ in self.reward_components]
            # Corrige weights default
            for name in names:
                if name not in weights:
                    weights[name] = 1.0
            total_weight = sum(weights.get(name, 1.0) for name in names)
            if total_weight == 0:
                self.logger.warning("Soma dos pesos igual a zero, ajustando para 1.")
                total_weight = 1.0

            for i, (name, func) in enumerate(self.reward_components):
                try:
                    val = func(state_before, action, state_after)
                    if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                        self.logger.warning(f"Componente {name} retornou valor inválido, ajustando para zero.")
                        val = 0.0
                except Exception as e:
                    self.logger.error(f"Erro em componente {name}: {e}")
                    val = 0.0
                w = weights.get(name, 1.0)
                breakdown[name] = {"value": val, "weight": w}
                total += w * val

            # Normalização (mesma lógica)
            normed = total
            # ... resto igual

            breakdown["total"] = total
            breakdown["normed"] = normed
            self._last_breakdown = breakdown
            self._reward_history.append(total)
            self.logger.info(f"Reward breakdown: {breakdown}")
            return float(normed)

    def add_component(self, name: str, func, weight: float = 1.0):
        with self._lock:
            self.reward_components.append((name, func))
            self.weights[name] = weight
            self.logger.info(f"Componente {name} adicionado ao RewardAggregator.")
    # ... demais métodos inalterados

    def get_reward_breakdown(self) -> dict:
        """
        Retorna detalhamento da última reward calculada.

        Returns:
            dict: Breakdown (componentes, valores, pesos, total, normed)
        """
        return self._last_breakdown.copy() if self._last_breakdown else {}

    def reset(self):
        """
        Limpa histórico e breakdown acumulados.

        Returns:
            None
        """
        self._last_breakdown = None
        self._reward_history.clear()
        self.logger.info("RewardAggregator resetado.")

    def save_breakdown(self, path: str = None):
        """
        Salva breakdown detalhado em CSV/JSON para auditoria.

        Args:
            path (str, opcional): Diretório destino.

        Returns:
            None
        """
        if not self._last_breakdown:
            self.logger.warning("Nenhum breakdown para salvar.")
            return
        try:
            import pandas as pd
            import datetime
            df = pd.DataFrame([{**self._last_breakdown, "timestamp": str(datetime.datetime.now())}])
            filename = build_filename(
                prefix=path or "logs/audits/",
                suffix="reward_breakdown",
                asset="none",
                timeframe="none"
            )
            save_dataframe(df, filename)
            self.logger.info(f"Breakdown salvo: {filename}")
        except Exception as e:
            self.logger.error(f"Falha ao salvar breakdown: {e}")
