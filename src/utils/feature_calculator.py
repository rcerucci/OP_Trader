# src/utils/feature_calculator.py

"""
feature_calculator.py

Classe utilitária para cálculo robusto de indicadores técnicos, padrões de candles e features de price action
para o pipeline Op_Trader. Permite fácil extensão e validação de features para modelos de trading.

Autor: Equipe Op_Trader
Data: 2025-06-06
"""

import numpy as np
import pandas as pd
from typing import Optional

from src.utils.logging_utils import get_logger
from src.utils.path_setup import ensure_project_root

ROOT_DIR = ensure_project_root(__file__)

class FeatureCalculator:
    """
    Calculadora de indicadores técnicos e padrões de candles.

    Métodos principais:
      - calculate_ema
      - calculate_rsi
      - calculate_macd_hist
      - calculate_atr
      - calculate_bb_width
      - calculate_return_pct
      - calculate_candle_direction
      - calculate_tick_volume_relative
      - calculate_pullback_to_ema20
      - calculate_hammer_pattern
      - calculate_inverted_hammer_pattern

    Args:
        debug (bool): Se True, logging detalhado.
    """

    def __init__(self, debug: bool = False):
        """
        Inicializa o FeatureCalculator.

        Args:
            debug (bool, optional): Se True, ativa logs em nível DEBUG. Default False.
        """
        level = "DEBUG" if debug else None
        self.logger = get_logger(self.__class__.__name__, level)

    def _validate_columns(self, df: pd.DataFrame, required: set, context: str):
        """Valida se as colunas necessárias estão presentes; raise e loga se não."""
        missing = required - set(df.columns)
        if missing:
            msg = f"Colunas obrigatórias ausentes para {context}: {missing}"
            self.logger.error(msg)
            raise KeyError(msg)

    def calculate_ema(self, df: pd.DataFrame, window: int, column: str = "close") -> pd.Series:
        """
        Calcula a EMA de janela especificada para a coluna dada.

        Args:
            df (pd.DataFrame): DataFrame com colunas de preço.
            window (int): Período da EMA.
            column (str, optional): Coluna para cálculo. Defaults to "close".

        Returns:
            pd.Series: Série com valores da EMA.

        Raises:
            KeyError: Se coluna de preço não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> ema_20 = calc.calculate_ema(df, window=20)
        """
        self._validate_columns(df, {column}, f"EMA[{window}]")
        self.logger.debug(f"Calculando EMA{window} para '{column}', shape={df.shape}")
        return df[column].ewm(span=window, adjust=False).mean()

    def calculate_rsi(self, df: pd.DataFrame, window: int = 14, column: str = "close") -> pd.Series:
        """
        Calcula o RSI (Relative Strength Index) de janela 'window'.

        Args:
            df (pd.DataFrame): DataFrame com colunas de preço.
            window (int, optional): Período do RSI. Defaults to 14.
            column (str, optional): Coluna para cálculo. Defaults to "close".

        Returns:
            pd.Series: Série com valores do RSI.

        Raises:
            KeyError: Se coluna de preço não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> rsi = calc.calculate_rsi(df)
        """
        self._validate_columns(df, {column}, "RSI")
        self.logger.debug(f"Calculando RSI{window} de '{column}', shape={df.shape}")
        delta = df[column].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd_hist(
        self,
        df: pd.DataFrame,
        span_short: int = 12,
        span_long: int = 26,
        span_signal: int = 9,
        column: str = "close",
    ) -> pd.Series:
        """
        Calcula o histograma do MACD (MACD_line - Signal_line).

        Args:
            df (pd.DataFrame): DataFrame com colunas de preço.
            span_short (int, optional): Período curto para EMA. Defaults to 12.
            span_long (int, optional): Período longo para EMA. Defaults to 26.
            span_signal (int, optional): Período para linha de sinal. Defaults to 9.
            column (str, optional): Coluna para cálculo. Defaults to "close".

        Returns:
            pd.Series: Série com valores do histograma do MACD.

        Raises:
            KeyError: Se coluna de preço não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> macd_hist = calc.calculate_macd_hist(df)
        """
        self._validate_columns(df, {column}, "MACD")
        self.logger.debug(f"Calculando MACD({span_short},{span_long},{span_signal}) para '{column}', shape={df.shape}")
        ema_short = df[column].ewm(span=span_short, adjust=False).mean()
        ema_long = df[column].ewm(span=span_long, adjust=False).mean()
        macd_line = ema_short - ema_long
        signal_line = macd_line.ewm(span=span_signal, adjust=False).mean()
        hist = macd_line - signal_line
        return hist

    def calculate_atr(self, df: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        Calcula o ATR (Average True Range) de janela 'window'.

        Args:
            df (pd.DataFrame): DataFrame com colunas 'high', 'low', 'close'.
            window (int, optional): Período para cálculo do ATR. Defaults to 14.

        Returns:
            pd.Series: Série com valores do ATR.

        Raises:
            KeyError: Se faltar coluna obrigatória.

        Example:
            >>> calc = FeatureCalculator()
            >>> atr = calc.calculate_atr(df)
        """
        self._validate_columns(df, {"high", "low", "close"}, "ATR")
        self.logger.debug(f"Calculando ATR{window}, shape={df.shape}")
        high = df["high"]
        low = df["low"]
        close_prev = df["close"].shift(1)
        tr1 = high - low
        tr2 = (high - close_prev).abs()
        tr3 = (low - close_prev).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=window, min_periods=window).mean()
        return atr

    def calculate_bb_width(self, df: pd.DataFrame, window: int = 20, column: str = "close") -> pd.Series:
        """
        Calcula a largura das Bollinger Bands: upper_band - lower_band.

        Args:
            df (pd.DataFrame): DataFrame com colunas de preço.
            window (int, optional): Período para cálculo de média móvel. Defaults to 20.
            column (str, optional): Coluna para cálculo. Defaults to "close".

        Returns:
            pd.Series: Série com valores da largura das Bollinger Bands.

        Raises:
            KeyError: Se faltar coluna.

        Example:
            >>> calc = FeatureCalculator()
            >>> bb_width = calc.calculate_bb_width(df)
        """
        self._validate_columns(df, {column}, "BB Width")
        self.logger.debug(f"Calculando BB Width{window} de '{column}', shape={df.shape}")
        sma = df[column].rolling(window=window, min_periods=window).mean()
        std = df[column].rolling(window=window, min_periods=window).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        bb_width = upper_band - lower_band
        return bb_width

    def calculate_return_pct(self, df: pd.DataFrame, column: str = "close") -> pd.Series:
        """
        Calcula a variação percentual para a coluna especificada.

        Args:
            df (pd.DataFrame): DataFrame com colunas de preço.
            column (str, optional): Coluna para cálculo. Defaults to "close".

        Returns:
            pd.Series: Série com valores de retorno percentual.

        Raises:
            KeyError: Se coluna não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> returns = calc.calculate_return_pct(df)
        """
        self._validate_columns(df, {column}, "Return %")
        self.logger.debug(f"Calculando retorno percentual de '{column}', shape={df.shape}")
        return df[column].pct_change()

    def calculate_candle_direction(self, df: pd.DataFrame) -> pd.Series:
        """
        Retorna +1 quando close > open, -1 quando close < open, ou 0 quando igual.

        Args:
            df (pd.DataFrame): DataFrame com colunas 'open' e 'close'.

        Returns:
            pd.Series: Série com valores em {1.0, -1.0, 0.0}.

        Raises:
            KeyError: Se colunas não existirem.

        Example:
            >>> calc = FeatureCalculator()
            >>> direction = calc.calculate_candle_direction(df)
        """
        self._validate_columns(df, {"open", "close"}, "Candle Direction")
        self.logger.debug(f"Calculando direção de candle, shape={df.shape}")
        diff = df["close"] - df["open"]
        direction = diff.apply(lambda x: 1.0 if x > 0 else (-1.0 if x < 0 else 0.0))
        return direction

    def calculate_tick_volume_relative(self, df: pd.DataFrame, window: int = 5) -> pd.Series:
        """
        Normaliza volume usando média e desvio sobre 'window' candles.

        Args:
            df (pd.DataFrame): DataFrame com coluna 'tick_volume'.
            window (int, optional): Janela para cálculo. Defaults to 5.

        Returns:
            pd.Series: Série com valores de volume relativo.

        Raises:
            KeyError: Se coluna não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> vol_rel = calc.calculate_tick_volume_relative(df)
        """
        self._validate_columns(df, {"tick_volume"}, "Tick Volume Relative")
        self.logger.debug(f"Calculando volume relativo (janela={window}), shape={df.shape}")
        vol = df["tick_volume"]
        ma = vol.rolling(window=window, min_periods=window).mean()
        std = vol.rolling(window=window, min_periods=window).std()
        vol_rel = (vol - ma) / std.replace(0, np.nan)
        return vol_rel

    def calculate_pullback_to_ema20(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula o pullback para a EMA de 20 períodos (diferença percentual entre close e EMA20).

        Args:
            df (pd.DataFrame): DataFrame com coluna 'close'.

        Returns:
            pd.Series: Série com valores de pullback para EMA20.

        Raises:
            KeyError: Se coluna 'close' não existir.

        Example:
            >>> calc = FeatureCalculator()
            >>> pullback = calc.calculate_pullback_to_ema20(df)
        """
        self._validate_columns(df, {"close"}, "Pullback EMA20")
        self.logger.debug(f"Calculando pullback para EMA20, shape={df.shape}")
        ema20 = self.calculate_ema(df, window=20)
        pullback = (df["close"] - ema20) / ema20
        return pullback

    def calculate_hammer_pattern(self, df: pd.DataFrame) -> pd.Series:
        """
        Retorna 1.0 se a vela for do tipo 'hammer': sombra inferior ≥ 2×corpo e corpo ≤ 30% do total.

        Args:
            df (pd.DataFrame): DataFrame com colunas 'open', 'high', 'low', 'close'.

        Returns:
            pd.Series: Série com valores em {1.0, 0.0}.

        Raises:
            KeyError: Se colunas não existirem.

        Example:
            >>> calc = FeatureCalculator()
            >>> hammer = calc.calculate_hammer_pattern(df)
        """
        self._validate_columns(df, {"open", "high", "low", "close"}, "Hammer Pattern")
        self.logger.debug(f"Calculando padrão Hammer, shape={df.shape}")
        body = (df["close"] - df["open"]).abs()
        lower_shadow = np.where(
            df["close"] > df["open"],
            df["open"] - df["low"],
            df["close"] - df["low"],
        )
        total_range = df["high"] - df["low"]
        is_hammer = (lower_shadow >= 2 * body) & (body <= 0.3 * total_range)
        return is_hammer.astype(float)

    def calculate_inverted_hammer_pattern(self, df: pd.DataFrame) -> pd.Series:
        """
        Retorna 1.0 se a vela for do tipo 'inverted hammer' (shooting star): sombra superior ≥ 2×corpo e corpo ≤ 30% do total.

        Args:
            df (pd.DataFrame): DataFrame com colunas 'open', 'high', 'low', 'close'.

        Returns:
            pd.Series: Série com valores em {1.0, 0.0}.

        Raises:
            KeyError: Se colunas não existirem.

        Example:
            >>> calc = FeatureCalculator()
            >>> inv_hammer = calc.calculate_inverted_hammer_pattern(df)
        """
        self._validate_columns(df, {"open", "high", "low", "close"}, "Inverted Hammer Pattern")
        self.logger.debug(f"Calculando padrão Inverted Hammer, shape={df.shape}")
        body = (df["close"] - df["open"]).abs()
        upper_shadow = np.where(
            df["open"] > df["close"],
            df["high"] - df["open"],
            df["high"] - df["close"],
        )
        total_range = df["high"] - df["low"]
        is_inverted = (upper_shadow >= 2 * body) & (body <= 0.3 * total_range)
        return is_inverted.astype(float)
