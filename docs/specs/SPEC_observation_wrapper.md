# SPEC\_observation\_wrapper.md — src/env/wrappers/observation\_wrapper.py

---

## 1. Objetivo e Contexto

O módulo **ObservationWrapper** permite transformação, filtragem, expansão ou compressão das observações retornadas pelos ambientes RL do Op\_Trader. É plugável e compatível com Gymnasium, facilitando ablação de features, engenharia de observações, normalização adicional, encriptação/mascaramento de inputs, concatenação de contexto, reorder ou clipping. Suporta logging detalhado, integração com ObservationBuilder e persistência para auditoria e debug.

---

## 2. Entradas e Assinatura

| Parâmetro | Tipo     | Obrigatório | Descrição                               | Exemplo                           |
| --------- | -------- | ----------- | --------------------------------------- | --------------------------------- |
| env       | obj      | Sim         | Ambiente RL Gymnasium a ser encapsulado | TrainEnvLong()                    |
| obs\_fn   | callable | Não         | Função customizada de transformação     | mask\_observation                 |
| logger    | Logger   | Não         | Logger estruturado Op\_Trader           | get\_logger("ObservationWrapper") |
| log\_dir  | str      | Não         | Diretório para salvar logs              | "logs/observation/"               |
| debug     | bool     | Não         | Ativa logs detalhados                   | True                              |
| action    | any      | Step        | Ação para step                          | 0                                 |
| path      | str      | save\_logs  | Caminho base para salvar logs           | "logs/teste"                      |

**Assinatura dos métodos:**

```python
class ObservationWrapper(gym.Wrapper):
    def __init__(self, env, obs_fn=None, logger=None, log_dir: str = None, debug: bool = False, **kwargs): ...
    def reset(self, **kwargs): ...
    def step(self, action): ...
    def set_obs_fn(self, obs_fn): ...
    def save_logs(self, path: str = None): ...
    def get_logs(self) -> dict: ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método       | Retorno                 | Descrição                                         |
| ------------ | ----------------------- | ------------------------------------------------- |
| reset        | obs,info                | Observação inicial transformada e info do reset   |
| step         | obs,rwd,term,trunc,info | Resultado do step completo, com obs transformada  |
| set\_obs\_fn | None                    | Permite troca dinâmica de função de transformação |
| save\_logs   | None                    | Salva histórico das transformações                |
| get\_logs    | dict                    | Retorna logs acumulados                           |
| close        | None                    | Garante salvamento/flush dos logs pendentes       |

---

## 4. Fluxo de Execução

* **reset:** Inicializa episódio, aplica obs\_fn à observação inicial, loga input/output.
* **step:** Executa ação, aplica obs\_fn à observação, loga input/output, edge cases.
* **set\_obs\_fn:** Troca dinâmica da função de transformação, com logging.
* **save\_logs:** Salva logs em CSV/JSON (file\_saver).
* **get\_logs:** Retorna estrutura de logs por episódio.
* **close:** Garante salvamento seguro e flush dos logs.

---

## 5. Edge Cases e Validações

* obs\_fn inválida: log erro, fallback para observação original
* Função lança exceção: log warning, usa obs original
* Output inválido (NaN, shape incorreto): log warning, corrige para original
* Log ausente: warning
* Concorrência: todos métodos thread-safe

---

## 6. Integração e Compatibilidade

* Herda de gymnasium.Wrapper, plugável em qualquer ambiente RL Op\_Trader
* Usa get\_logger (logging\_utils), build\_filename/save\_dataframe/get\_timestamp (file\_saver)
* Integra com ObservationBuilder, LoggingWrapper, etc.
* Compatível com pytest (testes usam tmp\_path), produção salva em logs/observation/
* Testado com Gymnasium >= 0.29

---

## 7. Docstring Google Style

```python
class ObservationWrapper(gym.Wrapper):
    """
    Wrapper para transformação, filtragem e logging de observações nos ambientes RL do Op_Trader.

    Métodos principais:
      - reset: aplica obs_fn e registra input/output.
      - step: transforma, valida e loga observações.
      - set_obs_fn: troca dinâmica da função.
      - save_logs: persistência.
      - get_logs: consulta estruturada.
      - close: flush/salva logs finais.

    Args:
        env (gym.Env): Ambiente RL encapsulado.
        obs_fn (callable, opcional): Função de transformação.
        logger (Logger, opcional): Logger estruturado.
        log_dir (str, opcional): Diretório dos logs.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.wrappers.observation_wrapper import ObservationWrapper
from src.env.environments.train_env_long import TrainEnvLong
from src.utils.logging_utils import get_logger

def mask_observation(obs):
    obs = obs.copy()
    obs[0] = 0.0  # Esconde o primeiro valor
    return obs

logger = get_logger("ObservationWrapper", cli_level="DEBUG")
env = TrainEnvLong(context_macro={"direction": "long"}, debug=True)
obs_env = ObservationWrapper(env, obs_fn=mask_observation, logger=logger)

obs, info = obs_env.reset()
done = False
while not done:
    action = agent.select_action(obs)
    obs, reward, done, truncated, info = obs_env.step(action)
obs_env.save_logs()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (reset, step, set\_obs\_fn, save\_logs, get\_logs, close, edge cases, concorrência)
* Testes usam tmp\_path do pytest, produção usa logs/observation/
* Testes recomendados:

```bash
pytest tests/unit/test_observation_wrapper.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui: transformação, edge case de exceção/NaN, troca dinâmica, multi-thread

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging detalhado, segregado e thread-safe
* [x] Edge cases (função inválida, exceção, NaN, shape)
* [x] Testes unitários, troca dinâmica, concorrência
* [x] Compatível com produção e auditoria
* [x] Nenhum erro bloqueia o ciclo, logs garantem rastreio
* [x] Pronto para uso plugável
* [x] Exemplo testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha ObservationWrapper, src/env/wrappers/observation\_wrapper.py, @CODE (marcar @STABLE ao final do ciclo wrappers)
* REFERENCE\_TABLE.md: a ser movido após o ciclo completo
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes unitários, edge cases e concorrência passaram
* TESTE: tests/unit/test\_observation\_wrapper.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---
