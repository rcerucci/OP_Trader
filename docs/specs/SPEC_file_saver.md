# SPEC\_file\_saver.md — src/utils/file\_saver.py

---

## 1. Objetivo

O módulo **file\_saver** centraliza funções e utilitários para geração de nomes de arquivos padronizados (com tags completas para rastreabilidade) e salvamento seguro de DataFrames, JSON, objetos serializáveis, artefatos de modelos e metadados no Op\_Trader.

**Funcionalidades principais:**

* Geração de nomes de arquivos robustos, versionados e auditáveis, incluindo step, broker, corretora, ativo, timeframe, período e timestamp.
* Salvamento seguro e auditável de DataFrames (`.csv`), metadados (`.json`), artefatos/scalers/modelos (`.pkl`), com logging e criação automática de diretórios.
* Suporte a salvamento centralizado de pipelines: batch, streaming, treino, tuning, checkpoints, logs auxiliares, evidências de CI/CD.
* Pronto para expansão (futuro): suporte a YAML, joblib, compressão, versionamento automático, leitura robusta (loaders).

---

## 2. Entradas

| Parâmetro   | Tipo         | Obrigatório | Descrição                                                       | Exemplo                  |
| ----------- | ------------ | ----------- | --------------------------------------------------------------- | ------------------------ |
| prefix      | str          | Sim         | Diretório base (ex: "data/processed")                           | "data/processed"         |
| step        | str          | Sim         | Etapa do dado ("features", "raw", "model", etc.)                | "features"               |
| broker      | str          | Sim         | Broker/fonte ("mt5", "binance")                                 | "mt5"                    |
| corretora   | str          | Sim         | Nome da corretora/server/provider ("xp", "rico", "n/a")         | "xp"                     |
| asset       | str          | Sim         | Ativo negociado                                                 | "EURUSD"                 |
| timeframe   | str          | Sim         | Timeframe dos dados                                             | "M5"                     |
| period      | str          | Não         | Período da amostra                                              | "2024-01-01\_2024-12-31" |
| timestamp   | str          | Não         | Timestamp (auto se vazio)                                       | "20250611\_211500"       |
| extension   | str          | Não         | Extensão do arquivo                                             | "csv"                    |
| df          | pd.DataFrame | Sim         | DataFrame a ser salvo                                           | df                       |
| meta        | dict         | Não         | Dicionário de metadados para meta.json                          | {"broker": "mt5", ...}   |
| scaler      | Any          | Não         | Scaler/modelo/artefato a ser salvo (.pkl)                       | mlp\_scaler              |
| obj         | Any          | Não         | Objeto serializável para save\_json/save\_pickle/save\_model... | {...}                    |
| output\_dir | str          | Não         | Diretório de saída                                              | "data/processed"         |
| debug       | bool         | Não         | Ativa logs detalhados                                           | True                     |

---

## 3. Saídas

| Função/Método             | Tipo Retorno | Descrição                                               | Exemplo Uso                                            |
| ------------------------- | ------------ | ------------------------------------------------------- | ------------------------------------------------------ |
| get\_timestamp            | str          | Gera timestamp padrão                                   | get\_timestamp()                                       |
| build\_filename           | str          | Nome completo, auditável, pronto para salvar/consultar  | build\_filename(...)                                   |
| save\_dataframe           | None         | Salva DataFrame como CSV, robusto                       | save\_dataframe(df, filepath)                          |
| save\_json                | None         | Salva objeto serializável como JSON                     | save\_json(meta, filepath)                             |
| save\_pickle              | None         | Salva objeto serializável via pickle                    | save\_pickle(scaler, filepath)                         |
| save\_model\_artifact     | None         | Salva modelos, tuning, checkpoints, configs (pickle)    | save\_model\_artifact(model, filepath, artifact\_type) |
| save\_dataframe\_metadata | dict         | Salva DataFrame + meta.json + scaler.pkl, retorna paths | save\_dataframe\_metadata(...)                         |

---

## 4. Performance e Complexidade

