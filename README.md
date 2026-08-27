# Síntese automática de heurísticas para busca de caminhos em videogames

**PIBIC/PAIC 2025–2026 · UFAM / Instituto de Computação**
Aluno: Alexandre Pereira de Souza Junior · Orientadora: Dra. Rosiane de Freitas Rodrigues
Projeto PIB-E/0151/2025 · Financiamento CNPq

> **Título do relatório:** *Estratégias para síntese automática de heurísticas baseadas em
> fórmulas e em memória na busca de caminhos em videogames.*

Comparação experimental de três classes de heurística para o algoritmo A\* em **17 mapas do
conjunto Dragon Age Origins** (Moving AI Lab), em grades 4-conectadas de custo unitário, tanto
no mapa original quanto sob **cinco padrões de degradação estrutural** em três níveis de
bloqueio (10%, 20%, 30%).

---

## Se você está voltando aqui depois de muito tempo, leia nesta ordem

| # | Documento | Para quê |
|---|---|---|
| 1 | **[docs/00-PROVENIENCIA.md](docs/00-PROVENIENCIA.md)** | ⭐ **Comece aqui.** Que código gerou que dado, em que data. Existem três versões do C++ neste repositório e **só uma delas produziu os números do relatório** — este documento diz qual, e por quê isso importa. |
| 2 | [docs/01-experimento.md](docs/01-experimento.md) | O que foi medido e como: as heurísticas, os mapas, as degradações, as métricas. |
| 3 | [docs/02-arquitetura-do-codigo.md](docs/02-arquitetura-do-codigo.md) | O código módulo a módulo, e o caminho que um dado percorre do `.map` até a tabela. |
| 4 | [docs/03-achados-estatisticos.md](docs/03-achados-estatisticos.md) | O que a reanálise de agosto/2026 descobriu — inclusive onde ela **contradiz** o relatório. |
| 5 | [docs/04-problemas-conhecidos.md](docs/04-problemas-conhecidos.md) | Bugs, limitações e armadilhas. Leia antes de reaproveitar qualquer coisa daqui. |
| 6 | [docs/05-como-reproduzir.md](docs/05-como-reproduzir.md) | Comandos exatos para recompilar e refazer as análises. |
| 7 | [dados/MANIFESTO.md](dados/MANIFESTO.md) | Onde estão os dados brutos (não cabem no Git) e o esquema de cada arquivo. |

O relatório final entregue está em
[`relatorio/`](relatorio/RelatorioFinal_PIBIC_2025-2026_AlexandrePereiraSouzaJunior.pdf).

---

## Mapa do repositório

```
.
├── codigo/
│   ├── run-referencia-2026-03/   ⭐ C++ que GEROU TODOS OS DADOS do relatório
│   ├── refatoracao-2026-06/         C++ reescrito DEPOIS do relatório (não usado nos resultados)
│   └── medicoes-2026-08/            C++ auxiliar, escrito para a reanálise estatística
│
├── analise/
│   ├── original-2026-03/            Python que produziu as tabelas/figuras da 1ª versão do texto
│   └── estatistica-2026-08/         Reanálise completa (A0–A12): 34 tabelas + 2 figuras
│
├── maps/                            Os 17 mapas + cenários do Moving AI Lab (formato HOG)
├── dados/                           Dados pequenos + MANIFESTO dos dados brutos
├── docs/                            Documentação (este README aponta para tudo)
│   ├── historico/                   Documentos originais, preservados sem edição
│   └── especificacoes/              Requisitos formais do experimento (formato OpenSpec)
├── relatorio/                       O PDF final entregue
└── Makefile                         `make ajuda` lista os alvos
```

## Começo rápido

```fish
make ajuda          # lista os alvos disponíveis
make referencia     # compila o código de março -> bin/pathfinding-referencia
make testes         # roda os testes unitários
```

> **Sempre compile e execute a partir da raiz do repositório.** Os binários procuram os mapas
> em `maps/`, por caminho relativo ao diretório atual.

⚠️ Rodar `bin/pathfinding-referencia` refaz o experimento inteiro — **levou cerca de 20 horas**
nos 17 mapas, e grava os quatro `resultados_*.csv` na raiz **em modo append**. Se os arquivos
já existirem, os dados novos são acrescentados aos antigos (foi assim que o mapa `arena` acabou
duplicado nos dados originais; ver [docs/04-problemas-conhecidos.md](docs/04-problemas-conhecidos.md), P7).

## Os dados brutos não estão no Git

Os quatro CSVs da execução de referência somam ~170 MB e ficam **fora do repositório**, no
pacote do Google Drive. Para rodar a reanálise estatística, aponte a variável de ambiente:

```fish
set -x HEURISTICAS_DADOS ~/caminho/para/02-dados-brutos
cd analise/estatistica-2026-08
.venv/bin/python scripts/run_all.py     # ~3 min, regenera as 34 tabelas e as 2 figuras
```

Detalhes, esquemas e checksums: [dados/MANIFESTO.md](dados/MANIFESTO.md).

---

## Crédito de terceiros

O subsistema de programação genética em `src/synthesis/` é uma **tradução de MATLAB para C++**
do código de **Saunders (2024)**, feita com assistência de IA. Os cabeçalhos dos arquivos
registram isso individualmente. Os mapas e cenários em `maps/` são do
[Moving AI Lab](https://movingai.com/benchmarks/), conjunto *Dragon Age: Origins*.
