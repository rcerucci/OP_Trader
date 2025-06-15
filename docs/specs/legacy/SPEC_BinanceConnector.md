# 📄 SPEC\_BinanceConnector.md — Especificação Formal (Versão Real-Time Ready)

---

## 1. Objetivo e Contexto

O módulo `BinanceConnector` provê integração segura, auditável e padronizada entre o pipeline de dados Op\_Trader e a API da Binance (spot/futuros), operando em **modo batch e real-time** (websocket, polling ou API streaming). Realiza coleta de dados OHLCV e tick, trata autenticação, limites de rate, detecção automática de gaps/outliers, eventos contínuos, edge cases da API e garante logging conforme padrão do projeto.

---

## 2. Entradas, Saídas e Interface

### 2.1 Entradas

* **config** (`dict` ou None): Configuração de credenciais, endpoint, rate limits, etc.
* **symbol** (`str`): Par de ativos (ex: "BTCUSDT")
* **timeframe** (`str`): Timeframe desejado (ex: "1m", "15m", "1h")
* **start\_date, end\_date** (`str`): Datas para coleta (batch)
* **data\_type** (`str`): "ohlcv" (default) ou "tick" (trade/agg)
* **mode** (`str`): "batch" ou "streaming"/"real-time" (**novo, obrigatório**)
* **gap\_params** (`dict`, opcional): Parâmetros para detecção de gaps
* **outlier\_params** (`dict`, opcional): Parâmetros para detecção de outliers
* **debug** (`bool`): Logging detalhado
* **kwargs**: Parâmetros avançados (limite, offset, etc)

### 2.2 Saídas

* DataFrame padronizado (OHLCV/tick; streaming: entrega incremental por evento/callback)
* Logs de autenticação, chamadas, gaps/outliers, limites atingidos, sucesso/falha
* Eventos/callbacks em modo streaming
* Mensagem/erro em caso de exceção crítica ou bloqueio por rate limit

---

## 3. Assinatura e API

```python
class BinanceConnector:
    """
    Conector de dados da Binance API (spot/futures) para o pipeline Op_Trader — batch/streaming.
    Args:
        config (dict, optional): Configuração de credenciais/endpoint/rate limit.
        mode (str, optional): 'batch' ou 'streaming' (default: 'batch').
        gap_params (dict, optional): Configuração para gaps.
        outlier_params (dict, optional): Configuração para outliers.
        debug (bool, optional): Ativa logging detalhado.
    """
    def __init__(self, config: dict = None, mode: str = "batch", gap_params: dict = None, outlier_params: dict = None, debug: bool = False):
        ...

    def connect(self) -> bool:
        """
        Inicializa a sessão/autenticação com a API Binance via utilitário oficial do projeto.
        Returns:
            bool: True se autenticação/sessão OK, False caso contrário.
        """
        ...

    def collect(self, symbol: str, timeframe: str, start_date: str = None, end_date: str = None, data_type: str = "ohlcv", **kwargs) -> pd.DataFrame:
        """
        Coleta dados históricos (batch) ou ativa modo streaming (websocket/API stream).
        Em modo streaming, entrega incremental de novo dado, com detecção automática de gaps/outliers.
        Args:
            symbol (str): Par de ativos.
            timeframe (str): Timeframe.
            start_date (str, optional): Data inicial (batch).
            end_date (str, optional): Data final (batch).
            data_type (str, optional): "ohlcv" (default) ou "tick".
            **kwargs: Parâmetros avançados (ex: limite, offset).
        Returns:
            DataFrame: Dados coletados (batch) ou None (streaming).
        Raises:
            Exception: Em caso de erro crítico, rate limit ou autenticação.
        """
        ...

    def on_new_data(self, callback_fn) -> None:
        """
        Registra callback/evento para entrega incremental de novo dado em modo streaming.
        Args:
            callback_fn (callable): Função a ser chamada a cada novo dado coletado.
        """
        ...

    def close(self) -> None:
        """
        Encerra sessão/conexão/libera recursos via utilitário oficial do projeto.
        """
        ...
```

---

## 4. Regras, Edge Cases e Restrições

* Parâmetro `mode` define batch/streaming; obrigatório informar.
* Parâmetros `gap_params`, `outlier_params` propagados internamente.
* Em modo streaming, ativa coleta incremental via websocket ou long polling, entrega incremental por callback/evento.
* Detecção automática de gaps/outliers obrigatória a cada novo dado.
* Logging detalhado de todas as chamadas, autenticação, gaps/outliers, erros, limites atingidos.
* Retry/backoff em caso de rate limit, delays crescentes.
* Paginação automática para períodos longos (batch).
* Em falha definitiva, log crítico + raise Exception.
* DataFrame padronizado conforme schema global.
* Teste para autenticação inválida, limite excedido, intervalo inválido, dados ausentes.
* Nunca persistir dados em disco diretamente.

---

## 5. Dependências

* `src/utils/binance_connection.py` (`connect_to_binance`, `close_binance_connection`)
* requests, binance-api/python-binance (ou libs equivalentes)
* utils: logging\_utils, file\_saver

---

## 6. Exemplo de Uso

```python
from src.data.data_libs.binance_connector import BinanceConnector

# Batch
conn = BinanceConnector(config={"api_key": "xxx", "api_secret": "yyy"}, mode="batch")
conn.connect()
df = conn.collect(symbol="BTCUSDT", timeframe="1m", start_date="2022-01-01", end_date="2023-01-01", data_type="ohlcv")
conn.close()

# Streaming
conn_rt = BinanceConnector(config={...}, mode="streaming")
def on_new_tick(df):
    print("Novo tick:", df.tail(1))
conn_rt.on_new_data(on_new_tick)
conn_rt.connect()
conn_rt.collect(symbol="BTCUSDT", timeframe="1m")
```

---

## 7. Testes e Validação

* Teste de batch vs streaming (websocket/long polling, triggers/eventos)
* Teste de detecção/tratamento de gaps/outliers
* Teste de autenticação correta/errada
* Teste de coleta OHLCV/tick (batch/streaming, limites)
* Teste de rate limit, retry/backoff
* Teste de range de datas, janela móvel
* Teste de erro crítico e logging
* Teste de fechamento/liberação de recursos
* Teste para garantir que não existe código duplicado de autenticação/conexão

---

## 8. Referências e Rastreamento

* ESPEC\_CONCEITUAL\_SRC\_DATA.md
* DEVELOP\_TABLE\_SRC\_DATA.md
* tests/unit/test\_binance\_connector.py
* src/utils/binance\_connection.py

---

## 9. Checklist Inicial

* [x] Suporte total a batch e streaming
* [x] Detecção/tratamento automático de gaps/outliers
* [x] Logging, eventos e fallback diferenciados
* [x] Pronto para codificação, testes e integração

---

**Autor:** Eng. Sênior Op\_Trader
**Última atualização:** 2025-06-10 (Real-Time Ready)
**Versão do template:** 2.1

---
