# CONTRIBUTING.md — Diretrizes de Desenvolvimento

Este guia define os padrões para o desenvolvimento do projeto `op_trader`, garantindo consistência, qualidade e escalabilidade nas contribuições. Ele cobre codificação, organização, testes, automação e logging para todas as funções que interagem com o código.

---

## 📁 Estrutura de Diretórios

A estrutura de diretórios do projeto é organizada para separar código, dados, modelos e logs:

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

---

## 🔧 Configuração do Ambiente

### Requisitos do Sistema
- **Sistema Operacional**: Windows 10/11
- **Python**: 3.10.x (obrigatório para MetaTrader 5 API)
- **Conda**: Miniconda ou Anaconda
- **MetaTrader 5**: Instalado e configurado
- **CUDA**: Opcional, para aceleração GPU
- **Docker**: Opcional, para containers
- **IDE Recomendada**: VSCode ou Spyder

### Configuração Passo a Passo

1. **Instale o Conda** (se não tiver):
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
   python --version     # Deve retornar Python 3.10.x
   python -c "import pandas, numpy, tensorflow; print('Dependências OK')"
   ```

5. **Configure o IDE**:
   ```bash
   # Instale e configure seu editor favorito (VSCode recomendado para debugging Python)
   ```

6. **Configure variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite .env com suas configurações (ex.: credenciais MT5)

### Solução de Problemas Comuns

| Problema | Solução |
|----------|---------|
| **Erro de dependências** | `conda clean -a && conda env create -f environment.yml --force` |
| **Python não encontrado** | Verificar se o ambiente está ativado: `conda activate op_trader` |
| **Import errors** | `pip install -r requirements.txt` |

---

## 📝 Padrões de Codificação

### 1. Importações Absolutas

**Obrigatório**: Todo script em `src/` deve usar importações absolutas com path patching:

```python
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
root_dir = Path(__file__).resolve().parents[2]  # Ajuste conforme localização
sys.path.append(str(root_dir))

# Importações absolutas
from src.utils.logging_utils import get_logger
from src.env.trading_env import TradingEnvironment
```

### 2. Estrutura de Script Padrão

```python
#!/usr/bin/env python3
"""
Descrição do módulo.

Este módulo faz X, Y e Z.
Autor: Developers Team
Data: YYYY-MM-DD
"""

import sys
from pathlib import Path
import argparse

# Path setup
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

