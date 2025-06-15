# SPEC\_config\_ini.md — Padrão Definitivo do config.ini Op\_Trader

---

## 1. Objetivo

Padronizar, documentar e versionar todos os parâmetros e seções possíveis do arquivo `config.ini` do Op\_Trader, garantindo compatibilidade com pipelines, rastreabilidade, governança, e integração futura com dashboard/API.

---

## 2. Princípios e Hierarquia

* CLI > config.ini > default do módulo (quando permitido)
* Parâmetros críticos (ex: broker, symbols, timeframes, features, modo, diretórios) devem estar sempre preenchidos por CLI/config. Nunca usar fallback silencioso.
* Todos os artefatos de dados/salvamentos devem registrar a configuração/hierarquia utilizada e um hash/config para rastreabilidade.
* Comentários explicativos e exemplos são obrigatórios em todas as seções/campos para facilitar edição manual e futura automação/dashboard.
* Comentários SEMPRE em linha separada ANTES do campo, nunca ao lado do valor!

---

## 3. Estrutura Geral e Seções Obrigatórias

* \[DATA]: Coleta, ativos, timeframes, datas, diretórios, pipeline\_type.
* \[FEATURE\_ENGINEER]: Lista de features e parâmetros técnicos.
* \[SCALER]: Configuração do scaler e colunas.
* \[DIAGNOSIS]: Níveis de log, debug, rotação.
* \[GAP\_CORRECTOR], \[OUTLIER\_CORRECTOR]: Correção de gaps/outliers.
* \[TRADING], \[ENV]: Parâmetros de risco, ambiente, episódio.
* \[REWARD]: Composição e pesos dos componentes de reward.
* \[PPO\_LONG], \[PPO\_SHORT], \[MLP\_DECISOR]: Hiperparâmetros de modelos (expansível).

---

## 4. Especificação Detalhada por Seção

### \[DATA]

```ini
[DATA]
# Lista de símbolos (separados por vírgula). Usado o primeiro se não passar --symbol na CLI.
# Exemplo: EURUSD,GBPUSD,USDJPY
symbols = EURUSD,GBPUSD,USDJPY

# Lista de timeframes (separados por vírgula). Usado o primeiro se não passar --timeframe na CLI.
# Valores aceitos: M1, M5, M15, M30, H1, H4, D1, W1, MN1
# Exemplo: M5,M15,H1
timeframes = M5,M15,H1

# Data inicial do histórico. Formato: YYYY-MM-DD. Fallback se não passar --start-date na CLI.
start_date = 2024-01-01
# Data final do histórico. Formato: YYYY-MM-DD. Fallback se não passar --end-date na CLI.
end_date = 2024-12-31

# Diretório para dados brutos (raw, coleta)
raw_dir = data/raw
# Diretório para dados limpos (após DataCleaner)
cleaned_dir = data/cleaned
# Diretório para dados corrigidos (após OutlierGapCorrector)
corrected_dir = data/corrected
# Diretório para dados com features calculadas (após FeatureEngineer, NUNCA normalizado)
features_dir = data/features
# Diretório para dados final normalizados (após ScalerUtils, apenas para MLP)
features_normalized_dir = data/features_normalized
# Diretório para arquivos de scaler tabular (.pkl) (apenas para MLP)
scaler_dir = data/scaler
# Diretório para artefatos VecNormalize (apenas para PPO)
vecnormalize_dir = data/vecnormalize

# Tipo de pipeline/modelo a ser processado:
#   ppo   = somente RL (NUNCA normaliza colunas tabulares, NÃO gera features_normalized nem scaler.pkl)
#   mlp   = somente supervisão (OBRIGA normalização tabular, gera features_normalized e scaler.pkl)
#   ambos = salva ambos fluxos separadamente, nunca sobrescreve arquivos de outro pipeline
pipeline_type = ppo

# Broker/fonte de dados (ex: mt5, binance)
broker = mt5
# Caminho para config extra do broker (json/yaml), se necessário (opcional)
# broker_extra_config =
```

---

### \[FEATURE\_ENGINEER]

```ini
[FEATURE_ENGINEER]
# Features core disponíveis atualmente (conforme FeatureCalculator):
# ema_fast, ema_slow, rsi, macd_hist, atr, bb_width, return_pct, candle_direction, volume_relative, pullback, hammer_pattern, inverted_hammer_pattern
# IMPORTANTE: mantenha esta lista sempre sincronizada com o código!
features = ema_fast, ema_slow, rsi, macd_hist, atr, bb_width, return_pct, candle_direction, volume_relative, pullback, hammer_pattern, inverted_hammer_pattern

# Parâmetros das features técnicas (apenas para features implementadas!):
ema_fast_window = 20
ema_slow_window = 50
rsi_window = 14
macd_short = 12
macd_long = 26
macd_signal = 9
atr_window = 14
bb_window = 20
```

---

### \[SCALER]

