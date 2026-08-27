# Orchestrator & Project Index

> **PROJECT**: Análise de desempenho de heurísticas sintetizadas por fórmulas e memória para busca de caminhos em videogames
> **AUTHOR**: Alexandre Pereira de Souza Junior

This file is the master index and orchestrator for the `heuristica` project. It contains the navigational map to understand the codebase, the architectural patterns in use, and the experimental methodology.

## 🧭 1. Knowledge Discovery Map (Where to find things)

Do not guess the architecture. Read the following detailed markdown files to load the full context into your context window:

1. **[Project Walkthrough](file:./project_walkthrough.md)**: Start here for a high-level overview, data flow diagrams, and the general experiment design.
2. **[Full Technical Context](file:./heuristica_full_context.md)**: Read this for exhaustive documentation on every module, AST node structure, genetic algorithm hyper-parameters, and Python analysis script logic.
3. **[Code Review & Fixes](file:./code_review.md)**: Read this to understand historical fixes, ensuring you do not reintroduce old bugs.

## 🔬 2. Escopo da Pesquisa (Current Project Scope)

This codebase implements an experimental comparative analysis of heuristic synthesis strategies for the A* Algorithm in digital game maps. 

**Heuristics Evaluated:**
1. **Manhattan**: Baseline classical heuristic.
2. **Memory-based (Pivots)**: Uses Farthest-First selection for 10, 20, 50, and 100 pivots.
3. **Formula-based**: Synthesized via Genetic Programming (ASTs) adapted to the map geometry.

**Experimental Constraints:**
*   **Maps**: 17 maps from the Dragon Age Origins dataset (Moving AI Lab).
*   **Degradation Patterns**: Static scenarios + 5 dynamic structural degradations applied cumulatively at 10%, 20%, and 30%:
    *   *Linear*: Straight barriers segmenting the map.
    *   *Organic*: Random walks from a seed cell.
    *   *Radial*: Circular obstructions.
    *   *Sparse*: Uniformly distributed blocks.
    *   *Stochastic*: Completely random blocks across the map.

**Key Metrics Evaluated:**
*   Node Expansions (Efficiency)
*   Execution Time (ms)
*   Degradation Factor (Robustness under dynamic changes)
*   Path Quality Ratio (Sub-optimality)

## 🏗️ 3. Codebase Architecture

The project is structured with a clean separation of concerns, heavily utilizing C++17 and standard OOP/TAD practices.

*   **`src/map.cpp` / `map.h`**: Grid parsing and the 5 procedural obstacle degradation patterns.
*   **`src/heuristics.cpp`**: Houses Manhattan, Memory-based (differential pivots via Triangulation), and the AST evaluation wrapper.
*   **`src/astar.cpp`**: The core A* search engine using Saunders tie-breaking.
*   **`src/synthesis/`**: The entire GP (Genetic Programming) subsystem.
    *   `HeuristicNode.h`: AST node hierarchy (Terminal, Unary, Binary).
    *   `HeuristicGrammar.cpp`: Random S-expression tree generation.
    *   `GeneticAlgorithm.cpp` & `SimulatedAnnealing.cpp`: Evolutionary optimization loops.
*   **`tests/`**: TDD infrastructure using a lightweight custom framework.
*   **`WPerformance/`**: Python 3.11+ scripts for CSV aggregation, statistical analysis, and plotting.

## 🛠️ 4. Rules for Code Modification:
1. **Never use `cat`, `grep`, or `sed`** to manipulate code. Use specialized IDE file-editing tools.
2. **Never** modify `src/astar.cpp` unless explicitly instructed; it is the highly optimized empirical benchmark engine.
3. If changing how formulas evaluate or adding new heuristics, update `tests/test_heuristics.cpp` immediately.
4. Keep Python analysis decoupled from C++ execution. They communicate strictly via CSVs.
