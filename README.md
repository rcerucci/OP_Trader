# 📈 Op_Trader

Sistema modular de trading automatizado baseado em Machine Learning e Reinforcement Learning, utilizando arquitetura PPO (Proximal Policy Optimization) para posições long/short e MLP (Multi-Layer Perceptron) para decisões de entrada/saída.

## 🎯 Visão Geral

O `Op_Trader` é um sistema completo de trading que integra:

- **Coleta de dados** em tempo real via MetaTrader 5
- **Processamento e engenharia** de features
- **Treinamento** de modelos PPO (long/short) e MLP decisor
- **Ambiente de simulação** com recompensas customizáveis
- **Execução automatizada** com modos debug e live
- **Monitoramento** e auditoria com logs estruturados

### Modelos Principais
- `ppo_long`: Agente para posições de compra
- `ppo_short`: Agente para posições de venda
- `mlp_decisor`: Rede neural para decisões de entrada/saída

### Modos de Operação
- `--debug`: Simulação com logs detalhados
- `--live`: Execução real no mercado
- Integração com MetaTrader 5 para dados e ordens

## 🏗️ Estrutura do Projeto

```
op_trader/
├── audits/                   # Auditorias, evidências, relatórios
├── config/                   # Configurações por ambiente/componente
├── data/                     # Dados (raw, processed, features, external)
├── docs/                     # Documentação técnica
├── infra/                    # Infraestrutura como código (Docker, Kubernetes)
├── logs/                     # Logs estruturados (trades, evaluations, system)
├── models/                   # Modelos ML, checkpoints, artefatos
├── scripts/                  # Scripts de automação e CLI
├── src/                      # Código-fonte principal
│   ├── agents/               # Agentes RL/ML
│   ├── api/                  # APIs REST/GraphQL
│   ├── connectors/           # Integrações com brokers/APIs
│   ├── core/                 # Orquestração, event bus, métricas
│   ├── data/                 # Ingestão, ETL, transformação
│   ├── env/                  # Ambientes, execução, rewards, state
│   ├── strategies/           # Estratégias de trading
│   ├── trade/                # Execução ao vivo/simulação
│   ├── train/                # Pipelines de treinamento
│   ├── tune/                 # Tuning de hiperparâmetros
│   └── utils/                # Utilitários
├── tests/                    # Testes funcionais e de integração
├── .env.example
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── README.md
├── CONTRIBUTING.md
├── DEVELOPMENT_FLOW.md
├── REFACTORING_STEPS.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── environment.yml
├── docker-compose.yml
└── Makefile
```

## 🚀 Início Rápido

### Pré-requisitos
- **Sistema Operacional**: Windows 10/11
- **Python**: 3.10.x (obrigatório para MetaTrader 5 API)
- **Conda**: Miniconda ou Anaconda
- **MetaTrader 5**: Instalado e configurado
- **CUDA**: Opcional, para aceleração GPU
- **Docker**: Opcional, para containers

### Instalação

1. **Instale o Conda** (se necessário):
   ```bash
   # Baixe e instale o Miniconda
   # https://docs.conda.io/en/latest/miniconda.html
   ```

2. **Clone o repositório**:
   ```bash
   git clone <repository-url>
   cd op_trader
   ```

3. **Crie o ambiente**:
   ```bash
   conda env create -f environment.yml
   conda activate op_trader
   ```

4. **Verifique a instalação**:
   ```bash
   python --version  # Deve retornar Python 3.10.x
   python -c "import pandas, numpy, tensorflow, stable_baselines3; print('Dependências OK')"
   ```

5. **Configure pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Configure variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite .env com suas configurações (ex.: credenciais MT5)
   ```

## 💻 Uso Básico

```bash
# Coleta e processamento de dados
python scripts/data_pipeline.py --symbol EURUSD --timeframe M5

# Treinamento de modelos
python src/train/ppo/ppo_trainer.py --debug --symbol EURUSD --timeframe M5

# Execução em modo debug
python src/trade/trade_executor.py --debug --symbol EURUSD --timeframe M5

# Execução live (cuidado!)
python src/trade/trade_executor.py --live --symbol EURUSD --timeframe M5
```

## 📊 Logs e Monitoramento

Logs estruturados são salvos em:

- `logs/rollouts/`: Dados de treinamento e episódios
- `logs/trades/`: Resultados de trading
- `logs/evaluations/`: Métricas de performance
- `logs/system/`: Logs gerais do sistema

Exemplo de configuração de logging:

```python
from src.utils.logging_utils import get_logger
logger = get_logger(__name__, debug=True)
logger.info("Iniciando execução...")
```

## 🧪 Testes Funcionais

Os testes são funcionais, validando comportamento real, fluxos completos, estados, erros e casos extremos (Black Box Testing). Eles cobrem:

- **Fluxos principais**: Ex.: abrir/fechar posições
- **Casos de erro**: Ex.: argumentos inválidos
- **Estados limítrofes**: Ex.: divisão por zero
- **Integração**: Ex.: operações multi-mercado

### Execução de Testes

```bash
# Todos os testes
pytest tests/ -v

# Testes unitários
pytest tests/unit/ -v

# Teste específico
pytest tests/unit/test_position_manager.py::test_open_buy_position -v

# Com logs detalhados
pytest tests/ -v -s --log-cli-level=DEBUG
```

### Exemplo de Teste

```python
import pytest
import math
from src.utils.path_setup import ensure_project_root
from src.env.env_libs.execution.position_manager import PositionManager

ROOT_DIR = ensure_project_root(__file__)

@pytest.fixture
def pm():
    """Instância nova de PositionManager."""
    return PositionManager(symbol="EURUSD", price_precision=5)

def test_open_buy_position(pm):
    """Abre uma posição 'buy' e valida atributos."""
    result = pm.process_action('buy', price=1.23456, step=0, size=2.0)
    assert result['status'] == 'opened'
    assert pm.get_current_position()['is_open'] is True
    assert math.isclose(pm.get_current_position()['entry_price'], 1.23456, abs_tol=1e-5)
```

## 📚 Documentação

- **Visão Geral**: Este README
- **Contribuição**: `CONTRIBUTING.md`
- **Fluxo de Desenvolvimento**: `DEVELOPMENT_FLOW.md`
- **Documentação Técnica**: `docs/`
- **API Reference**: `docs/api_reference.md`
- **Troubleshooting**: `docs/troubleshooting.md`

## 🔧 Configuração

- **Configurações**: `config/` (arquivos por ambiente)
- **Variáveis de Ambiente**: `.env` (nunca versionado)
- **Projeto Python**: `pyproject.toml`

## 🛡️ Segurança

- Variáveis sensíveis em `.env`
- Validação de entrada em endpoints
- Logs estruturados sem dados sensíveis
- Auditoria em `audits/`
- Uso de `ensure_project_root(__file__)` para caminhos consistentes

## 📈 Status do Projeto

- ✅ Coleta de dados MT5
- 🔄 Processamento e features
- 🔄 Ambiente de simulação
- 🔄 Treinamento PPO + MLP
- 🔄 Execução automatizada
- 🔄 Monitoramento avançado
- 🔄 API REST/GraphQL
- 📋 Interface web (planejada)

## 🤝 Contribuindo

Veja `CONTRIBUTING.md` para diretrizes de código, testes funcionais e fluxo de desenvolvimento.

## 📄 Licença

Licenciado sob `LICENSE`.

## ⚠️ Aviso

**Este sistema opera com dinheiro real. Teste em modo `--debug` antes de usar `--live`. O uso é por sua conta e risco.**