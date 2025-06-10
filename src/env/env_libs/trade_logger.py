"""
src/env/env_libs/trade_logger.py
TradeLogger: Logging estruturado e auditável de operações, rewards e contexto em ambientes RL.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
from datetime import datetime
from pathlib import Path
import json
import csv

from src.utils.logging_utils import get_logger
from src.utils.file_saver import build_filename, save_dataframe

class TradeLogger:
    """
    Logging estruturado/auditável para trades, rewards e contexto no pipeline RL do Op_Trader.

    Métodos principais:
      - log_trade: Registra operação de trade (abertura, fechamento, modificação)
      - log_reward: Registra recompensas e breakdowns
      - log_context: Registra decisões/contexto macro/micro
      - save_logs: Persiste logs segregados em CSV/JSON no padrão Op_Trader
      - get_logs: Retorna logs acumulados (dict)
      - reset: Limpa histórico interno

    Args:
        symbol (str): Ativo alvo dos logs.
        log_dir (str, opcional): Diretório para salvar logs.
        logger (Logger, opcional): Logger estruturado.
        debug (bool): Ativa logs detalhados.
    """

    def __init__(self, symbol: str, log_dir: str = None, logger=None, debug: bool = False, **kwargs):
        if not symbol:
            raise ValueError("symbol é obrigatório para TradeLogger")
        self.symbol = symbol
        self.log_dir = Path(log_dir) if log_dir else Path("logs/trades")
        self.logger = logger or get_logger("TradeLogger", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.Lock()
        self._logs = {
            "trade": [],
            "reward": [],
            "context": []
        }
        self.logger.info(f"TradeLogger inicializado para {symbol}, dir={self.log_dir}")

    def log_trade(self, trade_event: dict):
        """
        Registra operação de trade.

        Args:
            trade_event (dict): Evento de trade, com schema padrão do Op_Trader.

        Returns:
            None
        """
        with self._lock:
            event = trade_event.copy()
            event.setdefault("timestamp", datetime.utcnow().isoformat())
            event.setdefault("symbol", self.symbol)
            if not event.get("action") or not event.get("status"):
                self.logger.warning(f"TradeEvent malformado: {event}")
            self._logs["trade"].append(event)
            self.logger.info(f"[TRADE_LOG] {event}")

    def log_reward(self, reward_event: dict):
        """
        Registra evento de reward.

        Args:
            reward_event (dict): Evento de reward, com breakdown e contexto.

        Returns:
            None
        """
        with self._lock:
            event = reward_event.copy()
            event.setdefault("timestamp", datetime.utcnow().isoformat())
            event.setdefault("symbol", self.symbol)
            self._logs["reward"].append(event)
            self.logger.debug(f"[REWARD_LOG] {event}")

    def log_context(self, context_event: dict):
        """
        Registra evento de contexto/decisão.

        Args:
            context_event (dict): Evento de contexto macro/micro.

        Returns:
            None
        """
        with self._lock:
            event = context_event.copy()
            event.setdefault("timestamp", datetime.utcnow().isoformat())
            event.setdefault("symbol", self.symbol)
            self._logs["context"].append(event)
            self.logger.debug(f"[CONTEXT_LOG] {event}")

    def save_logs(self, path: str = None):
        """
        Persiste logs segregados em arquivos CSV/JSON padronizados.

        Args:
            path (str, opcional): Caminho base para salvar os logs.

        Returns:
            None
        """
        with self._lock:
            save_dir = Path(path) if path else self.log_dir
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            for log_type in self._logs:
                data = self._logs[log_type]
                if not data:
                    continue
                filename = build_filename(
                    prefix=str(save_dir),
                    suffix=log_type,
                    asset=self.symbol,
                    timeframe="none",  # corrigido!
                    period=timestamp,
                    timestamp=timestamp,
                    extension="csv"
                )
                # Salvar como CSV (linha por evento)
                try:
                    keys = sorted(set().union(*(d.keys() for d in data)))
                    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=keys)
                        writer.writeheader()
                        for row in data:
                            writer.writerow(row)
                    self.logger.info(f"Log salvo: {filename}")
                except Exception as e:
                    self.logger.error(f"Falha ao salvar {log_type}: {e}")

                # Opcional: também salva JSON para auditoria bruta
                try:
                    filename_json = filename.replace(".csv", ".json")
                    with open(filename_json, "w", encoding="utf-8") as jf:
                        json.dump(data, jf, indent=2)
                except Exception as e:
                    self.logger.error(f"Falha ao salvar JSON {log_type}: {e}")

    def get_logs(self) -> dict:
        """
        Retorna os logs acumulados.

        Returns:
            dict: Logs de trade, reward e contexto.
        """
        with self._lock:
            return {k: v.copy() for k, v in self._logs.items()}

    def reset(self):
        """
        Limpa o histórico interno de logs.

        Returns:
            None
        """
        with self._lock:
            for k in self._logs:
                self._logs[k].clear()
            self.logger.info("TradeLogger resetado.")
