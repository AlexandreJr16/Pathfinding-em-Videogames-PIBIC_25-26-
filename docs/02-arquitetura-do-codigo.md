# Arquitetura do código

Descreve **`codigo/run-referencia-2026-03/`**, o código que gerou os dados. Onde a versão de
junho difere de forma relevante, há uma nota. Ver `docs/00-PROVENIENCIA.md` para o porquê de
existirem três árvores.

---

## O caminho de um dado, do `.map` até a tabela

```
maps/den011d.map              arquivo HOG: cabeçalho + grade de '.' e '@'
        │
        │  loadMap()                                          map.cpp
        ▼
   grid[][]  (bool global)  +  originalTraversableCells
        │
        ├──────────────────────────────────────────┐
        │                                          │
        ▼  síntese, 1× por mapa                    ▼  degradação, por padrão × nível
   HeuristicGrammar ──► GeneticAlgorithm      degradaMapa*()                map.cpp
   (gera ASTs)          (80 indivíduos,       bloqueia células
        │                100 gerações)         cumulativamente
        │                     │                     │
        │                     ▼                     ▼
        │              currentFormula          grid[][] degradado
        │              (AST campeã)                  │
        └─────────────────────┴───────────┬──────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
                    aStar(start, goal, h)           verificaPontosConectados()
                    h ∈ {Manhattan, Fórmula,        (filtro: o par ainda
                         Memória, Zero}              tem caminho?)
                          │                                map.cpp
                          ▼  astar.cpp
                  SearchResult{ path, expansions }
                          │
                          ▼  main.cpp
              resultados_{base,robustez,ratio,sintese}.csv
                          │
                          ▼  analise/estatistica-2026-08/scripts/
                   tabelas/*.csv  +  figuras/*.pdf
```

Os quatro CSVs são a **única interface** entre o C++ e o Python. Nenhum script Python invoca o
binário do experimento; nenhum código C++ lê os resultados. Essa separação foi deliberada e é
o que tornou possível refazer toda a estatística em agosto sem tocar no C++.

---

## Núcleo C++ (`codigo/run-referencia-2026-03/src/`)

### `map.h` / `map.cpp` — a grade e as degradações

Estado **global**: `grid`, `height`, `width`, `originalTraversableCells`. Não é elegante, mas é
o que permite que `aStar` e as heurísticas leiam o mapa sem passá-lo por parâmetro.

| Função | O que faz |
|---|---|
| `loadMap(arquivo)` | lê o formato HOG; `grid[i][j] = (caractere == '.')` — **só `'.'` é transitável**, todo o resto (`@`, `T`, `S`, `W`) é bloqueio |
| `verificaPontosConectados(s, g)` | BFS de conectividade; é o filtro que decide quais pares sobrevivem à degradação |
| `radialObstacle` / `degradaMapa` | discos |
| `linearObstacle` / `degradaMapaLinear` | barreiras retas |
| `sparseObstacle` / `degradaMapaSparse` | discos com densidade 0,4 |
| `organicObstacle` / `degradaMapaOrganic` | passeios aleatórios |
| `degradaMapaSaunders` | células individuais sorteadas |

As cinco `degrada*` compartilham o mesmo contrato: recebem **quantas células ainda faltam
bloquear** e chamam a primitiva correspondente em laço até atingir o alvo, com um teto de
tentativas para não travar em mapa saturado. É por isso que `main.cpp` consegue aplicar
degradação cumulativa passando apenas a *diferença* entre um nível e o anterior.

Todas usam `rand()` (o gerador global do C), semeado por `srand(semente)` em `main.cpp`. Isso
mistura duas famílias de gerador no mesmo programa — ver P4.

### `astar.h` / `astar.cpp` — a busca

`aStar(start, goal, h_func)` → `SearchResult{ path, expansions }`.

Três características que importam para ler os resultados:

