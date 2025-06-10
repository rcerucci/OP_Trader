"""
src/env/env_libs/risk_manager.py
RiskManager: central de gestão de risco para o pipeline RL Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import yaml
import json
from datetime import datetime
from pathlib import Path

from src.utils.logging_utils import get_logger
from src.utils.file_saver import build_filename, save_dataframe

class RiskManager:
    """
    Gerencia limites de risco, sizing, SL/TP, drawdown e bloqueios em ambientes RL.

    Args:
        config_path (str, opcional): Caminho do arquivo de configuração.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logging detalhado.
    """

    def __init__(self, config_path: str = None, logger=None, debug: bool = False, **kwargs):
        self.logger = logger or get_logger("RiskManager", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.RLock()
        self.config = self._load_config(config_path)
        self.metrics = {
            "drawdown": 0.0,
            "max_drawdown": 0.0,
            "cum_pnl": 0.0,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "exposure": 0.0
        }
        self.limits = self.config.get("limits", {
            "max_risk": 0.02,  # risco máximo por operação (% do portfólio)
            "max_drawdown": 0.3,
            "max_exposure": 5.0  # múltiplo do portfólio
        })
        self.logger.info(f"RiskManager inicializado com limites: {self.limits}")

    def _load_config(self, config_path: str):
        # Carrega config YAML/JSON, fallback para defaults
        if not config_path:
            self.logger.warning("Config de risco não especificada, usando defaults.")
            return {}
        try:
            with open(config_path, "r") as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Falha ao carregar config {config_path}: {e}")
            return {}

    def validate_order(self, symbol: str, action: str, size: float, price: float, context: dict = None) -> dict:
        """
        Valida ordem conforme limites de risco, SL/TP, sizing, drawdown e contexto.

        Args:
            symbol (str): Ativo.
            action (str): "buy", "sell", etc.
            size (float): Quantidade.
            price (float): Preço.
            context (dict, opcional): Regime, perfil, etc.

        Returns:
            dict: Resultado da validação com status, motivo e ajuste.
        """
        with self._lock:
            result = {"status": "approved", "reason": "", "adjustment": None}
            # Limite de tamanho/exposição
            max_size = self.limits.get("max_exposure", 5.0)
            if size > max_size:
                result["status"] = "rejected"
                result["reason"] = f"Exposição acima do limite ({size} > {max_size})"
                self.logger.warning(result["reason"])
                return result
            # Limite de risco
            max_risk = self.limits.get("max_risk", 0.02)
            portfolio_value = (context or {}).get("portfolio_value", 10000)
            risk = abs(size * price) / max(portfolio_value, 1)
            if risk > max_risk:
                result["status"] = "rejected"
                result["reason"] = f"Risco acima do máximo permitido ({risk:.3f} > {max_risk})"
                self.logger.warning(result["reason"])
                return result
            # Drawdown
            max_dd = self.limits.get("max_drawdown", 0.3)
            drawdown = (context or {}).get("drawdown", 0.0)
            if drawdown > max_dd:
                result["status"] = "rejected"
                result["reason"] = f"Drawdown acima do limite ({drawdown:.3f} > {max_dd})"
                self.logger.warning(result["reason"])
                return result
            # SL/TP (exemplo, pode ser expandido)
            sl = (context or {}).get("stop_loss", None)
            tp = (context or {}).get("take_profit", None)
            if sl is not None and sl <= 0:
                result["status"] = "rejected"
                result["reason"] = f"Stop Loss inválido: {sl}"
                self.logger.error(result["reason"])
                return result
            if tp is not None and tp <= 0:
                result["status"] = "rejected"
                result["reason"] = f"Take Profit inválido: {tp}"
                self.logger.error(result["reason"])
                return result
            self.logger.info(f"Ordem validada: {symbol}, {action}, {size}@{price}")
            return result

    def check_risk_limits(self, position: dict, context: dict = None) -> dict:
        """
        Checa se a posição ativa está dentro dos limites de risco.

        Args:
            position (dict): Info da posição.
            context (dict, opcional): Contexto extra.

        Returns:
            dict: Status dos limites e alertas.
        """
        with self._lock:
            alerts = {}
            max_dd = self.limits.get("max_drawdown", 0.3)
            dd = position.get("drawdown", 0.0)
            if dd > max_dd:
                alerts["drawdown"] = f"Drawdown excedido: {dd:.3f} > {max_dd}"
            max_exp = self.limits.get("max_exposure", 5.0)
            exp = position.get("exposure", 0.0)
            if exp > max_exp:
                alerts["exposure"] = f"Exposição excedida: {exp:.2f} > {max_exp}"
            if not alerts:
                self.logger.info("Posição dentro dos limites de risco.")
            else:
                for a in alerts.values():
                    self.logger.warning(a)
            return alerts

    def calculate_position_size(self, symbol: str, risk_level: float, portfolio_value: float, context: dict = None) -> float:
        """
        Calcula tamanho de posição ideal dado o nível de risco e o portfólio.

        Args:
            symbol (str): Ativo.
            risk_level (float): Percentual de risco permitido (ex: 0.01).
            portfolio_value (float): Valor total do portfólio.
            context (dict, opcional): Pode conter volatilidade, SL/TP sugeridos, etc.

        Returns:
            float: Tamanho sugerido.
        """
        with self._lock:
            sl = (context or {}).get("stop_loss", 100)
            if sl <= 0:
                self.logger.warning("SL inválido, usando SL=100 (padrão).")
                sl = 100
            # Sizing básico: risco monetário / SL
            risk_cap = risk_level * portfolio_value
            size = risk_cap / max(abs(sl), 1)
            if size <= 0:
                self.logger.warning("Tamanho de posição impossível, ajustando para mínimo 0.01.")
                size = 0.01
            self.logger.info(f"Sizing: {size:.4f} ({symbol}, risco={risk_level}, SL={sl})")
            return size

    def update_risk_metrics(self, trade_result: dict):
        """
        Atualiza métricas de risco com o resultado do trade.

        Args:
            trade_result (dict): Deve conter pnl, drawdown, resultado.

        Returns:
            None
        """
        with self._lock:
            pnl = trade_result.get("pnl", 0.0)
            dd = trade_result.get("drawdown", 0.0)
            self.metrics["cum_pnl"] += pnl
            self.metrics["drawdown"] = dd
            self.metrics["max_drawdown"] = max(self.metrics["max_drawdown"], dd)
            self.metrics["trades"] += 1
            if pnl > 0:
                self.metrics["wins"] += 1
            elif pnl < 0:
                self.metrics["losses"] += 1
            self.logger.info(f"Risk metrics atualizadas: {self.metrics}")

    def get_current_limits(self) -> dict:
        """
        Retorna limites e métricas atuais.

        Returns:
            dict: Limites e métricas.
        """
        with self._lock:
            return {
                "limits": self.limits.copy(),
                "metrics": self.metrics.copy()
            }

    def reset(self):
        """
        Limpa métricas acumuladas.

        Returns:
            None
        """
        with self._lock:
            for k in self.metrics:
                if isinstance(self.metrics[k], float):
                    self.metrics[k] = 0.0
                elif isinstance(self.metrics[k], int):
                    self.metrics[k] = 0
            self.logger.info("Métricas de risco resetadas.")

    def save_snapshot(self, path: str = None):
        with self._lock:
            import pandas as pd
            snap = self.get_current_limits()
            df = pd.DataFrame([{**snap["limits"], **snap["metrics"], "timestamp": datetime.now()}])
            filename = build_filename(
                prefix=path or "logs/audits/",
                suffix="risk_snapshot",
                asset="none",
                timeframe="none"
            )
            save_dataframe(df, filename)
            self.logger.info(f"Risk snapshot salvo: {filename}")
