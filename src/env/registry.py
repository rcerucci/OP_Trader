"""
src/env/registry.py
Registry profissional centralizado e auditável para ambientes, wrappers e componentes do Op_Trader.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
from typing import Any, Optional, Dict, List
import logging
from src.utils.logging_utils import get_logger

class Registry:
    """
    Registro dinâmico e thread-safe de ambientes, wrappers e componentes RL do Op_Trader.

    Permite lookup, registro e gerenciamento por nome, com logging rastreável.

    Args:
        logger (Logger, opcional): Logger estruturado do projeto.
        debug (bool): Ativa logs detalhados.

    Example:
        >>> reg = Registry()
        >>> reg.register("train_env_long", TrainEnvLong)
        >>> env_cls = reg.get("train_env_long")
        >>> reg.unregister("train_env_long")
        >>> reg.reset()
    """
    def __init__(self, logger: Optional[Any] = None, debug: bool = False):
        self._registry: Dict[str, Any] = {}
        self._lock = threading.RLock()
        if logger is None:
            self.logger = get_logger("Registry")
        else:
            self.logger = logger
        self.debug = debug

    def register(self, name: str, obj: Any):
        with self._lock:
            if not isinstance(name, str) or not name.strip():
                self.logger.error(f"Nome inválido: '{name}'")
                raise ValueError(f"Nome inválido: '{name}'")
            if obj is None:
                self.logger.error(f"Tentativa de registrar objeto None para '{name}'")
                raise ValueError("Objeto None não pode ser registrado")
            if name in self._registry:
                self.logger.warning(f"'{name}' já registrado, sobrescrevendo objeto anterior.")
            self._registry[name] = obj
            self.logger.info(f"Registrado: '{name}' -> {obj}")

    def get(self, name: str):
        with self._lock:
            obj = self._registry.get(name)
            if obj is None:
                self.logger.warning(f"Lookup falhou: '{name}' não registrado.")
            else:
                self.logger.debug(f"Lookup: '{name}' -> {obj}")
            return obj

    def unregister(self, name: str):
        with self._lock:
            if name not in self._registry:
                self.logger.warning(f"Tentativa de remover '{name}' que não está registrado.")
                return
            obj = self._registry[name]
            if name.lower() in ("env_factory", "core", "main"):
                self.logger.critical(f"Remoção de objeto crítico: '{name}'")
            del self._registry[name]
            self.logger.info(f"Removido do registro: '{name}' -> {obj}")

    def list(self, type_filter: str = None) -> List[str]:
        with self._lock:
            if not type_filter:
                return list(self._registry.keys())
            filter_lower = type_filter.lower()
            result = []
            for name, obj in self._registry.items():
                type_name = type(obj).__name__ if not isinstance(obj, type) else obj.__name__
                if filter_lower in type_name.lower():
                    result.append(name)
            return result

    def reset(self):
        with self._lock:
            self.logger.info("Resetando registro (todos os objetos removidos).")
            self._registry.clear()
