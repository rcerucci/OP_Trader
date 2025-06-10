# 🏷️ TAGS\_INDEX.md — Significado Oficial das TAGs de Estado

Tabela de referência para interpretação dos estados (`Estado`) utilizados nos documentos `REFERENCE_TABLE.md` e `DEVELOP_TABLE.md`.

Cada tag representa um **estado do ciclo de vida** de uma função, classe ou módulo no projeto Op\_Trader.

---

## 🔄 TAGs Compartilhadas (ambas as tabelas)

| Tag      | Aplicável a            | Significado                                                               |
| -------- | ---------------------- | ------------------------------------------------------------------------- |
| `@CODED` | `REFERENCE`, `DEVELOP` | Implementado, documentado e com SPEC, mas ainda não validado oficialmente |

---

## 📘 TAGs da `REFERENCE_TABLE.md`

| Tag       | Significado                                                                |
| --------- | -------------------------------------------------------------------------- |
| `@STABLE` | Validado, revisado, testado e aprovado para uso e exposição pública        |
| `@LEGACY` | Código antigo, anterior ao sistema atual de validação, pendente de revisão |

---

## 🚧 TAGs da `DEVELOP_TABLE.md`

| Tag       | Significado                                                                 |
| --------- | --------------------------------------------------------------------------- |
| `@IDEA`   | Ideia ainda informal, sem SPEC                                              |
| `@PLAN`   | Planejado para desenvolvimento, mas sem SPEC final                          |
| `@SPEC`   | Com SPEC formal criado e aprovado                                           |
| `@CODE`   | Em codificação (em PR ou branch ativo)                                      |
| `@TEST`   | Em fase de testes (unitários ou integração)                                 |
| `@REVIEW` | Em revisão técnica ou aguardando aprovação de PR                            |
| `@DONE`   | Pronto para ser movido para `REFERENCE_TABLE.md` como `@CODED` ou `@STABLE` |

---
