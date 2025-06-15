# SPEC\_DataPipeline.md — src/data/data\_pipeline.py (Atualizada c/ pipeline\_type)

---

## 1. Objetivo

O **DataPipeline** é o orquestrador principal de processamento de dados do Op\_Trader. Ele integra todos os passos necessários para transformar dados brutos em dados prontos para treino, validação, backtest ou execução real-time de modelos, com rastreabilidade e governança total, **com controle explícito de pipeline\_type**.

**Fluxo oficial validado:**

```
DataPipeline.run()
  ↓
MT5Connector (conexão com broker para cada tipo de broker cirar um connector, quando desejado.) # faltou este passo 
  ↓
DataCollector (coleta bruta)
  ↓
DataCleanerWrapper (limpeza)
  ↓
OutlierGapCorrector (correção)
  ↓
FeatureEngineer/FeatureCalculator (features técnicas)
  ↓
# Passo CONDICIONAL: depende de pipeline_type
ScalerUtils (normalização, só para MLP)
# (PPO normalization via VecNormalize ocorre no treinamento, não aqui)
  ↓
SchemaUtils (validação final)
  ↓
Salvamento/logging/config hash
```

**Pilares do módulo:**

* Execução sequencial plugável, em modo batch ou streaming, com execução condicional por tipo de pipeline.
* Rastreabilidade: todo output tem hash/config de origem, impossível rodar pipeline ou modelo com parâmetros inconsistentes.
* Salvamento incremental e versionado de cada etapa.
* Logging robusto, docstrings Google e testes obrigatórios para todos edge cases.
* Hierarquia de configuração: CLI > config.ini > default (exceto argumentos críticos).
* **Proteção contra mistura de artefatos de pipelines distintos (MLP x PPO)**.

---

## 2. Entradas (Argumentos & Configuração)

| Parâmetro       | Tipo | Obrigatório | Fallback         | Fonte de configuração       | Observações                                                 |
| --------------- | ---- | ----------- | ---------------- | --------------------------- | ----------------------------------------------------------- |
| config          | dict | Sim         | -                | config.ini/json/dict        | Centraliza todos parâmetros, usado como base para fallback. |
| pipeline\_type  | str  | Sim         | config.ini       | CLI > config.ini > abort    | 'ppo', 'mlp' ou 'ambos'. Determina lógica do pipeline.      |
| mode            | str  | Sim         | config.ini       | CLI > config.ini > abort    | 'batch' ou 'streaming'. Abortar se ausente após fallback.   |
| broker          | str  | Sim         | config.ini       | CLI > config.ini > abort    | Nunca default.                                              |
| symbol          | str  | Sim         | config.ini       | CLI > config.ini > abort    | Nunca default.                                              |
| timeframe       | str  | Sim         | config.ini       | CLI > config.ini > abort    | Nunca default.                                              |
| features        | list | Sim         | config.ini       | CLI > config.ini > abort    | Lista de features técnicas. Nunca default.                  |
| start\_date     | str  | Não         | config.ini       | CLI > config.ini > abort(b) | Batch: aborta se ausente após fallback.                     |
| end\_date       | str  | Não         | config.ini       | CLI > config.ini > abort(b) | Batch: aborta se ausente após fallback.                     |
| gap\_params     | dict | Não         | config.ini       | CLI > config.ini > default  | Parametrização avançada para correção de gaps.              |
| outlier\_params | dict | Não         | config.ini       | CLI > config.ini > default  | Parametrização para outliers.                               |
| scaler\_params  | dict | Não         | config.ini       | CLI > config.ini > default  | Parâmetros do scaler.                                       |
| callbacks       | dict | Não         | -                | CLI/código                  | Funções para eventos/callbacks streaming.                   |
| debug           | bool | Não         | config.ini/False | CLI > config.ini > default  | Ativa logging detalhado.                                    |

---

## 3. Controle Condicional por pipeline\_type

* **Se `pipeline_type=ppo`:**

  * NÃO executa nem salva etapa de normalização tabular (ScalerUtils).
  * **Sem normalização aqui** (RL normalization via VecNormalize ocorre no treinamento).
  * Retorna DataFrame final não-normalizado.
