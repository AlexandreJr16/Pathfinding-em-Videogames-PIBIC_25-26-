# O experimento

## A pergunta

Uma heurística **sintetizada automaticamente por programação genética** consegue competir com
as duas alternativas clássicas — a Manhattan (barata e admissível) e as heurísticas
**baseadas em memória** (caras e precisas) — não só no mapa original, mas **quando o mapa muda**?

A hipótese: a heurística de memória vence com folga no mapa estático, mas depende de distâncias
pré-computadas que envelhecem mal; a fórmula sintetizada, por ser uma expressão fechada sobre a
geometria, deveria degradar menos. Se isso for verdade, a **ordem de mérito entre as estratégias
depende do regime de modificação do mapa** — e essa inversão é a tese do trabalho.

## As três classes de heurística

| Classe | Definição | Pré-processamento | Memória | Admissível? |
|---|---|---|---|---|
| **Manhattan** | `h(s,g) = \|Δlinha\| + \|Δcoluna\|` | nenhum | zero | sim |
| **Memória (pivôs)** | `h(s,g) = maxᵢ \|d(pᵢ,s) − d(pᵢ,g)\|`, com `d` exata por BFS | uma BFS por pivô | `O(pivôs × células)` | sim |
| **Fórmula (AG)** | expressão simbólica sobre `deltaX`/`deltaY`, evoluída como AST | a síntese em si | só a árvore | **não garantida** |

- Os pivôs são escolhidos por **Farthest-First Traversal**: o primeiro é sorteado
  uniformemente entre as células transitáveis, e cada seguinte é a célula mais distante de
  todos os já escolhidos. Testado com **10, 20, 50 e 100 pivôs**.
- A estimativa de memória é a **desigualdade triangular** aplicada a distâncias exatas — daí a
  admissibilidade.
- A fórmula é evoluída por um **algoritmo genético sobre árvores sintáticas** (população 80,
  100 gerações, elitismo 10%, penalidade de tamanho λ = 0,0005), com *fitness* igual ao
  *speedup* em expansões contra a Manhattan no conjunto de treino.

## Os mapas

17 mapas do conjunto **Dragon Age: Origins** do [Moving AI Lab](https://movingai.com/benchmarks/),
em `maps/`, no formato HOG (`.map` + `.map.scen`). Grades **4-conectadas**, custo unitário,
sem diagonais. Categorias usadas na análise:

| Prefixo | Categoria | Mapas |
|---|---|---|
| `arena` | Arena | arena, arena2 |
| `brc` | Área aberta | brc000d, brc100d, brc101d, brc201d, brc202d, brc203d |
| `den` | Dungeon | den000d, den005d, den011d, den012d, den500d, den501d, den602d |
| `hrt`, `lak` | Natureza | hrt201n, lak506d |

Cada `.map.scen` traz pares origem–destino com o **comprimento ótimo já conhecido**, o que dá
uma referência independente para medir subotimalidade. Total: **116.700 instâncias** por
configuração de heurística.

## As cinco degradações

Depois de medir no mapa original, o mapa é progressivamente bloqueado em **10%, 20% e 30%** das
células originalmente transitáveis — de forma **cumulativa**: o estado de 20% contém todos os
bloqueios de 10%. Cinco padrões, todos em `map.cpp`:

| Padrão | Função | Geometria |
|---|---|---|
| **Radial** | `degradaMapa` | discos de raio ≈ 5% da menor dimensão, em centros sorteados |
| **Linear** | `degradaMapaLinear` | barreiras retas de comprimento ≈ metade da menor dimensão, em direção sorteada |
| **Sparse** | `degradaMapaSparse` | discos maiores, mas bloqueando só 40% das células dentro deles |
| **Organic** | `degradaMapaOrganic` | passeios aleatórios a partir de uma célula-semente |
| **Stochastic** | `degradaMapaSaunders` | células individuais sorteadas em todo o mapa (modelo de Saunders) |

A intenção é cobrir um espectro: de bloqueios **estruturados e conexos** (linear, radial), que
seccionam o mapa e podem isolar regiões inteiras, até bloqueios **difusos** (estocástico), que
aumentam a densidade de obstáculos sem alterar a topologia global. As heurísticas reagem de
formas bem diferentes a esses dois extremos — é isso que o experimento explora.

> ⚠️ O relatório afirma que as heurísticas **não são reprocessadas** sob degradação. A reanálise
> de agosto mediu o código e mostrou que **as distâncias dos pivôs são recalculadas** — só as
> *posições* dos pivôs ficam congeladas. Ver `docs/03-achados-estatisticos.md` (A0) e
> `docs/04-problemas-conhecidos.md` (P1). É a divergência mais importante entre texto e código.

## As métricas

| Métrica | Por que |
|---|---|
| **Expansões de nós** | A métrica principal. É **determinística** e comparável entre máquinas. |
| **Tempo (ms)** | Registrado, mas **não confiável** — medição única, sem aquecimento nem isolamento de CPU. Nenhuma conclusão se apoia nele (ver P3). |
| **Tamanho do caminho** | Para a subotimalidade `ρ = caminho_obtido / caminho_ótimo`. Só faz sentido para a fórmula: as outras duas são admissíveis, logo ótimas. |
| **Fator de degradação δ** | `expansões_no_mapa_degradado / expansões_no_mapa_original`, pareado por instância. **É a métrica da tese** — mede robustez, não desempenho absoluto. |

## O desenho

- **5 sementes**: 42, 123, 456, 789, 1011. A semente controla a escolha dos pivôs e o sorteio
  das degradações, não a síntese da fórmula (que usa semente fixa 42 na gramática e nos
  operadores — mas ver P5).
- **Desenho pareado**: as 6 configurações (Manhattan, Fórmula, Memória-10/20/50/100) rodam
  sobre **exatamente os mesmos pares origem–destino**. Essa é a maior força estatística do
  conjunto de dados, e a análise de março não a aproveitava.
- **Treino da síntese**: amostra estratificada de `min(150, |cenário|/4)` problemas por mapa,
  sorteada com `srand(42)`. A fórmula é sintetizada **uma vez por mapa** e depois avaliada em
  todas as instâncias.
- **Filtro de conectividade**: pares que ficam desconexos sob 30% de bloqueio são descartados.
  O filtro é aplicado **uma única vez, no estado de 30%**, e o mesmo conjunto é usado nos três
  níveis — ver P2, é a limitação metodológica mais séria do desenho.

## O tamanho do resultado

| Arquivo | Linhas | O que é |
|---|---|---|
| `resultados_base.csv` | 700.200 | 6 configurações × 116.700 instâncias, mapa original |
| `resultados_robustez.csv` | 431.016 | as instâncias sobreviventes × 5 padrões × 3 níveis × 4 contagens de pivôs |
| `resultados_ratio.csv` | 116.700 | subotimalidade da fórmula, uma linha por instância |
| `resultados_sintese.csv` | 18 | uma fórmula campeã por mapa (17 mapas; `arena` aparece duas vezes — ver P7) |

Esquemas completos em [`dados/MANIFESTO.md`](../dados/MANIFESTO.md).
