# src/data/data_libs/scaler.py
"""
ScalerUtils — Utilitário oficial de normalização de features Op_Trader

Fornece métodos robustos para ajuste, aplicação e persistência de normalizadores
(StandardScaler) no pipeline batch/real-time. Em conformidade com padrões:
- Logging estruturado, propagate=False
- Fit/transform com suffix `_norm`
- Persistência via pickle com tratamento de erros

Autor: Equipe Op_Trader
Data: 2025-06-12
"""

import pickle
from pathlib import Path
from typing import Optional, List

import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.utils.logging_utils import get_logger


class ScalerUtils:
    """
    Utilitário para ajuste, aplicação e persistência de StandardScaler
    no Op_Trader.

    Atributos:
        scaler (StandardScaler): instância treinada.
        logger: logger com propagate=False.
    """

    def __init__(self, debug: bool = False):
        level = "DEBUG" if debug else None
        self.logger = get_logger(self.__class__.__name__, level)
        self.logger.propagate = False
        self.scaler: Optional[StandardScaler] = None

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta o StandardScaler e retorna DataFrame normalizado.

        Args:
            df: DataFrame não vazio de colunas contínuas.
        Returns:
            DataFrame com colunas renomeadas para '<col>_norm', preservando o index.
        Raises:
            ValueError: df inválido.
        """
        if not isinstance(df, pd.DataFrame) or df.empty:
            msg = "df deve ser um DataFrame não vazio para fit_transform."
            self.logger.error(msg)
            raise ValueError(msg)

        cols: List[str] = list(df.columns)
        self.logger.info(f"Ajustando StandardScaler nas colunas: {cols} (shape={df.shape})")

        scaler = StandardScaler()
        arr = scaler.fit_transform(df[cols])
        df_norm = pd.DataFrame(
            arr,
            index=df.index,
            columns=[f"{c}_norm" for c in cols]
        )

        self.scaler = scaler
        self.logger.debug("Scaler ajustado com sucesso.")
        return df_norm

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica o scaler treinado e retorna DataFrame normalizado.

        Args:
            df: DataFrame não vazio com mesmas colunas usadas no fit.
        Returns:
            DataFrame com colunas '<col>_norm'.
        Raises:
            RuntimeError: scaler não treinado.
            ValueError: df inválido.
        """
        if self.scaler is None:
            msg = "Scaler não treinado. Use fit_transform ou load_scaler antes."
            self.logger.error(msg)
            raise RuntimeError(msg)
        if not isinstance(df, pd.DataFrame) or df.empty:
            msg = "df deve ser um DataFrame não vazio para transform."
            self.logger.error(msg)
            raise ValueError(msg)

        cols: List[str] = list(df.columns)
        self.logger.info(f"Aplicando scaler nas colunas: {cols} (shape={df.shape})")

        arr = self.scaler.transform(df[cols])
        df_norm = pd.DataFrame(
            arr,
            index=df.index,
            columns=[f"{c}_norm" for c in cols]
        )

        self.logger.debug("Transformação aplicada com sucesso.")
        return df_norm

    def save_scaler(self, path: Path) -> None:
        """
        Persiste o scaler em disco via pickle.

        Args:
            path: caminho completo com extensão .pkl.
        Raises:
            RuntimeError: scaler não treinado.
        """
        if self.scaler is None:
            msg = "Nenhum scaler treinado para salvar."
            self.logger.error(msg)
            raise RuntimeError(msg)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                pickle.dump(self.scaler, f)
            self.logger.info(f"Scaler salvo com sucesso em: {path}")
        except Exception as e:
            self.logger.error(f"Falha ao salvar scaler em {path}: {e}")
            raise

    def load_scaler(self, path: Path) -> None:
        """
        Carrega scaler de disco e armazena em self.scaler.

        Args:
            path: caminho completo com extensão .pkl.
        Raises:
            FileNotFoundError: arquivo não existe.
        """
        if not path.exists():
            msg = f"Arquivo de scaler não encontrado: {path}"
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        try:
            with open(path, "rb") as f:
                self.scaler = pickle.load(f)
            self.logger.info(f"Scaler carregado com sucesso de: {path}")
        except Exception as e:
            self.logger.error(f"Falha ao carregar scaler de {path}: {e}")
            raise

# EOF