* **Se `pipeline_type=mlp`:**

  * OBRIGA execução de normalização tabular (ScalerUtils), gera `features_normalized`, `scaler.pkl`.
  * Retorna DataFrame normalizado.
* **Se `pipeline_type=ambos`:**

  * Executa ambos fluxos e salva outputs em diretórios distintos (`features_normalized` e `final_ml`, `final_ppo`).
  * Nunca sobrescreve artefatos de outro `pipeline_type`.
* **Validação:**

  * O pipeline aborta e loga ERRO CRÍTICO se detectar artefatos incompatíveis com o tipo declarado.
  * O nome dos artefatos deve incluir `pipeline_type`, `config_hash` e `timestamp` para evitar ambiguidade.

---

## 4. Fluxo Sequencial Detalhado

1. **DataCollector** → coleta bruta, retorna `(df, ohlc_decimals)`.
2. **DataCleanerWrapper** → `clean(df, ohlc_decimals)`, salva `cleaned`.
3. **OutlierGapCorrector** → `fix_gaps` e `fix_outliers`, salva `corrected`.
4. **FeatureEngineer** → `transform(corrected_df)`, salva `features`.
5. **Passo Condicional** (após features):

   * `mlp` → `ScalerUtils.fit_transform(features)`, salva `features_normalized` e `scaler.pkl`, retorna como `final`.
   * `ppo` → **nenhuma normalização** aqui, retorna `features` como `final_ppo`.
   * `ambos` → executa ambos fluxos e salva `final_mlp` e `final_ppo`.
6. **SchemaUtils** → aplica `load_feature_list()`, `align_dataframe_to_schema(final_df)`, `validate_dataframe_schema(...)`, salva `final_aligned`.
7. **Salvamento & Logging** → em cada etapa, chama `save_dataframe` e `save_json(meta)` com:

   * Hash/config de origem, versão dos módulos, timestamp, fonte de cada parâmetro (CLI/config.ini/default), dependências anteriores.

---

## 5. Exceções, Validações e Rastreabilidade

| Caso                                      | Exceção/Retorno | Descrição                                                             |
| ----------------------------------------- | --------------- | --------------------------------------------------------------------- |
| Parâmetro obrigatório ausente             | ValueError      | Falta de config essencial ou flag CLI.                                |
| Valor inválido de `pipeline_type`         | ValueError      | Abort com log crítico.                                                |
| Falha em coleta/limpeza/correção          | Exception       | Log crítico, raise exception.                                         |
| Dados inconsistentes (schema mismatch)    | Exception       | `validate_dataframe_schema` raise.                                    |
| Re-uso de artefatos de pipeline diferente | Exception       | Detecta `config_hash` ou `pipeline_type` divergente, aborta pipeline. |
| Falha ao salvar etapa                     | Exception       | Logging crítico, raise.                                               |

---

## 6. Checklists de Qualidade & Regras de Negócio

* Nunca avançar etapa sem validação pelo SchemaUtils.
* Sempre registrar fonte de cada argumento (CLI/config.ini/default) em metadados.
* Artefatos devem conter `pipeline_type`, `config_hash`, `timestamp` e parâmetros de configuração.
* Docstrings estilo Google, logging detalhado, edge cases cobertos em testes.
* Imports absolutos, type hints em funções públicas.
* Integração pronta para CI/CD, homologação e auditoria.

---

## 7. Histórico e Rastreabilidade

| Data       | Autor           | Alteração                                                        |
| ---------- | --------------- | ---------------------------------------------------------------- |
| 2025-06-11 | Eng. Op\_Trader | Versão original com pipeline\_type e rastreabilidade.            |
| 2025-06-12 | Eng. Op\_Trader | Removido VecNormalize do pré-processamento, atualização do SPEC. |

*Referências cruzadas: DEVELOP\_TABLE.md, README.md, CONTRIBUTING.md, SPEC\_TEMPLATE.md v2.0*
