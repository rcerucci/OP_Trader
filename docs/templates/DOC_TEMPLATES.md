# {{NOME_MODULO}} 

📌 {{DESCRICAO_BREVE}}

---

## 📑 Índice

- [{{NOME\_MODULO}}](#nome_modulo)
  - [📑 Índice](#-índice)
  - [⚙️ Visão Geral](#️-visão-geral)
    - [🔄 Fluxo Típico de Uso](#-fluxo-típico-de-uso)
    - [⚠️ Limitações Importantes](#️-limitações-importantes)
    - [⚡ Considerações de Performance](#-considerações-de-performance)
  - [📦 Instalação e Importação](#-instalação-e-importação)
  - [🧩 Classe Principal](#-classe-principal)
    - [🏗️ Inicialização](#️-inicialização)
      - [`__init__(self, {{PARAMETROS_INIT}})`](#__init__self-parametros_init)
    - [🔧 Métodos Principais](#-métodos-principais)
      - [`{{METODO_PRINCIPAL}}(self, {{PARAMETROS_METODO}}) -> {{TIPO_RETORNO}}`](#metodo_principalself-parametros_metodo---tipo_retorno)
      - [`{{METODO_SECUNDARIO}}(self, {{PARAMETROS_METODO_2}}) -> {{TIPO_RETORNO_2}}`](#metodo_secundarioself-parametros_metodo_2---tipo_retorno_2)
    - [📊 Métodos de Consulta](#-métodos-de-consulta)
      - [`{{METODO_CONSULTA}}(self, {{PARAMETROS_CONSULTA}}) -> {{TIPO_RETORNO_CONSULTA}}`](#metodo_consultaself-parametros_consulta---tipo_retorno_consulta)
  - [🧪 Exemplos Práticos](#-exemplos-práticos)
    - [Exemplo Básico](#exemplo-básico)
    - [Exemplo Avançado](#exemplo-avançado)
    - [Exemplo de Integração](#exemplo-de-integração)
  - [📋 Estruturas de Dados](#-estruturas-de-dados)
    - [📥 Entrada (Input)](#-entrada-input)
    - [📤 Saída (Output)](#-saída-output)
    - [🔄 Estados Internos](#-estados-internos)
  - [🛠️ Tratamento de Erros](#️-tratamento-de-erros)
    - [{{EXCECAO\_CUSTOMIZADA}}](#excecao_customizada)
    - [Cenários que Geram Exceções](#cenários-que-geram-exceções)
  - [🔧 Troubleshooting](#-troubleshooting)
    - [❌ Erros Comuns](#-erros-comuns)
      - [`{{EXCECAO_COMUM_1}}: "{{MENSAGEM_ERRO_1}}"`](#excecao_comum_1-mensagem_erro_1)
      - [`{{EXCECAO_COMUM_2}}: "{{MENSAGEM_ERRO_2}}"`](#excecao_comum_2-mensagem_erro_2)
    - [🐛 Fluxo de Debug](#-fluxo-de-debug)
    - [🧠 Melhores Práticas](#-melhores-práticas)
      - [1. {{PRATICA\_1}}](#1-pratica_1)
      - [2. {{PRATICA\_2}}](#2-pratica_2)
  - [❓ FAQ](#-faq)
    - [P: {{PERGUNTA\_FREQUENTE\_1}}?](#p-pergunta_frequente_1)
    - [P: {{PERGUNTA\_FREQUENTE\_2}}?](#p-pergunta_frequente_2)
    - [P: {{PERGUNTA\_FREQUENTE\_3}}?](#p-pergunta_frequente_3)
  - [⚡ Referência Rápida](#-referência-rápida)
    - [Métodos Essenciais](#métodos-essenciais)
    - [{{CONSTANTES\_IMPORTANTES}}](#constantes_importantes)
    - [{{ESTADOS\_VALIDOS}}](#estados_validos)
    - [{{CAMPOS\_IMPORTANTES}}](#campos_importantes)
  - [📂 Localização](#-localização)
  - [🧪 Testes](#-testes)
  - [📎 Referências Cruzadas e Rastreabilidade](#-referências-cruzadas-e-rastreabilidade)
  - [📝 Notas para o Documentador](#-notas-para-o-documentador)

---

## ⚙️ Visão Geral

{{DESCRICAO_DETALHADA}}

**Contexto no Sistema:**
{{CONTEXTO_SISTEMA}}

**Principais Funcionalidades:**
- {{FUNCIONALIDADE_1}}
- {{FUNCIONALIDADE_2}}
- {{FUNCIONALIDADE_N}}

### 🔄 Fluxo Típico de Uso

1. **{{ETAPA_1}}**: {{DESCRICAO_ETAPA_1}}
2. **{{ETAPA_2}}**: {{DESCRICAO_ETAPA_2}}
3. **{{ETAPA_3}}**: {{DESCRICAO_ETAPA_3}}
4. **{{ETAPA_N}}**: {{DESCRICAO_ETAPA_N}}

### ⚠️ Limitações Importantes

- **{{LIMITACAO_1}}**: {{EXPLICACAO_LIMITACAO_1}}
- **{{LIMITACAO_2}}**: {{EXPLICACAO_LIMITACAO_2}}
- **{{LIMITACAO_N}}**: {{EXPLICACAO_LIMITACAO_N}}

### ⚡ Considerações de Performance

- **💾 Memória**: {{CONSIDERACOES_MEMORIA}}
- **🚀 CPU**: {{CONSIDERACOES_CPU}}
- **📈 Escala**: {{CONSIDERACOES_ESCALA}}
- **🔄 Concorrência**: {{CONSIDERACOES_CONCORRENCIA}}

---

## 📦 Instalação e Importação

```python
from {{CAMINHO_MODULO}} import {{CLASSE_PRINCIPAL}}, {{EXCECAO_CUSTOMIZADA}}
```

**Dependências:**
- {{DEPENDENCIA_1}} ({{VERSAO_MINIMA_1}})
- {{DEPENDENCIA_2}} ({{VERSAO_MINIMA_2}})

**Instalação adicional (se necessário):**
```bash
{{COMANDO_INSTALACAO}}
```

---

## 🧩 Classe Principal

### 🏗️ Inicialização

#### `__init__(self, {{PARAMETROS_INIT}})`

{{DESCRICAO_CONSTRUTOR}}

**Parâmetros:**
- `{{PARAM_1}}` ({{TIPO_1}}): {{DESCRICAO_PARAM_1}}
- `{{PARAM_2}}` ({{TIPO_2}}, opcional): {{DESCRICAO_PARAM_2}}. Default = {{VALOR_DEFAULT}}

**Estado inicial:**
- {{PROPRIEDADE_1}} = {{VALOR_INICIAL_1}}
- {{PROPRIEDADE_2}} = {{VALOR_INICIAL_2}}

```python
{{EXEMPLO_INICIALIZACAO}}
```

### 🔧 Métodos Principais

#### `{{METODO_PRINCIPAL}}(self, {{PARAMETROS_METODO}}) -> {{TIPO_RETORNO}}`

{{DESCRICAO_METODO_PRINCIPAL}}

**Args:**
- `{{PARAM_1}}` ({{TIPO_1}}): {{DESCRICAO_E_RESTRICOES_1}}
- `{{PARAM_2}}` ({{TIPO_2}}): {{DESCRICAO_E_RESTRICOES_2}}

**Returns:**
{{DESCRICAO_RETORNO}}

**Raises:**
- `{{EXCECAO_CUSTOMIZADA}}`: {{QUANDO_LANCADA_1}}
- `ValueError`: {{QUANDO_LANCADA_2}}

**Exemplo:**
```python
{{EXEMPLO_USO_METODO}}
```

#### `{{METODO_SECUNDARIO}}(self, {{PARAMETROS_METODO_2}}) -> {{TIPO_RETORNO_2}}`

{{DESCRICAO_METODO_SECUNDARIO}}

**Args:**
- `{{PARAM_SEC_1}}` ({{TIPO_SEC_1}}): {{DESCRICAO_PARAM_SEC_1}}

**Returns:**
{{DESCRICAO_RETORNO_SEC}}

**Exemplo:**
```python
{{EXEMPLO_METODO_SECUNDARIO}}
```

### 📊 Métodos de Consulta

#### `{{METODO_CONSULTA}}(self, {{PARAMETROS_CONSULTA}}) -> {{TIPO_RETORNO_CONSULTA}}`

{{DESCRICAO_METODO_CONSULTA}}

**Args:**
- `{{PARAM_CONS_1}}` ({{TIPO_CONS_1}}): {{DESCRICAO_PARAM_CONS_1}}

**Returns:**
{{DESCRICAO_RETORNO_CONSULTA}}

**Exemplo:**
```python
{{EXEMPLO_CONSULTA}}
```

---

## 🧪 Exemplos Práticos

### Exemplo Básico

```python
# {{COMENTARIO_EXEMPLO_BASICO}}
{{CODIGO_EXEMPLO_BASICO}}

# {{RESULTADO_ESPERADO}}
print({{RESULTADO}})
# {{SAIDA_ESPERADA}}
```

### Exemplo Avançado

```python
# {{CENARIO_COMPLEXO}}
{{CODIGO_EXEMPLO_AVANCADO}}

# {{EXPLICACAO_RESULTADO_AVANCADO}}
```

### Exemplo de Integração

```python
# {{COMO_USAR_COM_OUTROS_MODULOS}}
{{CODIGO_INTEGRACAO}}
```

---

## 📋 Estruturas de Dados

### 📥 Entrada (Input)

{{DESCRICAO_ENTRADA}}

```python
{
    "{{CAMPO_ENTRADA_1}}": {{TIPO_ENTRADA_1}},  # {{DESCRICAO_CAMPO_1}}
    "{{CAMPO_ENTRADA_2}}": {{TIPO_ENTRADA_2}},  # {{DESCRICAO_CAMPO_2}}
}
```

### 📤 Saída (Output)

{{DESCRICAO_SAIDA}}

```python
{
    "{{CAMPO_SAIDA_1}}": {{TIPO_SAIDA_1}},  # {{DESCRICAO_SAIDA_1}}
    "{{CAMPO_SAIDA_2}}": {{TIPO_SAIDA_2}},  # {{DESCRICAO_SAIDA_2}}
}
```

### 🔄 Estados Internos

{{DESCRICAO_ESTADOS}}

```python
{
    "{{PROPRIEDADE_INTERNA_1}}": {{TIPO_PROP_1}},  # {{DESCRICAO_PROP_1}}
    "{{PROPRIEDADE_INTERNA_2}}": {{TIPO_PROP_2}},  # {{DESCRICAO_PROP_2}}
}
```

---

## 🛠️ Tratamento de Erros

### {{EXCECAO_CUSTOMIZADA}}

{{DESCRICAO_EXCECAO}}

```python
try:
    {{OPERACAO_QUE_PODE_FALHAR}}
except {{EXCECAO_CUSTOMIZADA}} as e:
    print(f"Erro específico: {e}")
```

### Cenários que Geram Exceções

| Exceção / Erro | Causa | Solução Sugerida |
|---------------|-------|------------------|
| `{{EXCECAO_1}}` | {{CAUSA_1}} | {{SOLUCAO_1}} |
| `{{EXCECAO_2}}` | {{CAUSA_2}} | {{SOLUCAO_2}} |

---

## 🔧 Troubleshooting

### ❌ Erros Comuns

#### `{{EXCECAO_COMUM_1}}: "{{MENSAGEM_ERRO_1}}"`
- **Causa**: {{EXPLICACAO_CAUSA_1}}
- **Solução**: {{COMO_RESOLVER_1}}
- **Prevenção**: {{COMO_EVITAR_1}}

#### `{{EXCECAO_COMUM_2}}: "{{MENSAGEM_ERRO_2}}"`
- **Causa**: {{EXPLICACAO_CAUSA_2}}
- **Solução**: {{COMO_RESOLVER_2}}
- **Debug**: {{COMO_INVESTIGAR_2}}

### 🐛 Fluxo de Debug

```python
def debug_{{NOME_MODULO_LOWER}}(instancia, {{PARAMETROS_DEBUG}}):
    """Função utilitária para debug do {{NOME_MODULO}}"""
    
    print("=== 🐛 DEBUG {{NOME_MODULO}} ===")
    
    # {{VERIFICACOES_ESTADO}}
    {{CODIGO_DEBUG}}
    
    print("=" * 30)

# Exemplo de uso
debug_{{NOME_MODULO_LOWER}}(instancia, {{ARGUMENTOS_DEBUG}})
```

### 🧠 Melhores Práticas

#### 1. {{PRATICA_1}}
```python
# ✅ CERTO: {{EXPLICACAO_CERTO_1}}
{{CODIGO_CORRETO_1}}

# ❌ ERRADO: {{EXPLICACAO_ERRADO_1}}
{{CODIGO_INCORRETO_1}}
```

#### 2. {{PRATICA_2}}
```python
# ✅ CERTO: {{EXPLICACAO_CERTO_2}}
{{CODIGO_CORRETO_2}}

# ❌ ERRADO: {{EXPLICACAO_ERRADO_2}}
{{CODIGO_INCORRETO_2}}
```

---

## ❓ FAQ

### P: {{PERGUNTA_FREQUENTE_1}}?
**R:** {{RESPOSTA_DETALHADA_1}}

### P: {{PERGUNTA_FREQUENTE_2}}?
**R:** {{RESPOSTA_DETALHADA_2}}

### P: {{PERGUNTA_FREQUENTE_3}}?
**R:** {{RESPOSTA_DETALHADA_3}}

---

## ⚡ Referência Rápida

### Métodos Essenciais
```python
instancia = {{CLASSE_PRINCIPAL}}({{ARGS_INIT}})     # {{DESCRICAO_INIT}}
instancia.{{METODO_1}}({{ARGS_1}})                  # {{DESCRICAO_METODO_1}}
instancia.{{METODO_2}}({{ARGS_2}})                  # {{DESCRICAO_METODO_2}}
instancia.{{METODO_CONSULTA}}()                     # {{DESCRICAO_CONSULTA}}
```

### {{CONSTANTES_IMPORTANTES}}
- `{{CONSTANTE_1}}` - {{DESCRICAO_CONSTANTE_1}}
- `{{CONSTANTE_2}}` - {{DESCRICAO_CONSTANTE_2}}

### {{ESTADOS_VALIDOS}}
- `"{{ESTADO_1}}"` - {{DESCRICAO_ESTADO_1}}
- `"{{ESTADO_2}}"` - {{DESCRICAO_ESTADO_2}}

### {{CAMPOS_IMPORTANTES}}
- `{{CAMPO_1}}` - {{DESCRICAO_CAMPO_1}}
- `{{CAMPO_2}}` - {{DESCRICAO_CAMPO_2}}

---

## 📂 Localização

```bash
{{CAMINHO_ARQUIVO}}
```

---

## 🧪 Testes

Resumo do teste associado:

- **Arquivo**: `{{CAMINHO_TESTE}}`
- **Casos testados**: {{CASOS_TESTADOS}}
- **Cobertura mínima esperada**: ≥ {{COBERTURA_MINIMA}}%

```python
# Exemplo de teste básico
{{EXEMPLO_TESTE}}
```

---

## 📎 Referências Cruzadas e Rastreabilidade

**Para documentação robusta e rastreável, inclua sempre:**

- Link direto para o SPEC do módulo, se houver (ex: [`docs/specs/SPEC_NomeModulo.md`](../../docs/specs/SPEC_NomeModulo.md))
- Link para o teste principal associado (ex: [`tests/integration/test_nome_modulo.py`](../../../tests/integration/test_nome_modulo.py))
- Versão do template utilizado
- Data da última atualização
- Autor/responsável

**Exemplo de bloco sugerido:**

```markdown
---

### 🔗 Rastreabilidade e Referências

- **SPEC Técnico:** [`docs/specs/SPEC_PositionManager.md`](../../docs/specs/SPEC_PositionManager.md)
- **Teste de Integração:** [`tests/integration/test_position_manager.py`](../../../tests/integration/test_position_manager.py)
- **README Geral:** [`../../README.md`](../../README.md)
- **CONTRIBUTING:** [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md)
- **Template usado:** `DOC_TEMPLATES.md v2.0`
- **Última atualização:** 2025-06-06
- **Autor:** Marcos Cerucci / Equipe Op_Trader

---

## ✍️ Autor

**Equipe de Desenvolvimento RL Trading** — documento mantido conforme:

- [`README.md`]({{LINK_README}})
- [`CONTRIBUTING.md`]({{LINK_CONTRIBUTING}})
- [`{{DOCUMENTO_REFATORACAO}}`]({{LINK_REFATORACAO}})

🗓️ **Última atualização**: {{DATA_ATUALIZACAO}}

---

*Documentação criada seguindo template  v2.0*

---

## 🤖 Tags para Automatização

```yaml
# Metadados para geração automática
module_name: "{{NOME_MODULO}}"
module_path: "{{CAMINHO_MODULO}}"
main_class: "{{CLASSE_PRINCIPAL}}"
test_path: "{{CAMINHO_TESTE}}"
dependencies: ["{{DEPENDENCIA_1}}", "{{DEPENDENCIA_2}}"]
version: "{{VERSAO_MODULO}}"
last_updated: "{{DATA_ATUALIZACAO}}"
documentation_version: "2.0"
template_type: "hybrid"
```

---

## 📝 Notas para o Documentador

**Instruções de uso:**

1. **Substitua todas as tags** `{{VARIAVEL}}` pelo conteúdo específico
2. **Mantenha todos os emojis** para facilitar navegação visual
3. **Use a seção de metadados YAML** para automatização
4. **Teste todos os códigos** antes de publicar
5. **Remova esta seção** "Notas para o Documentador" na versão final

**Para automatização:**
- Tags seguem padrão `{{NOME_VARIAVEL}}`
- Metadados YAML facilitam parsing
- Estrutura consistente permite templates dinâmicos