# Imports
from src.utils.logging_utils import get_logger

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Descrição do script")
    parser.add_argument("--debug", action="store_true", 
                       help="Ativa modo debug com logs detalhados")
    args = parser.parse_args()
    
    logger = get_logger(__name__, debug=args.debug)
    logger.info("Iniciando script...")
    
    try:
        # Lógica principal aqui
        pass
    except Exception as e:
        logger.error(f"Erro na execução: {e}")
        if args.debug:
            logger.exception("Stacktrace completo:")
        return 1
    
    logger.info("Script finalizado com sucesso.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 3. Estilo de Código

- **Siga PEP 8** rigorosamente
- **Use type hints**:
  ```python
  def process_data(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
  ```
- **Docstrings no formato Google**:
  ```python
  def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
      """Calcula o RSI (Relative Strength Index).

      Args:
          prices (pd.Series): Série de preços de fechamento.
          period (int, optional): Período para cálculo. Defaults to 14.

      Returns:
          pd.Series: Valores do RSI.

      Raises:
          ValueError: Se o período for menor que 1.
      """
  ```

### 4. Convenções de Nomenclatura

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| **Variáveis** | snake_case | `market_data`, `rsi_values` |
| **Funções** | snake_case | `calculate_indicators()` |
| **Classes** | PascalCase | `TradingEnvironment` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_POSITIONS`, `DEFAULT_TIMEFRAME` |
| **Arquivos** | snake_case | `data_collector.py` |
| **Diretórios** | snake_case | `env_libs`, `reward_components` |

---

## 🚀 Execução de Scripts

### 1. Flag --debug Obrigatória

Todos os scripts executáveis devem implementar:

```python
parser = argparse.ArgumentParser(description="Descrição do script")
parser.add_argument("--debug", action="store_true", 
                   help="Ativa modo debug com logs detalhados")
parser.add_argument("--symbol", type=str, default="EURUSD",
                   help="Símbolo para processar")
parser.add_argument("--timeframe", type=str, default="M5",
                   help="Timeframe dos dados")
args = parser.parse_args()
```

### 2. Comportamento por Modo

#### Modo Normal (sem --debug):
- Logs nível `INFO`
- Erros tratados com `logger.error`
- Execução não interrompida por erros não-críticos
- Saída limpa e profissional

#### Modo Debug (com --debug):
- Logs nível `DEBUG`
- Stacktraces completos com `logger.exception`
- Arquivos extras salvos (métricas detalhadas, logs brutos)
- Informações detalhadas de performance

# Execução em modo debug
python src/trade/trade_executor.py --debug --symbol EURUSD --timeframe M5

# Execução em modo live (atenção!)
python src/trade/trade_executor.py --live --symbol EURUSD --timeframe M5

Todos os scripts executáveis devem implementar pelo menos:
- `--debug`: Ativa modo de logs detalhados.
- `--live`: Executa no modo operacional real (atenção, risco financeiro real).
- `--symbol`, `--timeframe`, etc.

### 3. Exemplos de Execução

```bash
# Modo normal
python src/data/data_collector.py --symbol EURUSD --timeframe M5

# Modo debug
python src/train/ppo/ppo_trainer.py --debug --symbol GBPUSD

# Com múltiplos parâmetros
python src/trade/backtest_runner.py --debug --start-date 2024-01-01 --end-date 2024-12-31
```

---

## 📊 Sistema de Logging

### 1. Configuração Padrão

Use sempre o logger configurado em `src/utils/logger_template.py`:

```python
from src.utils.logging_utils import get_logger

# No início da função main()
logger = get_logger(__name__, debug=args.debug)
```

### 2. Níveis de Log e Cores

| Nível | Cor | Uso | Exemplo |
|-------|-----|-----|---------|
| **DEBUG** | Cyan | Detalhes técnicos | `logger.debug(f"Processando {len(data)} registros")` |
| **INFO** | Green | Informações gerais | `logger.info("Modelo treinado com sucesso")` |
| **WARNING** | Yellow | Alertas não-críticos | `logger.warning("Dados incompletos para período")` |
| **ERROR** | Red | Erros recuperáveis | `logger.error("Falha na conexão, tentando novamente")` |
| **CRITICAL** | Bold Red | Erros fatais | `logger.critical("Sistema não pode continuar")` |

### 3. Integração com tqdm

Para loops com barra de progresso:

```python
from tqdm import tqdm

for i in tqdm(range(1000), desc="Processando dados"):
    # Sua lógica aqui
    
    # Para logs durante o loop, use tqdm.write()
    if i % 100 == 0:
        tqdm.write(f"Checkpoint: {i}/1000 processados")
```

### 4. Logging em Classes

```python
class DataProcessor:
    def __init__(self, debug: bool = False):
        self.logger = get_logger(self.__class__.__name__, debug=debug)
    
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        self.logger.info(f"Processando {len(data)} registros")
        # ... lógica ...
        self.logger.debug(f"Memória utilizada: {data.memory_usage().sum()} bytes")
        return processed_data
```

---
## 🧪 Testes de Funcionalidade

### 1. Estrutura de Testes

```
tests/
├── unit/                    # Testes de funcionalidade por módulo
│   ├── test_data_processor.py
│   ├── test_trading_env.py
│   └── test_rewards.py
├── integration/             # Testes de funcionalidade integrada
│   ├── test_ppo_training.py
│   └── test_full_pipeline.py
├── fixtures/                # Dados de teste
│   ├── sample_data.csv
│   └── mock_responses.json
├── logs/                    # Logs gerados pelos testes
│   ├── test_logs.log
│   └── test_results/
└── conftest.py             # Configurações pytest
```

### 2. Padrões de Teste Funcional

```python
import pytest
import pandas as pd
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import logging

from src.data.data_processor import DataProcessor

class TestDataProcessor:
    
    @pytest.fixture
    def temp_logs_dir(self):
        """Cria diretório temporário para logs de teste."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logs_dir = os.path.join(temp_dir, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            yield logs_dir
    
    @pytest.fixture
    def sample_market_data(self):
        """Dados de mercado reais para testes."""
        return pd.DataFrame({
            'datetime': pd.date_range('2024-01-01', periods=1000, freq='5min'),
            'open': [1.1000 + i*0.0001 for i in range(1000)],
            'high': [1.1015 + i*0.0001 for i in range(1000)],
            'low': [0.9995 + i*0.0001 for i in range(1000)],
            'close': [1.1010 + i*0.0001 for i in range(1000)],
            'volume': [1000 + i*10 for i in range(1000)]
        })
    
    def test_complete_data_processing_functionality(self, sample_market_data, temp_logs_dir):
        """Testa funcionalidade completa do processamento de dados."""
        # Configurar processor com logging real
        processor = DataProcessor(
            symbol="EURUSD", 
            timeframe="M5",
            debug=True,
            logs_dir=temp_logs_dir
        )
        
        # Testar processamento completo
        result = processor.process(sample_market_data)
        
        # Verificar funcionalidades básicas
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_market_data)
        
        # Verificar cálculos de indicadores técnicos
        assert 'rsi' in result.columns
        assert 'sma_20' in result.columns
        assert 'ema_12' in result.columns
        
        # Verificar valores dos cálculos
        assert result['rsi'].min() >= 0
        assert result['rsi'].max() <= 100
        assert not result['sma_20'].isna().all()
        
        # Verificar logs foram criados
        log_files = list(Path(temp_logs_dir).glob("*.log"))
        assert len(log_files) > 0
        
        # Verificar conteúdo dos logs
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert "Processando 1000 registros" in log_content
            assert "Calculando indicadores técnicos" in log_content
            assert "Processamento concluído" in log_content
    
    def test_error_handling_and_logging(self, temp_logs_dir):
        """Testa tratamento de erros e logging de exceções."""
        processor = DataProcessor(
            symbol="INVALID", 
            timeframe="M5",
            debug=True,
            logs_dir=temp_logs_dir
        )
        
        # Testar dados vazios
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Dados vazios não podem ser processados"):
            processor.process(empty_df)
        
        # Verificar erro foi logado
        log_files = list(Path(temp_logs_dir).glob("*.log"))
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert "ERROR" in log_content
            assert "Dados vazios não podem ser processados" in log_content
    
    def test_debug_mode_functionality(self, sample_market_data, temp_logs_dir):
        """Testa funcionalidade específica do modo debug."""
        # Modo debug ativado
        processor_debug = DataProcessor(
            symbol="EURUSD", 
            timeframe="M5",
            debug=True,
            logs_dir=temp_logs_dir
        )
        
        result_debug = processor_debug.process(sample_market_data)
        
        # Verificar arquivos extras salvos em modo debug
        debug_files = list(Path(temp_logs_dir).glob("*debug*"))
        assert len(debug_files) > 0
        
        # Verificar logs detalhados
        log_files = list(Path(temp_logs_dir).glob("*.log"))
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert "DEBUG" in log_content
            assert "Memória utilizada:" in log_content
            assert "Performance metrics:" in log_content
    
    def test_file_saving_functionality(self, sample_market_data, temp_logs_dir):
        """Testa funcionalidade de salvamento de arquivos."""
        processor = DataProcessor(
            symbol="EURUSD", 
            timeframe="M5",
            output_dir=temp_logs_dir
        )
        
        result = processor.process_and_save(sample_market_data)
        
        # Verificar arquivo foi salvo
        saved_files = list(Path(temp_logs_dir).glob("*processed*.csv"))
        assert len(saved_files) == 1
        
        # Verificar conteúdo do arquivo salvo
        saved_data = pd.read_csv(saved_files[0])
        assert len(saved_data) == len(result)
        assert list(saved_data.columns) == list(result.columns)
        
        # Verificar nomenclatura do arquivo
        filename = saved_files[0].name
        assert "EURUSD" in filename
        assert "M5" in filename
        assert "processed" in filename
    
    def test_calculation_accuracy(self, sample_market_data):
        """Testa precisão dos cálculos matemáticos."""
        processor = DataProcessor()
        result = processor.process(sample_market_data)
        
        # Testar cálculo do RSI manualmente
        price_changes = sample_market_data['close'].diff()
        gains = price_changes.where(price_changes > 0, 0)
        losses = -price_changes.where(price_changes < 0, 0)
        
        avg_gain = gains.rolling(window=14).mean()
        avg_loss = losses.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        expected_rsi = 100 - (100 / (1 + rs))
        
        # Comparar com resultado do processor (tolerância para arredondamento)
        pd.testing.assert_series_equal(
            result['rsi'].dropna(), 
            expected_rsi.dropna(), 
            check_names=False,
            rtol=1e-3
        )
```

### 3. Testes de Sistema Completo

```python
class TestTradingEnvironment:
    
    def test_complete_trading_simulation(self, sample_market_data, temp_logs_dir):
        """Testa simulação completa de trading."""
        from src.env.trading_env import TradingEnvironment
        
        env = TradingEnvironment(
            data=sample_market_data,
            symbol="EURUSD",
            initial_balance=10000,
            debug=True,
            logs_dir=temp_logs_dir
        )
        
        # Simular episódio completo
        state = env.reset()
        total_reward = 0
        actions_taken = []
        
        for step in range(100):
            # Ação aleatória para teste
            action = env.action_space.sample()
            actions_taken.append(action)
            
            state, reward, done, info = env.step(action)
            total_reward += reward
            
            if done:
                break
        
        # Verificar funcionalidades
        assert len(actions_taken) > 0
        assert isinstance(total_reward, (int, float))
        assert env.current_balance != env.initial_balance  # Alguma atividade ocorreu
        
        # Verificar logs de trades
        trade_logs = list(Path(temp_logs_dir).glob("*trades*.csv"))
        assert len(trade_logs) > 0
        
        trades_df = pd.read_csv(trade_logs[0])
        assert 'action' in trades_df.columns
        assert 'reward' in trades_df.columns
        assert 'balance' in trades_df.columns
    
    def test_reward_calculation_functionality(self, sample_market_data):
        """Testa funcionalidade de cálculo de recompensas."""
        from src.env.rewards import RewardCalculator
        
        calculator = RewardCalculator(risk_penalty=0.1, drawdown_penalty=0.2)
        
        # Simular trade
        entry_price = 1.1000
        exit_price = 1.1020
        position_size = 1.0
        trade_duration = 10
        
        reward = calculator.calculate_trade_reward(
            entry_price=entry_price,
            exit_price=exit_price,
            position_size=position_size,
            trade_duration=trade_duration,
            action_type="buy"
        )
        
        # Verificar cálculo
        expected_profit = (exit_price - entry_price) * position_size
        assert reward > 0  # Trade lucrativo
        assert isinstance(reward, (int, float))
        
        # Testar trade perdedor
        losing_reward = calculator.calculate_trade_reward(
            entry_price=entry_price,
            exit_price=1.0980,  # Preço menor
            position_size=position_size,
            trade_duration=trade_duration,
            action_type="buy"
        )
        
        assert losing_reward < 0  # Trade com perda
```

### 4. Testes de Integração com APIs

```python
class TestDataCollection:
    
    @patch('src.connectors.mt5_connector.MetaTrader5')
    def test_real_data_collection_simulation(self, mock_mt5, temp_logs_dir):
        """Testa coleta de dados simulando conexão real."""
        from src.data.data_collector import DataCollector
        
        # Mock da resposta do MT5
        mock_data = pd.DataFrame({
            'time': [1640995200 + i*300 for i in range(100)],  # timestamps
            'open': [1.1000 + i*0.0001 for i in range(100)],
            'high': [1.1015 + i*0.0001 for i in range(100)],
            'low': [0.9995 + i*0.0001 for i in range(100)],
            'close': [1.1010 + i*0.0001 for i in range(100)],
            'volume': [1000 + i*10 for i in range(100)]
        })
        mock_mt5.copy_rates_range.return_value = mock_data.to_records(index=False)
        
        collector = DataCollector(
            symbol="EURUSD",
            timeframe="M5",
            debug=True,
            logs_dir=temp_logs_dir
        )
        
        # Testar coleta
        data = collector.collect_data(
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        
        # Verificar funcionalidade
        assert len(data) == 100
        assert 'datetime' in data.columns
        assert data['datetime'].dtype == 'datetime64[ns]'
        
        # Verificar logs de conexão
        log_files = list(Path(temp_logs_dir).glob("*.log"))
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert "Conectando ao MT5" in log_content
            assert "Coletando dados para EURUSD" in log_content
            assert "Coleta finalizada: 100 registros" in log_content
```






### 5. Execução e Validação de Testes

```bash
# Executar todos os testes de funcionalidade
pytest tests/ -v --tb=short

# Testes com logs detalhados (debug)
pytest tests/ -v -s --log-cli-level=DEBUG

# Testar funcionalidade específica
pytest tests/unit/test_data_processor.py::TestDataProcessor::test_complete_data_processing_functionality -v -s

# Validar que logs foram criados
pytest tests/ -v --capture=no

# Executar testes de integração (mais demorados)
pytest tests/integration/ -v --timeout=300
```

### 6. Requisitos de Funcionalidade

#### Testes Obrigatórios para Cada Módulo:

- **Funcionalidade Principal**: Testar o propósito principal do módulo
- **Cálculos Matemáticos**: Validar precisão de fórmulas e algoritmos  
- **Tratamento de Erros**: Simular cenários de erro e verificar handling
- **Logging Real**: Verificar se logs são salvos nos locais corretos
- **Modo Debug**: Testar funcionalidades extras do modo debug
- **Salvamento de Arquivos**: Verificar nomenclatura e conteúdo de arquivos reais
- **Performance**: Medir tempo de execução para operações críticas
- **Integração**: Testar interação com outros módulos

#### Critérios de Aprovação:

- **100% dos testes passando**: Sem exceções
- **Logs gerados**: Todos os testes devem produzir logs reais
- **Arquivos salvos**: Verificar criação correta de arquivos reais de saída
- **Cálculos validados**: Resultados matemáticos conferidos manualmente
- **Erros tratados**: Todos os cenários de erro testados
- **Performance aceitável**: Tempo de execução dentro dos limites

### 7. Debugging de Testes

```python
# Exemplo de teste com debugging avançado
def test_with_detailed_debugging(self, sample_data, temp_logs_dir):
    """Teste com debugging detalhado para investigação."""
    
    # Configurar logging do teste
    test_logger = logging.getLogger('test_debug')
    handler = logging.FileHandler(os.path.join(temp_logs_dir, 'test_debug.log'))
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.DEBUG)
    
    processor = DataProcessor(debug=True)
    
    # Log estado inicial
    test_logger.debug(f"Dados iniciais: {len(sample_data)} registros")
    test_logger.debug(f"Colunas: {list(sample_data.columns)}")
    
    # Executar com monitoramento
    import time
    start_time = time.time()
    
    result = processor.process(sample_data)
    
    end_time = time.time()
    test_logger.debug(f"Processamento levou {end_time - start_time:.2f} segundos")
    
    # Validações com logs detalhados
    for col in ['rsi', 'sma_20', 'ema_12']:
        if col in result.columns:
            null_count = result[col].isnull().sum()
            test_logger.debug(f"{col}: {null_count} valores nulos de {len(result)}")
            assert null_count < len(result) * 0.5, f"Muitos valores nulos em {col}"
```
---

---

## 📄 Documentação Técnica e Templates

Toda documentação técnica de novos módulos deve obrigatoriamente ser criada a partir do template oficial disponível em:

- Especificação de módulos: [`docs/templates/SPEC_TEMPLATE.md`](docs/templates/SPEC_TEMPLATE.md)
- Template de testes de integração: [`docs/templates/INTEGRATION_TEST_TEMPLATE.md`](docs/templates/INTEGRATION_TEST_TEMPLATE.md)

> Ao criar ou atualizar um módulo, gere a especificação técnica correspondente em `docs/specs/`, conforme o fluxo detalhado em `docs/flows/DEVELOPMENT_FLOW.md` e `docs/flows/REFACTORING_STEPS.md`.

## 💾 Salvamento de Arquivos

### 1. Padrão de Nomenclatura

**Formato geral**:
```
<categoria>/<subcategoria>/<prefixo>_<ativo>_<timeframe>_<tipo>_<período>_<timestamp>.<extensão>
```

**Exemplos**:
```
# Dados
data/processed/features_EURUSD_M5_processed_2020-01-01-2025-05-31_20250531_143022.csv

# Modelos
models/buy/ppo_EURUSD_M5_long_20250531_143022/
├── model.zip
├── scaler.pkl
├── config.json
└── training_log.csv

# Logs
logs/trades/trades_EURUSD_M5_live_20250531.csv
logs/evaluations/backtest_EURUSD_M5_2024-01-01-2024-12-31_20250531_143022.csv
```

### 2. Utilitário de Salvamento

```python
from src.utils.file_saver import (
    get_timestamp, 
    build_filename, 
    save_dataframe,
    create_model_directory
)

# Exemplo de uso
timestamp = get_timestamp()

# Para DataFrames
filename = build_filename(
    prefix="data/processed",
    suffix="features",
    asset="EURUSD",
    timeframe="M5",
    period="2024-01-01_2024-12-31",
    timestamp=timestamp,
    extension="csv"
)
save_dataframe(df, filename)

# Para modelos
model_dir = create_model_directory(
    category="buy",  # buy, sell, both
    model_type="ppo",
    asset="EURUSD",
    timeframe="M5",
    timestamp=timestamp
)
```

### 3. Estrutura de Lotes (.zip)

Quando enviar múltiplos arquivos:

```
modelo_completo_EURUSD_M5_20250531_143022.zip
├── README.md                    # Instruções de uso
├── models/
│   ├── ppo_long.zip
│   ├── ppo_short.zip
│   └── mlp_decisor.pkl
├── data/
│   ├── training_data.csv
│   └── validation_data.csv
├── config/
│   └── model_config.json
└── logs/
    └── training_metrics.csv
```

**Conteúdo do README.md no .zip**:
```markdown
# Modelo Op_Trader - EURUSD M5

## Arquivos Incluídos
- `models/`: Modelos treinados (PPO Long/Short + MLP)
- `data/`: Dados de treinamento e validação
- `config/`: Configurações utilizadas
- `logs/`: Métricas de treinamento

## Como Usar
1. Extrair arquivos na pasta `op_trader/models/`
2. Executar: `python src/trade/load_model.py --model-dir models/buy/ppo_EURUSD_M5_20250531_143022`

## Métricas de Performance
- Sharpe Ratio: 1.85
- Max Drawdown: 3.2%
- Win Rate: 67.3%
```

---

## 🤖 Machine Learning e Dados

### 1. Gestão de Datasets

```python
# Estrutura padrão para datasets
class DatasetManager:
    def __init__(self, symbol: str, timeframe: str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = get_logger(self.__class__.__name__)
    
    def load_raw_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Carrega dados brutos."""
        filename = f"data/raw/{self.symbol}_{self.timeframe}_raw_{start_date}_{end_date}.csv"
        self.logger.info(f"Carregando dados de {filename}")
        return pd.read_csv(filename)
    
    def save_processed_data(self, data: pd.DataFrame, suffix: str = "processed") -> str:
        """Salva dados processados."""
        timestamp = get_timestamp()
        filename = build_filename(
            prefix="data/processed",
            suffix=suffix,
            asset=self.symbol,
            timeframe=self.timeframe,
            timestamp=timestamp,
            extension="csv"
        )
        save_dataframe(data, filename)
        return filename
```

### 2. Versionamento de Modelos

```python
class ModelManager:
    def __init__(self, model_type: str, symbol: str, timeframe: str):
        self.model_type = model_type  # ppo_long, ppo_short, mlp_decisor
        self.symbol = symbol
        self.timeframe = timeframe
        self.logger = get_logger(self.__class__.__name__)
    
    def save_model(self, model, metrics: dict, config: dict) -> str:
        """Salva modelo com metadados."""
        timestamp = get_timestamp()
        model_dir = create_model_directory(
            category=self._get_category(),
            model_type=self.model_type,
            asset=self.symbol,
            timeframe=self.timeframe,
            timestamp=timestamp
        )
        
        # Salvar modelo
        model.save(f"{model_dir}/model.zip")
        
        # Salvar metadados
        metadata = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "model_type": self.model_type,
            "timestamp": timestamp,
            "metrics": metrics,
            "config": config
        }
        
        with open(f"{model_dir}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return model_dir
```

### 3. Otimização com Optuna

```python
import optuna
from optuna.integration import TFKerasPruningCallback

def optimize_hyperparameters(symbol: str, timeframe: str, n_trials: int = 100):
    """Otimiza hiperparâmetros usando Optuna."""
    
    def objective(trial):
        # Sugerir hiperparâmetros
        learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)
        batch_size = trial.suggest_categorical('batch_size', [32, 64, 128])
        n_steps = trial.suggest_categorical('n_steps', [1024, 2048, 4096])
        
        # Treinar modelo com hiperparâmetros
        model = create_ppo_model(learning_rate, batch_size, n_steps)
        metrics = train_model(model)
        
        return metrics['sharpe_ratio']  # Objetivo a maximizar
    
    # Criar estudo
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=n_trials, callbacks=[optuna_progress_callback])
    
    return study.best_params
