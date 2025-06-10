# src/env/wrappers/action_wrapper.py
"""
src/env/wrappers/action_wrapper.py
Wrapper profissional de ações RL para o Op_Trader. 
Transforma, valida, corrige dtype/shape, loga e rastreia todas as ações enviadas ao ambiente Gymnasium.
Autor: Equipe Op_Trader
Data: 2025-06-08
"""

import gymnasium as gym
import numpy as np
import threading
from typing import Callable, Any, Optional, Union
from src.utils.logging_utils import get_logger
from src.utils.file_saver import save_dataframe, build_filename, get_timestamp

class ActionWrapper(gym.Wrapper):
    """
    Wrapper plugável para ações RL, 100% aderente ao padrão Op_Trader.
    Corrige dtype/shape, aplica função customizada, valida range, gera logs e auditoria de todas as ações.

    Args:
        env (gym.Env): Ambiente RL encapsulado.
        action_fn (Callable, opcional): Função customizada para transformação/validação da ação.
        logger (logging.Logger, opcional): Logger estruturado do projeto.
        log_dir (str, opcional): Diretório para salvar logs CSV de ações.
        cli_level (str|int, opcional): Nível do logger (ex: "DEBUG", "INFO").
        **kwargs: Parâmetros extras.
    """

    def __init__(
        self,
        env: gym.Env,
        action_fn: Optional[Callable] = None,
        logger: Optional[Any] = None,
        log_dir: Optional[str] = None,
        cli_level: Optional[Union[str, int]] = "INFO",
        **kwargs
    ):
        super().__init__(env)
        self.action_fn = action_fn
        self.log_dir = log_dir
        self._action_logs = []
        self._lock = threading.RLock()
        self.logger = logger or get_logger("ActionWrapper", cli_level=cli_level)

    def step(self, action: Any):
        """
        Processa a ação recebida, aplica transformação customizada, corrige dtype/shape,
        valida o range via action_space.contains e loga o ciclo completo.

        Args:
            action (Any): Ação bruta do agente RL.

        Returns:
            Tuple: (obs, reward, terminated, truncated, info)

        Raises:
            ValueError: Se ação estiver fora do espaço permitido após transformação/correção.
        """
        with self._lock:
            orig_action = np.array(action)
            transformed_action = orig_action

            # Aplica função customizada, se fornecida
            try:
                if self.action_fn is not None:
                    transformed_action = self.action_fn(orig_action)
                    self.logger.debug(f"Ação transformada: {orig_action} -> {transformed_action}")
            except Exception as e:
                self.logger.warning(f"Falha em action_fn: {e}. Usando ação original.")
                transformed_action = orig_action

            # Corrige NaN (auto-fix)
            if isinstance(transformed_action, np.ndarray) and np.any(np.isnan(transformed_action)):
                self.logger.warning("Ação NaN detectada. Corrigindo para zero.")
                transformed_action = np.nan_to_num(transformed_action)

            # Garante dtype/shape corretos (Gymnasium <0.29 é sensível a isso)
            space = self.env.action_space
            try:
                if hasattr(space, "dtype"):
                    transformed_action = np.asarray(transformed_action, dtype=space.dtype)
                if hasattr(space, "shape"):
                    if transformed_action.shape != space.shape:
                        transformed_action = np.reshape(transformed_action, space.shape)
                        self.logger.debug(f"Ação reshapeada para {space.shape}: {transformed_action}")
            except Exception as e:
                self.logger.error(f"Erro ao corrigir dtype/shape da ação: {e}")
                raise ValueError(f"Ação inválida para o espaço: {transformed_action}")

            # Validação final: lança erro se fora do espaço
            if hasattr(space, "contains"):
                if not space.contains(transformed_action):
                    msg = (f"Ação fora do espaço permitido: {transformed_action} "
                           f"(dtype={transformed_action.dtype}, esperado={space.dtype}, "
                           f"shape={transformed_action.shape}, esperado={space.shape})")
                    self.logger.error(msg)
                    raise ValueError(msg)

            # Rastreia ação para auditoria
            self._action_logs.append({
                "timestamp": get_timestamp(),
                "original_action": orig_action.tolist() if hasattr(orig_action, 'tolist') else orig_action,
                "transformed_action": transformed_action.tolist() if hasattr(transformed_action, 'tolist') else transformed_action
            })
            self.logger.info(f"Ação enviada ao ambiente: {transformed_action}")

            # Passa ao ambiente
            return self.env.step(transformed_action)

    def set_action_fn(self, action_fn: Callable):
        """
        Atualiza dinamicamente a função customizada de transformação/validação.

        Args:
            action_fn (Callable): Nova função para processar ações.
        """
        with self._lock:
            self.logger.info("Função action_fn atualizada dinamicamente.")
            self.action_fn = action_fn

    def save_logs(self, path: Optional[str] = None):
        """
        Salva histórico de ações transformadas para auditoria.

        Args:
            path (str, opcional): Caminho do arquivo. Usa log_dir padrão se omitido.
        """
        with self._lock:
            if not self._action_logs:
                self.logger.warning("Nenhum log de ação a salvar.")
                return
            import pandas as pd
            df = pd.DataFrame(self._action_logs)
            out_path = path or (self.log_dir and build_filename(
                prefix=self.log_dir,
                suffix="action_logs",
                asset="env",
                timeframe="NA",
                timestamp=get_timestamp(),
                extension="csv"
            )) or "action_logs.csv"
            save_dataframe(df, out_path)
            self.logger.info(f"Logs de ação salvos em: {out_path}")

    def get_logs(self) -> list:
        """
        Retorna os logs acumulados de ações transformadas.

        Returns:
            list[dict]: Lista de dicionários com timestamp, ação original e transformada.
        """
        with self._lock:
            return list(self._action_logs)

    def reset(self, **kwargs):
        """
        Reinicia o ambiente e limpa logs internos.

        Returns:
            tuple: (obs, info)
        """
        with self._lock:
            self._action_logs.clear()
            self.logger.debug("Logs de ação limpos no reset.")
            return self.env.reset(**kwargs)

    def close(self):
        """
        Finaliza o wrapper, salva logs e libera recursos.
        """
        with self._lock:
            if self._action_logs:
                self.save_logs()
            self.logger.info("ActionWrapper fechado.")
            super().close()
