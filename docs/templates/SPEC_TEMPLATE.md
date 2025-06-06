# PositionManager — Technical Specification (SPEC.md)

## Docstring Padrão do Projeto

```python
"""
src/env/env_libs/execution/position_manager.py
Gerenciamento de posições (abertura, modificação e encerramento) para ambientes de reforço em trading no sistema Op_Trader.
Compatível com múltiplos ativos (multimercado), incluindo precisão variável de preço por símbolo.
Autor: Developers Team
Data: 2025-06-04
"""
```

---

## 1. Objetivo

Este módulo é responsável pelo **gerenciamento completo de posições de trading**, sendo utilizado no **pipeline de execução** para **controlar abertura, modificação e encerramento de posições** em ambientes de trading automatizado. Integra-se com **RiskManager, Logger e State** e serve como **componente central de execução** no sistema Op_Trader.

**Funcionalidades principais:**
- Abertura de posições (long/short)
- Modificação de posições existentes (stop loss, take profit)
- Encerramento de posições (parcial/total)
- Suporte multimercado com precisão dinâmica por símbolo
- Validação de regras de risco antes da execução

---

## 2. Entradas

| Parâmetro | Tipo | Obrigatório | Descrição | Exemplo |
|-----------|------|-------------|-----------|---------|
| symbol | str | Sim | Símbolo do ativo a ser negociado | "EURUSD" |
| action | str | Sim | Ação a ser executada ("open", "modify", "close") | "open" |
| position_type | str | Condicional | Tipo da posição ("long", "short") - obrigatório para "open" | "long" |
| volume | float | Condicional | Volume da posição - obrigatório para "open" | 0.1 |
| price | float | Não | Preço de execução (None para market price) | 1.08450 |
| stop_loss | float | Não | Nível de stop loss | 1.08000 |
| take_profit | float | Não | Nível de take profit | 1.09000 |
| position_id | int | Condicional | ID da posição - obrigatório para "modify"/"close" | 12345 |

---

## 3. Saídas

| Nome | Tipo | Descrição | Exemplo |
|------|------|-----------|---------|
| success | bool | Status de sucesso da operação | True |
| position_id | int | ID único da posição criada/modificada | 12345 |
| executed_price | float | Preço real de execução | 1.08452 |
| message | str | Mensagem descritiva do resultado | "Position opened successfully" |
| timestamp | datetime | Timestamp da execução | 2025-06-04T10:30:15.123456 |

---

## 4. Exceções e Validações

| Caso | Exceção/Retorno | Descrição |
|------|-----------------|-----------|
| Symbol inválido | ValueError | Erro se símbolo não existe ou formato inválido |
| Volume <= 0 | ValueError | Volume deve ser positivo para abertura |
| Position não encontrada | PositionNotFoundError | ID da posição não existe para modify/close |
| Margem insuficiente | InsufficientMarginError | Não há margem suficiente para a operação |
| Mercado fechado | MarketClosedError | Tentativa de operar fora do horário |
| Action inválida | ValueError | Action deve ser "open", "modify" ou "close" |

---

## 5. Docstring Padrão (Google Style)

```python
def manage_position(
    self,
    symbol: str,
    action: str,
    position_type: Optional[str] = None,
    volume: Optional[float] = None,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    position_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Gerencia posições de trading (abertura, modificação, encerramento).
    
    Args:
        symbol (str): Símbolo do ativo (ex: "EURUSD", "USDJPY").
        action (str): Ação a executar ("open", "modify", "close").
        position_type (str, optional): Tipo da posição ("long", "short"). 
            Obrigatório para action="open".
        volume (float, optional): Volume da posição. 
            Obrigatório para action="open".
        price (float, optional): Preço de execução. None para market price.
        stop_loss (float, optional): Nível de stop loss.
        take_profit (float, optional): Nível de take profit.
        position_id (int, optional): ID da posição. 
            Obrigatório para action="modify"/"close".
    
    Returns:
        Dict[str, Any]: Dicionário com resultado da operação contendo:
            - success (bool): Status de sucesso
            - position_id (int): ID da posição
            - executed_price (float): Preço de execução
            - message (str): Mensagem descritiva
            - timestamp (datetime): Timestamp da operação
    
    Raises:
        ValueError: Se parâmetros obrigatórios estão ausentes ou inválidos.
        PositionNotFoundError: Se position_id não existe.
        InsufficientMarginError: Se não há margem suficiente.
        MarketClosedError: Se mercado está fechado.
    
    Example:
        >>> pm = PositionManager()
        >>> result = pm.manage_position("EURUSD", "open", "long", 0.1)
        >>> print(result["success"])
        True
    """
```

---

## 6. Exemplo de Uso

