# CHECKLIST\_DE\_DESENVOLVIMENTO\_DE\_CODIGO.md — Op\_Trader

> Checklist oficial do fluxo de desenvolvimento, teste e rastreabilidade de módulos no Op\_Trader, já incluindo todas as melhores práticas, ações para dependências não enviadas e automação de execução de testes.

---

## 1. Hierarquização e Sequenciamento

* [ ] Analisar DEVELOP\_TABLE.md e definir a ordem/hierarquia dos módulos.
* [ ] Registrar sequência de produção (bottom-up: dos utilitários para os ambientes/wrappers).

## 2. Ciclo Automatizado por Módulo

Para **cada módulo da ordem definida**:

* [ ] Selecionar o próximo módulo e solicitar/validar a SPEC respectiva.
* [ ] Validar SPEC (template, exemplos, edge cases).
* [ ] Caso o módulo tenha imports de dependências ainda não enviadas (e não cobertas na REFERENCE\_TABLE.md):

  * [ ] Solicitar imediatamente o código do(s) módulo(s) dependente(s).
* [ ] **Implementar e exibir no chat:**

  * [ ] **Código-fonte completo do módulo** (com todos comentários, docstrings, logging, edge cases, etc.)
  * [ ] **Código dos testes pytest (unitários/integrados)**
  * [ ] **Comando para executar o teste pytest**
* [ ] Gerar SPEC .md atualizada e salva na aba lateral/canvas.
* [ ] Implementar e executar os testes, mostrando logs e resultados.
* [ ] Validar outputs e logs conforme padrão.
* [ ] Marcar como @CODE na DEVELOP\_TABLE.md.
* [ ] Registrar ciclo, decisões e evidências no DEV\_LOG.md.

## 3. Rastreabilidade e Auditoria

* [ ] Ao final do ciclo, atualizar de uma vez só a REFERENCE\_TABLE.md com estado @STABLE dos módulos finalizados.
* [ ] Validar todas as SPECs, logs e evidências salvos na aba lateral.
* [ ] Sincronizar DEVELOP\_TABLE.md, DEV\_LOG.md, TAGS\_INDEX.md, README.md, docs/specs/.

## 4. Homologação e Sucesso

* [ ] Revisão técnica final registrada (responsável e data).
* [ ] Todos os testes passaram, edge cases cobertos.
* [ ] Todos rastreamentos/documentos sincronizados.
* [ ] Ciclo de sucesso repetido para todos módulos até 100% @STABLE.

---

## YAML Workflow (para automação e revisão ágil)

```yaml
- Para cada módulo:
    - Selecionar módulo e pedir SPEC
    - Validar SPEC
    - Para cada dependência não enviada/importada:
        - Solicitar código do módulo dependente
    - Mostrar no chat:
        - Código-fonte do módulo
        - Código dos testes pytest
        - Comando pytest para rodar os testes
    - Gerar SPEC .md na aba lateral
    - Executar testes e mostrar logs
    - Validar outputs e logs
    - Marcar @CODE na DEVELOP_TABLE.md
    - Atualizar DEV_LOG.md
- Ao fim do ciclo:
    - Atualizar REFERENCE_TABLE.md para @STABLE
    - Revisar e homologar rastreamentos
```

---

> **Aplique este checklist rigorosamente em cada ciclo de desenvolvimento, garantindo que nada seja deixado para trás, especialmente dependências e automação de execução de testes.**
