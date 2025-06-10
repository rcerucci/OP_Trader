"""
src/env/env_libs/position_manager.py
PositionManager: gestão de posições para ambientes RL Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
from datetime import datetime

from src.utils.logging_utils import get_logger
from src.utils.file_saver import build_filename, save_dataframe

class PositionManager:
    """
    Gerencia posição aberta, execução, fechamento e snapshot, com controle thread-safe.

    Args:
        symbol (str): Ativo negociado.
        risk_manager (obj, opcional): Validação de risco.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """

    def __init__(self, symbol: str, risk_manager=None, logger=None, debug: bool = False, **kwargs):
        if not symbol:
            raise ValueError("symbol obrigatório para PositionManager")
        self.symbol = symbol
        self.risk_manager = risk_manager
        self.logger = logger or get_logger("PositionManager", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.RLock()
        self.position = None  # None ou dict com detalhes da posição
        self.history = []
        self.logger.info(f"PositionManager inicializado para {symbol}")

    def open_position(self, action: str, price: float, size: float, context: dict = None) -> dict:
        """
        Abre nova posição, valida parâmetros e consulta RiskManager.

        Args:
            action (str): Tipo de ação ("buy", "sell").
            price (float): Preço de abertura.
            size (float): Quantidade.
            context (dict, opcional): Contexto adicional.

        Returns:
            dict: Estado da posição aberta.
        """
        with self._lock:
            if self.position is not None:
                self.logger.critical("Tentativa de abrir posição com posição já aberta!")
                return {"status": "rejected", "reason": "Já existe posição aberta", "position": self.position}
            if not action or not isinstance(price, (float, int)) or price <= 0 or not isinstance(size, (float, int)) or size <= 0:
                self.logger.error(f"Parâmetros inválidos para abertura: {action}, {price}, {size}")
                raise ValueError("Parâmetros inválidos para abrir posição.")
            # Validação de risco
            if self.risk_manager:
                risk_result = self.risk_manager.validate_order(self.symbol, action, size, price, context)
                if risk_result.get("status") != "approved":
                    self.logger.warning(f"Risco rejeitou abertura: {risk_result}")
                    return {"status": "rejected", "reason": risk_result.get("reason"), "position": None}
            self.position = {
                "symbol": self.symbol,
                "action": action,
                "open_price": float(price),
                "size": float(size),
                "open_time": datetime.utcnow().isoformat(),
                "context": context or {},
                "status": "open"
            }
            self.history.append({"event": "open", **self.position})
            self.logger.info(f"Posição aberta: {self.position}")
            return {"status": "opened", "position": self.position.copy()}

    def close_position(self, price: float, context: dict = None) -> dict:
        """
        Fecha posição ativa, computa PnL, registra evento e zera posição.

        Args:
            price (float): Preço de fechamento.
            context (dict, opcional): Contexto adicional.

        Returns:
            dict: Detalhes do fechamento (inclui PnL).
        """
        with self._lock:
            if self.position is None:
                self.logger.warning("Tentativa de fechar posição sem posição aberta.")
                return {"status": "no_position", "reason": "Nenhuma posição aberta."}
            if not isinstance(price, (float, int)) or price <= 0:
                self.logger.error(f"Preço inválido para fechamento: {price}")
                raise ValueError("Preço inválido para fechar posição.")
            pnl = (float(price) - self.position["open_price"]) * self.position["size"]
            result = {
                "symbol": self.symbol,
                "action": self.position["action"],
                "open_price": self.position["open_price"],
                "close_price": float(price),
                "size": self.position["size"],
                "open_time": self.position["open_time"],
                "close_time": datetime.utcnow().isoformat(),
                "pnl": pnl,
                "context": context or {},
                "status": "closed"
            }
            # Validação de risco (se necessário)
            if self.risk_manager:
                self.risk_manager.update_risk_metrics({"pnl": pnl, "drawdown": context.get("drawdown", 0.0) if context else 0.0})
            self.history.append({"event": "close", **result})
            self.logger.info(f"Posição fechada: {result}")
            self.position = None
            return {"status": "closed", "result": result}

    def get_current_position(self) -> dict:
        """
        Retorna snapshot da posição ativa (ou None).

        Returns:
            dict ou None: Estado atual da posição.
        """
        with self._lock:
            return self.position.copy() if self.position else None

    def manage_position(self, action: str, price: float, size: float, context: dict = None) -> dict:
        """
        Gerencia ciclo de posição (open, close, increase, reduce).

        Args:
            action (str): "open", "close", "increase", "reduce".
            price (float): Preço de execução.
            size (float): Quantidade.
            context (dict, opcional): Contexto.

        Returns:
            dict: Resultado da operação.
        """
        if action == "open":
            return self.open_position(action=context.get("action", "buy") if context else "buy", price=price, size=size, context=context)
        elif action == "close":
            return self.close_position(price, context=context)
        # Extensível para "increase", "reduce" etc.
        else:
            self.logger.error(f"Ação não suportada: {action}")
            return {"status": "rejected", "reason": "Ação não suportada."}

    def reset(self):
        """
        Limpa posição ativa e histórico.

        Returns:
            None
        """
        with self._lock:
            self.position = None
            self.history.clear()
            self.logger.info("PositionManager resetado.")

    def save_snapshot(self, path: str = None):
        """
        Salva histórico de eventos e posição para auditoria (CSV).

        Args:
            path (str, opcional): Caminho para salvar.

        Returns:
            None
        """
        with self._lock:
            import pandas as pd
            df = pd.DataFrame(self.history)
            filename = build_filename(
                prefix=path or "logs/audits/",
                suffix="position_snapshot",
                asset=self.symbol,
                timeframe="none"
            )
            save_dataframe(df, filename)
            self.logger.info(f"Snapshot de posição salvo: {filename}")