```ini
[SCALER]
# Tipo de scaler: minmax, standard, robust, none (default: standard)
scaler_type = standard

# Colunas a normalizar (separadas por vírgula). Exemplo: open,high,low,close,volume,rsi,ema_fast,macd_hist...
# Atenção: use exatamente as colunas desejadas no modelo MLP.
scaler_columns = open,high,low,close,volume

# Diretório para salvar objetos scaler (.pkl) — NÃO usar nome fixo, pipeline gera nomes com hash/config.
scaler_dir = data/scaler
```

---

### \[GAP\_CORRECTOR]

```ini
[GAP_CORRECTOR]
# Estratégia para gaps: forward_fill, backward_fill, interpolate, drop (default: forward_fill)
gap_strategy = forward_fill
# Tolerância máxima para preenchimento (em candles)
max_gap_tolerance = 5
```

---

### \[OUTLIER\_CORRECTOR]

```ini
[OUTLIER_CORRECTOR]
# Estratégia: zscore, iqr, rolling (default: zscore)
outlier_strategy = zscore
# Limite (default: 3.0 para zscore)
outlier_threshold = 3.0
```

---

### \[DIAGNOSIS]

```ini
[DIAGNOSIS]
# Nível de log padrão: NONE, ERROR, WARNING, INFO, DEBUG (default: DEBUG)
log_level = DEBUG
# Nível detalhado de debug: DEBUG/INFO/WARNING/ERROR/NONE (default: DEBUG)
debug_level = DEBUG
# Tamanho máximo do arquivo de log
max_log_size = 10MB
# Quantidade de arquivos de backup de log
backup_count = 5
```

---

### \[TRADING]

```ini
[TRADING]
# Limite de posições abertas simultâneas
max_positions = 3
# Risco por operação
risk_per_trade = 0.02
# Limite máximo de perda diária
max_daily_loss = 0.05
# Fator de stop loss
stop_loss_factor = 0.02
# Fator de take profit
take_profit_factor = 0.04
# Permite hedge? (true/false)
allow_hedge = false
```

---

### \[ENV]

```ini
[ENV]
# Modo do ambiente: batch/streaming/long/short (default: batch)
mode = batch
# Saldo inicial
initial_balance = 100000
# Percentual de stop loss
sl_pct = 1.5
# Percentual de take profit
tp_pct = 2.0
# Tamanho da posição (% do capital)
position_size_pct = 0.05
# Máximo de steps por episódio
max_episode_steps = 500
# Componentes de reward (separados por vírgula)
reward_components = pnl,drawdown,time_penalty,trade_cost,atr_risk
# Tamanho da janela temporal
window_size = 120
# Caminho para features/scaler já prontos (opcional)
# features_file =
# scaler_file =
```

---

### \[REWARD]

```ini
[REWARD]
# Pesos dos componentes de reward (nome=valor, separados por vírgula)
# Exemplo: pnl=1.0,drawdown=-0.5,time_penalty=-0.1,trade_cost=-0.05,atr_risk=0.7
reward_weights = pnl=1.0,drawdown=-0.5,time_penalty=-0.1,trade_cost=-0.05,atr_risk=0.7
```

---

### \[PPO\_LONG] (expansível)

```ini
[PPO_LONG]
# Hiperparâmetros do PPO longo
learning_rate = 0.0003
batch_size = 128
n_steps = 2048
n_epochs = 10
hidden_layers = 64,64
activation = relu
optimizer = adam
clip_range = 0.2
dropout = 0.1
```

---

## 5. Regras de Validação

* Todos os campos obrigatórios devem ser validados em runtime.
* NUNCA usar fallback default para argumentos críticos (broker, symbols, timeframes, features, modo, diretórios).
* Comentários sempre informam separador de listas, formatos, valores possíveis e exemplos reais.
* O arquivo `config.ini` pode ser convertido para/JSON para uso em dashboard/API.
* Os campos preenchidos no pipeline são sempre registrados como snapshot junto aos artefatos.
* Nunca colocar comentários ao lado do valor, apenas antes do campo!

---

## 6. Governança, Rastreabilidade e Expansão

* Toda execução, coleta ou experimento deve salvar uma cópia do `config.ini` utilizado.
* Artefatos de dados/salvamentos (csv, modelo, scaler, etc.) incluem hash/config dos argumentos efetivos.
* Para dashboard: todos os campos devem ser documentados com tipo, obrigatoriedade e help-text nos comentários, para futura automação.
* Padrão extensível: novas seções/campos podem ser adicionados, mantendo comentários e exemplos obrigatórios.

---

## 7. Histórico

| Data       | Autor           | Alteração                                                                                                     |
| ---------- | --------------- | ------------------------------------------------------------------------------------------------------------- |
| 2025-06-11 | Eng. Op\_Trader | Versão homologada, comentários acima do campo, pipeline\_type, diretórios segregados, 100% aderente ao código |

---

*Este SPEC é o padrão definitivo para governança e rastreabilidade do config.ini Op\_Trader — pronto para produção, dashboard e automação.*
