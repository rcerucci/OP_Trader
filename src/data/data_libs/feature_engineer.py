#!/usr/bin/env python3
"""
src/data/data_libs/feature_engineer.py

FeatureEngineer Op_Trader — Cálculo modular e robusto de features técnicas e derivadas,
recebendo lista de features e parâmetros explicitamente do pipeline/runner.

Nunca faz parsing de config.ini, nem de CLI.
Pronto para produção, automação e downstream.

Autor: Equipe Op_Trader
Data: 2025-06-14
"""

from typing import List, Dict, Optional
from src.data.data_libs.feature_calculator import FeatureCalculator
from src.utils.logging_utils import get_logger

class FeatureEngineer:
    """
    Pipeline de cálculo de features técnicas/derivadas Op_Trader.

    Todos os parâmetros (features e params) devem ser recebidos explicitamente pelo construtor.
    Nunca busca config, ini, ou CLI internamente.
    """

    def __init__(
        self,
        features: List[str],
        params: Optional[Dict[str, Dict[str, any]]] = None,
        debug: bool = False,
    ):
        """
        Parâmetros
        ----------
        features : List[str]
            Lista de features a calcular (ex: ['ema_fast', 'rsi', ...]).
        params : Dict[str, Dict[str, any]], opcional
            Dicionário com parâmetros para cada feature. Exemplo:
            {
                'ema_fast': {'window': 20},
                'rsi': {'window': 14},
                ...
            }
        debug : bool, opcional
            Ativa log detalhado para troubleshooting.
        """
        self.features = features
        self.params = params or {}
        self.debug = debug
        self.logger = get_logger("op_trader.feature_engineer", "DEBUG" if debug else None)

    def transform(self, df):
        """
        Aplica o cálculo das features especificadas no DataFrame recebido.

        Parâmetros
        ----------
        df : pd.DataFrame
            DataFrame de entrada já limpo e corrigido.

        Retorno
        -------
        pd.DataFrame
            DataFrame com as novas features adicionadas.
        """
        self.logger.info(f"Calculando features: {self.features}")
        if self.debug:
            self.logger.debug(f"Parâmetros de features: {self.params}")
        calculator = FeatureCalculator(debug=self.debug)
        return calculator.calculate_all(
            df,
            features=self.features,
            params=self.params
        )
