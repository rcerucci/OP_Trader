"""
src/env/env_libs/validators.py
Utilitário central para validação de entradas, permissões, contexto e schema do pipeline Op_Trader.
Responsável: Equipe Op_Trader
Data: 2025-06-08
"""

from threading import Lock
import math
import numbers
from src.utils.logging_utils import get_logger

class Validators:
    """
    Classe utilitária para validações robustas e auditáveis em todos os fluxos do pipeline Op_Trader.

    Métodos principais:
        - validate_action: Verifica ação permitida.
        - validate_price: Valida preços (>0, finito).
        - validate_size: Valida tamanho de posição.
        - validate_context: Checa integridade de contexto macro/micro.
        - validate_schema: Valida presença de campos/tipos.
        - validate_permissions: Confere permissões de usuário.
        - log_validation: Loga e audita todas validações.

    Args:
        logger (logging.Logger, opcional): Logger estruturado.
        debug (bool, opcional): Ativa logs detalhados.
    """

    def __init__(self, logger=None, debug: bool = False, **kwargs):
        self.logger = logger or get_logger("Validators", debug=debug)
        self.debug = debug
        self._lock = Lock()

    @staticmethod
    def validate_action(action: str, allowed: list) -> bool:
        """
        Verifica se uma ação está no conjunto permitido (case-insensitive).

        Args:
            action (str): Ação a ser validada ("buy", "sell", etc.).
            allowed (list): Lista de ações permitidas.

        Returns:
            bool: True se permitido, False caso contrário.
        """
        if not isinstance(action, str):
            return False
        allowed_lower = [str(a).lower() for a in allowed]
        return action.lower() in allowed_lower

    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Valida se preço é um número positivo, finito e não nulo.

        Args:
            price (float): Preço a ser validado.

        Returns:
            bool: True se válido, False caso contrário.
        """
        if not isinstance(price, numbers.Number):
            return False
        if price is None or math.isnan(price) or math.isinf(price) or price <= 0:
            return False
        return True

    @staticmethod
    def validate_size(size: float, min_size: float = 1e-5) -> bool:
        """
        Valida se o tamanho da posição é positivo, finito e acima do mínimo.

        Args:
            size (float): Tamanho a ser validado.
            min_size (float, opcional): Tamanho mínimo permitido. Defaults a 1e-5.

        Returns:
            bool: True se válido, False caso contrário.
        """
        if not isinstance(size, numbers.Number):
            return False
        if size is None or math.isnan(size) or math.isinf(size) or size < min_size:
            return False
        return True

    @staticmethod
    def validate_context(context: dict, required_keys: list = None) -> bool:
        """
        Checa se todas as chaves obrigatórias estão presentes no contexto.

        Args:
            context (dict): Dicionário de contexto macro/micro.
            required_keys (list, opcional): Lista de chaves obrigatórias.

        Returns:
            bool: True se contexto válido, False caso contrário.
        """
        if not isinstance(context, dict):
            return False
        if required_keys:
            for k in required_keys:
                if k not in context:
                    return False
        return True

    @staticmethod
    def validate_schema(data: dict, schema: list) -> bool:
        """
        Valida se os campos obrigatórios do schema estão presentes nos dados.

        Args:
            data (dict): Dados a serem validados.
            schema (list): Campos obrigatórios.

        Returns:
            bool: True se schema válido, False caso contrário.

        Raises:
            ValueError: Se schema inconsistente.
        """
        if not isinstance(data, dict) or not isinstance(schema, list):
            raise ValueError("Data ou schema inválidos para validação.")
        for field in schema:
            if field not in data:
                raise ValueError(f"Campo '{field}' ausente no dado para validação.")
        return True

    @staticmethod
    def validate_permissions(user: str, required_role: str, context: dict = None) -> bool:
        """
        Checa permissões do usuário de acordo com contexto.

        Args:
            user (str): Nome do usuário.
            required_role (str): Papel requerido.
            context (dict, opcional): Contexto com permissões atuais.

        Returns:
            bool: True se permitido, False caso contrário.
        """
        if not user or not required_role:
            return False
        if context and "role" in context:
            return context["role"] == required_role
        # Fallback permissivo (pode ser customizado)
        return True

    def log_validation(self, item: str, valid: bool, details: str = ""):
        """
        Loga e audita o resultado da validação, thread safe.

        Args:
            item (str): Item ou campo validado.
            valid (bool): Resultado da validação.
            details (str, opcional): Mensagem adicional.

        Returns:
            None
        """
        with self._lock:
            status = "VALID" if valid else "INVALID"
            msg = f"[VALIDATION] {item} -> {status}. {details}"
            if valid:
                self.logger.info(msg)
            else:
                self.logger.warning(msg)
