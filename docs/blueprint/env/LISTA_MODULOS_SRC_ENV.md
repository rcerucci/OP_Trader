# 🗂️ Lista de Módulos — src/env/

## 1. Ambientes RL (`environments/`)

* `base_env.py`
  *Contrato universal RL, define reset, step, interface de contexto macro.*
* `train_env_long.py`
  *Ambiente RL para PPO long (só buy/hold).*
* `train_env_short.py`
  *Ambiente RL para PPO short (só sell/hold).*

## 2. Componentes Centrais (`env_libs/`)

* `position_manager.py`
  *Gestão de posições/ordens dentro do ambiente.*
* `risk_manager.py`
  *Enforce de SL/TP, sizing, filtros de risco por trade.*
* `reward_aggregator.py`
  *Agrega/calcule rewards customizáveis.*
* `observation_builder.py`
  *Gera as features/observações entregues ao agente RL.*
* `trade_logger.py`
  *Logging estruturado de ordens, execuções, rewards e contexto macro.*
* `validators.py`
  *Valida parâmetros de entrada, integridade e permissões.*

## 3. Wrappers (`wrappers/`)

* `logging_wrapper.py`
  *Logging detalhado por step/episódio sem poluir ambiente principal.*
* `normalization_wrapper.py`
  *Normalização online de observações/rewards (VecNormalize ou similar).*
* `reward_wrapper.py` *(opcional, para arquitetura plugável)*
* `observation_wrapper.py` *(opcional)*
* `action_wrapper.py` *(opcional)*

## 4. Orquestração

* `env_factory.py`
  *Função/fábrica para criar ambientes com componentes plugáveis.*
* `registry.py` *(opcional, facilita lookup/registro dinâmico de ambientes/componentes)*

## 5. Documentação

* `README.md`
  *Documentação do pipeline src/env/.*

---

## Estrutura enxuta inicial:

```text
src/env/
├── environments/
│   ├── base_env.py
│   ├── train_env_long.py
│   └── train_env_short.py
├── env_libs/
│   ├── position_manager.py
│   ├── risk_manager.py
│   ├── reward_aggregator.py
│   ├── observation_builder.py
│   ├── trade_logger.py
│   └── validators.py
├── wrappers/
│   ├── logging_wrapper.py
│   ├── normalization_wrapper.py
│   ├── reward_wrapper.py      # opcional
│   ├── observation_wrapper.py # opcional
│   └── action_wrapper.py      # opcional
├── env_factory.py
├── registry.py                # opcional
└── README.md
```

---

## Notas

* Ambientes como backtest, simulation, paper/live trading podem ser adicionados depois.
* Essa estrutura é suficiente e escalável para iniciar e evoluir o pipeline MLP (macro) + 2 PPO (micro).
