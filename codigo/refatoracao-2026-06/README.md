# Código refatorado — junho/2026

⚠️ **Esta versão nunca executou o experimento completo. Nenhum número do relatório vem daqui.**

Era o `HEAD` do repositório público (commits `fed66f5` e `198b984`, 02/06/2026) até a
reorganização de agosto. Foi mantida porque contém correções de bugs reais — mas **não
reproduz os resultados publicados**, por três motivos:

1. adiciona uma etapa de **Simulated Annealing** depois do algoritmo genético, mudando a
   fórmula final;
2. adiciona quatro **modos de operação** (`--mode absolute|delta|admissibility|hybrid`);
3. acrescenta as colunas `implementacao` e `modo` a todos os CSVs, e troca as colunas de
   `resultados_sintese.csv` — **esquema incompatível** com os dados publicados.

Tabela completa das diferenças em `docs/00-PROVENIENCIA.md`.

```fish
make refatoracao    # -> bin/pathfinding-refatorado
make testes         # roda tests/ — 2 casos
```

`tests/` é a única parte do projeto com teste automatizado: um framework mínimo
(`test_framework.h`, ~40 linhas) com dois casos sobre as heurísticas.

Os bugs que esta versão corrige — e os dois que ela introduz (P9, P10) — estão em
`docs/04-problemas-conhecidos.md` e, com o diagnóstico completo, em
`docs/historico/code_review.md`.
