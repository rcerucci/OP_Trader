# README — Pipeline de Ambientes RL (src/env/)

---

## 1. Visão Geral

O diretório `src/env/` centraliza **todo o pipeline de ambientes de Reinforcement Learning** do Op\_Trader, fornecendo arquitetura modular, plugável, auditável e profissional para **treinamento, simulação, validação, auditoria e produção de agentes de trading**. Todos os módulos são pensados para máxima flexibilidade: PPO, MLP, multiativo, multiwrapper, multi-stratégia e auditoria total — sempre prontos para rastreabilidade e integração CI/CD.

* **Ambientes RL (environments/):** contratos principais, separando long/short/base.
* **Libs centrais (env\_libs/):** managers, builders, loggers e validadores plugáveis e auditáveis.
* **Wrappers (wrappers/):** instrumentação plugável para logging, reward, normalização, observação e ação.
* **Orquestração:** factory e registry para criação dinâmica, injeção de dependências, integração multi-pipeline.

> Todos os módulos, classes e funções seguem os padrões e templates oficiais do Op\_Trader (SPEC\_TEMPLATE.md, CONTRIBUTING.md, DEVELOPMENT\_FLOW\.md). Código, documentação e testes são rastreados nas meta-tabelas do projeto.

---

## 2. Estrutura Detalhada do Diretório

```text
src/env/
├── environments/
│   ├── base_env.py             # Contrato RL Gymnasium: step, reset, log
│   ├── train_env_long.py       # Ambiente RL para ciclos Long
│   └── train_env_short.py      # Ambiente RL para ciclos Short
│
├── env_libs/
│   ├── observation_builder.py  # Geração, validação e normalização de observações
│   ├── position_manager.py     # Gestão robusta de posição (open/close, snapshot)
│   ├── reward_aggregator.py    # Agregação, normalização e breakdown de rewards
│   ├── risk_manager.py         # Validação, sizing e limites dinâmicos de risco
│   ├── trade_logger.py         # Logging detalhado de trades e auditoria
│   ├── validators.py           # Validação robusta de entradas, schemas, permissões
│   └── __init__.py
│
├── wrappers/
│   ├── action_wrapper.py        # Tradução/validação de ações do agente
│   ├── logging_wrapper.py       # Logging estruturado, segregado por episódio/evento
│   ├── normalization_wrapper.py # Normalização plugável (VecNorm, minmax, zscore)
│   ├── observation_wrapper.py   # Customização/interceptação da observação
│   ├── reward_wrapper.py        # Interceptação/customização da reward
│   └── __init__.py
│
├── env_factory.py              # Factory de ambientes plugáveis, multi-wrapper
├── registry.py                 # Registry centralizado (envs, wrappers, libs)
└── README.md                   # Este arquivo
```

---

## 3. Guia Visual — Diagrama do Pipeline RL

```text
[EnvFactory] ──> [Ambiente RL]
      │                 │
      │       [Wrappers: Logging → Normalization → Reward → Obs → Action]
      │                 │
[RiskManager][PositionManager][RewardAggregator][ObservationBuilder][Validators][TradeLogger]
```

* **Todo ciclo (reset, step, close, save\_logs) é rastreável e auditável.**
* **Wrappers podem ser empilhados dinamicamente conforme configuração e tuning.**
* **Todos os componentes expõem métodos de snapshot/salvamento e logging granular.**

---

## 4. Exemplos de Uso Profissional e Casos de Uso Ilustrados

### 4.1. Criação via Factory + Wrappers Plugáveis

