# 📄 SPEC\_BinanceConnection.md — Especificação Formal

---

## 1. Objetivo e Contexto

O módulo `binance_connection.py` fornece utilitários oficiais para conexão, autenticação e encerramento de sessão com a API da Binance (spot/futures) de forma padronizada, auditável e segura para todo o Op\_Trader. Centraliza leitura de credenciais do `.env`, fallback para config.ini, logging padronizado, tratamento de erros, e previne exposição ou duplicidade de lógica de autenticação.

---

## 2. Entradas, Saídas e Interface

### 2.1 Entradas

* **cli\_level** (`Optional[str]`): Nível de logging ("DEBUG", "INFO", ...)
* **config** (`dict` ou None): Configuração opcional sobrescrevendo `.env`

### 2.2 Saídas

* Sessão/objeto autenticado (ex: client do python-binance ou requests.Session)
* Logging de conexão, autenticação, encerramento
* Raise/erro em caso de credencial ausente, autenticação inválida, bloqueio, etc.

---

## 3. Assinatura e API

```python
from typing import Optional

def connect_to_binance(cli_level: Optional[str] = None, config: Optional[dict] = None):
    """
    Inicializa conexão segura com a API Binance, lendo credenciais do .env ou config, logging padronizado.

    Args:
        cli_level (Optional[str]): Nível de log.
        config (Optional[dict]): Parâmetros para sobrescrever credenciais padrão.
    Returns:
        client: Objeto client autenticado (ex: python-binance Client ou requests.Session).
    Raises:
        RuntimeError: Se faltar credenciais obrigatórias, erro de autenticação, bloqueio, etc.
    """
    ...

def close_binance_connection(client, cli_level: Optional[str] = None) -> None:
    """
    Encerra/destrói sessão/conexão autenticada da API Binance, logging padronizado.

    Args:
        client: Objeto client autenticado a ser encerrado.
        cli_level (Optional[str]): Nível de log.
    Raises:
        RuntimeError: Em caso de falha no encerramento.
    """
    ...
```

---

## 4. Regras, Edge Cases e Restrições

* **Credenciais obrigatoriamente lidas do `.env` na raiz do projeto**, nunca hardcoded
* Permitir override via config (ex: para CI/CD)
* Logging padronizado usando get\_logger, com nível por CLI/config.ini
* Raise explícito e logging crítico para variáveis ausentes ou autenticação inválida
* Nunca expor segredos no log, nem aceitar credenciais via CLI/args
* Encerramento sempre logado e seguro (mesmo se sessão não for explicitamente autenticada)
* Suporte a spot e futuros (parâmetro em config)
* Prover exemplos para python-binance e fallback para requests caso lib não esteja instalada

---

## 5. Dependências

* python-binance (preferencialmente), requests, dotenv
* utils: logging\_utils, path\_setup

---

## 6. Exemplo de Uso

```python
from src.utils.binance_connection import connect_to_binance, close_binance_connection

client = connect_to_binance(cli_level="INFO")
# ... usa client para fazer requests
close_binance_connection(client, cli_level="INFO")
```

---

## 7. Testes e Validação

* Teste de conexão com credenciais válidas e inválidas
* Teste de bloqueio por rate limit/autenticação
* Teste de fallback CLI/config.ini
* Teste de encerramento seguro
* Teste de logging de cada etapa

---

## 8. Referências e Rastreamento

* ESPEC\_CONCEITUAL\_SRC\_DATA.md
* DEVELOP\_TABLE\_SRC\_DATA.md
* tests/unit/test\_binance\_connection.py

---

## 9. Checklist Inicial

* [x] Lê credenciais apenas do .env/config
* [x] Logging e segurança compatíveis com o projeto
* [x] Entradas/saídas documentadas e rastreáveis
* [x] Pronto para codificação, testes e integração

---
