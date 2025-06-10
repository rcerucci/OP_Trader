# SPEC\_acoplamento\_pipeline\_ambientes.md

## 1. Visão Geral

Este SPEC define como deve ser feito o acoplamento inequívoco entre qualquer pipeline superior do Op\_Trader (ex: trade, train, evaluate, tune, inference) e o pipeline de ambiente (EnvFactory, wrappers, logging e rastreio de episódios).
O objetivo é garantir que qualquer uso — desde casos simples até fluxos multi-modelo ou multi-env — seja plugável, rastreável, fácil de testar e de auditar, independente do modo de operação (loop manual, rollout automatizado, treino supervisionado ou RL clássico).

---

## 2. Objetivos e Justificativa

A integração entre pipelines superiores (ex: `trade.py`, `train.py`) e o pipeline de ambiente do Op\_Trader foi projetada para atender os seguintes objetivos:

* **Plug-and-play real**: integrar rapidamente modelos, callbacks e infra sem retrabalho.
* **Rastreabilidade total**: garantir logs detalhados de todas as transições, ações, recompensas, resets e eventos de erro.
* **Robustez operacional**: suportar edge cases (reset no meio do rollout, ação inválida, falha de log, exceptions em wrappers).
* **Expansão fácil**: preparar para casos avançados (multi-env, multi-model, integração supervisionada, validação cruzada).
* **Padronização de interface**: reduzir ambiguidade na orquestração, logs, nomes de arquivos, argumentos de criação de ambiente/modelo e de logging.

---

## 3. Requisitos de Integração

### 3.1 Interfaces

* O pipeline superior deve ser capaz de:

  * **Instanciar o ambiente** via EnvFactory, com registro automático de todos os wrappers.
  * **Definir explicitamente o `log_dir` para todos os wrappers** em qualquer execução (ex: `logs/train/ep1/`).
  * **Passar o argumento `debug`** (bool) para ativar logs detalhados em todos os wrappers e no ambiente.
  * **Resetar o ambiente entre episódios e garantir que todos os logs de steps, actions, rewards, obs, info sejam persistidos no diretório definido**.
  * **Fornecer/receber callbacks** de logging, early stop e métricas durante treino/execução (opcional, mas recomendado).
  * **Acessar o registry auditável de envs/wrappers** da instância EnvFactory.
  * **Validar que todos os tipos de ação semântica ("buy", "hold", "sell", "close") estejam presentes nos logs da execução**.
  * **Permitir configuração de métricas de performance e periodicidade de salvamento/checkpoint**.
  * **Executar um teste de integração do pipeline ANTES de rodar com modelo real** (obrigatório para CI/CD, recomendável para dev).

---

### 3.2 Contratos Obrigatórios

* O pipeline superior DEVE:

  * Registrar no log principal o pipeline, os wrappers e os paths de logs a cada instância.
  * Garantir que após cada episódio/loop:

    * Todos os arquivos de log (`csv`, `json`) estejam presentes em `log_dir`.
    * O log contenha ações e resultados semanticamente corretos.
    * Qualquer falha de serialização ou logging seja capturada, reportada e não silenciosamente ignorada.
  * Garantir que o ambiente seja corretamente fechado e seus logs salvos, independentemente do término do episódio ou exceção.
  * Validar o passo a passo via caso de teste automatizado: `test_pipeline_returns_all_cases.py`.

---

## 4. Comportamento Esperado e Fluxos Típicos

### 4.1 Acoplamento Simples (pipeline padrão)

```python
from src.env.env_factory import EnvFactory

# Instanciação do ambiente com pipeline completo
env_factory = EnvFactory(config)
env = env_factory.create_env(
    name="train_env_long",
    wrappers=["action", "reward", "normalization", "observation", "logging"],
    log_dir="logs/train/exp01/",
    debug=True,
)
model = PPOModel(env=env, ...)
# Loop padrão
obs, info = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
env.save_logs()
```

### 4.2 Acoplamento Multi-episódio com Callback, Logging, Early Stop

```python
env = env_factory.create_env("trade_env", wrappers=["action", "reward", "normalization", "observation", "logging"], log_dir="logs/trade/session_001/")
model = PPOModel.load("models/best_model.zip")
n_episodes = 10
for ep in range(n_episodes):
    obs, info = env.reset()
    done = False
    steps = 0
    while not done:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        steps += 1
        if terminated or truncated:
            break
    env.save_logs()
    # Callback pode ser chamado aqui para early stop, métricas, etc.
```