```

---

## 🔄 Automação e DevOps

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Miniconda
      uses: conda-incubator/setup-miniconda@v2
      with:
        activate-environment: op_trader
        environment-file: environment.yml
        python-version: 3.10
    
    - name: Lint with flake8
      shell: bash -l {0}
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      shell: bash -l {0}
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 2. Scripts de Automação

```python
# src/utils/automation.py
def run_full_pipeline(symbol: str, timeframe: str, retrain: bool = False):
    """Executa pipeline completo de dados → treinamento → validação."""
    
    logger = get_logger(__name__)
    
    try:
        # 1. Coleta de dados
        logger.info("Iniciando coleta de dados...")
        run_command(f"python src/data/data_collector.py --symbol {symbol} --timeframe {timeframe}")
        
        # 2. Processamento
        logger.info("Processando dados...")
        run_command(f"python src/data/data_processor.py --symbol {symbol} --timeframe {timeframe}")
        
        # 3. Treinamento (se necessário)
        if retrain:
            logger.info("Treinando modelos...")
            run_command(f"python src/train/ppo/ppo_trainer.py --symbol {symbol} --timeframe {timeframe}")
            run_command(f"python src/train/mlp/mlp_trainer.py --symbol {symbol} --timeframe {timeframe}")
        
        # 4. Validação
        logger.info("Executando validação...")
        run_command(f"python src/trade/backtest_runner.py --symbol {symbol} --timeframe {timeframe}")
        
        logger.info("Pipeline executado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no pipeline: {e}")
        raise
```

---

## 📈 Monitoramento e Métricas

### 1. Callback de Progresso

```python
# src/utils/callbacks.py
class TrainingProgressCallback:
    def __init__(self, total_steps: int, save_freq: int = 1000):
        self.pbar = tqdm(total=total_steps, desc="Treinamento")
        self.save_freq = save_freq
        self.step_count = 0
        self.metrics_history = []
    
    def on_step(self, metrics: dict):
        self.step_count += 1
        self.pbar.update(1)
        
        # Atualizar descrição com métricas
        self.pbar.set_postfix({
            'reward': f"{metrics.get('reward', 0):.3f}",
            'loss': f"{metrics.get('loss', 0):.3f}"
        })
        
        # Salvar checkpoint
        if self.step_count % self.save_freq == 0:
            self.save_checkpoint(metrics)
    
    def save_checkpoint(self, metrics: dict):
        """Salva checkpoint do treinamento."""
        checkpoint_data = {
            'step': self.step_count,
            'metrics': metrics,
            'timestamp': get_timestamp()
        }
        self.metrics_history.append(checkpoint_data)
```

### 2. Monitor de Sistema

```python
# src/utils/system_monitor.py
import psutil
import time

class SystemMonitor:
    def __init__(self, log_interval: int = 60):
        self.log_interval = log_interval
        self.logger = get_logger(self.__class__.__name__)
        self.running = False
    
    def start_monitoring(self):
        """Inicia monitoramento do sistema."""
        self.running = True
        
        while self.running:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.logger.info(f"CPU: {cpu_percent}% | "
                           f"RAM: {memory.percent}% | "
                           f"Disk: {disk.percent}%")
            
            # Alertas
            if cpu_percent > 90:
                self.logger.warning(f"CPU alta: {cpu_percent}%")
            if memory.percent > 85:
                self.logger.warning(f"Memória alta: {memory.percent}%")
            
            time.sleep(self.log_interval)
