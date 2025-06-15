# SPEC\_schema\_utils.md — src/data/data\_libs/schema\_utils.py

---

## 1. Objetivo

O módulo **schema\_utils.py** centraliza o carregamento, alinhamento e validação de schema de DataFrames para o pipeline Op\_Trader, garantindo consistência estrutural dos dados em todas as etapas do fluxo (batch/real-time). Serve como referência única para padronização e checagem de features, tipos e ordem das colunas, prevenindo erros silenciosos em downstream, auditando divergências e facilitando a manutenção de schemas múltiplos/versionados.

**Funcionalidades principais:**

* Carregar lista de features ativa a partir do controle JSON (multi-schema ready).
* Alinhar DataFrames ao schema (colunas, ordem, dtype float64, preenchimento de ausências).
* Validar DataFrames (nomes, ordem, tipos), logar divergências e lançar exceção se necessário.
* Logging estruturado e auditável.
* Compatível com uso incremental em batch e streaming.

---

## 2. Entradas

| Parâmetro             | Tipo               | Obrigatório | Descrição                                         | Exemplo                       |
| --------------------- | ------------------ | ----------- | ------------------------------------------------- | ----------------------------- |
| schema\_control\_path | str (opcional)     | Não         | Caminho do feature\_schema.json (default=project) | '/projeto/config/schema.json' |
| df                    | pd.DataFrame       | Sim         | DataFrame a ser alinhado/validado                 | -                             |
| schema\_cols          | list\[str] / tuple | Sim         | Colunas referência para alinhamento/validação     | \['close','rsi','ema\_20']    |
| strict                | bool (opcional)    | Não         | Validação estrita (ordem/nome/tipo)               | True                          |
| raise\_on\_error      | bool (opcional)    | Não         | Lança exceção em divergência (default: False)     | True                          |

---

## 3. Saídas

| Função/Método                | Tipo Retorno | Descrição                                               | Exemplo Uso                           |
| ---------------------------- | ------------ | ------------------------------------------------------- | ------------------------------------- |
| load\_feature\_list          | list\[str]   | Carrega lista de features ativa do schema controlado    | load\_feature\_list()                 |
| align\_dataframe\_to\_schema | DataFrame    | Alinha DataFrame às colunas do schema, dtype float64    | align\_dataframe\_to\_schema(df, ...) |
| validate\_dataframe\_schema  | bool         | Valida nomes, ordem e tipos, loga e pode lançar exceção | validate\_dataframe\_schema(df, ...)  |

---

## 4. Performance e Complexidade

| Método/Função                | Complexidade Temporal | Complexidade Espacial | Observações           |
| ---------------------------- | --------------------- | --------------------- | --------------------- |
| load\_feature\_list          | O(1)                  | O(1)                  | Leitura de JSON       |
| align\_dataframe\_to\_schema | O(n)                  | O(n)                  | n = linhas do DF      |
| validate\_dataframe\_schema  | O(m)                  | O(1)                  | m = colunas no schema |

---

## 5. Exceções e Validações

| Caso                                   | Exceção/Retorno | Descrição                                            |
| -------------------------------------- | --------------- | ---------------------------------------------------- |
| Arquivo schema/controle ausente        | FileNotFoundErr | Logging crítico, aborta operação                     |
| Campo obrigatório ausente (json)       | KeyError        | Logging crítico, aborta operação                     |
| Colunas divergentes (strict=True)      | False ou ValueE | Log ERROR, retorna False ou lança (raise\_on\_error) |
| Tipos divergentes (float64)            | False ou ValueE | Log WARNING, retorna False ou lança                  |
| Colunas extras/ausentes (strict=False) | False/ValueE    | Log WARNING, retorna False ou lança                  |

---

## 6. Dependências e Compatibilidade

* `pandas`, `numpy`, `json`, `pathlib`
* `src.utils.logging_utils.get_logger`, `src.utils.path_setup.ensure_project_root`

**Compatibilidade testada:**

* Python: 3.10+
* pandas: >=1.4
* pytest: >=7.0
* Integração total com todos os módulos core de dados Op\_Trader

---

## 7. Docstring Padrão (Google Style)

```python
"""
Módulo utilitário para alinhamento e validação de schema de DataFrames.
Principais funções:
    - load_feature_list(schema_control_path=None): lista de features ativas
    - align_dataframe_to_schema(df, schema_cols): garante ordem e dtype
    - validate_dataframe_schema(df, schema_cols, strict=True, raise_on_error=False): checa nomes, ordem e tipos
Recomenda-se sempre alinhar DataFrame antes de validar.
"""
```

---

## 8. Exemplos de Uso

### Uso básico (pipeline batch):

```python
from src.data.data_libs.schema_utils import load_feature_list, align_dataframe_to_schema, validate_dataframe_schema

features = load_feature_list()
df_aligned = align_dataframe_to_schema(df_raw, features)
validate_dataframe_schema(df_aligned, features, strict=True, raise_on_error=True)
```

### Uso em streaming:

```python
features = load_feature_list(schema_control_path='/custom/path/feature_schema.json')
for df in streaming_batches:
    aligned = align_dataframe_to_schema(df, features)
    validate_dataframe_schema(aligned, features, strict=False)  # apenas loga divergências
```

