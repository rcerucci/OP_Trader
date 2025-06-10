# 📏 DIRETIVA OFICIAL DE CODIFICAÇÃO — `src/env/`

## 1. Obediência Estrita ao Padrão de Projeto

* NUNCA iniciar ou aprovar codificação sem antes:

  * Ter SPEC.md completo, versionado e validado (template: `SPEC_TEMPLATE.md`)
  * Checklist de arquitetura e integração preenchido (conforme `DEVELOPMENT_FLOW.md`)

## 2. Processo de Desenvolvimento Modular e Auditável

Todo novo componente ou alteração em `src/env/` deve obrigatoriamente seguir este fluxo:

1. **Planejamento e Especificação**

   * Definir claramente objetivo, entradas, saídas, integrações, edge cases, performance e dependências.
   * Usar o template SPEC (nunca começar a codificar sem SPEC validado).
2. **Desenho de API e Contratos**

   * Esboçar assinaturas, classes, interfaces e docstrings no padrão Google.
   * Revisar dependências e impactos na arquitetura (injeção, factory, integração).
3. **Implementação Modular**

   * Cada módulo/função/classe deve ser implementado com:

     * Type hints e docstrings completos
     * Validação explícita de entrada
     * Logging estruturado
     * Tratamento robusto de erros
     * Conformidade absoluta com naming convention
     * Separação clara de responsabilidades
4. **Testes Unitários e de Integração**

   * Implementar testes para todos os fluxos (válidos, inválidos, edge cases).
   * Todos os testes devem produzir logs e outputs reais (auditorias).
   * Testes de integração obrigatórios usando o template de integração.
5. **Auditoria e Evidência**

   * Salvar todos os logs, evidências e outputs de teste nos diretórios certos.
   * Validar e versionar evidências junto ao código.
6. **Documentação e Cross-Referências**

   * Atualizar README, SPEC e documentação técnica de todos os componentes tocados.
   * Inserir referências cruzadas para cada SPEC, teste, config e log relevante.
7. **Checklist Final de Qualidade**

   * NÃO permitir merge/push sem checklist completo, revisão cruzada e evidências versionadas.

## 3. Padrões Técnicos Invioláveis

* Imports sempre absolutos
* Docstring Google Style obrigatória em tudo
* Logging padronizado, auditável, sem dados sensíveis
* Testes >90% de cobertura, com edge cases
* Flag `--debug` obrigatória em scripts
* Naming convention consistente e paths sincronizados
* Todos exemplos e configs sempre testados

## 4. Validação e Revisão

* Código só é aprovado com:

  * Checklist de codificação e integração preenchido
  * Revisão por outro Engenheiro Sênior (não pode ser autoaprovado)
  * Evidência de execução (logs, arquivos, prints, outputs)
  * Atualização de README e SPEC correspondente

## 5. Automação e Compliance

* Executar scripts de lint, security scan, tests e benchmarks a cada alteração relevante.
* Validação automática e manual de todos exemplos e paths de integração.
* Referenciar todos os templates, padrões e artefatos no início de cada módulo/código.

---

## Checklist Sintético para Processo de Codificação — src/env/

```markdown
# Checklist de Codificação src/env/

- [ ] SPEC.md validado e versionado
- [ ] Planejamento auditável registrado (objetivo, entradas, saídas, integrações)
- [ ] Assinaturas e API desenhadas conforme padrão
- [ ] Implementação com type hints, docstrings, logging e tratamento de erro robustos
- [ ] Testes unitários e de integração criados e executados
- [ ] Logs e outputs de teste salvos e versionados
- [ ] Documentação (README/SPEC) atualizada e referenciada
- [ ] Checklist final preenchido e aprovado por outro Engenheiro Sênior
```

---

## Resumo da Diretiva

> **NUNCA codifique, altere ou aprove qualquer parte de `src/env/` sem SPEC validada, checklist completo, evidência versionada, revisão cruzada e total aderência aos templates e fluxos definidos.**
> **Toda codificação deve ser auditável, rastreável e compatível com a arquitetura enterprise do Op\_Trader.**
