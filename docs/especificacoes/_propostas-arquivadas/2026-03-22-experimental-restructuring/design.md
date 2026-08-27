## Context

The current pathfinding experiment needs to be restructured to ensure reproducibility and statistical power. The primary goal is to iterate over multiple seeds and capture more detailed metrics in various CSV files.

## Goals / Non-Goals

**Goals:**
- Implement nested loops: For each map -> Seed synthesis -> For each seed (42, 123, 456, 789, 1011) -> Baseline -> Robustness (10%, 20%, 30%).
- Ensure cumulative degradation is handled correctly across all types.
- Calculate optimality ratio using Dijkstra (h=0) for each pair.
- Standardize the output CSV format for easier downstream analysis.

**Non-Goals:**
- Modifying the A* algorithm logic.
- Changing the heuristic synthesis (genetic algorithm) parameters beyond adding metrics tracking.

## Decisions

### 1. Loop Hierarchy
The experiment will follow this hierarchy:
1. `mapas` (Loop through all maps)
    - `Heuristic Synthesis` (Succeeds once per map)
        - `resultados_sintese.csv` (Write synthesis metrics)
    - `sementes` (Loop through 5 fixed seeds)
        - `srand(semente)`
        - `Baseline (0%)`
            - `resultados_base.csv`
            - `resultados_ratio.csv` (Dijkstra baseline)
        - `Degradation Type` (Radial, Linear, etc.)
            - `Fixed Pair Selection` (Filter connected pairs at 30% state)
            - `Degradation Percentages` (10, 20, 30 cumulative)
                - `resultados_robustez.csv` (Compare with baseline data stored in memory)

### 2. Optimality Ratio via Dijkstra
To calculate the path quality ratio, the system will run A* with `heuristicaZero` (Dijkstra) once for each pair in the original map to find the `caminho_otimo`.

### 3. Robustness Row Data Structure
A temporary `std::map` or `std::vector` will store the baseline results for a given (map, seed, pair) to avoid re-running baseline experiments during the robustness phase.

### 4. File I/O Management
CSV files will be opened in append mode to prevent accidental data loss. Headers will only be written if the file is new/empty.

## Risks / Trade-offs

- **[Risk]** → Longer execution time due to 5 seeds.
- **Mitigation** → Ensure efficient data reuse (baseline data) and potentially use OpenMP if loops allow.
- **[Risk]** → Disk space for large CSV files.
- **Mitigation** → Keep output rows concise and focused on necessary metrics.