---

## 9. Configuração e Customização

* `schema_control_path` customiza localização do schema principal (útil para múltiplos pipelines).
* Validação flexível via `strict` e modo auditoria via `raise_on_error`.
* Logging detalhado (INFO/WARNING/ERROR/CRITICAL) para rastreabilidade total.
* Testes prontos para pytest, integração CI/CD.

---

## 10. Regras de Negócio e Observações

* Sempre alinhar o DataFrame ao schema antes de validar.
* O módulo não corrige tipos (só valida e alinha); conversão é sempre para float64.
* Logging padronizado para toda divergência, inclusive em produção/streaming.
* Suporte a schemas múltiplos (controlados por feature\_schema.json).

---

## 11. Edge Cases e Cenários Especiais

| Cenário                     | Comportamento Esperado     | Observações         |
| --------------------------- | -------------------------- | ------------------- |
| DataFrame vazio             | Validação retorna True     | Nenhum erro lançado |
| Schema com coluna extra     | Log WARNING, retorna False | strict=False        |
| Coluna ausente no DataFrame | Log WARNING, retorna False | strict=False        |
| Tipos incorretos            | Log WARNING, retorna False | dtype diferente     |
| Ordem trocada               | Log ERROR, retorna False   | strict=True         |
| raise\_on\_error=True       | Lança ValueError se falhar | Uso em CI/prod      |

---

## 12. Testes e Validação

### Casos de Teste Obrigatórios

* [x] Carregamento correto do schema (multi-path)
* [x] Alinhamento de DataFrame à ordem e tipos
* [x] Validação estrita: nomes, ordem, tipos
* [x] Validação flexível: apenas loga diferenças
* [x] Edge cases: DF vazio, colunas extras, tipos errados
* [x] Logging capturável via caplog/pytest
* [x] Tratamento de exceção com raise\_on\_error

### Métricas de Qualidade

* Cobertura pytest > 95%
* Tempo < 1s para 10.000 linhas
* Todas divergências logadas
* Integração CI/CD aprovada

---

## 13. Monitoramento e Logging

* Todos logs emitidos via logger "schema\_utils" (níveis: INFO, WARNING, ERROR, CRITICAL)
* Logging detalhado para divergências, uso de raise, caminhos de arquivos, etc.
* Integração plug and play em todo pipeline de dados do Op\_Trader

---

## 14. Checklist de Qualidade (conforme CONTRIBUTING.md)

* [x] Código segue PEP 8, docstring Google, padrão Op\_Trader
* [x] Imports absolutos com `src.`
* [x] Type hints completos em todas funções públicas
* [x] Logging auditável
* [x] Testes unitários para todos fluxos
* [x] Edge cases cobertos
* [x] Pronto para batch/streaming/CI/CD
* [x] Integração plugável

---

## 15. Validação Final Spec-Código

* [x] Assinatura confere exatamente com código real
* [x] Parâmetros opcionais documentados
* [x] Todas exceções implementadas/documentadas
* [x] Exemplos funcionam (testados)
* [x] Performance e edge cases validados
* [x] Integração plugável em pipeline

### Aprovação Final

* [x] Revisor técnico: \[ChatGPT Sênior Op\_Trader] - Data: 2025-06-11
* [x] Teste de integração: Passou nos testes de CI/CD
* [x] Documentação revisada

---

## 16. Histórico

| Data       | Autor          | Alteração                        |
| ---------- | -------------- | -------------------------------- |
| 2025-06-11 | Op\_Trader Eng | Criação e homologação definitiva |
| 2025-06-11 | ChatGPT Sênior | Revisão padrão SPEC Op\_Trader   |

---

## 🚨 Observações Finais

* SPEC criada segundo template oficial Op\_Trader (SPEC\_TEMPLATE.md v2.0).
* Pronto para produção, CI/CD, integração e expansão incremental.
* Rastreabilidade completa com DEVELOP\_TABLE.md e DEV\_LOG.md.

---

## 🔗 Rastreabilidade e Referências

* **DEVELOP\_TABLE.md:** \[linha correspondente]
* **README.md:** [../../README.md](../../README.md)
* **CONTRIBUTING.md:** [../../CONTRIBUTING.md](../../CONTRIBUTING.md)
* **Teste Unitário:** [../../../tests/unit/test\_schema\_utils.py](../../../tests/unit/test_schema_utils.py)
* **Template usado:** `SPEC_TEMPLATE.md v2.0`
* **Última atualização:** 2025-06-11
* **Autor:** Op\_Trader Eng

---

## 🤖 Tags para Automatização

```yaml
module_name: "schema_utils"
module_path: "src/data/data_libs/schema_utils.py"
test_path: "tests/unit/test_schema_utils.py"
dependencies: ["logging", "pandas", "numpy", "json", "pathlib"]
version: "1.0"
last_updated: "2025-06-11"
documentation_version: "2.0"
template_type: "hybrid"
```

---

*Documentação criada seguindo template SPEC\_TEMPLATE.md v2.0 — Op\_Trader.*

---