1. **É puramente funcional e thread-safe.** Todo o estado (`fechado`, `pai`, `melhorG`, fila) é
   local. Foi isso que permitiu paralelizar a avaliação da população do AG com OpenMP.
2. **Fila de prioridade com desempate de Saunders** (`comparadorTipoNo`): a `f` menor vence;
   empatou, vence o **maior `g`** — ou seja, prefere o nó mais profundo, o que reduz expansões
   em platôs. Está em `astar.h`, dentro do comparador.
3. **Nós obsoletos são descartados na saída da fila** (`if (atual.g != melhorG[...]) continue;`),
   e não por uma operação de *decrease-key*. `expansions` conta apenas os nós efetivamente
   expandidos, então a contagem é comparável entre heurísticas.

A heurística entra por `std::function`, o que custa uma chamada indireta por vizinho mas mantém
uma única implementação de A\* para as quatro heurísticas — nenhuma delas ganha vantagem por
estar num laço especializado.

### `heuristics.h` / `heuristics.cpp` — as quatro heurísticas

| Função | Nota |
|---|---|
| `heuristicaManhattan` | `\|Δlinha\| + \|Δcoluna\|` |
| `heuristicaZero` | sempre 0 — transforma o A\* em **Dijkstra**, usado para obter o caminho ótimo e o baseline de expansões |
| `heuristicaMemoryBased` | máximo de `\|dS − dG\|` sobre os pivôs; **pula pivôs inalcançáveis** (`d == -1`) |
| `heuristicaFormula` | avalia a AST em `currentFormula`; se for nula, cai num *fallback* `75 · max(dx,dy)` |
| `generatePivots(n)` | Farthest-First; o **primeiro pivô é sorteado uniformemente** |
| `bfsPivo` / `computarDistPivos` / `computarDistPivosFixos` | pré-computação das distâncias |

Dois detalhes com consequência empírica grande, ambos investigados na reanálise:

- **`heuristicaMemoryBased` pula pivôs inalcançáveis.** Se *nenhum* pivô for alcançável a
  partir dos dois extremos, o máximo fica em 0 e `h ≡ 0` — o A\* silenciosamente vira Dijkstra.
  É a causa exata do desvio-padrão anômalo de 138,44 no relatório (achado A11, P8).
- **`computarDistPivosFixos` recebe as *posições* dos pivôs, mas roda `bfsPivo` de novo** sobre
  a grade atual. Sob degradação, isso significa recalcular todas as distâncias no mapa já
  modificado — o oposto do que o relatório afirma (achado A0, P1).

### `synthesis/` — programação genética

Tradução de MATLAB para C++ do código de **Saunders (2024)**, com assistência de IA; os
cabeçalhos dos arquivos registram isso.

| Arquivo | Papel |
|---|---|
| `HeuristicNode.h` | hierarquia da AST: `TerminalNode`, `UnaryNode`, `BinaryNode`. `evaluate()`, `toString()` (notação prefixa), `clone()`, navegação. Tamanho e profundidade são **cacheados** na construção, o que torna `size()` `O(1)`. |
| `HeuristicGrammar.cpp` | gera árvores aleatórias. Terminais: `deltaX`, `deltaY`, constante. Operadores: `+ - * / max min sqr sqrt abs neg`. |
| `GeneticOperators.cpp` | crossover e mutação de subárvore |
| `GeneticAlgorithm.cpp` | laço evolutivo: avaliação (`#pragma omp parallel for`), elitismo 10%, reprodução |
| `SimulatedAnnealing.cpp` | refinamento pós-AG (T₀ = 1,0; resfriamento 0,95). **Presente no diretório, mas `main.cpp` de março não o chama** — só a versão de junho usa. |

As constantes são geradas como `round(x·10)/10` e impressas com `%.1f`. Isso não é cosmético:
garante que a ida e volta *texto → AST → texto* seja exata, o que é a base da retomada por
checkpoint nas medições de agosto.

