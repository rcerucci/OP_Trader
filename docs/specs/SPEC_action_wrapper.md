# SPEC\_action\_wrapper.md — src/env/wrappers/action\_wrapper.py

---

## 1. Objetivo e Contexto

Módulo **ActionWrapper**: wrapper plugável, profissional e auditável para transformação, validação, correção de dtype/shape e logging seguro das ações enviadas ao ambiente RL do Op\_Trader.
Garante compatibilidade Gymnasium <0.29, integra função customizada, logging, auditoria, rastreamento e validação estrita (dtype/shape/range). Essencial para compliance, experimentação e robustez em pipelines RL.

---

## 2. Entradas e Assinatura

| Parâmetro  | Tipo     | Obrigatório | Descrição                                       | Exemplo                      |
| ---------- | -------- | ----------- | ----------------------------------------------- | ---------------------------- |
| env        | gym.Env  | Sim         | Ambiente RL encapsulado                         | TrainEnvLong(), DummyEnv()   |
| action\_fn | Callable | Não         | Função customizada para transformação/validação | lambda x: np.clip(x, -1, 1)  |
| logger     | Logger   | Não         | Logger estruturado (get\_logger)                | get\_logger("ActionWrapper") |
| log\_dir   | str      | Não         | Diretório para salvar logs CSV de ações         | "./logs/"                    |
| cli\_level | str/int  | Não         | Nível do logger ("DEBUG", "INFO", etc.)         | "INFO"                       |

**Assinatura dos métodos:**

```python
class ActionWrapper(gym.Wrapper):
    def __init__(self, env, action_fn=None, logger=None, log_dir=None, cli_level="INFO", **kwargs): ...
    def step(self, action): ...
    def set_action_fn(self, action_fn): ...
    def save_logs(self, path=None): ...
    def get_logs(self) -> list: ...
    def reset(self, **kwargs): ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método          | Retorno | Descrição                                                    |
| --------------- | ------- | ------------------------------------------------------------ |
| step            | tuple   | obs, reward, terminated, truncated, info                     |
| set\_action\_fn | None    | Atualiza função customizada                                  |
| save\_logs      | None    | Salva histórico/log CSV das ações                            |
| get\_logs       | list    | Lista de dicionários (timestamp, ação original/transformada) |
| reset           | tuple   | (obs, info) padrão Gymnasium                                 |
| close           | None    | Fecha wrapper e salva logs                                   |

---

## 4. Fluxo de Execução

* ****init**:** Inicializa wrapper, logger, função customizada, logs internos.
* **step:**

  1. Recebe ação do agente
  2. Aplica função customizada se existir
  3. Corrige NaN (para zero)
  4. Corrige dtype/shape conforme action\_space
  5. Valida com contains (raise ValueError se inválido)
  6. Loga ciclo completo
  7. Passa ao ambiente
* **set\_action\_fn:** Permite troca dinâmica da função de transformação/validação.
* **save\_logs:** Persiste o histórico de ações processadas (CSV).
* **get\_logs:** Retorna os logs acumulados.
* **reset:** Limpa logs internos e reinicia ambiente.
* **close:** Salva logs (se houver) e finaliza wrapper.

---

## 5. Edge Cases e Validações

* Ação do dtype errado: converte automaticamente para o dtype do espaço antes da validação.
* Shape incompatível: reshape automático (se possível), senão ValueError.
* NaN na ação: substitui por zero, loga warning.
* Função customizada lança exceção: loga warning e usa ação original.
* Ação fora do espaço: lança ValueError, loga erro crítico.
* Nenhum log para salvar: loga warning.
* Concorrência: proteção via RLock.

---

## 6. Integração e Compatibilidade

* Compatível com Gymnasium <0.29, Gym clássico, pytest, produção.
* Suporta wrappers encadeados (ex: NormalizationWrapper, LoggingWrapper).
* Integra logging\_utils (get\_logger), file\_saver, DEV\_LOG, rastreio auditoria.
* Pronto para pipelines RL, testes unitários/integrados, CI/CD.

---

## 7. Docstring Google Style

```python
class ActionWrapper(gym.Wrapper):
    """
    Wrapper plugável de ação para ambientes RL do Op_Trader.

    Corrige dtype/shape, aplica função customizada, valida, loga e rastreia todas as ações.

    Args:
        env (gym.Env): Ambiente RL encapsulado.
        action_fn (Callable, opcional): Função customizada para transformação de ação.
        logger (Logger, opcional): Logger estruturado Op_Trader.
        log_dir (str, opcional): Diretório para logs CSV.
        cli_level (str|int, opcional): Nível de log ("INFO", "DEBUG", ...).

    Métodos principais:
        - step: processamento e rastreamento completo da ação.
        - set_action_fn: atualização dinâmica.
        - save_logs/get_logs: auditoria e compliance.
        - reset/close: ciclo de vida e limpeza.

    Raises:
        ValueError: Para ações fora do espaço permitido.

    Example:
        >>> from src.env.wrappers.action_wrapper import ActionWrapper
        >>> from src.env.environments.train_env_long import TrainEnvLong
        >>> wrapper = ActionWrapper(TrainEnvLong(), action_fn=lambda x: np.clip(x, -1, 1))
        >>> obs, info = wrapper.reset()
        >>> obs, reward, terminated, truncated, info = wrapper.step([1.5, -2.0])
    """
```

---

## 8. Exemplo de Uso

```python
from src.env.wrappers.action_wrapper import ActionWrapper
from src.env.environments.train_env_long import TrainEnvLong
import numpy as np

def clip_action(action):
    return np.clip(action, -1, 1)

env = TrainEnvLong(context_macro={"direction": "long"}, debug=True)
action_env = ActionWrapper(env, action_fn=clip_action, cli_level="DEBUG", log_dir="./logs/")

obs, info = action_env.reset()
done = False
while not done:
    action = np.random.uniform(-2, 2, size=(2,))  # Exemplo agente aleatório
    obs, reward, terminated, truncated, info = action_env.step(action)
    done = terminated or truncated
action_env.save_logs()
```

---

## 9. Testes e Validação

* Cobertura unitária (Pytest): transformação, validação, dtype/shape, logging, save\_logs, edge cases.
* Testes críticos:

  * dtype errado (float64 vs float32): auto-correção, aceitação
  * ação fora do range: raise ValueError
  * action\_fn lança erro: fallback, warning
  * logging e save\_logs criam arquivos rastreáveis

**Comando de teste:**

```bash
pytest tests/unit/test_action_wrapper.py -v -s --log-cli-level=DEBUG
```

---

## 10. Checklist de Qualidade

* [x] Docstrings Google Style, padrão Op\_Trader
* [x] Logging detalhado, rastreável
* [x] Edge cases e tratamento robusto de erro
* [x] Testes unitários e integração completos
* [x] Compatibilidade total Gymnasium <0.29, produção, CI/CD
* [x] Exemplo de uso validado
* [x] Auditoria via save\_logs, get\_logs

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha ActionWrapper, src/env/wrappers/action\_wrapper.py, @STABLE
* REFERENCE\_TABLE.md: mover após ciclo completo de homologação
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes passaram
* TESTE: tests/unit/test\_action\_wrapper.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader
