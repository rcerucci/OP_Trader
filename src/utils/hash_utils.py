# src/utils/hash_utils.py

import hashlib
import json

def generate_config_hash(config: dict, length: int = 10) -> str:
    """
    Gera um hash estável (SHA256 truncado) a partir de um dicionário de configuração.
    Args:
        config (dict): Dicionário de configuração (ex: snapshot do pipeline)
        length (int): Tamanho do hash truncado (default: 10)
    Returns:
        str: Hash alfanumérico (ex: 'ab12c34d5e')
    """
    # Serialização estável (ordenação por chave)
    config_str = json.dumps(config, sort_keys=True, separators=(',', ':'))
    hash_full = hashlib.sha256(config_str.encode('utf-8')).hexdigest()
    return hash_full[:length]
