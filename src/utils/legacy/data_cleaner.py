# src/utils/data_cleaner.py

"""
data_cleaner.py

Classe utilitária para limpeza ESTRITA de DataFrames de candles no pipeline Op_Trader.
NÃO padroniza nomes, NÃO renomeia colunas, NÃO tenta converter schema.
Apenas valida presença, tipos e remove linhas inválidas. Responsabilidade total sobre schema é do coletor.

Autor: Equipe Op_Trader
Data: 2025-06-10 (versão aderente ao contrato)
"""

import pandas as pd
from typing import Optional

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)

COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'time']

class DataCleaner:
    """
    Limpador ESTRITO de DataFrames de candles para o pipeline Op_Trader.

    - NÃO renomeia ou cria colunas.
    - Apenas valida presença das colunas obrigatórias, tipos e remove linhas inválidas.
    - Não tenta converter schema, apenas rejeita e loga erro crítico se schema incorreto.

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
        Limpeza estrita:
            1. Valida presença de todas as colunas obrigatórias.
            2. Converte tipos das colunas obrigatórias (se possível).
            3. Remove linhas com NaN nas colunas essenciais.
            4. Ordena por "datetime" (nunca por "time").
        NÃO altera nomes de colunas nem tenta corrigir schema.

        Args:
            df (pd.DataFrame): DataFrame bruto, já padronizado pelo conector.

        Returns:
            pd.DataFrame: DataFrame limpo (ou vazio se inconsistente).
        """
        self.logger.info(f"Iniciando limpeza: shape={df.shape}")

        if not isinstance(df, pd.DataFrame):
            msg = "Entrada não é DataFrame."
            self.logger.critical(msg)
            return pd.DataFrame(columns=COLUMNS_REQUIRED)

        if df.empty:
            msg = "DataFrame de entrada está vazio."
            self.logger.critical(msg)
            return pd.DataFrame(columns=COLUMNS_REQUIRED)

        # 1. Validar colunas obrigatórias
        missing = [col for col in COLUMNS_REQUIRED if col not in df.columns]
        if missing:
            msg = f"Colunas obrigatórias ausentes: {missing}"
            self.logger.critical(msg)
            return pd.DataFrame(columns=COLUMNS_REQUIRED)

        # 2. Converter tipos das colunas obrigatórias
        try:
            df = df.copy()
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df["time"] = pd.to_numeric(df["time"], errors="coerce", downcast="integer")
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception as e:
            msg = f"Falha ao converter tipos das colunas obrigatórias: {e}"
            self.logger.critical(msg)
            return pd.DataFrame(columns=COLUMNS_REQUIRED)

        # 3. Remove linhas com NaN em qualquer coluna essencial
        before = len(df)
        df_clean = df.dropna(subset=COLUMNS_REQUIRED)
        after = len(df_clean)
        dropped = before - after
        if dropped > 0:
            self.logger.info(f"Linhas removidas por NaN em colunas essenciais: {dropped} (antes={before}, depois={after})")

        # 4. Ordenar por "datetime"
        df_clean = df_clean.sort_values(by="datetime").reset_index(drop=True)
        self.logger.info(f"Limpeza concluída. Shape final: {df_clean.shape}")

        # 5. Garante somente as colunas obrigatórias na ordem correta (evita vazamento de colunas extras)
        df_clean = df_clean[COLUMNS_REQUIRED]

        return df_clean
