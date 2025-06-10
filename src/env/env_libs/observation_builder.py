"""
src/env/env_libs/observation_builder.py
ObservationBuilder: construção, validação e normalização de observações para agentes RL.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import numpy as np

from src.utils.logging_utils import get_logger
from src.utils.data_shape_utils import load_feature_list, align_dataframe_to_schema
from src.utils.file_saver import build_filename, save_dataframe

class ObservationBuilder:
    """
    Gera, valida e normaliza observações/features para ambientes RL do Op_Trader.

    Args:
        feature_schema (list): Lista de features obrigatórias/permitidas.
        calculators (list): Lista de componentes plugáveis (FeatureCalculator, etc).
        scaler (obj, opcional): Normalizador de features.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """

    def __init__(self, feature_schema: list = None, calculators: list = None, scaler=None, logger=None, debug: bool = False, **kwargs):
        self.feature_schema = feature_schema or load_feature_list()
        self.calculators = calculators or []
        self.scaler = scaler
        self.logger = logger or get_logger("ObservationBuilder", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.Lock()
        self._last_snapshot = None
        self.logger.info(f"ObservationBuilder inicializado. Features: {self.feature_schema}")

    def build_observation(self, market_data: dict, portfolio_data: dict, context: dict = None) -> dict:
        """
        Constrói observação a partir dos dados de mercado, portfólio e contexto.

        Args:
            market_data (dict): Dados de mercado do step.
            portfolio_data (dict): Estado do portfólio.
            context (dict, opcional): Dados de contexto macro/micro.

        Returns:
            dict: Observação final (features validadas e normalizadas).
        """
        with self._lock:
            obs = {}
            # Agrega dados brutos
            obs.update(market_data or {})
            obs.update(portfolio_data or {})
            if context:
                obs.update(context)
            # Calculadoras plugadas
            for calc in self.calculators:
                try:
                    calc_feats = calc.calculate(market_data, portfolio_data, context)
                    if isinstance(calc_feats, dict):
                        obs.update(calc_feats)
                except Exception as e:
                    self.logger.warning(f"Calculator {calc} falhou: {e}")
            # Validação de features
            valid = self.validate_features(obs)
            if not valid:
                self.logger.error("Observação inválida após agregação.")
                raise ValueError("Observação inválida.")
            # Normalização
            if self.scaler:
                obs = self.normalize_observation(obs)
            self._last_snapshot = obs.copy()
            return obs

    def validate_features(self, observation: dict) -> bool:
        """
        Valida presença, tipagem e valores das features.

        Args:
            observation (dict): Observação a validar.

        Returns:
            bool: True se válido, False se algum campo faltar ou for inválido.
        """
        missing = [k for k in self.feature_schema if k not in observation]
        if missing:
            self.logger.warning(f"Features ausentes: {missing}")
            return False
        for k in self.feature_schema:
            v = observation[k]
            if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
                self.logger.warning(f"Feature {k} inválida: {v}")
                return False
        return True

    def get_feature_names(self) -> list:
        """
        Retorna a lista de features do schema.

        Returns:
            list: Lista das features esperadas.
        """
        return list(self.feature_schema)

    def normalize_observation(self, observation: dict) -> dict:
        """
        Aplica scaler/normalizador plugado na observação.

        Args:
            observation (dict): Dicionário de features a normalizar.

        Returns:
            dict: Dicionário normalizado.
        """
        try:
            arr = np.array([observation[k] for k in self.feature_schema], dtype=np.float32).reshape(1, -1)
            arr_norm = self.scaler.transform(arr)
            obs_norm = {k: float(arr_norm[0, i]) for i, k in enumerate(self.feature_schema)}
            return obs_norm
        except Exception as e:
            self.logger.warning(f"Falha ao normalizar: {e}")
            return observation

    def save_snapshot(self, path: str = None):
        """
        Salva o último snapshot de observação em CSV para auditoria.

        Args:
            path (str, opcional): Caminho para salvar.

        Returns:
            None
        """
        if self._last_snapshot is None:
            self.logger.warning("Nenhum snapshot para salvar.")
            return
        try:
            import pandas as pd
            df = pd.DataFrame([self._last_snapshot])
            filename = build_filename(
                prefix=path or "logs/audits/",
                suffix="obs_snapshot",
                asset="none",
                timeframe="none"
            )
            save_dataframe(df, filename)
            self.logger.info(f"Snapshot salvo: {filename}")
        except Exception as e:
            self.logger.error(f"Falha ao salvar snapshot: {e}")

    def reset(self):
        """
        Limpa o snapshot armazenado.

        Returns:
            None
        """
        self._last_snapshot = None
        self.logger.info("Snapshot de observação resetado.")