---

### 4.3 Integração Avançada (Multi-env, Multi-model, Custom Logging)

* Permitir múltiplos ambientes paralelos (ex: avaliação com ensemble de modelos).
* Cada ambiente deve ter seu próprio `log_dir` e registro, sem sobrescrever arquivos.
* Todos os logs, inclusive de erros e callbacks, devem ser persistidos por ambiente/modelo/seed.
* O pipeline deve permitir swap dinâmico de modelo/env e reter audit trail.

---

## 5. Casos de Erro e Edge Cases

* **Falha ao salvar log**: O pipeline deve capturar, logar criticamente e tentar salvar um snapshot mínimo (fallback) antes de seguir ou abortar.
* **Ação inválida**: Deve ser rejeitada com exception rastreável e logada no arquivo de erro do pipeline.
* **Falha de wrapper intermediário**: Não pode corromper episódio/ambiente; deve logar e tentar continuar, exceto se for falha grave.
* **Reset durante step**: Deve fechar arquivos de log intermediários e reabrir novo arquivo na próxima chamada.
* **Exceção não tratada**: Deve ser capturada pelo logger principal, com stack trace e dump do episódio corrente.

---

## 6. Limitações e Recomendações

* O acoplamento do pipeline não suporta logs em múltiplos formatos não padronizados (ex: só csv e json).
* O ambiente espera sempre que as ações recebidas sejam inteiros ou arrays compatíveis com o espaço de ação; outras entradas devem ser validadas antes.
* Para integração com frameworks externos, garantir sempre conversão para dtypes compatíveis com numpy/pandas antes do log.
* Não recomendado rodar com o log\_dir em disco de rede sem lock/controle de concorrência (risco de race condition em logs).

---

## 7. Exemplos de Validação e Auditoria

* Para validar acoplamento:

  * Rode `pytest tests/integration/test_pipeline_returns_all_cases.py`.
  * Verifique que todos os logs (actions, rewards, obs, info, callbacks) estão presentes e semanticamente corretos.
  * Execute buscas simples nos logs para garantir presença das ações `"buy"`, `"hold"`, `"sell"`, `"close"` em pelo menos um episódio de cada pipeline.

---

## 8. Sugestão de Implementação

* Preferencialmente, crie uma função utilitária `orchestrate_pipeline(pipeline_type, config, log_dir, debug, **kwargs)` que:

  * Instancia EnvFactory, wrappers e logger conforme o padrão acima.
  * Aceita modelos, callbacks, seeds, e orquestra a execução do ciclo, reset, logging e save de logs em pontos chave.
  * Retorna um status final, paths dos logs e um dict de métricas para auditoria.

---

## 9. Observações Finais

* Esta especificação é **obrigatória** para todos os pipelines do Op\_Trader que rodem com o ambiente customizado.
* A não aderência a este padrão pode resultar em perda de rastreabilidade, logs inconsistentes ou impossibilidade de debug em produção/treino.
* Recomenda-se sempre auditar as integrações novas via um caso real de uso e reportar problemas neste SPEC.

---

### Dúvidas ou sugestões para a evolução deste SPEC devem ser registradas no README.md e DEV\_LOG.md.

---

**Fim do SPEC — Acoplamento Inequívoco de Pipelines com Ambiente Op\_Trader**

# SPEC\_acoplamento\_pipeline\_ambientes\_EXPANDIDA.md

---

## 1. Visão Geral

Esta SPEC detalha, de forma didática e inequívoca, o acoplamento de qualquer pipeline superior do Op\_Trader (train, trade, evaluate, tune, inferência supervisionada, etc) ao pipeline de ambientes (EnvFactory, wrappers, logging, rastreamento e controle de ciclo). Inclui fluxos completos, tabelas, edge cases, integração multi-modelo e recomendações de produção.

---

## 2. Tabela-Resumo de Parâmetros por Pipeline

