# src/utils/data_cleaner.py

"""
data_cleaner.py

Classe utilitária para limpeza e padronização de DataFrames de candles no pipeline Op_Trader.
Padroniza nomes, valida presença e tipo das colunas, converte tipos, remove NaNs e ordena.

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import pandas as pd
from typing import Optional

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)

class DataCleaner:
    """
    Limpa e padroniza DataFrames de candles para o pipeline Op_Trader.

    Métodos:
        - clean(df): Limpa, valida e retorna DataFrame pronto para feature engineering.

    Args:
        debug (bool): Se True, logging detalhado.
    """

    def __init__(self, debug: bool = False):
        """
        Inicializa o DataCleaner.

        Args:
            debug (bool, optional): Se True, ativa logs em nível DEBUG. Default False.
        """
        level = "DEBUG" if debug else None
        self.logger = get_logger(self.__class__.__name__, level)

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza a limpeza e padronização do DataFrame:
            1. Renomeia colunas: "date"→"time", "volume"→"tick_volume"
            2. Valida presença das colunas obrigatórias: {"time", "open", "high", "low", "close", "tick_volume"}
            3. Converte "time" para datetime
            4. Converte colunas numéricas para float64
            5. Remove linhas com NaN em colunas essenciais
            6. Ordena por "time"

        Args:
            df (pd.DataFrame): DataFrame bruto lido do CSV.

        Returns:
            pd.DataFrame: DataFrame limpo e padronizado.

        Raises:
            KeyError: Se faltar coluna obrigatória.
            ValueError: Se DataFrame de entrada estiver vazio ou com tipos inválidos.

        Example:
            >>> cleaner = DataCleaner(debug=True)
            >>> df_clean = cleaner.clean(df_raw)
        """
        self.logger.info(f"Iniciando limpeza: shape={df.shape}")

        if df.empty:
            msg = "DataFrame de entrada está vazio."
            self.logger.error(msg)
            raise ValueError(msg)

        # 1. Renomear "date"→"time" e "volume"→"tick_volume"
        rename_cols = {}
        if "date" in df.columns and "time" not in df.columns:
            rename_cols["date"] = "time"
        if "volume" in df.columns and "tick_volume" not in df.columns:
            rename_cols["volume"] = "tick_volume"
        if rename_cols:
            df = df.rename(columns=rename_cols)
            self.logger.debug(f"Colunas renomeadas: {rename_cols}")

        # 2. Verificar colunas obrigatórias
        required_cols = {"time", "open", "high", "low", "close", "tick_volume"}
        missing = required_cols - set(df.columns)
        if missing:
            msg = f"Colunas obrigatórias ausentes: {missing}"
            self.logger.error(msg)
            raise KeyError(msg)

        # 3. Converter "time" para datetime
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        n_time_nat = df["time"].isna().sum()
        if n_time_nat > 0:
            self.logger.warning(f"{n_time_nat} valores 'time' inválidos convertidos para NaT.")

        # 4. Converter para float64
        num_cols = ["open", "high", "low", "close", "tick_volume"]
        for col in num_cols:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
            except Exception as e:
                msg = f"Falha ao converter coluna '{col}' para float64: {e}"
                self.logger.error(msg)
                raise ValueError(msg)
        # 5. Remove linhas com NaN em qualquer coluna essencial
        before = len(df)
        df = df.dropna(subset=list(required_cols))
        after = len(df)
        dropped = before - after
        if dropped > 0:
            self.logger.info(f"Linhas removidas por NaN em colunas essenciais: {dropped} (antes={before}, depois={after})")

        # 6. Ordenar por "time"
        df = df.sort_values(by="time").reset_index(drop=True)
        self.logger.info(f"Limpeza concluída. Shape final: {df.shape}")

        return df
