"""
OutlierGapCorrector — Op_Trader (v2)
====================================

Correção de gaps/outliers sem inflar o número de linhas em fins‑de‑semana e
horários fora de negociação.

→ Mantém *exatamente* as mesmas assinaturas públicas do módulo original, para
  não quebrar nenhum contrato existente.
→ Adiciona filtragem de *trading‑days* e *trading‑hours* antes de reindexar.
→ Nova flag `gap_fixed` continua sendo criada quando um candle inexistente é
  preenchido dentro do horário de mercado.

Copyright © 2025
"""
from __future__ import annotations

from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

from src.utils.logging_utils import get_logger

class OutlierGapCorrector:  # assinatura preservada
    """Corrige gaps e outliers em DataFrames de candles (batch/streaming)."""

    SUPPORTED_OUTLIER_METHODS = ["iqr", "zscore", "rolling"]
    SUPPORTED_OUTLIER_CORRECTIONS = ["nan", "mean", "interpolate", "zero"]
    SUPPORTED_GAP_METHODS = ["forward_fill", "backward_fill", "interpolate", "drop"]

    # === NOVO: parâmetros default globais de agenda de mercado ===
    _TRADING_WEEKDAYS = set(range(0, 5))  # 0=segunda … 4=sexta
    _SESSION_START_MINUTE = 5   # UTC 00:05 (evita rollover)
    _SESSION_END_HOUR = 23      # UTC 23:55 último candle M5
    _SESSION_END_MINUTE = 55

    def __init__(
        self,
        freq: str,
        debug: bool = False,
        mode: str = "batch",
        gap_params: Optional[Dict[str, Any]] = None,
        outlier_params: Optional[Dict[str, Any]] = None,
    ):
        self.freq = freq
        self.debug = debug
        self.mode = mode.lower()
        self.gap_params = gap_params or {}
        self.outlier_params = outlier_params or {}
        self._logger = get_logger(
            self.__class__.__name__, cli_level="DEBUG" if self.debug else None
        )
        self._gaps_report: List[pd.Timestamp] = []
        self._outliers_report: List[Dict[str, Any]] = []

        # Aliases legados (inalterados)
        if "gap_strategy" in self.gap_params and "method" not in self.gap_params:
            self.gap_params["method"] = self.gap_params["gap_strategy"]
        if "outlier_strategy" in self.outlier_params and "method" not in self.outlier_params:
            self.outlier_params["method"] = self.outlier_params["outlier_strategy"]
        if "outlier_threshold" in self.outlier_params and "threshold" not in self.outlier_params:
            self.outlier_params["threshold"] = self.outlier_params["outlier_threshold"]

        self._logger.info(f"OutlierGapCorrector inicializado em modo '{self.mode}'.")
        self._logger.debug(f"gap_params={self.gap_params}, outlier_params={self.outlier_params}")

    # ---------------------------------------------------------------------
    # 🆕  Agenda de mercado (helper estático)                                 
    # ---------------------------------------------------------------------
    @staticmethod
    def _is_trading_datetime(ts: pd.Timestamp) -> bool:
        """Retorna True se *ts* estiver dentro de dias/horas normais de trading."""
        if ts.weekday() not in OutlierGapCorrector._TRADING_WEEKDAYS:
            return False
        if ts.hour == 0 and ts.minute < OutlierGapCorrector._SESSION_START_MINUTE:
            return False
        if ts.hour > OutlierGapCorrector._SESSION_END_HOUR or (
            ts.hour == OutlierGapCorrector._SESSION_END_HOUR
            and ts.minute > OutlierGapCorrector._SESSION_END_MINUTE
        ):
            return False
        return True

    # --------------------------- GAPS ------------------------------------

    def detect_gaps(self, df: pd.DataFrame, datetime_col: str = "datetime") -> pd.DataFrame:
        if datetime_col not in df.columns:
            self._logger.critical(f"[{self.mode}] Coluna '{datetime_col}' não encontrada.")
            return pd.DataFrame()

        idx_full = pd.date_range(
            start=df[datetime_col].min(),
            end=df[datetime_col].max(),
            freq=self.freq,
        )
        # Filtra somente horário de mercado
        idx = idx_full[[self._is_trading_datetime(ts) for ts in idx_full]]
        gaps = idx.difference(df[datetime_col])
        if not gaps.empty:
            self._logger.warning(f"[{self.mode}] Gaps detectados: {len(gaps)}")
            self._gaps_report = list(gaps)
        else:
            self._logger.debug(f"[{self.mode}] Nenhum gap detectado.")
        return pd.DataFrame({datetime_col: gaps})

    def fix_gaps(
        self,
        df: pd.DataFrame,
        method: Optional[str] = None,
        max_gap_tolerance: Optional[int] = None,
        datetime_col: str = "datetime",
    ) -> pd.DataFrame:
        """Corrige gaps dentro do horário de mercado sem inflar fins‑de‑semana."""
        method = method or self.gap_params.get("method", "forward_fill")
        max_gap_tolerance = max_gap_tolerance or self.gap_params.get("max_gap_tolerance", None)

        if method not in self.SUPPORTED_GAP_METHODS:
            raise ValueError(
                f"Gap method '{method}' não suportado. Escolha um dos: {self.SUPPORTED_GAP_METHODS}"
            )

        df = df.copy()
        if datetime_col not in df.columns:
            self._logger.critical(f"[{self.mode}] Coluna '{datetime_col}' não encontrada.")
            return df

        # Cria grade completa apenas para horários de trading
        idx_full = pd.date_range(
            start=df[datetime_col].min(),
            end=df[datetime_col].max(),
            freq=self.freq,
        )
        idx = [ts for ts in idx_full if self._is_trading_datetime(ts)]

        df.set_index(datetime_col, inplace=True)
        df = df.reindex(idx)

        # Flag gap_fixed
        df["gap_fixed"] = df.isnull().any(axis=1)

        # Preenchimento por coluna
        for col in df.columns.difference(["gap_fixed"]):
            if method == "forward_fill":
                df[col] = df[col].ffill()
            elif method == "backward_fill":
                df[col] = df[col].bfill()
            elif method == "interpolate":
                df[col] = df[col].interpolate(method="linear")
            elif method == "drop":
                df = df[~df["gap_fixed"]]
            else:
                self._logger.warning(
                    f"[{self.mode}] Estratégia '{method}' não reconhecida para gaps. Usando forward_fill."
                )
                df[col] = df[col].ffill()

        df.reset_index(inplace=True)
        df.rename(columns={"index": datetime_col}, inplace=True)
        self._logger.info(f"[{self.mode}] Gaps corrigidos com '{method}'.")
        return df

    # --------------------------- OUTLIERS -------------------------------
    # (Código intocado da versão original para preservar contratos)

    def detect_outliers(
        self,
        df: pd.DataFrame,
        method: Optional[str] = None,
        threshold: Optional[float] = None,
        window: Optional[int] = None,
    ) -> pd.DataFrame:
        method = method or self.outlier_params.get("method", "iqr")
        if threshold is None:
            threshold = 3.0 if method in ("zscore", "rolling") else None
        if method == "rolling" and window is None:
            window = 20
        if method not in self.SUPPORTED_OUTLIER_METHODS:
            raise ValueError(
                f"Outlier method '{method}' não suportado. Escolha um dos: {self.SUPPORTED_OUTLIER_METHODS}"
            )

        df_out = pd.DataFrame(index=df.index)
        for col in df.select_dtypes(include=[np.number]).columns:
            if method == "iqr":
                q1, q3 = df[col].quantile([0.25, 0.75])
                iqr = q3 - q1
                low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                mask = (df[col] < low) | (df[col] > high)
            elif method == "zscore":
                z = (df[col] - df[col].mean()) / df[col].std(ddof=0)
                mask = z.abs() > threshold
            elif method == "rolling":
                mean = df[col].rolling(window, center=True, min_periods=1).mean()
                std = df[col].rolling(window, center=True, min_periods=1).std().replace(0, 1e-8)
                mask = (df[col] - mean).abs() > threshold * std
            else:
                mask = pd.Series(False, index=df.index)
            df_out[f"{col}_outlier"] = mask
            cnt = int(mask.sum())
            if cnt:
                self._outliers_report.append({"column": col, "count": cnt, "method": method})
                self._logger.debug(f"[{self.mode}] Outliers em {col}: {cnt}")
        return df_out

    def fix_outliers(
        self,
        df: pd.DataFrame,
        method: Optional[str] = None,
        correction: Optional[str] = None,
        threshold: Optional[float] = None,
        window: Optional[int] = None,
    ) -> pd.DataFrame:
        method = method or self.outlier_params.get("method", "iqr")
        correction = correction or self.outlier_params.get("correction", "interpolate")
        if threshold is None:
            threshold = 3.0 if method in ("zscore", "rolling") else None
        if method == "rolling" and window is None:
            window = 20
        if method not in self.SUPPORTED_OUTLIER_METHODS:
            raise ValueError(
                f"Outlier method '{method}' não suportado. Escolha um dos: {self.SUPPORTED_OUTLIER_METHODS}"
            )
        if correction not in self.SUPPORTED_OUTLIER_CORRECTIONS:
            raise ValueError(
                f"Correção '{correction}' não suportada. Escolha um dos: {self.SUPPORTED_OUTLIER_CORRECTIONS}"
            )

        df = df.copy()
        flags = self.detect_outliers(df, method=method, threshold=threshold, window=window)
        for col in df.select_dtypes(include=[np.number]).columns:
            m = flags.get(f"{col}_outlier", pd.Series(False, index=df.index))
            if not m.any():
                continue
            if correction == "nan":
                df.loc[m, col] = np.nan
            elif correction == "mean":
                df.loc[m, col] = df.loc[~m, col].mean()
            elif correction == "interpolate":
                df.loc[m, col] = np.nan
                df[col] = df[col].interpolate(method="linear")
            elif correction == "zero":
                df.loc[m, col] = 0
            df[f"{col}_fixed"] = m
        fixed_cols = [c for c in df.columns if c.endswith("_fixed")]
        if fixed_cols:
            df["outlier_fixed"] = df[fixed_cols].any(axis=1)
        self._logger.info(f"[{self.mode}] Outliers corrigidos ({method}/{correction}).")
        return df

    # ----------------- Relatórios -----------------
    def get_gaps_report(self) -> List[pd.Timestamp]:
        return self._gaps_report

    def get_outliers_report(self) -> List[Dict[str, Any]]:
        return self._outliers_report

# EOF
