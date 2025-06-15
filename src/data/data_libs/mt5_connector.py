# src/data/data_libs/mt5_connector.py

"""
MT5Connector — Op_Trader

Conector seguro e padronizado para coleta de dados do MetaTrader 5 (batch/streaming),
seguindo contrato e padrões do Op_Trader.

- Garante schema 100% padronizado: ['datetime', 'open', 'high', 'low', 'close', 'volume', 'time']
- Volume: fallback seguro entre múltiplos campos (ex: 'real_volume', 'tick_volume'), mas permite campo custom via `volume_column`.
- Decimais (ohlc_decimals): obtido **sempre** do broker via mt5.symbol_info, nunca de fonte externa.
- Logging estruturado, edge cases protegidos, fail-fast crítico em inconsistências.
- Nome real do broker/servidor obtido dinamicamente, via método público get_broker_name().

Autor: Equipe Op_Trader
Data: 2025-06-11
"""

from typing import Optional, Callable, Dict, Any, Tuple
import pandas as pd
import threading

from src.utils.mt5_connection import connect_to_mt5, close_mt5_connection
from src.utils.logging_utils import get_logger

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

COLUMNS_REQUIRED = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'time']


class MT5Connector:
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        mode: str = "batch",
        gap_params: Optional[dict] = None,
        outlier_params: Optional[dict] = None,
        debug: bool = False,
        volume_sources: Optional[list] = None,
        volume_column: Optional[str] = None,
    ):
        self.config = config or {}
        self.mode = mode.lower()
        self.gap_params = gap_params or {}
        self.outlier_params = outlier_params or {}
        self.debug = debug
        self.volume_sources = volume_sources or ["real_volume", "tick_volume", "volume_real"]
        self.volume_column = volume_column
        self._callback = None
        self._logger = get_logger(self.__class__.__name__, cli_level="DEBUG" if debug else None)
        self._stream_thread = None
        self._stop_event = threading.Event()
        self._broker_name = None  # Nome real do broker, obtido após conexão

        if mt5 is None:
            self._logger.critical("MetaTrader5 package is not installed. MT5Connector will not work.")
            raise ImportError("MetaTrader5 package is required.")

    def connect(self) -> bool:
        # Implementação padrão de connect_to_mt5 com retries e logging
        connected = connect_to_mt5(self.config)
        if connected:
            try:
                self._broker_name = mt5.account_info().server
            except Exception:
                self._logger.warning("Não foi possível obter o nome real do broker MT5 após conectar.")
        return connected

    def get_broker_name(self) -> Optional[str]:
        return self._broker_name

    def collect(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        data_type: str = "ohlc",
        **kwargs
    ) -> Tuple[pd.DataFrame, Optional[int]]:
        if self.mode == "batch":
            return self._collect_batch(symbol, timeframe, start_date, end_date, data_type, **kwargs)
        else:
            self._collect_streaming(symbol, timeframe, data_type, **kwargs)
            return None, None

    def _collect_batch(
        self,
        symbol: str,
        timeframe: str,
        start_date: Optional[str],
        end_date: Optional[str],
        data_type: str,
        **kwargs
    ) -> Tuple[pd.DataFrame, Optional[int]]:
        self._logger.info(f"Iniciando coleta batch: {symbol}, {timeframe}, {data_type}")
        if not self.connect():
            raise RuntimeError("Não foi possível conectar ao MT5.")

        ohlc_decimals = self._get_decimals_for_symbol(symbol)
        if ohlc_decimals is None:
            return pd.DataFrame(columns=COLUMNS_REQUIRED), None

        # Exemplo de mapeamento de timeframes
        tf_map = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
                  "M15": mt5.TIMEFRAME_M15, "H1": mt5.TIMEFRAME_H1,
                  "D1": mt5.TIMEFRAME_D1}
        tf = tf_map.get(timeframe.upper())

        # Coleta de dados via MT5
        rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
        df = pd.DataFrame(rates)

        if df.empty:
            return pd.DataFrame(columns=COLUMNS_REQUIRED), ohlc_decimals

        # Identifica campos de volume válidos
        valid_volumes = [v for v in self.volume_sources if v in df.columns and df[v].notna().any()]
        if not valid_volumes:
            self._logger.critical(
                f"Nenhum campo de volume válido encontrado para {symbol}.")
            return pd.DataFrame(columns=COLUMNS_REQUIRED), ohlc_decimals

        # Escolha de volume (respeitando volume_column se fornecido)
        if self.volume_column and self.volume_column in valid_volumes:
            chosen_volume = self.volume_column
        else:
            if len(valid_volumes) > 1:
                msg = (
                    f"Mais de um campo de volume com valores válidos: {valid_volumes}."
                    " Defina explicitamente o campo correto via volume_column no init do MT5Connector."
                )
                self._logger.warning(msg)
            chosen_volume = valid_volumes[0]

        df["volume"] = df[chosen_volume]
        self._logger.info(f"Campo de volume utilizado: '{chosen_volume}'")

        # Padroniza nomes
        rename_map = {"time": "datetime"}
        df = df.rename(columns=rename_map)

        # Conversão de timestamp para segundos (unit='s')
        if "datetime" in df.columns:
            df["time"] = pd.to_datetime(df["datetime"], unit="s").astype(int) // 10**9
        else:
            self._logger.critical("Coluna 'datetime' ausente após padronização.")
            return pd.DataFrame(columns=COLUMNS_REQUIRED), ohlc_decimals

        # Valida colunas obrigatórias
        for col in COLUMNS_REQUIRED:
            if col not in df.columns:
                self._logger.critical(f"Coluna obrigatória '{col}' ausente após padronização.")
                return pd.DataFrame(columns=COLUMNS_REQUIRED), ohlc_decimals

        # Tipagem e ordenação
        df = df[COLUMNS_REQUIRED]
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df.sort_values("datetime", inplace=True)
        df["time"] = pd.to_numeric(df["time"], errors="coerce", downcast="integer")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df, ohlc_decimals

    def _get_decimals_for_symbol(self, symbol: str) -> Optional[int]:
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info and hasattr(symbol_info, 'digits'):
                return symbol_info.digits
            self._logger.critical(
                f"Falha crítica ao obter decimais do ativo '{symbol}' via MT5.")
            return None
        except Exception as e:
            self._logger.critical(
                f"Erro inesperado ao consultar decimais do ativo '{symbol}' via MT5: {e}")
            return None

    def _detect_gaps_outliers(self, df: pd.DataFrame) -> None:
        # Placeholder para detecção de gaps/outliers
        pass

    def on_new_data(self, callback: Callable):
        self._callback = callback
        self._logger.info("Callback de novos dados registrado.")
