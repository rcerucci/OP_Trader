# SPEC\_logging\_wrapper.md — src/env/wrappers/logging\_wrapper.py

---

## 1. Objetivo e Contexto

O módulo **LoggingWrapper** fornece um wrapper plugável (Gymnasium style) para logging estruturado, detalhado e segregado de todos os ciclos de steps, resets, episódios, ações, rewards, eventos de risco e auditoria em ambientes RL do Op\_Trader. Garante rastreabilidade, compliance e análise retroativa, com integração plugável, granularidade configurável e logs compatíveis com auditoria externa.

---

## 2. Entradas e Assinatura

| Parâmetro     | Tipo   | Obrigatório | Descrição                               | Exemplo                       |
| ------------- | ------ | ----------- | --------------------------------------- | ----------------------------- |
| env           | obj    | Sim         | Ambiente RL Gymnasium a ser encapsulado | TrainEnvLong()                |
| logger        | Logger | Não         | Logger estruturado Op\_Trader           | get\_logger("LoggingWrapper") |
| trade\_logger | obj    | Não         | Logger especializado de trades          | TradeLogger()                 |
| log\_level    | str    | Não         | Nível de logging ("DEBUG", "INFO")      | "DEBUG"                       |
| log\_dir      | str    | Não         | Diretório para salvar logs              | "logs/episodes/"              |
| debug         | bool   | Não         | Ativa logs detalhados                   | True                          |
| action        | any    | Step        | Ação para step                          | 0                             |
| event\_type   | str    | log\_event  | Tipo do evento customizado              | "risk\_alert"                 |
| data          | dict   | log\_event  | Dados do evento customizado             | {"msg": "alerta"}             |
| path          | str    | save\_logs  | Caminho base para salvar logs           | "logs/teste"                  |

**Assinatura dos métodos:**

```python
class LoggingWrapper(gym.Wrapper):
    def __init__(self, env, logger=None, trade_logger=None, log_level: str = "INFO", log_dir: str = None, debug: bool = False, **kwargs): ...
    def reset(self, **kwargs): ...
    def step(self, action): ...
    def log_event(self, event_type: str, data: dict): ...
    def save_logs(self, path: str = None): ...
    def get_logs(self) -> dict: ...
    def close(self): ...
```

---

## 3. Saídas e Retornos

| Método     | Retorno                 | Descrição                                     |
| ---------- | ----------------------- | --------------------------------------------- |
| reset      | obs,info                | Observação inicial e info do reset            |
| step       | obs,rwd,term,trunc,info | Resultado do step completo                    |
| log\_event | None                    | Loga evento customizado por episódio          |
| save\_logs | None                    | Salva logs do ciclo em CSV/JSON padronizados  |
| get\_logs  | dict                    | Retorna todos logs acumulados do wrapper      |
| close      | None                    | Garante salvamento e flush dos logs pendentes |

---

## 4. Fluxo de Execução

* **reset:** Inicializa episódio, loga contexto inicial, seed, cria estrutura de logs. O evento `"INIT"` é sempre registrado como primeiro log do primeiro episódio (após o primeiro reset). Nenhum evento é registrado fora do contexto de um episódio.
* **step:** Executa a ação, loga o resultado completo do ciclo, garante atomicidade dos logs.
* **log\_event:** Loga eventos customizados, sempre agregando ao episódio corrente (logs thread-safe).
* **save\_logs:** Salva todos os logs agregados, usando nomes padronizados, nos formatos CSV e JSON.
* **get\_logs:** Retorna a estrutura completa de logs para análise programática.
* **close:** Garante salvamento e flush dos logs ao encerrar o wrapper.

---

## 5. Edge Cases e Validações

* Falha de logging (I/O, espaço, permissão): log crítico, tenta fallback
* TradeLogger ausente: warning, segue só com logger padrão
* Concorrência: todos métodos são thread-safe
* Log de evento malformado: warning, não grava
* Eventos só são registrados a partir do reset
* Logs muito grandes: permite rotação ou truncamento (futuro)

---

## 6. Integração e Compatibilidade

* Herda de `gymnasium.Wrapper`, plugável em qualquer ambiente RL Op\_Trader
* Usa get\_logger (logging\_utils), build\_filename/save\_dataframe/get\_timestamp (file\_saver)
* Integra com TradeLogger e demais utilitários homologados
* Compatível com pytest (testes usam tmp\_path), produção salva em logs/episodes
* Testado para Gymnasium >= 0.29

---

## 7. Docstring Google Style

```python
class LoggingWrapper(gym.Wrapper):
    """
    Wrapper para logging estruturado, segregado por episódio e thread-safe para ambientes RL do Op_Trader.

    Métodos principais:
      - reset: inicia episódio, registra contexto inicial.
      - step: loga ação, reward e infos.
      - log_event: registra eventos customizados.
      - save_logs: salva todos os logs no formato CSV/JSON.
      - get_logs: retorna todos logs do wrapper.
      - close: flush/salva logs ao final.

    Args:
        env (gym.Env): Ambiente RL a ser encapsulado.
        logger (Logger, opcional): Logger estruturado do projeto.
        trade_logger (TradeLogger, opcional): Logger especializado de trades.
        log_level (str): Nível de logging.
        log_dir (str, opcional): Diretório dos logs.
        debug (bool): Ativa logs detalhados.
    """
    ...
```

---

## 8. Exemplo de Uso

```python
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.environments.train_env_long import TrainEnvLong
from src.utils.logging_utils import get_logger

logger = get_logger("LoggingWrapper", cli_level="DEBUG")
env = TrainEnvLong(context_macro={"direction": "long"}, debug=True)
wrapped_env = LoggingWrapper(env, logger=logger, log_level="DEBUG", log_dir="logs/episodes/")

obs, info = wrapped_env.reset()
done = False
while not done:
    action = agent.select_action(obs)
    obs, reward, done, truncated, info = wrapped_env.step(action)
    if reward < -10:
        wrapped_env.log_event("risk_alert", {"msg": "drawdown crítico"})
wrapped_env.save_logs()
```

---

## 9. Testes e Validação

* Cobertura unitária dos métodos (reset, step, log\_event, save\_logs, get\_logs, close, edge cases, concorrência)
* Testes usam tmp\_path do pytest, produção usa logs/episodes/
* Testes recomendados:

```bash
pytest tests/unit/test_logging_wrapper.py -v -s --log-cli-level=DEBUG
```

* Homologação inclui cenário multi-thread, logs malformados, ausência de trade\_logger e falha de escrita

---

## 10. Checklist de Qualidade

* [x] Código PEP8, docstrings Google, imports absolutos
* [x] Logging estruturado, segregado por episódio, auditável e thread-safe
* [x] Edge cases (iniciais, eventos malformados, sem trade\_logger, falha I/O)
* [x] Testes unitários e concorrência
* [x] Compatível com produção e auditoria
* [x] Nenhum log fora de contexto de episódio
* [x] Estrutura de logs preparada para rotação/truncamento
* [x] Exemplo testado

---

## 11. Rastreabilidade e Histórico

* DEVELOP\_TABLE.md: \[linha correspondente]
* REFERENCE\_TABLE.md: \[finalizar ciclo]
* DEV\_LOG.md: \[entrada do ciclo]
* TESTE: tests/unit/test\_logging\_wrapper.py
* SPEC\_TEMPLATE.md: v2.0
* Última atualização: 2025-06-08
* Autor: Equipe Op\_Trader

---
