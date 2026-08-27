## Why

The current experimental setup only uses a single seed and lacks comprehensive metrics for formula synthesis and path quality compared to Dijkstra. To ensure methodological rigor and statistical significance, the experiment needs to run across multiple seeds, use cumulative degradation consistently, and record detailed performance metrics for both original and degraded map states.

## What Changes

- **Multi-Seed Execution**: Iterate over 5 fixed seeds ({42, 123, 456, 789, 1011}) for all experiments.
- **Strict Cumulative Degradation**: Ensure all degradation types follow a 10% -> 20% -> 30% sequence using the same seed.
- **Fixed Pair Selection at 30%**: Origin-destination pairs will be selected and fixed based on connectivity at the most restrictive (30%) state.
- **Enhanced Data Recording**:
    - `resultados_base.csv`: Record performance on original maps.
    - `resultados_robustez.csv`: Record detailed comparison between original and degraded states, including time, expansions, and path sizes for all heuristics.
    - `resultados_ratio.csv`: Compare formula heuristic against Dijkstra (h=0) for optimality ratio.
    - `resultados_sintese.csv` (NEW): Record formula synthesis parameters, time, and final fitness.
- **Append Mode**: Open CSV files in append mode to allow resuming experiments.

## Capabilities

### New Capabilities
- `multi-seed-reproducibility`: Manage execution across multiple fixed seeds.
- `dijkstra-baseline`: Compute optimal path sizes using Dijkstra (A* with h=0) for ratio analysis.
- `synthesis-metrics-tracking`: Track and record metrics of the genetic algorithm synthesis process.
- `comprehensive-robustness-logging`: Log matched original and degraded performance data in a single row.

### Modified Capabilities
- `cumulative-map-degradation`: Ensure all 5 types follow the 10->20->30 sequence.
- `fixed-pair-selection`: Standardize filtering at the 30% level.

## Impact

- `src/main.cpp`: Complete rewrite of the experimental loop to support multi-seed iteration and new CSV formats.
- `resultados_base.csv`, `resultados_robustez.csv`, `resultados_ratio.csv`: Format changes to match the new requirements.
- `resultados_sintese.csv`: New output file.
