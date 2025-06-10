#!/usr/bin/env python3
"""
src/env/env_factory.py
Fábrica central de ambientes RL plugáveis do Op_Trader, com registro dinâmico de ambientes, wrappers, injeção de dependências e logging.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import threading
import importlib
from src.utils.logging_utils import get_logger
import yaml
import json
import os

class EnvFactory:
    """
    Fábrica central de ambientes RL do Op_Trader.
    Permite registro e criação plugável de ambientes e wrappers, injeção de componentes e configuração dinâmica.

    Args:
        registry (Registry, opcional): Instância do Registry global do pipeline (obrigatória no Op_Trader).
        config_path (str, opcional): Caminho do arquivo de configuração global (YAML/JSON).
        logger (Logger, opcional): Logger estruturado do projeto.
        debug (bool): Ativa logs detalhados.
        kwargs: Opções adicionais.
    """
    def __init__(self, registry=None, config_path: str = None, logger=None, debug: bool = False, **kwargs):
        self.registry = registry  # <- ESSENCIAL: precisa existir!
        self._env_registry = {}
        self._wrapper_registry = {}
        self.config_path = config_path
        self.logger = logger or get_logger("EnvFactory", cli_level="DEBUG" if debug else "INFO")
        self.debug = debug
        self._lock = threading.RLock()
        self._config = {}
        if config_path:
            self._load_config(config_path)
        self.logger.info(f"EnvFactory inicializado. Config: {self._config}")

    def _load_config(self, config_path):
        """Carrega configuração global (YAML/JSON)."""
        try:
            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f)
            elif config_path.endswith(".json"):
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                raise ValueError("Formato de configuração não suportado")
        except Exception as e:
            self.logger.warning(f"Falha ao carregar config {config_path}: {e}")
            self._config = {}

    def create_env(
        self,
        env_type: str,
        wrappers: list = None,
        config_overrides: dict = None,
        **kwargs
    ):
        """
        Cria e retorna uma instância de ambiente RL, aplicando wrappers na ordem especificada.
        Busca o ambiente no registry usando o nome exato (sem transformação).

        Args:
            env_type (str): Nome do ambiente registrado no Registry (exatamente igual à chave registrada).
            wrappers (list): Lista de dicionários {"name": str, "params": dict} de wrappers a aplicar.
            config_overrides (dict): Parâmetros extras de configuração para o ambiente.
            **kwargs: Argumentos extras.

        Returns:
            env (gym.Env): Instância do ambiente encadeado com wrappers.

        Raises:
            ValueError: Se o ambiente não estiver registrado.
        """
        self.logger.info(f"EnvFactory.create_env chamado para '{env_type}'")
        if not hasattr(self, "registry") or self.registry is None:
            raise ValueError("Registry não definido na EnvFactory.")

        # Busca o ambiente no registry usando o nome exato
        env_cls = self.registry.get(env_type)
        if env_cls is None:
            self.logger.critical(f"Ambiente '{env_type}' não registrado.")
            raise ValueError(f"Ambiente '{env_type}' não registrado.")

        # Aplica overrides/config extras ao instanciar o ambiente
        env_args = config_overrides.copy() if config_overrides else {}
        env_args.update(kwargs)
        env = env_cls(**env_args)

        # Aplica wrappers na ordem definida
        if wrappers:
            for wrapper in wrappers:
                name = wrapper.get("name")
                params = wrapper.get("params", {})
                wrapper_cls = self.registry.get(name)
                if wrapper_cls is None:
                    raise ValueError(f"Wrapper '{name}' não registrado.")
                env = wrapper_cls(env, **params)
                self.logger.info(f"Wrapper '{name}' aplicado.")

        return env

    # --- Métodos de registro e utilitários (podem ser mantidos/expandido conforme padrão):
    def register_env(self, env_type: str, env_class):
        """
        Registra um novo ambiente no registry interno.

        Args:
            env_type (str): Nome/alias do ambiente.
            env_class (type): Classe do ambiente (herda BaseEnv).
        """
        with self._lock:
            if env_type in self._env_registry:
                self.logger.warning(f"Ambiente '{env_type}' já registrado — sobrescrevendo.")
            self._env_registry[env_type] = env_class
            self.logger.info(f"Ambiente '{env_type}' registrado: {env_class}")

    def register_wrapper(self, wrapper_name: str, wrapper_class):
        """
        Registra um novo wrapper no registry interno.

        Args:
            wrapper_name (str): Nome/alias do wrapper.
            wrapper_class (type): Classe do wrapper.
        """
        with self._lock:
            if wrapper_name in self._wrapper_registry:
                self.logger.warning(f"Wrapper '{wrapper_name}' já registrado — sobrescrevendo.")
            self._wrapper_registry[wrapper_name] = wrapper_class
            self.logger.info(f"Wrapper '{wrapper_name}' registrado: {wrapper_class}")

    def list_envs(self) -> list:
        """Retorna nomes dos ambientes registrados internamente."""
        with self._lock:
            return list(self._env_registry.keys())

    def list_wrappers(self) -> list:
        """Retorna nomes dos wrappers registrados internamente."""
        with self._lock:
            return list(self._wrapper_registry.keys())

    def reset_registry(self):
        """Reseta todos os registros (para testes/hot-reload)."""
        with self._lock:
            self._env_registry = {}
            self._wrapper_registry = {}
            self.logger.info("Registry de ambientes/wrappers resetado.")

    def _resolve_wrapper(self, wrapper):
        """Resolve wrapper por nome, classe ou função."""
        if isinstance(wrapper, str):
            if wrapper not in self._wrapper_registry:
                self.logger.critical(f"Wrapper '{wrapper}' não registrado.")
                raise ValueError(f"Wrapper '{wrapper}' não registrado.")
            return self._wrapper_registry[wrapper]
        elif callable(wrapper):
            return wrapper
        else:
            raise ValueError("Wrapper inválido (não é string nem função/classe)")