| Método/Função             | Complexidade Temporal | Complexidade Espacial | Observações                   |
| ------------------------- | --------------------- | --------------------- | ----------------------------- |
| get\_timestamp            | O(1)                  | O(1)                  | -                             |
| build\_filename           | O(1)                  | O(1)                  | -                             |
| save\_dataframe           | O(n)                  | O(1)                  | n = linhas do DataFrame       |
| save\_json                | O(k)                  | O(1)                  | k = len(obj)                  |
| save\_pickle              | O(k)                  | O(1)                  | k = tamanho do objeto         |
| save\_dataframe\_metadata | O(n+k+m)              | O(1)                  | n=linhas df, k=meta, m=scaler |

---

## 5. Exceções e Validações

| Caso                         | Exceção/Retorno | Descrição                                           |
| ---------------------------- | --------------- | --------------------------------------------------- |
| Campos obrigatórios ausentes | ValueError      | Não inicializa nome/arquivo se campo estiver vazio  |
| DataFrame vazio              | ValueError      | Não permite salvar DataFrame vazio                  |
| Erro ao criar diretório      | IOError         | Falha em os.makedirs, permissão negada, disco cheio |
| Falha ao salvar CSV/JSON/pkl | IOError         | Qualquer erro ao serializar/salvar                  |
| Objeto não serializável      | IOError         | Se não conseguir salvar meta ou scaler/model        |

---

## 6. Dependências e Compatibilidade

**Dependências obrigatórias:**

* `os`, `json`, `pickle`, `pandas`
* `src.utils.logging_utils.get_logger`
* `src.utils.path_setup.ensure_project_root`

**Compatibilidade testada:**

* Python: 3.10+
* pandas: 1.5+

**Não deve depender de:**

* Bibliotecas externas não-auditáveis para serialização
* Caminhos relativos não robustos (tudo auditável/absoluto)

---

## 7. Docstring Padrão (Google Style)

```python
def save_dataframe_metadata(
    df: pd.DataFrame,
    step: str,
    broker: str,
    corretora: str,
    asset: str,
    timeframe: str,
    period: str = "",
    meta: Optional[dict] = None,
    scaler: Any = None,
    output_dir: str = "data/processed",
    timestamp: str = None,
    extension: str = "csv",
    debug: bool = False
) -> Dict[str, str]:
    """
    Salva DataFrame, metadados (JSON) e scaler/modelo (Pickle), tudo versionado e auditável.
    Retorna os caminhos dos arquivos gerados.

    Args:
        df (pd.DataFrame): DataFrame a ser salvo.
        step (str): Etapa do dado.
        broker (str): Nome do broker/fonte.
        corretora (str): Nome da corretora/server/provider.
        asset (str): Ativo.
        timeframe (str): Timeframe.
        period (str, opcional): Período referenciado.
        meta (dict, opcional): Metadados para salvar como JSON.
        scaler (Any, opcional): Objeto scaler/modelo auxiliar.
        output_dir (str, opcional): Diretório de saída.
        timestamp (str, opcional): Timestamp customizado.
        extension (str, opcional): Extensão do DataFrame principal.
        debug (bool, opcional): Logging detalhado.

    Returns:
        Dict[str, str]: Mapeamento dos arquivos gerados: data, meta, scaler.
    """
    ...
```

---

## 8. Exemplos de Uso

### Uso Básico: salvar DataFrame, meta e scaler

```python
from src.utils.file_saver import save_dataframe_metadata

result = save_dataframe_metadata(
    df=df_features,
    step="features",
    broker="mt5",
    corretora="xp",
    asset="EURUSD",
    timeframe="M5",
    period="2024-01-01_2024-12-31",
    meta={
        "broker": "mt5",
        "corretora": "xp",
        "pipeline_version": "2025-06-11",
        "params": {...}
    },
    scaler=mlp_scaler,
    output_dir="data/processed"
)
print(result)
```

### Uso Avançado: apenas DataFrame (raw)

```python
save_dataframe_metadata(
    df=df_raw,
    step="raw",
    broker="binance",
    corretora="main",
    asset="BTCUSDT",
    timeframe="1m"
)
```

### Uso isolado dos utilitários