| Pipeline | Parâmetro     | Tipo     | Obrigatório | Default | Descrição                                     | Exemplo                 |
| -------- | ------------- | -------- | ----------- | ------- | --------------------------------------------- | ----------------------- |
| train    | env\_name     | str      | Sim         | -       | Nome do ambiente RL                           | "train\_env\_long"      |
|          | log\_dir      | str/path | Sim         | -       | Diretório de logs do pipeline                 | "logs/train/exp01/"     |
|          | model\_class  | RLModel  | Sim         | -       | Classe do modelo RL                           | PPOModel                |
|          | n\_episodes   | int      | Não         | 1       | Quantidade de episódios para treino           | 10                      |
|          | callbacks     | list     | Não         | \[]     | Callbacks customizados (early stop, métricas) | \[CheckpointCallback()] |
| trade    | env\_name     | str      | Sim         | -       | Nome do ambiente                              | "trade\_env"            |
|          | model\_path   | str      | Sim         | -       | Caminho do modelo salvo                       | "models/best.zip"       |
|          | log\_dir      | str/path | Sim         | -       | Diretório para logs do trade                  | "logs/trade/run42/"     |
|          | n\_episodes   | int      | Não         | 1       | Quantidade de episódios                       | 1                       |
| evaluate | env\_name     | str      | Sim         | -       | Nome do ambiente de avaliação                 | "eval\_env"             |
|          | model\_paths  | list     | Sim         | -       | Modelos a avaliar (ensemble, crossval, etc)   | \["m1.zip", ...]        |
|          | log\_dir      | str/path | Sim         | -       | Diretório para logs                           | "logs/eval/bench/"      |
| tune     | env\_name     | str      | Sim         | -       | Nome do ambiente de tuning                    | "train\_env\_long"      |
|          | search\_space | dict     | Sim         | -       | Espaço de busca para tuning                   | {lr: \[1e-4,1e-3]}      |
|          | n\_trials     | int      | Não         | 20      | Nº de execuções de tuning                     | 50                      |
|          | log\_dir      | str/path | Sim         | -       | Diretório para logs do tuning                 | "logs/tune/grid/"       |

---

## 3. Fluxos Completos — Exemplos Por Caso de Uso

### 3.1 Treinamento RL — Single Model, Logging Centralizado

```python
from src.env.env_factory import EnvFactory
from src.env.wrappers import *
from src.models.rl import PPOModel

config = load_config("config_train.yaml")
env_factory = EnvFactory(config)
env = env_factory.create_env(
    name="train_env_long",
    wrappers=["action", "reward", "normalization", "observation", "logging"],
    log_dir="logs/train/exp01/",
    debug=True
)
model = PPOModel(env=env)

for ep in range(5):
    obs, info = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    env.save_logs()
```

#### **Validação do Logging:**

* Todos os arquivos `.csv` e `.json` de cada wrapper salvos em `logs/train/exp01/`
* Logs semanticamente rastreáveis: buy/hold/sell/close presentes

---

### 3.2 Execução/Trade RL — Com Modelo Carregado

```python
env = env_factory.create_env("trade_env", wrappers=["action", "reward", "normalization", "observation", "logging"], log_dir="logs/trade/run42/")
model = PPOModel.load("models/best.zip")
obs, info = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break
env.save_logs()
```

* Pode ser facilmente expandido para múltiplos episódios e diferentes seeds.

---

### 3.3 Avaliação Multi-Modelo — Ensemble/Benchmarks

```python
model_paths = ["models/best_A.zip", "models/best_B.zip"]
for mp in model_paths:
    env = env_factory.create_env("eval_env", wrappers=[...], log_dir=f"logs/eval/{mp}/")
    model = PPOModel.load(mp)
    obs, info = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    env.save_logs()
```

* Logs e métricas separados por modelo/ambiente, rastreáveis por pasta.

---

### 3.4 Tuning Automatizado (ex: Optuna, Grid Search)

```python
from src.tune import tune_model

search_space = {"lr": [1e-4, 1e-3], "batch_size": [64, 256]}
tune_model(
    env_name="train_env_long",
    model_class=PPOModel,
    search_space=search_space,
    n_trials=10,
    log_dir="logs/tune/grid/",
)
```

---

### 3.5 Pipeline Supervisionado — Preditor + RL (DecisionModel)

