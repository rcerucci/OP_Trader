# src/utils/scaler_utils.py

"""
scaler_utils.py

Classe utilitária para ajuste, aplicação e persistência de StandardScaler (scikit-learn)
em DataFrames de features contínuas do pipeline Op_Trader.

Permite:
    - fit_transform/transform seguro e rastreável
    - Salvamento/carregamento robusto do scaler
    - Logging detalhado de todos os passos

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import pickle
from pathlib import Path
from typing import Optional, List

import pandas as pd

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)

class ScalerUtils:
    """
    Utilitário para ajustar, aplicar e persistir um StandardScaler
    apenas nas colunas contínuas especificadas.

    Args:
        debug (bool): Se True, ativa logs detalhados.

    Atributos:
        scaler: Instância interna do StandardScaler.
    """

    def __init__(self, debug: bool = False):
        """
        Inicializa o ScalerUtils e configura o logger.

        Args:
            debug (bool, optional): Se True, ativa logs em nível DEBUG. Default False.
        """
        level = "DEBUG" if debug else None
        self.logger = get_logger(self.__class__.__name__, level)
        self.scaler = None

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajusta um StandardScaler usando todas as colunas de df (assumindo que são contínuas),
        armazena o scaler em self.scaler e retorna um DataFrame contendo cada coluna
        normalizada com sufixo "_norm".

        Args:
            df (pd.DataFrame): DataFrame contendo apenas colunas contínuas a serem normalizadas.

        Returns:
            pd.DataFrame: DataFrame com as colunas normalizadas (mesma ordem de df, cada coluna renomeada para "<col>_norm").

        Raises:
            ValueError: Se df estiver vazio ou não for DataFrame.

        Example:
            >>> scaler = ScalerUtils(debug=True)
            >>> df_norm = scaler.fit_transform(df_features)
        """
        if not isinstance(df, pd.DataFrame) or df.empty:
            msg = "df deve ser um DataFrame não vazio para fit_transform."
            self.logger.error(msg)
            raise ValueError(msg)
        from sklearn.preprocessing import StandardScaler

        columns = list(df.columns)
        self.logger.info(f"Ajustando StandardScaler nas colunas: {columns} (shape={df.shape})")
        scaler = StandardScaler()
        arr = scaler.fit_transform(df[columns])
        df_norm = pd.DataFrame(
            arr,
            columns=[f"{c}_norm" for c in columns],
            index=df.index,
        )
        self.scaler = scaler
        self.logger.debug("Scaler ajustado com sucesso.")
        return df_norm

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica o scaler já treinado (self.scaler) às colunas contínuas de df,
        retornando um DataFrame com cada coluna normalizada e sufixo "_norm".

        Args:
            df (pd.DataFrame): DataFrame contendo apenas as mesmas colunas contínuas que foram usadas no fit_transform.

        Returns:
            pd.DataFrame: DataFrame com as colunas normalizadas (cada coluna renomeada para "<col>_norm").

        Raises:
            RuntimeError: Se nenhum scaler tiver sido carregado ou treinado em self.scaler.
            ValueError: Se df for vazio ou tipos não compatíveis.

        Example:
            >>> scaler = ScalerUtils()
            >>> df_norm = scaler.transform(df_new)
        """
        if self.scaler is None:
            msg = "Scaler não foi carregado ou treinado. Chame fit_transform ou load_scaler primeiro."
            self.logger.error(msg)
            raise RuntimeError(msg)
        if not isinstance(df, pd.DataFrame) or df.empty:
            msg = "df deve ser um DataFrame não vazio para transform."
            self.logger.error(msg)
            raise ValueError(msg)
        columns = list(df.columns)
        self.logger.info(f"Aplicando scaler nas colunas: {columns} (shape={df.shape})")
        arr = self.scaler.transform(df[columns])
        df_norm = pd.DataFrame(
            arr,
            columns=[f"{c}_norm" for c in columns],
            index=df.index,
        )
        self.logger.debug("Transformação aplicada com sucesso.")
        return df_norm

    def save_scaler(self, path: Path) -> None:
        """
        Persiste o scaler treinado (self.scaler) em disco usando pickle.

        Args:
            path (Path): Caminho completo (incluindo nome de arquivo .pkl) onde o scaler será salvo.

        Raises:
            RuntimeError: Se self.scaler for None (nenhum scaler treinado).
            Exception: Propaga erros de escrita em disco.

        Example:
            >>> scaler.save_scaler(Path("models/buy/scaler_features.pkl"))
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
        Carrega um scaler previamente treinado de disco e armazena em self.scaler.

        Args:
            path (Path): Caminho completo (incluindo nome de arquivo .pkl) de onde o scaler será carregado.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            Exception: Se ocorrer erro ao carregar o pickle.

        Example:
            >>> scaler = ScalerUtils()
            >>> scaler.load_scaler(Path("models/buy/scaler_features.pkl"))
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