```python
from src.utils.file_saver import build_filename, save_json

fname = build_filename(
    prefix="data/processed",
    step="tuning",
    broker="mt5",
    corretora="xp",
    asset="EURUSD",
    timeframe="M5",
    timestamp="20250611_212222",
    extension="json"
)
save_json({"params": [1,2,3]}, fname)
```

---

## 9. Configuração e Customização

* O campo `output_dir` pode ser definido por ambiente.
* Logging detalhado via parâmetro `debug`.
* Pode ser integrado com pipelines de treino, tuning, checkpoints, logs e exportações.

---

## 10. Regras de Negócio e Observações

* Todo arquivo gerado deve conter as tags de rastreio no nome.
* DataFrame vazio nunca deve ser salvo.
* Logs e meta.json sempre incluem broker/corretora para rastreabilidade total.
* Padrão único para todos os pipelines (dados, modelos, tuning, logs).
* Preparado para compactação, hashing e exportação futura.

---

## 11. Edge Cases e Cenários Especiais

| Cenário                   | Comportamento Esperado          | Observações                       |
| ------------------------- | ------------------------------- | --------------------------------- |
| DataFrame vazio           | Lança ValueError, loga CRITICAL | -                                 |
| meta ou scaler ausentes   | Ignora, loga INFO               | Não bloqueia salvamento principal |
| Erro de permissão/disco   | Lança IOError, loga ERROR       | Não continua salvando             |
| Falha serialização scaler | Loga WARNING, mas salva df/meta | Caminho 'scaler' fica vazio       |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] Salvar DataFrame, meta, scaler (tudo)
* [x] DataFrame vazio (erro)
* [x] meta e scaler ausentes
* [x] Permissão negada (erro)
* [x] Falha de serialização (warning)
* [x] Logging detalhado (debug=True)

### Métricas de Qualidade

* Cobertura: >95% dos fluxos (pytest)
* Performance: Tempo de execução < 1s para 10k linhas
* Logging: 100% rastreável, auditável

---

## 13. Monitoramento e Logging

* Logging padronizado para cada salvamento, erro, diretório criado.
* Logging detalhado se debug=True.
* Logs críticos para DataFrame vazio e erros de permissão/disco.
* Integração plugável com logger central Op\_Trader.

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Código PEP8, docstrings Google
* [x] Imports absolutos
* [x] Type hints em todas funções públicas
* [x] Logging padronizado e auditável
* [x] Testes unitários para todos fluxos principais e edge cases
* [x] Exemplos de uso testados
* [x] Compatibilidade garantida
* [x] Estrutura preparada para expansão

---

## 15. Validação Final Spec-Código

* [x] Assinaturas conferem com código
* [x] Parâmetros opcionais documentados
* [x] Exceções implementadas
* [x] Exemplos funcionam
* [x] Performance validada
* [x] Edge cases testados
* [x] Integração plugável

### Aprovação Final

* [x] Revisor técnico: \[NOME] - Data: \[YYYY-MM-DD]
* [x] Teste de integração: OK
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor             | Alteração                |
| ---------- | ----------------- | ------------------------ |
| 2025-06-11 | Equipe Op\_Trader | Criação inicial completa |
| 2025-06-11 | ChatGPT Sênior    | Revisão, padronização    |

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md**: \[linha correspondente]
* **README.md**: [../../README.md](../../README.md)
* **CONTRIBUTING.md**: [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **SPEC Técnico**: [../../docs/specs/SPEC\_file\_saver.md](../../docs/specs/SPEC_file_saver.md)
* **Testes Unitários**: [../../../tests/unit/test\_file\_saver.py](../../../tests/unit/test_file_saver.py)
* **Template usado**: SPEC\_TEMPLATE.md v2.0
* **Última atualização**: 2025-06-11
* **Autor**: Equipe Op\_Trader

---

## 🤖 Tags para Automatização

```yaml
module_name: "file_saver"
module_path: "src/utils/file_saver.py"
main_functions: ["build_filename", "save_dataframe", "save_json", "save_pickle", "save_dataframe_metadata"]
test_path: "tests/unit/test_file_saver.py"
dependencies: ["os", "json", "pickle", "pandas"]
version: "1.0"
last_updated: "2025-06-11"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

---