```python
from src.env.env_factory import EnvFactory
from src.env.environments.train_env_long import TrainEnvLong
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.wrappers.normalization_wrapper import NormalizationWrapper
from src.env.env_libs.risk_manager import RiskManager
from src.env.env_libs.position_manager import PositionManager
from src.env.env_libs.reward_aggregator import RewardAggregator
from src.utils.logging_utils import get_logger

logger = get_logger("PipelineExample", debug=True)
factory = EnvFactory(logger=logger)

# Registro dos ambientes/wrappers/componentes
factory.register_env("train_env_long", TrainEnvLong)
factory.register_wrapper("logging", LoggingWrapper)
factory.register_wrapper("normalization", NormalizationWrapper)

risk_manager = RiskManager(logger=logger)
position_manager = PositionManager(symbol="EURUSD", risk_manager=risk_manager, logger=logger)
reward_aggregator = RewardAggregator(logger=logger)

env = factory.create_env(
    env_type="train_env_long",
    wrappers=["logging", "normalization"],
    components={
        "risk_manager": risk_manager,
        "position_manager": position_manager,
        "reward_aggregator": reward_aggregator
    },
    config_overrides={"debug": True}
)

obs, info = env.reset()
done = False
while not done:
    action = ... # lógica do agente PPO
    obs, reward, done, truncated, info = env.step(action)
env.save_logs()  # Salva logs detalhados de episódios
```

### 4.2. Debugging e Logging Avançado (Multiwrapper + Diagnóstico)

```python
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.wrappers.reward_wrapper import RewardWrapper
from src.env.environments.train_env_short import TrainEnvShort

env = TrainEnvShort(debug=True)
env = LoggingWrapper(env, log_level="DEBUG", log_dir="logs/debug/")
env = RewardWrapper(env, reward_fn=lambda r: max(min(r, 10.0), -10.0), logger=None)

obs, info = env.reset()
for step in range(10):
    action = ... # lógica customizada
    obs, reward, done, truncated, info = env.step(action)
    if reward < -8.0:
        env.log_event("drawdown_warning", {"reward": reward, "step": step})
env.save_logs()
```

### 4.3. Encadeamento Manual e Edge Cases (Fallback Seguro)

```python
from src.env.wrappers.normalization_wrapper import NormalizationWrapper
from src.env.environments.base_env import BaseEnv

env = BaseEnv(...)  # Ambiente customizado
env = NormalizationWrapper(env, norm_type="z_score", debug=True)

try:
    obs, info = env.reset()
    # ciclo RL...
except Exception as e:
    print(f"Erro ao resetar/step: {e}")
    # Todos os erros críticos são logados pelo wrapper e nunca quebram o pipeline
```

### 4.4. Integração Multi-Estratégia/Ativo

```python
from src.env.env_factory import EnvFactory
from src.env.environments.train_env_long import TrainEnvLong
from src.env.environments.train_env_short import TrainEnvShort

factory = EnvFactory()
factory.register_env("train_env_long", TrainEnvLong)
factory.register_env("train_env_short", TrainEnvShort)

env_long = factory.create_env("train_env_long", wrappers=["logging", "normalization"], config_overrides={"symbol": "EURUSD"})
env_short = factory.create_env("train_env_short", wrappers=["logging"], config_overrides={"symbol": "GBPUSD"})
```

---

## 5. Troubleshooting, Diagnóstico e Auditoria

* **Falha ao salvar log/auditoria:** verifique permissões, path relativo/absoluto, espaço em disco.
* **Erro de integração entre wrappers:** todos wrappers e componentes devem ser registrados antes de criar o ambiente.
* **Edge cases críticos:** DummyEnv, reward NaN, normalização fora de padrão, erros de logging, snapshot ausente.
* **Logs detalhados:** utilize o parâmetro `log_dir` por execução e sempre ative `debug=True` para rastreio total.
* **Auditoria:** utilize `save_logs`, `save_snapshot`, métodos dos managers, e sempre registre logs por episódio.

---

## 6. Referências, Rastreabilidade e Especificações

* **Todos os módulos e integrações estão rastreados nas tabelas meta oficiais:**

  * [REFERENCE\_TABLE.md](../../docs/meta/REFERENCE_TABLE.md)
  * [TAGS\_INDEX.md](../../docs/meta/TAGS_INDEX.md)
