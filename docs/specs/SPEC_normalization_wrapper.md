# SPEC\_normalization\_wrapper.md — src/env/wrappers/normalization\_wrapper.py

---

## 1. Objetivo e Contexto

O módulo **NormalizationWrapper** fornece um wrapper plugável (compatível Gymnasium) para normalização online e reversível de observações, recompensas e métricas em ambientes RL do Op\_Trader. Implementa estratégias de normalização (ex: VecNormalize, min-max, z-score) durante o ciclo de treinamento ou execução, garantindo consistência, performance e compatibilidade para PPO, MLP e integrações futuras. Permite persistência, hot-reload, auditoria e logging detalhado dos parâmetros de normalização. Ao rodar em ambiente não-VecNormalize, eventos são logados e nunca causam travamento do ciclo.

---

## 2. Entradas e Assinatura

| Parâmetro     | Tipo   | Obrigatório | Descrição                                                            | Exemplo                             |
| ------------- | ------ | ----------- | -------------------------------------------------------------------- | ----------------------------------- |
| env           | obj    | Sim         | Ambiente RL Gymnasium a ser encapsulado                              | TrainEnvLong()                      |
| norm\_type    | str    | Não         | Estratégia de normalização ("vecnorm", "z\_score", "minmax", "none") | "z\_score"                          |
| obs\_stats    | dict   | Não         | Parâmetros prévios de observação                                     | {"mean": \[0.], "std": \[1.]}       |
| reward\_stats | dict   | Não         | Parâmetros prévios de recompensa                                     | {"mean": 0., "std": 1.}             |
| logger        | Logger | Não         | Logger estruturado Op\_Trader                                        | get\_logger("NormalizationWrapper") |
| save\_path    | str    | Não         | Caminho para salvar estado                                           | "models/vecnorm.pkl"                |
| debug         | bool   | Não         | Ativa logs detalhados                                                | True                                |
| action        | any    | Step        | Ação para step                                                       | 0                                   |
| path          | str    | save/load   | Caminho base para salvar/carregar norm state                         | "models/vecnorm.pkl"                |

**Assinatura dos métodos:**

```python
class NormalizationWrapper(gym.Wrapper):
    def __init__(self, env, norm_type: str = "vecnorm", obs_stats: dict = None, reward_stats: dict = None, logger=None, save_path: str = None, debug: bool = False, **kwargs): ...
    def reset(self, **kwargs): ...
    def step(self, action): ...
    def save_norm_state(self, path: str = None): ...
    def load_norm_state(self, path: str = None): ...
    def get_norm_params(self) -> dict: ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método            | Retorno                 | Descrição                                           |
| ----------------- | ----------------------- | --------------------------------------------------- |
| reset             | obs,info                | Observação inicial normalizada e info               |
| step              | obs,rwd,term,trunc,info | Resultado do step completo e normalizado            |
| save\_norm\_state | None                    | Salva estado de normalização persistente            |
| load\_norm\_state | None                    | Carrega estado salvo (se possível)                  |
| get\_norm\_params | dict                    | Retorna snapshot dos parâmetros/estatísticas atuais |
| close             | None                    | Garante salvamento e flush dos logs pendentes       |

---

## 4. Fluxo de Execução

* **reset:** Inicializa/reset estatísticas, tenta restaurar VecNormalize se disponível, normaliza a primeira observação.
* **step:** Normaliza observação e recompensa, atualiza estatísticas, registra logs.
* **save\_norm\_state:** Persiste estado atual se tipo "vecnorm" (log de erro caso DummyEnv ou similar).
* **load\_norm\_state:** Restaura estado salvo se tipo "vecnorm" (log de warning/erro caso não aplicável).
* **get\_norm\_params:** Retorna snapshot completo dos parâmetros correntes, pronto para rastreamento/auditoria.
* **close:** Garante salvamento seguro e fechamento de recursos.

---

## 5. Edge Cases e Validações

* Estado de normalização ausente/corrompido: log warning, fallback seguro
* Tentativa de usar VecNormalize com DummyEnv: log ERROR e segue execução
* Parâmetros incompatíveis: log erro, raise se crítico
* Concorrência: métodos thread-safe
* Tentativa de normalizar dados inválidos (NaN, shape incorreto): log warning, não aplica
* Mudança dinâmica de norm\_type: log info, reinicializa

---

## 6. Integração e Compatibilidade

* Herda de `gymnasium.Wrapper`, plugável em qualquer ambiente RL Op\_Trader
* Usa get\_logger (logging\_utils), save\_vecnormalize/load\_vecnormalize (vecnorm\_loader)
* Integra com ObservationBuilder, RewardAggregator, TradeLogger
* Compatível com pytest (testes usam tmp\_path), produção salva em logs/audits
* Compatível com Gymnasium >=0.29 e pipelines Op\_Trader

---

## 7. Docstring Google Style

```python
class NormalizationWrapper(gym.Wrapper):
    """
    Wrapper para normalização online, reversível e thread-safe de observações/recompensas nos ambientes RL do Op_Trader.

    Métodos principais:
      - reset: inicializa/restaura stats.
      - step: normaliza observação e reward.
      - save_norm_state/load_norm_state: persistência/auditoria.
      - get_norm_params: snapshot stats.
      - close: flush/salva estado final.

    Args:
        env (gym.Env): Ambiente RL encapsulado.
        norm_type (str): Estratégia de normalização.
        obs_stats (dict, opcional): Parâmetros prévios de observação.
        reward_stats (dict, opcional): Parâmetros prévios de recompensa.
        logger (Logger, opcional): Logger estruturado.
        save_path (str, opcional): Caminho persistência.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.wrappers.normalization_wrapper import NormalizationWrapper
from src.env.environments.train_env_long import TrainEnvLong
from src.utils.logging_utils import get_logger

logger = get_logger("NormalizationWrapper", cli_level="DEBUG")
env = TrainEnvLong(context_macro={"direction": "long"}, debug=True)
norm_env = NormalizationWrapper(env, norm_type="vecnorm", save_path="models/vecnorm.pkl", logger=logger)

obs, info = norm_env.reset()
done = False
while not done:
    action = agent.select_action(obs)
    obs, reward, done, truncated, info = norm_env.step(action)
norm_env.save_norm_state()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (reset, step, save/load state, get\_params, close, edge cases, concorrência)
* Testes usam tmp\_path do pytest, produção usa logs/audits/
* Testes recomendados:

```bash
pytest tests/unit/test_normalization_wrapper.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui cenários: inicialização, ciclo, persistência, DummyEnv sem VecNormalize, multi-thread, edge cases

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging detalhado, segregado e thread-safe
* [x] Edge cases (estatísticas ausentes, tipos, dummy, falha I/O)
* [x] Testes unitários, concorrência e persistência
* [x] Compatível com produção e auditoria
* [x] Nenhum erro bloqueia o ciclo, logs garantem rastreio
* [x] Pronto para uso plugável por qualquer pipeline RL
* [x] Exemplo testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: linha RewardWrapper, src/env/wrappers/reward\_wrapper.py, @CODE (marcar @STABLE ao final do ciclo wrappers)
* REFERENCE\_TABLE.md: a ser movido após o ciclo completo
* DEV\_LOG.md: ciclo 2025-06-08 homologado, todos os testes unitários, edge cases e concorrência passaram
* TESTE: tests/unit/test\_reward\_wrapper.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---