**Onde a reprodutibilidade se perde:** `GeneticAlgorithm.cpp:19` e `:68` criam
`std::mt19937 gen(std::random_device{}())` **dentro** de `initPopulation` e `reproduction`.
A gramática e os operadores recebem semente 42, mas o AG em si sorteia da entropia do sistema.
Ver P5.

### `main.cpp` — o roteiro do experimento

288 linhas, um único `main`, sem funções auxiliares. É um roteiro linear, e lê-se de cima para
baixo:

```
para cada um dos 17 mapas:
    loadMap + loadScenario
    ── sintetiza a fórmula (AG, 100 gerações) ─────────► resultados_sintese.csv
    para cada uma das 5 sementes:
        srand(semente)
        ── mapa original ──────────────────────────────► resultados_base.csv
        │   Manhattan, Fórmula, Dijkstra (p/ o ótimo) ─► resultados_ratio.csv
        │   Memória com 10, 20, 50, 100 pivôs ─────────► resultados_base.csv
        └── para cada um dos 5 padrões de degradação:
                aplica 10% → 20% → 30% (cumulativo)
                seleciona os pares válidos NO ESTADO DE 30%   ← ver P2
                para cada nível e cada contagem de pivôs:
                    mede as 3 heurísticas ────────────► resultados_robustez.csv
```

Os quatro `ofstream` são abertos em **`ios::app`**. Rodar duas vezes sem limpar os arquivos
**acrescenta** aos dados anteriores — foi exatamente assim que `arena` acabou duplicado nos
dados publicados (P7).

> **Na versão de junho** `main.cpp` tem 455 linhas: ganha o parser de `--mode`, o bloco de
> Simulated Annealing, o cálculo de `admissibility_rate` e as colunas `implementacao`/`modo`
> em todos os CSVs.

---

## Análise em Python

### `analise/original-2026-03/` — o que gerou o texto original

`analise.py` imprime 11 blocos de tabelas no terminal; `gerarGraficos.py` e os `gerar_*.py`
produzem as figuras. São os scripts que sustentam a versão do relatório anterior à reanálise —
inclusive os números que a reanálise depois corrigiu.

`variante-2026-06/` guarda as versões desses mesmos scripts adaptadas ao esquema de CSV de
junho (com a coluna `modo`). Nunca rodaram sobre dados reais, porque o experimento de junho
nunca foi executado.

### `analise/estatistica-2026-08/` — a reanálise

13 scripts, `a0`…`a12`, orquestrados por `scripts/run_all.py` (~3 min). `scripts/comum.py`
concentra as três regras metodológicas que mudam quase todos os números:

1. razões agregam por **média geométrica**, nunca aritmética;
2. expansões são **normalizadas por mapa** antes de agrupar entre mapas;
3. a unidade de replicação para generalizar é o **mapa (n = 17)**, não a instância (n = 116.050).

`comum.py` também **deduplica `arena`** em toda carga (P7) e expõe `celulas_degeneradas()`,
que identifica as células em que a heurística de memória colapsou (P8).

`scripts/sintese_pool.py` é o supervisor que roda as re-sínteses do A9 em paralelo, com
checkpoint por geração e retomada segura; o manual está em `docs/historico/ANALISE_RETOMAR.md`.

### `codigo/medicoes-2026-08/` — o C++ que a reanálise precisou escrever

| Programa | Mede |
|---|---|
| `medir_dijkstra` | expansões do A\* com `h = 0`, para normalizar expansões entre mapas |
| `medir_pivos` | memória e tempo de pré-computação dos pivôs; diagnostica o colapso de pivô |
| `verifica_reprocessamento` | quanto das distâncias pré-computadas muda sob degradação |
| `sintese_repetida` / `sintese_worker` | re-síntese com semente explícita |

`maps` aqui é um link simbólico para `../../maps`, para que os binários rodem a partir do
próprio diretório sem duplicar 3 MB de mapas.
