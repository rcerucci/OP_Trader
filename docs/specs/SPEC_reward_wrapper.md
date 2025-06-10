# SPEC\_reward\_wrapper.md — src/env/wrappers/reward\_wrapper.py

---

## 1. Objetivo e Contexto

O módulo **RewardWrapper** fornece um wrapper plugável, robusto e thread-safe para modificação, pós-processamento e logging de recompensas em ambientes RL do Op\_Trader. Permite aplicar transformações customizadas (clipping, escalonamento, penalidades, delays, shaping, smoothing, etc.), facilitando tuning, ablação, análise de sensibilidade e experimentação sem alterar o ambiente base. Integra logging detalhado e é empilhável com outros wrappers.

---

## 2. Entradas e Assinatura

| Parâmetro  | Tipo     | Obrigatório | Descrição                                       | Exemplo                       |
| ---------- | -------- | ----------- | ----------------------------------------------- | ----------------------------- |
| env        | gym.Env  | Sim         | Ambiente RL encapsulado                         | TrainEnvShort()               |
| reward\_fn | Callable | Não         | Função customizada para transformação de reward | lambda r: np.clip(r, -10, 10) |
| logger     | Logger   | Não         | Logger estruturado Op\_Trader                   | get\_logger("RewardWrapper")  |
| log\_dir   | str      | Não         | Diretório para salvar logs                      | "logs/reward"                 |
| debug      | bool     | Não         | Ativa logs detalhados                           | True                          |

**Assinatura dos métodos:**

```python
class RewardWrapper(gym.Wrapper):
    def __init__(self, env, reward_fn=None, logger=None, log_dir: str = None, debug: bool = False, **kwargs): ...
    def step(self, action): ...
    def set_reward_fn(self, reward_fn): ...
    def save_logs(self, path: str = None): ...
    def get_logs(self) -> dict: ...
    def reset(self, **kwargs): ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método          | Retorno                                  | Descrição                                   |
| --------------- | ---------------------------------------- | ------------------------------------------- |
| step            | obs, reward, terminated, truncated, info | Resultado padrão Gymnasium                  |
| set\_reward\_fn | None                                     | Atualiza função de transformação            |
| save\_logs      | None                                     | Salva logs do ciclo em CSV/JSON             |
| get\_logs       | dict                                     | Dicionário com todos logs por episódio      |
| reset           | obs, info                                | Observação e info do reset do ambiente      |
| close           | None                                     | Garante flush e salvamento de todos os logs |

---

## 4. Fluxo de Execução

* ****init****: Inicializa logger, reward\_fn, log\_dir, estrutura interna e proteção thread-safe.
* **reset**: Chama reset do ambiente, loga contexto inicial, episódio.
* **step**: Chama step do ambiente, aplica reward\_fn, trata edge cases, loga transformação.
* **set\_reward\_fn**: Permite troca dinâmica da função de transformação.
* **save\_logs**: Salva todos os logs do ciclo (CSV/JSON, nomes padronizados).
* **get\_logs**: Retorna todos os logs acumulados do wrapper.
* **close**: Salva e flush dos logs pendentes e encerra recursos do ambiente.

---

## 5. Edge Cases e Validações

* Função reward\_fn inválida ou lança exceção: log warning, usa reward original.
* Output da reward\_fn inválido (NaN, inf, tipo errado): log warning, corrige para zero.
* Log de transformação ausente: warning.
* Concorrência: métodos protegidos por RLock.

---

## 6. Integração e Compatibilidade

* Plugável em qualquer ambiente RL do Op\_Trader.
* Integra com RewardAggregator, TradeLogger, LoggingWrapper, file\_saver.
* Gera logs auditáveis para DEV\_LOG, análise e compliance.
* Usabilidade direta em dev, experimentação, produção e CI/CD.

---

## 7. Docstrings Google Style

```python
class RewardWrapper(gym.Wrapper):
    """
    Wrapper para modificação, pós-processamento e logging de recompensas no RL Op_Trader.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        reward_fn (callable, opcional): Função customizada para transformação.
        logger (Logger, opcional): Logger estruturado.
        log_dir (str, opcional): Diretório para logs.
        debug (bool): Ativa logs detalhados.
        **kwargs: Argumentos extras plugáveis.

    Métodos principais:
        - step: Transformação de recompensa e logging.
        - set_reward_fn: Atualização dinâmica da função de reward.
        - save_logs/get_logs: Exportação e auditoria.
        - reset/close: Ciclo de vida e limpeza.

    Raises:
        Exception: Para erros críticos durante o logging.

    Example:
        >>> from src.env.wrappers.reward_wrapper import RewardWrapper
        >>> from src.env.environments.train_env_short import TrainEnvShort
        >>> def clip_reward(r):
        ...     return max(min(r, 10.0), -10.0)
        >>> logger = get_logger("RewardWrapper", debug=True)
        >>> env = TrainEnvShort(context_macro={"direction": "short"}, debug=True)
        >>> rew_env = RewardWrapper(env, reward_fn=clip_reward, logger=logger)
        >>> obs, info = rew_env.reset()
        >>> done = False
        >>> while not done:
        ...     action = agent.select_action(obs)
        ...     obs, reward, done, truncated, info = rew_env.step(action)
        >>> rew_env.save_logs()
    """
```

---

## 8. Exemplo de Uso

```python
from src.env.wrappers.reward_wrapper import RewardWrapper
from src.env.environments.train_env_short import TrainEnvShort
from src.utils.logging_utils import get_logger

def clip_reward(reward):
    return max(min(reward, 10.0), -10.0)

logger = get_logger("RewardWrapper", debug=True)
env = TrainEnvShort(context_macro={"direction": "short"}, debug=True)
rew_env = RewardWrapper(env, reward_fn=clip_reward, logger=logger)

obs, info = rew_env.reset()
done = False
while not done:
    action = agent.select_action(obs)
    obs, reward, done, truncated, info = rew_env.step(action)
rew_env.save_logs()
```

---

## 9. Testes e Validação

* Testes unitários validam:

  * Logging correto de step, transformação e reset
  * Salvamento e estrutura de arquivos
  * Thread safety
  * Robustez nos edge cases de reward\_fn
  * Integração multi-wrapper

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style em todos métodos
* [x] Logging detalhado de transformações
* [x] Edge cases e tratamento robusto de erro
* [x] Testes unitários e integração multi-ambiente
* [x] Thread safety validada
* [x] Evidência de execução salva (save\_logs)
* [x] Pronto para uso plugável em pipelines RL

---

## 11. Rastreabilidade e Histórico

* Arquivo: `src/env/wrappers/reward_wrapper.py`
* Testes: `tests/unit/test_reward_wrapper.py`
* Última atualização: 2025-06-08
* Responsável: Equipe Op\_Trader
* Status: @STABLE homologado