```python
from src.env.env_libs.execution.position_manager import PositionManager

# Inicializar o gerenciador
pm = PositionManager()

# Exemplo 1 - Abertura de posição
result = pm.manage_position(
    symbol="EURUSD",
    action="open",
    position_type="long",
    volume=0.1,
    stop_loss=1.08000,
    take_profit=1.09000
)
print(f"Posição aberta: {result['position_id']}")

# Exemplo 2 - Modificação de posição
result = pm.manage_position(
    symbol="EURUSD",
    action="modify",
    position_id=12345,
    stop_loss=1.08100,  # Novo stop loss
    take_profit=1.09200  # Novo take profit
)

# Exemplo 3 - Encerramento de posição
result = pm.manage_position(
    symbol="EURUSD",
    action="close",
    position_id=12345
)

# Exemplo 4 - Tratamento de erros
try:
    result = pm.manage_position("INVALID", "open", "long", 0.1)
except ValueError as e:
    print(f"Erro de validação: {e}")
except MarketClosedError as e:
    print(f"Mercado fechado: {e}")
```

---

## 7. Regras de Negócio e Observações

- **Precisão dinâmica:** O módulo detecta automaticamente a precisão de preço por símbolo (2-5 casas decimais)
- **Validação de margem:** Sempre valida margem disponível antes de abrir posições
- **Multimercado:** Suporta operação simultânea em múltiplos símbolos
- **Thread-safe:** Implementa locks para operações concorrentes
- **Auditoria completa:** Gera logs detalhados para todas as operações
- **Market/Limit orders:** Suporta tanto ordens a mercado quanto com preço específico
- **Horário de funcionamento:** Respeita horários de mercado por símbolo
- **Risk management:** Integra com RiskManager para validações adicionais

---

## 8. Edge Cases

- **Volume zero ou negativo:** Rejeita com ValueError
- **Preços inválidos:** Valida se preços estão dentro de ranges aceitáveis
- **Position ID inexistente:** Retorna PositionNotFoundError específico
- **Símbolo não configurado:** Verifica se símbolo existe na configuração
- **Modificação de posição fechada:** Detecta e rejeita modificações em posições já encerradas
- **Operações simultâneas:** Usa locks para evitar race conditions
- **Conexão perdida:** Implementa retry automático com circuit breaker
- **Valores None inesperados:** Valida todos os parâmetros obrigatórios

---

## 9. Dependências

**Depende de:**
- `src/core/logger.py` - Sistema de logging padronizado
- `src/core/state_manager.py` - Gerenciamento de estado das posições
- `src/env/env_libs/risk/risk_manager.py` - Validações de risco
- `src/utils/market_utils.py` - Utilitários de mercado e precisão
- `src/config/trading_config.py` - Configurações de trading

**Não deve depender de:**
- Interface gráfica ou elementos UI
- Acesso direto ao banco de dados (usa State Manager)
- Bibliotecas de machine learning
- Conexões de rede diretas (usa abstrações)

---

## 10. Checklist de Qualidade (conforme CONTRIBUTING.md)

- [x] Código segue PEP 8 e convenções do projeto
- [x] Imports absolutos utilizando `src.` como raiz
- [x] Type hints em todas as funções públicas
- [x] Docstrings padrão Google em todas as funções/classes públicas
- [x] Testes para inputs válidos, edge cases e tratamento de erros
- [x] Logging implementado (DEBUG para traces, INFO para operações, ERROR para falhas)
- [x] Tratamento explícito de erros com exceções customizadas
- [x] Nomenclatura consistente (snake_case para funções, PascalCase para classes)
- [x] Cobertura de testes > 90% comprovada
- [x] Exemplos de uso documentados e testados

---

## 11. Histórico

| Data | Autor | Alteração |
|------|-------|-----------|
| 2025-06-04 | Developers Team | Criação inicial do módulo |
| 2025-06-05 | Developers Team | Adição de suporte multimercado |
| 2025-06-06 | Developers Team | Implementação de precisão dinâmica |

---

## Como Usar Este Template

**Para criar uma nova especificação:**

1. **Copie este arquivo** e renomeie para `SPEC_[nome_do_modulo].md`
2. **Substitua "PositionManager"** pelo nome do seu módulo
3. **Atualize a docstring** com o caminho e descrição corretos
4. **Preencha as tabelas** com os parâmetros reais do seu módulo
5. **Adapte os exemplos** para refletir o uso real
6. **Revise as regras de negócio** específicas do módulo
7. **Valide o checklist** antes de finalizar
8. **Remova esta seção** na versão final

**Estrutura de pastas sugerida:**
```
docs/
├── specs/
│   ├── SPEC_PositionManager.md
│   ├── SPEC_RiskManager.md
│   └── SPEC_[seu_modulo].md
└── templates/
    └── SPEC_template.md (este arquivo)
```

## ⚠️ Nota:
Este template é genérico para qualquer módulo do projeto.  
Adapte todas as seções, exemplos e tabelas conforme o fluxo, requisitos e contratos do módulo que você está especificando.