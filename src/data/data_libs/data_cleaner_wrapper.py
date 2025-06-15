# src/data/data_libs/data_cleaner_wrapper.py
"""
DataCleanerWrapper — Op_Trader (Batch/Streaming)

Limpeza estrita e padronizada para DataFrames de candles/features:
- Remove linhas inválidas/NaN nas colunas essenciais dinâmicas.
- Garante datetime e ordenação (se presente).
- Arredonda colunas numéricas conforme ohlc_decimals.
- Converte flags booleanas em inteiros (0/1) se existirem.
- Mantém apenas as colunas informadas na lista dinâmica.

Compatível com batch e streaming (modo).
Autor: Equipe Op_Trader
Data: 2025-06-12
"""

from typing import Optional, List
import pandas as pd
from src.utils.logging_utils import get_logger

class DataCleanerWrapper:
    """
    Limpeza estrita e padronizada de DataFrames Op_Trader.
    Compatível com batch e streaming (param mode).
    """

    def __init__(self, debug: bool = False, mode: str = "batch"):
        self.debug = debug
        self.mode = mode.lower()
        self._logger = get_logger(
            self.__class__.__name__, cli_level="DEBUG" if self.debug else None
        )

    def clean(
        self,
        df: pd.DataFrame,
        ohlc_decimals: int,
        columns_required: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Limpa e padroniza DataFrame, removendo linhas inválidas e arredondando as colunas indicadas.

        Args:
            df (pd.DataFrame): DataFrame bruto.
            ohlc_decimals (int): Casas decimais para colunas de preço/features.
            columns_required (list): Lista dinâmica de colunas essenciais (ex: OHLCV + features de preço + flags).

        Returns:
            pd.DataFrame: DataFrame limpo, padronizado e sem NaNs nas colunas essenciais.
        """
        if columns_required is None:
            self._logger.critical("Lista de colunas obrigatórias não informada.")
            return pd.DataFrame()

        if not isinstance(df, pd.DataFrame) or df.empty:
            self._logger.critical("DataFrame vazio ou inválido recebido.")
            return pd.DataFrame(columns=columns_required)
        missing = [col for col in columns_required if col not in df.columns]
        if missing:
            self._logger.critical(f"Colunas obrigatórias ausentes: {missing}")
            return pd.DataFrame(columns=columns_required)
        if ohlc_decimals is None:
            self._logger.critical("Parâmetro 'ohlc_decimals' não informado.")
            return pd.DataFrame(columns=columns_required)

        try:
            df_clean = df.copy()
            # 1. Garante datetime correto e ordena (se presente)
            if 'datetime' in df_clean.columns:
                df_clean['datetime'] = pd.to_datetime(df_clean['datetime'], errors='coerce')
                df_clean.sort_values('datetime', inplace=True)
            # 2. Remove linhas inválidas nas colunas essenciais
            before = len(df_clean)
            df_clean.dropna(subset=columns_required, inplace=True)
            after = len(df_clean)
            dropped = before - after
            if dropped > 0:
                self._logger.info(f"Linhas removidas por NaN: {dropped} (antes={before}, depois={after})")
            # 3. Arredonda todas as colunas numéricas exceto datetime
            for col in columns_required:
                if col != 'datetime' and pd.api.types.is_numeric_dtype(df_clean[col]):
                    df_clean[col] = df_clean[col].round(ohlc_decimals)
                    df_clean[col] = df_clean[col].astype(float)
                    self._logger.debug(f"Coluna '{col}' arredondada para {ohlc_decimals} casas decimais.")
            # 4. Converte flags booleanas para inteiro (0/1), se existirem
            for flag_col in ['gap_fixed', 'volume_fixed', 'outlier_fixed']:
                if flag_col in df_clean.columns:
                    df_clean[flag_col] = df_clean[flag_col].astype(int)
                    self._logger.debug(f"Coluna '{flag_col}' convertida para inteiro 0/1.")
            # 5. Mantém apenas as colunas indicadas, na ordem
            df_clean = df_clean[columns_required].reset_index(drop=True)
        except Exception as e:
            self._logger.critical(f"Erro crítico na limpeza: {e}. Retornando DataFrame vazio.")
            return pd.DataFrame(columns=columns_required)

        self._logger.info(f"DataFrame limpo (shape final={df_clean.shape}).")
        return df_clean

# EOF