* **Todos os SPECs técnicos ficam em:** `OP_Trader/docs/specs/` (versão oficial de rastreamento e auditoria)
* **Lista dos SPECs principais (ambientes, managers, wrappers, utilitários):**

  * [SPEC\_envioriments.md](../../docs/specs/SPEC_envioriments.md)
  * [SPEC\_base\_env.md](../../docs/specs/SPEC_base_env.md)
  * [SPEC\_train\_env\_long.md](../../docs/specs/SPEC_train_env_long.md)
  * [SPEC\_train\_env\_short.md](../../docs/specs/SPEC_train_env_short.md)
  * [SPEC\_logging\_wrapper.md](../../docs/specs/SPEC_logging_wrapper.md)
  * [SPEC\_normalization\_wrapper.md](../../docs/specs/SPEC_normalization_wrapper.md)
  * [SPEC\_position\_manager.md](../../docs/specs/SPEC_position_manager.md)
  * [SPEC\_risk\_manager.md](../../docs/specs/SPEC_risk_manager.md)
  * [SPEC\_reward\_aggregator.md](../../docs/specs/SPEC_reward_aggregator.md)
  * [SPEC\_observation\_builder.md](../../docs/specs/SPEC_observation_builder.md)
  * [SPEC\_validators.md](../../docs/specs/SPEC_validators.md)
  * [SPEC\_registry.md](../../docs/specs/SPEC_registry.md)
  * [SPEC\_env\_factory.md](../../docs/specs/SPEC_env_factory.md)
  * [SPEC\_action\_wrapper.md](../../docs/specs/SPEC_action_wrapper.md)
  * [SPEC\_observation\_wrapper.md](../../docs/specs/SPEC_observation_wrapper.md)
  * [SPEC\_reward\_wrapper.md](../../docs/specs/SPEC_reward_wrapper.md)
  * [SPEC\_trade\_logger.md](../../docs/specs/SPEC_trade_logger.md)
  * [README.md](../../README.md)
  * [CONTRIBUTING.md](../../CONTRIBUTING.md)

> Consulte sempre os SPECs para integração avançada, edge cases, limitações, onboarding e auditoria. Toda evolução técnica, bug fix, ou extensão de pipeline exige atualização e rastreamento nesta pasta e nas meta-tabelas.

---

## 7. Checklist Profissional de Qualidade (para implementação e integração)

* [x] Usou apenas módulos/componentes @STABLE e homologados
* [x] Logging segregado, auditável, persistente por experimento
* [x] Wrappers sempre via factory (evite hardcode direto)
* [x] Auditoria, snapshot, logs salvos e rastreados
* [x] Parâmetros testados: debug, log\_dir, symbol, multiativo
* [x] Integração validada em pytest e CI/CD

---

## 8. Referência Rápida de Imports Essenciais

```python
from src.env.env_factory import EnvFactory
from src.env.environments.train_env_long import TrainEnvLong
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.env_libs.reward_aggregator import RewardAggregator
from src.env.env_libs.observation_builder import ObservationBuilder
from src.env.env_libs.position_manager import PositionManager
from src.env.env_libs.risk_manager import RiskManager
from src.env.env_libs.trade_logger import TradeLogger
from src.env.env_libs.validators import Validators
```

---

## 9. Expansão: Mini-FAQ e Recomendações Avançadas

* **Posso empilhar múltiplos wrappers customizados?** Sim, via factory ou manualmente.
* **Como faço tuning/debugging de logs em produção?** Use log\_dir diferente por execução, ative debug nos wrappers principais, confira logs de auditoria.
* **Como diagnosticar falha crítica no ciclo RL?** Todos os eventos críticos geram logs estruturados por episódio. Consulte os logs, snapshots e outputs dos managers.
* **Como plugo componentes externos (customizados)?** Registre o wrapper/componente no registry/factory antes de criar o ambiente, siga o SPEC.
* **Como garantir compliance/auditoria?** Execute testes unitários e integração (pytest), salve todos logs, snapshots e outputs em local versionado.

---

## 10. Histórico e Governança

* Toda alteração nesta documentação é rastreada em DEV\_LOG.md, DEVELOP\_TABLE.md e nas tags do projeto.
* Última atualização: 2025-06-09
* Autor responsável: Equipe Op\_Trader (ChatGPT Sênior)
* Revisores e ciclo: ver tabelas de meta-documentação.

---
