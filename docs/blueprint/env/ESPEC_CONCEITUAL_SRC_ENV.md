# 📑 Especificações Conceituais do src/env/ — Op\_Trader

## 1. Objetivo Central

O diretório `src/env/` é o núcleo de ambientes RL/trading do Op\_Trader, especializado para pipelines hierárquicos macro/micro. Garante modularidade, segurança, rastreabilidade e integração limpa para modelos do tipo MLP (macro) + 2 PPO (micro).

---

## 2. Tipos de Ambiente e Assinaturas

### 2.1. Ambiente Base (Contrato Universal)

```python
class BaseEnv(gym.Env):
    def __init__(self, allowed_actions: list[str], context_macro: dict = None, **kwargs):
        ...
    def reset(self, *, context_macro: dict = None, seed: int = None, options: dict = None) -> tuple:
        ...
    def step(self, action) -> tuple:
        ...
    def set_context_macro(self, context_macro: dict):
        ...
    def get_logs(self) -> dict:
        ...
```

### 2.2. Ambientes Específicos

* `TrainEnvLong(BaseEnv)` — apenas ações “long”
* `TrainEnvShort(BaseEnv)` — apenas ações “short”
* (Outros ambientes podem herdar do base conforme demanda)

Assinaturas são padronizadas para receber:

* **allowed\_actions**: lista de ações permitidas \["buy", "sell", ...]
* **context\_macro**: dicionário/objeto com o contexto macro (ex: direção, regime, flags)

---

## 3. Contrato de Contexto Macro

O contexto macro deve ser passado ao ambiente:

* **Na criação:** como parâmetro obrigatório ou opcional.
* **No reset:** pode ser atualizado a cada episódio.
* **Durante o episódio:** pode ser atualizado via método `set_context_macro()` se necessário.

### Exemplo de contexto macro:

```python
context_macro = {
    "direction": "long",              # direção autorizada: "long", "short", "hold"
    "trend_strength": 0.83,            # força da tendência (ex: output do MLP)
    "regime": "breakout",             # regime de mercado: "trend", "range", "breakout"
    "timestamp": "2025-06-07T09:15:00Z"
}
```

O ambiente **nunca toma decisões macro**: apenas executa ações permitidas pelo contexto.

---

## 4. Fluxos de Logging

### 4.1. Eventos Críticos Logados

* Recepção de contexto macro e alterações
* Decisões do macro (regime/direção liberada)
* Ação micro executada (PPO long/short)
* Execução de trade (simulado/real)
* Resultado de trade (reward, SL/TP, erro)
* Qualquer exceção, anomalia ou rejeição de ação
* Parâmetros do episódio e versão dos modelos

### 4.2. Estrutura dos Logs

* **Logs segregados:** por ambiente, por data, por símbolo e por tipo de execução (treino, teste, produção)
* **Formato estruturado:** JSON, CSV ou log padrão (para integração futura com auditoria/dashboard)
* **Exemplo de registro logado:**

```json
{
  "timestamp": "2025-06-07T09:16:03Z",
  "env": "TrainEnvLong",
  "macro_decision": {"direction": "long", "trend_strength": 0.81},
  "micro_action": "buy",
  "order_result": {"price": 1.09635, "volume": 0.1, "sl": 1.09500, "tp": 1.09800},
  "reward": 2.2,
  "episode": 205,
  "model_versions": {"mlp": "v1.1.2", "ppo_long": "v2.0.0"}
}
```

* Logs críticos também incluem erros de validação, rejeições de ordem, quebras de regra de risco, etc.

---

## 5. Princípios de Modularidade, Testabilidade e Segurança

* Todos os ambientes devem ser testáveis de forma unitária e integrada (mock de contexto macro).
* Parâmetros e versões são sempre rastreados nos logs e outputs.
* Nenhuma lógica macro implementada dentro dos ambientes — apenas execução do contexto recebido.
* Plugabilidade total para position/risk/reward/logger/wrappers.

---

## 6. Estrutura Recomendada do src/env/

```
src/env/
├── environments/
│   ├── base_env.py
│   ├── train_env_long.py
│   ├── train_env_short.py
│   └── ...
├── env_libs/
│   ├── position_manager.py
│   ├── risk_manager.py
│   ├── reward_aggregator.py
│   ├── observation_builder.py
│   └── ...
├── wrappers/
│   ├── logging_wrapper.py
│   ├── normalization_wrapper.py
│   └── ...
├── env_factory.py
├── registry.py
└── README.md
```

---

## 7. Checklist de Qualidade e Rastreabilidade

* [ ] Ambientes aceitam e aplicam contexto macro corretamente
* [ ] Só executam ações autorizadas (long/short/hold conforme configuração)
* [ ] Logging crítico detalhado e segregado
* [ ] Gestão de risco plugável e centralizada
* [ ] Estrutura modular e testável
* [ ] Nenhuma decisão macro embutida no ambiente
* [ ] Pronto para expansão (novos wrappers, ambientes, componentes)
