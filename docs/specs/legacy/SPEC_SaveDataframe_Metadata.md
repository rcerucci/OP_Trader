# 📄 SPEC\_SaveDataframe\_Metadata.md — Salvamento Auditável de DataFrame + Metadados

---

## 1. Objetivo

O módulo/função `save_dataframe_metadata` garante a **persistência auditável** de qualquer DataFrame no pipeline Op\_Trader, com geração de nomes padronizados, versionamento via timestamp, salvamento de metadados (JSON) e integração com arquivos auxiliares (ex: scaler/modelos). Padroniza a rastreabilidade de todo dado, modelo e artefato gerado no pipeline.

---

## 2. Entradas, Saídas e Interface

### Entradas

* **df** (`pd.DataFrame`): DataFrame a ser salvo
* **step** (`str`): Nome da etapa/lógica de processamento (ex: "features", "mlp\_normalized")
* **meta** (`dict`, opcional): Dicionário de metadados a ser salvo como JSON (ex: features usadas, parâmetros, origem dos dados)
* **scaler** (`obj`, opcional): Objeto scaler/auxiliar para serialização
* **asset** (`str`): Ativo (ex: "EURUSD")
* **timeframe** (`str`): Timeframe (ex: "M5")
* **period** (`str`, opcional): Período referenciado (ex: "2020-01-01\_2025-01-01")
* **output\_dir** (`str`, opcional): Diretório base para saída (default: "data/processed")
* **timestamp** (`str`, opcional): Timestamp para versionamento (default: None → gera automático)
* **extension** (`str`, opcional): Extensão do DataFrame (default: "csv")
* **debug** (`bool`, opcional): Logging detalhado

### Saídas

* Caminho completo do arquivo principal salvo (CSV, por padrão)
* Caminhos dos arquivos auxiliares (meta.json, scaler.pkl, etc)
* Logging detalhado do processo

---

## 3. Assinatura e API

```python
def save_dataframe_metadata(
    df: pd.DataFrame,
    step: str,
    meta: dict = None,
    scaler = None,
    asset: str = "",
    timeframe: str = "",
    period: str = "",
    output_dir: str = "data/processed",
    timestamp: str = None,
    extension: str = "csv",
    debug: bool = False
) -> dict:
    """
    Salva DataFrame e arquivos auxiliares (metadados, scaler), versionando e logando tudo.

    Args:
        df (pd.DataFrame): Dados a serem salvos.
        step (str): Nome lógico da etapa (usado no nome do arquivo).
        meta (dict, opcional): Metadados a salvar como JSON.
        scaler (obj, opcional): Objeto scaler/auxiliar (usará joblib/pickle).
        asset (str): Ativo.
        timeframe (str): Timeframe.
        period (str, opcional): Período de referência.
        output_dir (str, opcional): Diretório base.
        timestamp (str, opcional): Timestamp para versionamento.
        extension (str, opcional): Extensão principal (csv).
        debug (bool, opcional): Ativa logs detalhados.
    Returns:
        dict: Mapeamento de arquivos gerados { 'data': path, 'meta': path, 'scaler': path (opcional) }
    Raises:
        IOError: Se falhar ao salvar qualquer arquivo obrigatório.
    """
    ...
```

---

## 4. Regras, Edge Cases e Restrições

* Gera timestamp automaticamente se não for fornecido
* Nome dos arquivos sempre segue padrão do build\_filename (asset, timeframe, step, período, timestamp, extensão)
* Salva DataFrame, meta.json e scaler.pkl (se aplicável) no mesmo output\_dir
* Gera diretórios automaticamente se não existirem
* Logging detalhado do início ao fim (sucesso e erro)
* Falha ao salvar algum arquivo obrigatório → raise
* Edge cases:

  * DataFrame vazio: log crítico e raise
  * meta não serializável: warning e não salva
  * scaler não serializável: warning e não salva
  * Permissões insuficientes: log crítico e raise
* Sempre retorna dicionário de caminhos salvos para rastreamento posterior

---

## 5. Dependências

* pandas
* os, json, joblib/pickle
* src.utils.file\_saver (get\_timestamp, build\_filename, save\_dataframe)
* logging\_utils

---

## 6. Exemplo de Uso

```python
from src.data.data_libs.save_dataframe_metadata import save_dataframe_metadata

# Salva DataFrame, meta e scaler
result = save_dataframe_metadata(
    df=features_df,
    step="features_MLPnorm",
    meta=meta_dict,
    scaler=mlp_scaler,
    asset="EURUSD",
    timeframe="M5",
    period="2020-01-01_2025-01-01"
)
print(result['data'])   # caminho do CSV
print(result['meta'])   # caminho do meta.json
print(result.get('scaler')) # caminho do scaler (se houver)
```

---

## 7. Testes e Validação

* Testa salvamento completo (dados, meta, scaler)
* Testa logs e versionamento correto dos nomes/arquivos
* Testa falhas simuladas (diretório, permissão, meta não serializável, scaler não serializável)
* Testa DataFrame vazio (raise)
* Testa ausência de meta e scaler (comportamento esperado)

---

## 8. Referências e Rastreamento

* ESPEC\_CONCEITUAL\_SRC\_DATA.md
* DEVELOP\_TABLE\_SRC\_DATA.md
* tests/unit/test\_save\_dataframe\_metadata.py
* src/utils/file\_saver.py

---

## 9. Checklist Inicial

* [x] Cumpre SPEC global de persistência e rastreio
* [x] Entradas/saídas documentadas e auditáveis
* [x] Pronto para codificação, testes e integração

---

**Autor:** Eng. Sênior Op\_Trader
**Última atualização:** 2025-06-10
**Versão do template:** 2.0

---