```

---

## ✅ Checklist de Qualidade

### Antes de Fazer Commit

- [ ] **Código segue PEP 8** (verificar com `flake8`)
- [ ] **Imports absolutos** configurados corretamente
- [ ] **Flag --debug** implementada em scripts executáveis
- [ ] **Docstrings** no formato Google para funções públicas
- [ ] **Type hints** em funções principais
- [ ] **Testes funcionais** escritos para toda nova funcionalidade
- [ ] **Não perseguir cobertura cega:** cobertura alta é desejável, mas nunca mais importante que a utilidade dos testes
- [ ] **Logs apropriados** em todos os níveis
- [ ] **Tratamento de erros** implementado
- [ ] **Nomenclatura consistente** de arquivos e variáveis
- [ ] **Veja também o `DEVELOPMENT_FLOW.md`** para fluxo macro de desenvolvimento.

### Antes de Fazer Deploy

- [ ] **Todos os testes passando**
- [ ] **Linting sem erros críticos**
- [ ] **Documentação atualizada**
- [ ] **Configurações validadas**
- [ ] **Backup dos modelos** atual
- [ ] **Logs de sistema** funcionais
- [ ] **Monitoramento** configurado
- [ ] **Rollback plan** definido

---

## 🔧 Ferramentas e Dependências

### Core Dependencies
```yaml
# environment.yml (principais)
dependencies:
  - python=3.10
  - pandas>=1.5.0
  - numpy>=1.24.0
  - tensorflow>=2.12.0
  - stable-baselines3>=2.0.0
  - optuna>=3.0.0
  - colorlog>=6.7.0
  - tqdm>=4.64.0
  - pytest>=7.0.0
  - pytest-cov>=4.0.0
  - flake8>=6.0.0
