# README.md — Pipeline de Ambientes RL (src/env/)

## 1. Visão Geral

Este diretório centraliza o pipeline de ambientes RL do Op\_Trader, fornecendo arquitetura modular, plugável e auditável para treinamento, simulação, validação e produção de agentes de trading com PPO, MLP e demais técnicas. Permite construção e orquestração de ambientes multi-ativo, multi-stratégia e totalmente customizáveis.

## 2. Estrutura de Diretórios

```
src/env/
├── environments/           # Ambientes RL específicos (long, short, base, etc.)
├── env_libs/               # Componentes centrais (position, risk, reward, obs, logger, validator)
├── wrappers/               # Wrappers plugáveis (logging, normalization, reward, obs, action, etc.)
├── env_factory.py          # Factory de ambientes plugáveis e configuráveis
├── registry.py             # Registro dinâmico de ambientes/wrappers/componentes
└── README.md               # Este arquivo
```

## 3. Componentes Principais

### Ambientes RL

* `BaseEnv`, `TrainEnvLong`, `TrainEnvShort`: contratos principais para ciclos RL de compra/venda.

### Componentes (env\_libs/)

* `PositionManager`, `RiskManager`, `RewardAggregator`, `ObservationBuilder`, `TradeLogger`, `Validators`

### Wrappers (wrappers/)

* `LoggingWrapper`, `NormalizationWrapper`, `RewardWrapper`, `ObservationWrapper`, `ActionWrapper`

### Orquestração

* `env_factory.py`, `registry.py`: criação e lookup plugáveis, injeção de dependências, integração total.

## 4. Exemplos de Uso

### 4.1 Criação de ambiente com factory e wrappers

```python
from src.env.env_factory import EnvFactory
from src.env.wrappers.logging_wrapper import LoggingWrapper
from src.env.environments.train_env_long import TrainEnvLong
from src.env.env_libs.risk_manager import RiskManager
from src.utils.logging_utils import get_logger

logger = get_logger("EnvPipeline", debug=True)
factory = EnvFactory(config_path="config/environments/training.yaml", logger=logger)
factory.register_env("train_env_long", TrainEnvLong)
factory.register_wrapper("logging", LoggingWrapper)
factory.register_wrapper("normalization", NormalizationWrapper)

risk = RiskManager(config_path="config/environments/training.yaml", logger=logger)

env = factory.create_env(
    env_type="train_env_long",
    wrappers=["logging", "normalization"],
    components={"risk_manager": risk},
    config_overrides={"debug": True}
)
```

### 4.2 Encadeando wrappers manualmente

```python
from src.env.wrappers.reward_wrapper import RewardWrapper
from src.env.wrappers.observation_wrapper import ObservationWrapper

def clip_reward(r):
    return max(min(r, 5.0), -5.0)

def mask_obs(obs):
    obs["price"] = 0.0
    return obs

env = RewardWrapper(env, reward_fn=clip_reward, logger=logger)
env = ObservationWrapper(env, obs_fn=mask_obs, logger=logger)
```

## 5. Links Cruzados e Rastreabilidade

* Especificações detalhadas (SPEC\_xxx.md) de todos módulos em `docs/specs/`.
* Referência oficial de utilitários e contratos: \[REFERENCE\_TABLE.md], \[DEVELOP\_TABLE\_SRC\_ENV.md], \[DEV\_LOG.md]

## 6. Boas Práticas e Dicas

* Sempre utilize factory e registry para instanciar ambientes — evita hardcode e facilita manutenção/testes.
* Para tuning/testes rápidos, altere wrappers e componentes via parâmetros do factory.
* Logging detalhado pode ser ajustado ("DEBUG", "INFO", "AUDIT") conforme necessidade do experimento ou produção.
* Utilize o `save_logs`, `save_snapshot` e funções análogas para auditoria e rastreabilidade de execuções.
* Consulte sempre os SPECs para integrações customizadas e edge cases.

## 7. Licença

Este pipeline segue as normas internas do projeto Op\_Trader.

---

> Dúvidas, melhorias ou sugestões? Consulte as especificações oficiais ou abra uma issue/documentação no repositório do projeto.
