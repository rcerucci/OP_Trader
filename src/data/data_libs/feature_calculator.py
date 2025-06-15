#!/usr/bin/env python3
"""
src/data/data_libs/feature_calculator.py

FeatureCalculator — Calculadora plugável de indicadores técnicos Op_Trader

Autor: Equipe Op_Trader
Data: 2025-06-14
"""

import pandas as pd
import numpy as np
import numba as nb
from tqdm import tqdm
from typing import Callable, Optional, List, Dict, Any
from src.utils.logging_utils import get_logger

@nb.njit
def _calc_optimal_action_numba(close, lookforward, pip_size):
    n = len(close)
    result = np.full(n, np.nan)
    
    for i in range(n - lookforward):
        current_price = close[i]
        
        # Encontra max/min na janela futura
        max_price = close[i+1]
        min_price = close[i+1]
        
        for j in range(i+2, i+1+lookforward):
            if close[j] > max_price:
                max_price = close[j]
            if close[j] < min_price:
                min_price = close[j]
        
        max_up = max_price - current_price
        max_down = current_price - min_price
        optimal_points = max(max_up, max_down)
        result[i] = optimal_points / pip_size
    
    return result

@nb.njit  
def _calc_trend_following_numba(close, lookforward, pip_size):
    n = len(close)
    result = np.full(n, np.nan)
    
    for i in range(n - lookforward):
        result[i] = (close[i + lookforward] - close[i]) / pip_size
    
    return result