```

### Development Tools
```bash
# Linting
flake8 src/ --max-line-length=127 --extend-ignore=E203,W503

# Testing
pytest tests/ --cov=src --cov-report=html  # Cobertura é acompanhada, mas não obrigatória


# Type checking (opcional)
mypy src/ --ignore-missing-imports

# Formatação (opcional)
black src/ --line-length=127
```

---

## 📖 Documentação Adicional

- **API Reference**: `docs/api_reference.md`
- **User Guide**: `docs/user_guide.md`
- **Architecture**: `docs/architecture.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Examples**: `docs/examples/`

---

## 🆘 Suporte e Solução de Problemas

### Problemas Comuns

1. **Import Error**: Verificar se `sys.path` está configurado corretamente
2. **Conda Environment**: Recriar ambiente com `conda env create -f environment.yml --force`
3. **Memory Issues**: Monitorar uso com `SystemMonitor`
4. **Test Failures**: Executar com `pytest -v -s` para debug detalhado

### Contato

- **Issues**: Usar GitHub Issues para bugs e features
- **Discussions**: GitHub Discussions para dúvidas
- **Documentation**: Contribuir via Pull Request

---

## ⚠️ Aviso

**Este sistema opera com dinheiro real. Teste em modo `--debug` antes de usar `--live`. O uso é por sua conta e risco.**

*Este guia é atualizado regularmente. Última revisão: 06/06/2025