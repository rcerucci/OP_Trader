# src/data/data_libs/data_collector_mt5.py

"""
DataCollectorMT5 — Coletor dedicado ao MetaTrader5 para pipeline Op_Trader.
Agora retorna DataFrame com COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume']
e index padrão (RangeIndex). Retorna também nome da corretora e ohlc_decimals.

Autor: Equipe Op_Trader
Data: 2025-06-12
"""

import decimal
import pandas as pd
import MetaTrader5 as mt5
from typing import List, Optional, Tuple, Callable
from datetime import datetime
from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root
import os
from dotenv import load_dotenv

ROOT_DIR = ensure_project_root(__file__)
COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume']

class DataCollectorMT5:
    """
    Coletor dedicado para MetaTrader 5 (MT5), compatível com batch e streaming.
    Retorna df_raw (COLUMNS_REQUIRED, index padrão), nome da corretora e ohlc_decimals.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        start_date: str,
        end_date: str,
        volume_sources: List[str],
        volume_column: str = "",
        debug: bool = False
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.volume_sources = [s.strip() for s in volume_sources if s.strip()]
        self.volume_column = volume_column.strip()
        self.debug = debug

        cli_level = "DEBUG" if self.debug else "INFO"
        self._logger = get_logger(self.__class__.__name__, cli_level=cli_level)
        self.broker_name = None

        self._connect_mt5()

    def _connect_mt5(self):
        """Inicializa conexão ao MT5 usando variáveis do .env"""
        env_path = ROOT_DIR / ".env"
        load_dotenv(dotenv_path=env_path)
        login = os.getenv("MT5_LOGIN")
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")
        try:
            if not login or not password or not server:
                raise RuntimeError("Variáveis MT5_LOGIN, MT5_PASSWORD ou MT5_SERVER ausentes.")
            login = int(login)
            if not mt5.initialize(login=login, password=password, server=server):
                code, msg = mt5.last_error()
                self._logger.error(f"MT5: falha ao inicializar ({code}) {msg}")
                raise RuntimeError("Falha ao conectar no MT5")
            self.broker_name = server
            self._logger.info(f"Conectado ao MT5: servidor '{server}'")
        except Exception as e:
            self._logger.error(f"Erro ao conectar ao MT5: {e}")
            raise

    def _shutdown_mt5(self):
        """Encerra a conexão com o MT5."""
        try:
            mt5.shutdown()
            self._logger.info("Conexão MT5 encerrada.")
        except Exception as e:
            self._logger.error(f"Erro ao encerrar conexão MT5: {e}")

    def _get_mt5_timeframe(self) -> int:
        """Mapeia string de timeframe para constante MT5."""
        tf_map = {
            "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1, "W1": mt5.TIMEFRAME_W1, "MN1": mt5.TIMEFRAME_MN1
        }
        tf = self.timeframe.upper()
        if tf not in tf_map:
            raise ValueError(f"Timeframe inválido: {self.timeframe}")
        return tf_map[tf]

    def _fetch_ohlcv(self) -> Tuple[pd.DataFrame, int]:
        timeframe = self._get_mt5_timeframe()
        start = pd.to_datetime(self.start_date)
        end = pd.to_datetime(self.end_date)
        rates = mt5.copy_rates_range(self.symbol, timeframe, start, end)
        if rates is None or len(rates) == 0:
            self._logger.error(f"Nenhum dado retornado para {self.symbol} {self.timeframe}")
            raise RuntimeError("MT5: Nenhum dado retornado")
        df = pd.DataFrame(rates)
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        # Novo: Determina os decimais a partir do tick_size do símbolo no MT5
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is not None and hasattr(symbol_info, "point"):
                tick_size = symbol_info.point
                if tick_size > 0:
                    dec = abs(decimal.Decimal(str(tick_size)).as_tuple().exponent)
                else:
                    dec = 5  # fallback
            else:
                dec = 5  # fallback
        except Exception:
            dec = 5
        self._logger.debug(f"Decimais OHLC extraídos: {dec}")
        return df, dec

    def _select_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """Seleciona a coluna de volume de acordo com prioridade."""
        candidates = [col for col in df.columns if any(src in col.lower() for src in self.volume_sources)]
        selected = None
        if self.volume_column and self.volume_column in df.columns:
            selected = self.volume_column
            self._logger.info(f"Usando coluna de volume explícita: {selected}")
        else:
            for src in self.volume_sources:
                for col in df.columns:
                    if src in col.lower():
                        if df[col].notna().sum() > 0 and df[col].sum() > 0:
                            selected = col
                            break
                if selected:
                    break
        if not selected and candidates:
            selected = candidates[0]
            self._logger.warning(f"Usando primeira coluna disponível de volume: {selected}")
        if not selected:
            df['volume'] = 0
            self._logger.warning("Nenhuma coluna válida de volume encontrada. Usando zeros.")
        else:
            if selected != 'volume':
                df = df.rename(columns={selected: 'volume'})
            drop_cols = [col for col in candidates if col != selected and col != 'volume']
            if drop_cols:
                df.drop(columns=drop_cols, inplace=True)
        return df

    def _finalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza DataFrame para COLUMNS_REQUIRED (index padrão, sem set_index!)."""
        if df.empty:
            raise RuntimeError("DataFrame vazio após coleta")
        df = self._select_volume(df)
        # Reordena e filtra as colunas
        required = COLUMNS_REQUIRED
        # Checa e loga colunas faltantes
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise RuntimeError(f"Colunas obrigatórias ausentes: {missing}")
        df = df[required].copy()
        df.reset_index(drop=True, inplace=True)  # Index padrão!
        return df

    def collect_batch(self) -> Tuple[pd.DataFrame, str, int]:
        """
        Coleta e retorna df_raw, nome da corretora e ohlc_decimals (para pipeline batch).

        Returns:
            Tuple[pd.DataFrame, str, int]: df_raw (COLUMNS_REQUIRED, index padrão), nome corretora, ohlc_decimals
        """
        try:
            df_raw, ohlc_decimals = self._fetch_ohlcv()
            df_final = self._finalize_dataframe(df_raw)
            return df_final, self.broker_name, ohlc_decimals
        finally:
            self._shutdown_mt5()

    def collect_streaming(self, callback: Callable[[pd.DataFrame], None], poll_interval: float = 5.0):
        """
        Loop de streaming: chama o callback a cada poll_interval se houver novo dado.
        (Para streaming, não retorna decimais — somente df_raw no callback, com COLUMNS_REQUIRED)
        """
        import time
        last_max_dt = None
        try:
            while True:
                df_raw, _ = self._fetch_ohlcv()
                df_final = self._finalize_dataframe(df_raw)
                # Callback só em novos dados
                current_max = df_final['datetime'].max() if not df_final.empty else None
                if df_final.empty or (last_max_dt is not None and current_max == last_max_dt):
                    time.sleep(poll_interval)
                    continue
                last_max_dt = current_max
                callback(df_final)
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            self._logger.info("Streaming interrompido pelo usuário.")
        finally:
            self._shutdown_mt5()

# EOF