@nb.njit
def _calc_mean_reversion_numba(close, lookforward, pip_size):
    n = len(close)
    result = np.full(n, np.nan)
    
    for i in range(n - lookforward):
        current_price = close[i]
        
        # Calcula mediana da janela futura
        future_window = close[i+1:i+1+lookforward]
        
        # Ordena para encontrar mediana
        sorted_window = np.sort(future_window)
        window_len = len(sorted_window)
        
        if window_len % 2 == 0:
            median = (sorted_window[window_len//2 - 1] + sorted_window[window_len//2]) / 2.0
        else:
            median = sorted_window[window_len//2]
        
        result[i] = (current_price - median) / pip_size
    
    return result

class FeatureCalculator:
    """
    Calculadora de indicadores técnicos para DataFrames padronizados Op_Trader.

    Usage:
        calc = FeatureCalculator(debug=True)
        df_out = calc.calculate_all(df, features=[...], params={...})
        df_out = FeatureCalculator.add_time_features(df_out, modelo="ppo")  # ou modelo="mlp"
    """

    def __init__(self, debug: bool = False):
        self.logger = get_logger("op_trader.feature_calculator", "DEBUG" if debug else None)
        self.logger.propagate = False
        self._registry: Dict[str, Callable] = {}
        self._last_metadata: Dict[str, Any] = {}
        self.debug = debug
        self._register_core_features()

    def register_feature(self, name: str, func: Callable):
        self._registry[name] = func
        self.logger.debug(f"Feature registrada: {name}")

    def list_available_features(self) -> List[str]:
        return list(self._registry.keys())

    def get_last_metadata(self) -> Dict[str, Any]:
        return self._last_metadata

    def calculate_all(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None,
        params: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> pd.DataFrame:
        """
        Calcula todas as features requisitadas no DataFrame, com barra de progresso padrão Op_Trader.
        """
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("DataFrame vazio ou inválido.")

        features_to_calc = features or self.list_available_features()
        out_df = df.copy()
        log_feats: List[str] = []
        calc_params: Dict[str, Any] = {}

        # Barra de progresso (exibe somente se não estiver em modo silencioso)
        barra = tqdm(
            features_to_calc,
            desc="[Op_Trader] Calculando features",
            unit="feature",
            disable=False, # self.debug,  # Exibe só em debug, se quiser sempre visível, troque para False
            leave=True,
            # ncols=80
        )

        for feat in barra:
            func = self._registry.get(feat)
            if func is None:
                self.logger.warning(f"Feature '{feat}' não registrada. Ignorando.")
                continue
            feat_params = (params or {}).get(feat, {})
            self.logger.debug(f"Cálculo '{feat}' params={feat_params}")

            result = func(out_df, **feat_params)
            if isinstance(result, pd.Series):
                out_df[feat] = result
            elif isinstance(result, pd.DataFrame):
                for col in result.columns:
                    out_df[col] = result[col]
            else:
                raise ValueError(f"Feature '{feat}' retornou tipo inválido: {type(result)}")

            log_feats.append(feat)
            calc_params[feat] = feat_params
            barra.set_postfix_str(feat)

        self._last_metadata = {"features": log_feats, "params": calc_params}
        self.logger.info(f"Features calculadas: {log_feats}")
        return out_df

    # ======================== REGISTRO DE FEATURES ============================
    def _register_core_features(self):
        """
        Registra todas as funções de cálculo de features disponíveis no pipeline,
        resolvendo corretamente conflitos de parâmetros e priorizando o uso de
        kwargs propagados pelo pipeline externo (run_pipeline/DataPipeline).

        Todos os parâmetros obrigatórios de cada feature devem ser fornecidos
        via kwargs — evitando conflito (ex: 'window', 'lag').

        Garantia: NÃO será passado duplamente nenhum argumento obrigatório.

        Padrão: Se a feature recebe param fixo, propaga apenas se não vier em kwargs.
        """
        core_funcs = {
            "ema_fast": self._calc_ema_fast,
            "ema_slow": self._calc_ema_slow,
            "rsi": self._calc_rsi,
            "macd_hist": self._calc_macd_hist,
            "atr": self._calc_atr,
            "bb_width": self._calc_bb_width,
            "return_pct": self._calc_return_pct,
            "candle_direction": self._calc_candle_direction,
            "volume_relative": self._calc_volume_relative,
            "pullback": self._calc_pullback,
            "hammer_pattern": self._calc_hammer_pattern,
            "inverted_hammer_pattern": self._calc_inverted_hammer_pattern,
            "roc_5": self._calc_roc,
            "roc_10": self._calc_roc,
            "roc_20": self._calc_roc,
            "momentum_3": self._calc_momentum,
            "momentum_5": self._calc_momentum,
            "williams_r": self._calc_williams_r,
            "stoch_k": self._calc_stoch_k,
            "stoch_d": self._calc_stoch_d,
            "adx": self._calc_adx,
            "cci": self._calc_cci,
            "trix": self._calc_trix,
            "atr_normalized": self._calc_atr_normalized,
            "realized_vol_5": self._calc_realized_vol,
            "realized_vol_10": self._calc_realized_vol,
            "parkinson_vol": self._calc_parkinson_vol,
            "gap_analysis": self._calc_gap_analysis,
            "breakout_signals": self._calc_breakout_signals,
            "support_resistance": self._calc_support_resistance,
            "pivot_points": self._calc_pivot_points,
            "fibonacci_levels": self._calc_fibonacci_levels,
            "price_channels": self._calc_price_channels,
            "session_phase": self._calc_session_phase,
            "day_of_week": self._calc_day_of_week,
            "week_of_month": self._calc_week_of_month,
            "market_hours": self._calc_market_hours,
            "intraday_mean_reversion": self._calc_intraday_mean_reversion,
            "trend_strength": self._calc_trend_strength,
            "market_regime": self._calc_market_regime,
            "volatility_regime": self._calc_volatility_regime,
            "risk_adjusted_return": self._calc_risk_adjusted_return,
            "max_drawdown_risk": self._calc_max_drawdown_risk,
            "sharpe_estimate": self._calc_sharpe_estimate,
            "risk_on_off": self._calc_risk_on_off,
            "higher_tf_trend": self._calc_higher_tf_trend,
            "daily_range_position": self._calc_daily_range_position,
            "weekly_momentum": self._calc_weekly_momentum,
            "price_clusters": self._calc_price_clusters,
            "anomaly_score": self._calc_anomaly_score,
            "regime_probability": self._calc_regime_probability,
            "forecast_error": self._calc_forecast_error,
            "delta_points": self._calc_delta_points,
        }
        self.feature_funcs = core_funcs
        for name, func in core_funcs.items():
            self.register_feature(name, func)

    # ======================== FUNÇÕES DE FEATURE ==============================

    def _require_cols(self, df, cols, label):
        missing = set(cols) - set(df.columns)
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes para {label}: {missing}")

    def _calc_ema_fast(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, f"EMA Fast[{window}]")
        return df[column].ewm(span=window, adjust=False).mean()

    def _calc_ema_slow(self, df: pd.DataFrame, window: int = 50, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, f"EMA Slow[{window}]")
        return df[column].ewm(span=window, adjust=False).mean()

    def _calc_rsi(self, df: pd.DataFrame, window: int = 14, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, f"RSI[{window}]")
        delta = df[column].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calc_macd_hist(
        self, df: pd.DataFrame, span_short: int = 12, span_long: int = 26,
        span_signal: int = 9, column: str = "close", **kwargs
    ) -> pd.Series:
        self._require_cols(df, {column}, "MACD")
        ema_short = df[column].ewm(span=span_short, adjust=False).mean()
        ema_long = df[column].ewm(span=span_long, adjust=False).mean()
        macd_line = ema_short - ema_long
        signal_line = macd_line.ewm(span=span_signal, adjust=False).mean()
        return macd_line - signal_line

    def _calc_atr(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "ATR")
        high, low, prev = df["high"], df["low"], df["close"].shift(1)
        tr1 = high - low
        tr2 = (high - prev).abs()
        tr3 = (low - prev).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.rolling(window=window, min_periods=window).mean()

    def _calc_bb_width(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "BB Width")
        ma = df[column].rolling(window=window).mean()
        std = df[column].rolling(window=window).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        return upper - lower

    def _calc_return_pct(self, df: pd.DataFrame, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Return %")
        return df[column].pct_change()

    def _calc_candle_direction(self, df: pd.DataFrame, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Candle Direction")
        diff = df[column].diff()
        arr = np.where(diff > 0, 1, np.where(diff < 0, -1, 0))
        return pd.Series(arr, index=df.index)

    def _calc_volume_relative(self, df: pd.DataFrame, window: int = 20, column: str = "volume", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Volume Relative")
        mean_vol = df[column].rolling(window=window).mean()
        return df[column] / (mean_vol.replace(0, np.nan))

    def _calc_pullback(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Pullback")
        ma = df[column].rolling(window=window).mean()
        return df[column] - ma

    def _calc_hammer_pattern(self, df: pd.DataFrame, window: int = 5, **kwargs) -> pd.Series:
        self._require_cols(df, {"open", "high", "low", "close"}, "Hammer Pattern")
        body = (df["close"] - df["open"]).abs()
        lower = np.where(
            df["close"] > df["open"], df["open"] - df["low"], df["close"] - df["low"],
        )
        is_hammer = (lower >= 2 * body) & (body <= 0.3 * (df["high"] - df["low"]))
        return is_hammer.astype(float)

    def _calc_inverted_hammer_pattern(self, df: pd.DataFrame, window: int = 5, **kwargs) -> pd.Series:
        self._require_cols(df, {"open", "high", "low", "close"}, "Inverted Hammer")
        body = (df["close"] - df["open"]).abs()
        upper = np.where(
            df["close"] > df["open"], df["high"] - df["close"], df["high"] - df["open"],
        )
        is_inv_hammer = (upper >= 2 * body) & (body <= 0.3 * (df["high"] - df["low"]))
        return is_inv_hammer.astype(float)

    def _calc_roc(self, df: pd.DataFrame, window: int = 5, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, f"ROC[{window}]")
        return df[column].diff(window) / df[column].shift(window)

    def _calc_momentum(self, df: pd.DataFrame, lag: int = 3, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, f"Momentum[{lag}]")
        return df[column] - df[column].shift(lag)

    def _calc_williams_r(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "Williams %R")
        high_roll = df["high"].rolling(window)
        low_roll = df["low"].rolling(window)
        highest_high = high_roll.max()
        lowest_low = low_roll.min()
        return -100 * (highest_high - df["close"]) / (highest_high - lowest_low)

    def _calc_stoch_k(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "Stochastic %K")
        lowest_low = df["low"].rolling(window=window).min()
        highest_high = df["high"].rolling(window=window).max()
        return 100 * (df["close"] - lowest_low) / (highest_high - lowest_low)

    def _calc_stoch_d(self, df: pd.DataFrame, window: int = 3, **kwargs) -> pd.Series:
        self._require_cols(df, {"stoch_k"}, "Stochastic %D")
        return df["stoch_k"].rolling(window=window).mean()

    def _calc_adx(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "ADX")
        plus_dm = df["high"].diff()
        minus_dm = df["low"].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr = pd.concat([
            df["high"] - df["low"],
            (df["high"] - df["close"].shift(1)).abs(),
            (df["low"] - df["close"].shift(1)).abs()
        ], axis=1).max(axis=1)
        tr_smooth = tr.rolling(window).mean()
        plus_di = 100 * (plus_dm.rolling(window).sum() / tr_smooth)
        minus_di = 100 * (minus_dm.abs().rolling(window).sum() / tr_smooth)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        return dx.rolling(window=window).mean()

    @nb.njit
    def _mean_deviation(values):
        """Calcula desvio médio absoluto de forma otimizada"""
        mean_val = np.mean(values)
        return np.mean(np.abs(values - mean_val))

    def _calc_cci(self, df: pd.DataFrame, window: int = 20, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "CCI")
        
        tp = (df["high"] + df["low"] + df["close"]) / 3
        ma = tp.rolling(window=window).mean()
        
        # Versão numba - muito mais rápida
        md = tp.rolling(window=window).apply(
            self._mean_deviation, 
            engine='numba', 
            raw=True
        )
        
        return (tp - ma) / (0.015 * md)

    def _calc_trix(self, df: pd.DataFrame, window: int = 15, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "TRIX")
        ema1 = df[column].ewm(span=window, adjust=False).mean()
        ema2 = ema1.ewm(span=window, adjust=False).mean()
        ema3 = ema2.ewm(span=window, adjust=False).mean()
        return ema3.pct_change()

    def _calc_atr_normalized(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        atr = self._calc_atr(df, window=window)
        self._require_cols(df, {"close"}, "ATR Normalized")
        return atr / df["close"]

    def _calc_realized_vol(self, df: pd.DataFrame, window: int = 5, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Realized Vol")
        returns = df[column].pct_change()
        return returns.rolling(window=window).std()

    def _calc_parkinson_vol(self, df: pd.DataFrame, window: int = 10, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low"}, "Parkinson Vol")
        return (1.0 / (4.0 * np.log(2))) * ((np.log(df["high"] / df["low"])) ** 2).rolling(window).mean()

    def _calc_gap_analysis(self, df: pd.DataFrame, threshold: float = 0.002, **kwargs) -> pd.Series:
        self._require_cols(df, {"open", "close"}, "Gap Analysis")
        gap = (df["open"] - df["close"].shift(1)).abs() / df["close"].shift(1)
        return (gap > threshold).astype(int)

    def _calc_breakout_signals(self, df: pd.DataFrame, window: int = 20, threshold: float = 0.002, **kwargs) -> pd.Series:
        self._require_cols(df, {"high", "low", "close"}, "Breakout Signals")
        high_roll = df["high"].rolling(window=window).max()
        low_roll = df["low"].rolling(window=window).min()
        breakout = (df["close"] >= high_roll * (1 + threshold)) | (df["close"] <= low_roll * (1 - threshold))
        return breakout.astype(int)

    def _calc_support_resistance(self, df: pd.DataFrame, lookback: int = 20, **kwargs) -> pd.DataFrame:
        self._require_cols(df, {"high", "low", "close"}, "Support/Resistance")
        dist_resistance = (df["high"].rolling(window=lookback).max() - df["close"])
        dist_support = (df["close"] - df["low"].rolling(window=lookback).min())
        return pd.DataFrame({
            "dist_resistance": dist_resistance,
            "dist_support": dist_support
        })

    def _calc_pivot_points(self, df: pd.DataFrame, method: str = "classic", **kwargs) -> pd.DataFrame:
        self._require_cols(df, {"high", "low", "close"}, "Pivot Points")
        high = df["high"]
        low = df["low"]
        close = df["close"]
        pp = (high + low + close) / 3
        if method == "classic":
            r1 = (2 * pp) - low
            s1 = (2 * pp) - high
            r2 = pp + (high - low)
            s2 = pp - (high - low)
        else:
            # Adicione outros métodos conforme necessário
            r1 = r2 = s1 = s2 = pp
        return pd.DataFrame({"pp": pp, "r1": r1, "r2": r2, "s1": s1, "s2": s2})

    def _calc_fibonacci_levels(self, df: pd.DataFrame, lookback: int = 20, **kwargs) -> pd.DataFrame:
        self._require_cols(df, {"high", "low"}, "Fibonacci Levels")
        high = df["high"].rolling(window=lookback).max()
        low = df["low"].rolling(window=lookback).min()
        diff = high - low
        fib_0 = low
        fib_236 = low + 0.236 * diff
        fib_382 = low + 0.382 * diff
        fib_5 = low + 0.5 * diff
        fib_618 = low + 0.618 * diff
        fib_786 = low + 0.786 * diff
        fib_1 = high
        return pd.DataFrame({
            "fib_0": fib_0, "fib_236": fib_236, "fib_382": fib_382, "fib_5": fib_5,
            "fib_618": fib_618, "fib_786": fib_786, "fib_1": fib_1
        })

    def _calc_price_channels(self, df: pd.DataFrame, window: int = 20, **kwargs) -> pd.DataFrame:
        self._require_cols(df, {"high", "low"}, "Price Channels")
        channel_high = df["high"].rolling(window=window).max()
        channel_low = df["low"].rolling(window=window).min()
        return pd.DataFrame({"channel_high": channel_high, "channel_low": channel_low})

    def _calc_session_phase(self, df: pd.DataFrame, bins: int = 3, **kwargs) -> pd.Series:
        # Dummy implementation: divida o dia em 'bins' partes (melhore conforme sua regra real)
        if "datetime" not in df.columns:
            raise ValueError("session_phase requer coluna datetime")
        minutes = pd.to_datetime(df["datetime"]).dt.hour * 60 + pd.to_datetime(df["datetime"]).dt.minute
        phase = pd.cut(minutes, bins, labels=False)
        return phase

    def _calc_day_of_week(self, df: pd.DataFrame, format: str = "int", **kwargs) -> pd.Series:
        if "datetime" not in df.columns:
            raise ValueError("day_of_week requer coluna datetime")
        dow = pd.to_datetime(df["datetime"]).dt.dayofweek
        return dow if format == "int" else dow.astype(str)

    def _calc_week_of_month(self, df: pd.DataFrame, mode: str = "simple", **kwargs) -> pd.Series:
        if "datetime" not in df.columns:
            raise ValueError("week_of_month requer coluna datetime")
        days = pd.to_datetime(df["datetime"]).dt.day
        return ((days - 1) // 7 + 1).astype(int)

    def _calc_market_hours(self, df: pd.DataFrame, session: str = "london,newyork,tokyo", **kwargs) -> pd.Series:
        # Implementação simplificada, ajuste conforme necessidade
        if "datetime" not in df.columns:
            raise ValueError("market_hours requer coluna datetime")
        hours = pd.to_datetime(df["datetime"]).dt.hour
        return pd.Series(
            np.select(
                [
                    (hours >= 8) & (hours < 16),   # London
                    (hours >= 14) & (hours < 23),  # New York
                    (hours >= 0) & (hours < 9)     # Tokyo
                ],
                [0, 1, 2], -1
            ),
            index=df.index
        )
    def _calc_intraday_mean_reversion(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Intraday Mean Reversion")
        day = pd.to_datetime(df["datetime"]).dt.date
        group = df[column].groupby(day)
        mean = group.transform("mean")
        return df[column] - mean

    def _calc_trend_strength(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        atr = self._calc_atr(df, window=window)
        high = df["high"].rolling(window=window).max()
        low = df["low"].rolling(window=window).min()
        return (high - low) / atr

    def _calc_market_regime(self, df: pd.DataFrame, method: str = "std", window: int = 14, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Market Regime")
        if method == "std":
            std = df[column].rolling(window=window).std()
            return (std > std.mean()).astype(int)
        return pd.Series(0, index=df.index)

    def _calc_volatility_regime(self, df: pd.DataFrame, method: str = "atr", window: int = 14, **kwargs) -> pd.Series:
        if method == "atr":
            atr = self._calc_atr(df, window=window)
            return (atr > atr.mean()).astype(int)
        return pd.Series(0, index=df.index)

    def _calc_risk_adjusted_return(self, df: pd.DataFrame, window: int = 14, **kwargs) -> pd.Series:
        atr = self._calc_atr(df, window=window)
        self._require_cols(df, {"close"}, "Risk Adjusted Return")
        ret = df["close"].pct_change()
        return ret / (atr + 1e-8)

    def _calc_max_drawdown_risk(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Max Drawdown Risk")
        roll_max = df[column].rolling(window=window, min_periods=1).max()
        roll_min = df[column].rolling(window=window, min_periods=1).min()
        return (roll_max - roll_min) / roll_max

    def _calc_sharpe_estimate(self, df: pd.DataFrame, window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Sharpe Estimate")
        returns = df[column].pct_change()
        mean = returns.rolling(window=window).mean()
        std = returns.rolling(window=window).std()
        return mean / (std + 1e-8)

    def _calc_risk_on_off(self, df: pd.DataFrame, **kwargs) -> pd.Series:
        # Dummy: sempre zero. Ajuste conforme lógica real.
        return pd.Series(0, index=df.index)

    def _calc_higher_tf_trend(self, df: pd.DataFrame, tf: str = "H1", window: int = 10, column: str = "close", **kwargs) -> pd.Series:
        # Dummy para exemplo: tendência do rolling window
        self._require_cols(df, {column}, "Higher TF Trend")
        return df[column].rolling(window=window).mean().diff().apply(np.sign)

    def _calc_daily_range_position(self, df: pd.DataFrame, lookback: int = 1, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Daily Range Position")
        day = pd.to_datetime(df["datetime"]).dt.date
        high = df.groupby(day)["high"].transform("max")
        low = df.groupby(day)["low"].transform("min")
        return (df[column] - low) / (high - low + 1e-8)

    def _calc_weekly_momentum(self, df: pd.DataFrame, lag: int = 5, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Weekly Momentum")
        return df[column] - df[column].shift(lag)

    def _calc_price_clusters(self, df: pd.DataFrame, n: int = 3, method: str = "kmeans", column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Price Clusters")
        # Dummy: clusterização linear
        quantiles = pd.qcut(df[column], n, labels=False, duplicates="drop")
        return quantiles

    def _calc_anomaly_score(self, df: pd.DataFrame, method: str = "isolation_forest", window: int = 20, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Anomaly Score")
        # Dummy: score zero, substitua por implementação real se necessário.
        return pd.Series(0, index=df.index)

    def _calc_regime_probability(self, df: pd.DataFrame, method: str = "hmm", states: int = 2, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Regime Probability")
        # Dummy: probabilidade igual
        return pd.Series(1 / states, index=df.index)

    def _calc_forecast_error(self, df: pd.DataFrame, method: str = "rolling_mean", window: int = 5, column: str = "close", **kwargs) -> pd.Series:
        self._require_cols(df, {column}, "Forecast Error")
        if method == "rolling_mean":
            pred = df[column].rolling(window=window).mean()
            return df[column] - pred
        return pd.Series(0, index=df.index)

    def _calc_delta_points(self, df: pd.DataFrame, lookforward: int = 12, pip_size: float = 0.0001,
                        method: str = "optimal_action", min_hold: int = 3, **kwargs) -> pd.Series:
        """
        Calcula delta points usando implementação otimizada com numba
        """
        logger = getattr(self, "logger", None)
        
        # Verificação de requisitos mínimos
        if len(df) < lookforward + min_hold:
            if logger:
                logger.warning("[Op_Trader] delta_points: Amostra insuficiente para cálculo.")
            return pd.Series(np.nan, index=df.index)
        
        # Verifica se coluna close existe
        if 'close' not in df.columns:
            if logger:
                logger.error("[Op_Trader] delta_points: Coluna 'close' não encontrada.")
            return pd.Series(np.nan, index=df.index)
        
        close = df['close'].values
        
        # Verifica se há valores NaN
        if np.any(np.isnan(close)):
            if logger:
                logger.warning("[Op_Trader] delta_points: Valores NaN encontrados na série de preços.")
        
        try:
            if method == "optimal_action":
                result = _calc_optimal_action_numba(close, lookforward, pip_size)
            elif method == "trend_following":
                result = _calc_trend_following_numba(close, lookforward, pip_size)
            elif method == "mean_reversion":
                result = _calc_mean_reversion_numba(close, lookforward, pip_size)
            else:
                if logger:
                    logger.warning(f"[Op_Trader] delta_points: Método '{method}' não reconhecido.")
                result = np.full(len(close), np.nan)
            
            return pd.Series(result, index=df.index)
            
        except Exception as e:
            if logger:
                logger.error(f"[Op_Trader] delta_points: Erro no cálculo: {str(e)}")
            return pd.Series(np.nan, index=df.index)


    # ======================== EXTRAS ==========================================
    @staticmethod
    def add_time_features(df: pd.DataFrame, modelo: str = "ppo") -> pd.DataFrame:
        # Adiciona colunas de time/ciclo para downstream (exemplo simples)
        df = df.copy()
        if "datetime" in df.columns:
            dt = pd.to_datetime(df["datetime"])
            df["bar_of_day"] = dt.dt.hour * 12 + dt.dt.minute // 5  # exemplo M5
            df["sin_time"] = np.sin(2 * np.pi * df["bar_of_day"] / 288)
            df["cos_time"] = np.cos(2 * np.pi * df["bar_of_day"] / 288)
        return df

# EOF
