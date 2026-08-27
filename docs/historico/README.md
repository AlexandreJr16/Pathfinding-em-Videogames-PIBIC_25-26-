# Documentos históricos

Preservados **sem edição**, como estavam quando foram escritos. Os documentos em `docs/` (fora
desta pasta) sintetizam e organizam o que está aqui; estes são a fonte.

## Da época do desenvolvimento

| Arquivo | Quando | O que é |
|---|---|---|
| `CONTEXTO_MODIFICACOES.md` | mar/2026 | O que mudou no sistema depois do resumo estendido da SBC — OpenMP, thread-safety do A\*, restrição da gramática a terminais relativos, log caso a caso, degradação estocástica. Escrito pelo autor, na época. |
| `log-execucao-referencia-2026-03.txt` | mar/2026 | Log da execução que gerou os dados. |
| `AI_ORCHESTRATOR.md` | jun/2026 | Índice do projeto escrito para assistentes de IA. |
| `project_walkthrough.md` | jun/2026 | Visão geral com diagrama de arquitetura. Os caminhos de arquivo que ele cita são de antes da reorganização. |
| `heuristica_full_context.md` | jun/2026 | Documentação técnica exaustiva: cada módulo, a estrutura da AST, os hiperparâmetros do AG, a lógica dos scripts Python. O documento mais detalhado sobre o código. |
| `code_review.md` | jun/2026 | Revisão crítica: 3 bugs, 4 imprecisões metodológicas, 4 preocupações de projeto. Origem de boa parte de `docs/04-problemas-conhecidos.md`. |

## Da reanálise estatística

| Arquivo | O que é |
|---|---|
| `BRIEFING_ANALISE_ESTATISTICA.md` | O briefing que motivou a reanálise: o que a orientadora pediu, o diagnóstico E1–E10, e o inventário dos dados. |
| `ANALISE_RESUMO.md` | Os achados, com a frase pronta em português para cada um. |
| `ANALISE_DADOS.md` | O que há em cada uma das 34 tabelas, análise por análise (A0–A12). |
| `ANALISE_LIMITACOES.md` | L1–L10: o que **não** foi possível computar, e por quê. |
| `ANALISE_CORRECOES_TEXTO.md` | C1–C11: trechos do `main.tex` a corrigir, com linha e redação sugerida. |
| `ANALISE_RETOMAR.md` | Manual de parada e retomada da re-síntese longa do A9. |
| `auditoria.html`, `correcoes.html` | Os mesmos conteúdos em página navegável. |

> **Sobre os links de arquivo.** Os documentos de junho/2026 (`AI_ORCHESTRATOR.md`,
> `project_walkthrough.md`, `heuristica_full_context.md`) contêm links `file://` para caminhos
> absolutos de uma pasta que não existe mais (`~/Documentos/heuristica/...`). Já estavam
> quebrados antes desta reorganização, e foram mantidos assim porque estes arquivos são
> preservados sem edição. Para achar o arquivo correspondente hoje, troque
> `heuristicas/src/` por `codigo/run-referencia-2026-03/src/` e `heuristicas/WPerformance/`
> por `analise/original-2026-03/`.

> **Sobre as citações de linha.** Referências como `main.cpp:227` ou
> `GeneticAlgorithm.cpp:19` são à **versão de março**, hoje em
> `codigo/run-referencia-2026-03/src/`, copiada para lá sem edição — os números continuam
> válidos. Referências a `main.tex:NNN` são ao fonte LaTeX do relatório, que não está neste
> repositório (só o PDF compilado, em `relatorio/`).
