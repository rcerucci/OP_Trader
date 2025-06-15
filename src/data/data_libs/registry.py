# src/data/data_libs/registry.py

"""
Registro central de conectores de brokers para o DataCollector do Op_Trader.
Permite plugabilidade/extensão sem alteração do orquestrador.
"""

from src.data.data_libs.mt5_connector import MT5Connector
# from src.data.data_libs.binance_connector import BinanceConnector
# Outros brokers podem ser importados e registrados abaixo

BROKER_CONNECTORS = {
    "mt5": MT5Connector,
    # "binance": BinanceConnector,
    # "outrobroker": OutroBrokerConnector,
}