```python
from src.models.decision import DecisionModel
from src.models.rl import PPOModel

# Preditor supervisionado
decision_model = DecisionModel(features, labels)
decision_model.train()

env = env_factory.create_env("train_env_long", wrappers=[...], log_dir="logs/sup+rl/expA/")
model = PPOModel(env=env, decision_model=decision_model)
...
```

* Logs supervisionados e RL centralizados, métricas paralelas.

---

### 3.6 Multi-env Paralelo/Assíncrono (para avaliação/treino distribuído)

```python
envs = [
    env_factory.create_env(f"env_{i}", wrappers=[...], log_dir=f"logs/multi/env_{i}/")
    for i in range(4)
]
# Loop paralelo ou via VecEnv
```

---

## 4. Edge Cases & Design para Falha

| Caso                 | Comportamento esperado                                                                    |
| -------------------- | ----------------------------------------------------------------------------------------- |
| Falha ao salvar log  | Logger gera mensagem crítica, salva snapshot mínimo em fallback                           |
| Ação inválida        | Exception, log em error\_log, pipeline pode pausar ou continuar sob política configurável |
| Falha em wrapper     | Exception, logs críticos, pipeline pode abortar ou pular step dependendo da gravidade     |
| Reset inesperado     | Fecha logs intermediários, inicia novo arquivo para novo episódio                         |
| Falha no modelo RL   | Exception registrada, pipeline tenta salvar estado parcial/log antes de abortar           |
| Log\_dir inexistente | Diretório é criado automaticamente, loga warning                                          |

---

## 5. Recomendações Avançadas

* **Centralize sempre todos logs em `logs/` ou subpastas bem nomeadas** (exp, modelo, seed).
* **Sempre versionar logs, métricas, checkpoints e configs com timestamp**.
* **Valide todo pipeline rodando `pytest tests/integration/test_pipeline_returns_all_cases.py`** antes de runs reais ou de produção.
* **Evite rodar com log\_dir em rede/discos concorrentes** sem política de lock/rotacionamento.
* **Para debug profundo**, ative o modo `debug=True` nos wrappers e rode com menor batch/episódio para inspeção manual.
* **Integre callbacks customizados para early stop, métricas ou hooks de auditoria conforme os exemplos acima**.
* **Na integração supervisionada, sempre audite as features e targets nos logs e guarde versões dos datasets.**
* **Para multi-env/ensemble, use pastas separadas por instância para logs e outputs.**

---

## 6. Checklist Completo de Homologação e Auditoria

* [x] Todos os logs de wrappers (action, reward, observation, logging) salvos em cada run.
* [x] Todos os tipos de ação semântica (“buy”, “hold”, “sell”, “close”) presentes nos logs.
* [x] Episódios terminando por terminated e truncated testados.
* [x] Erros de logging/serialização auditados nos logs.
* [x] Teste de integração (`test_pipeline_returns_all_cases.py`) passa sem warnings/críticos.
* [x] Integração multi-modelo e multi-env documentada e testada.
* [x] Limitações e edge cases documentados e checados.
* [x] Parâmetros, exemplos e paths rastreáveis em todos pipelines.
* [x] Políticas de log\_dir, versionamento e debug formalizadas.

---

## 7. Tabela-Resumo: Onde Encontrar Logs/Métricas/Artifacts

| Pipeline       | Tipo de Log         | Extensão   | Pasta Exemplo        |
| -------------- | ------------------- | ---------- | -------------------- |
| train          | action/reward/obs   | .csv/.json | logs/train/exp01/    |
| trade          | action/reward/obs   | .csv/.json | logs/trade/run42/    |
| evaluate       | action/reward/obs   | .csv/.json | logs/eval/modelA/    |
| tune           | tuning/result/score | .csv/.json | logs/tune/grid/      |
| supervisionado | feature/target      | .csv/.json | logs/sup+rl/expA/    |
| multi-env      | tudo separado       | .csv/.json | logs/multi/env\_{i}/ |

---

## 8. Referências, Expansão e Governança

* **Deve ser referenciada no README, DEVELOP\_TABLE, DEV\_LOG, e scripts de orquestração**.
* **Expansão da SPEC deve ser registrada via versionamento (ex: bloco changelog no início do .md)**.
* **Toda evolução de pipeline ou wrapper deve ser refletida nesta SPEC**.

---

**Fim da SPEC EXPANDIDA — Acoplamento Pipelines Op\_Trader**
