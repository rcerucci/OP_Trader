| Import Path                                 | Nome                 | Tipo  | Estado   | SPEC                           | Teste Unitário                 | Observação                             |
|---------------------------------------------|----------------------|-------|----------|--------------------------------|--------------------------------|----------------------------------------|
| src/env/environments/base_env.py            | BaseEnv              | class | @STABLE  | SPEC_base_env.md               | test_base_env.py               | Ambiente RL base universal             |
| src/env/environments/train_env_long.py      | TrainEnvLong         | class | @STABLE  | SPEC_train_env_long.md         | test_train_env_long.py         | Ambiente RL long-only                  |
| src/env/environments/train_env_short.py     | TrainEnvShort        | class | @STABLE  | SPEC_train_env_short.md        | test_train_env_short.py        | Ambiente RL short-only                 |
| src/env/wrappers/logging_wrapper.py         | LoggingWrapper       | class | @STABLE  | SPEC_logging_wrapper.md        | test_logging_wrapper.py        | Logging estruturado                    |
| src/env/wrappers/normalization_wrapper.py   | NormalizationWrapper | class | @STABLE  | SPEC_normalization_wrapper.md  | test_normalization_wrapper.py  | Normalização de observações/rewards    |
| src/env/wrappers/reward_wrapper.py          | RewardWrapper        | class | @STABLE  | SPEC_reward_wrapper.md         | test_reward_wrapper.py         | Transformação e logging de rewards     |
| src/env/wrappers/observation_wrapper.py     | ObservationWrapper   | class | @STABLE  | SPEC_observation_wrapper.md    | test_observation_wrapper.py    | Transformação/logging de observações   |
| src/env/env_factory.py                      | EnvFactory           | func  | @STABLE  | SPEC_env_factory.md            | test_env_factory.py            | Fábrica central de ambientes RL        |
| src/env/wrappers/action_wrapper.py          | ActionWrapper        | class | @SPEC    | SPEC_action_wrapper.md         | -                              | NÃO HOMOLOGADO NESTE CICLO             |
| src/env/registry.py                         | Registry             | class | @SPEC    | SPEC_registry.md               | -                              | NÃO HOMOLOGADO NESTE CICLO             |
| src/env/env_libs/position_manager.py        | PositionManager      | class | @STABLE  | SPEC_position_manager.md       | test_position_manager.py        |                                         |
| src/env/env_libs/risk_manager.py            | RiskManager          | class | @STABLE  | SPEC_risk_manager.md           | test_risk_manager.py            |                                         |
| src/env/env_libs/reward_aggregator.py       | RewardAggregator     | class | @STABLE  | SPEC_reward_aggregator.md      | test_reward_aggregator.py        |                                         |
| src/env/env_libs/observation_builder.py     | ObservationBuilder   | class | @STABLE  | SPEC_observation_builder.md    | test_observation_builder.py      |                                         |
| src/env/env_libs/trade_logger.py            | TradeLogger          | class | @STABLE  | SPEC_trade_logger.md           | test_trade_logger.py            |                                         |
| src/env/env_libs/validators.py              | Validators           | class | @STABLE  | SPEC_validators.md             | test_validators.py               |                                         |
| src/env/README_env.md                       | README_env           | doc   | @SPEC    | -                              | -                              | Documentação, não precisa homologação   |
