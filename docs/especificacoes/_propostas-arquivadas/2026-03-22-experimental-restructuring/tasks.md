## 1. CSV Infrastructure

- [x] 1.1 Implement a `writeCSVHeader` helper to write headers only to empty/new files.
- [x] 1.2 Set up `ofstream` objects for all 4 CSV files in append mode.
- [x] 1.3 Add synthesis metrics tracking to `resultados_sintese.csv`.

## 2. Experimental Loop Structure

- [x] 2.1 Refactor `main.cpp` to include the outer seed loop `{42, 123, 456, 789, 1011}`.
- [x] 2.2 Ensure `srand()` is called correctly at each seed transition.
- [x] 2.3 Implement Dijkstra baseline (A* with h=0) for path quality ratio calculation.

## 3. Robustness Experiments

- [x] 3.1 Refactor the robustness phase to store baseline results (original map) in memory.
- [x] 3.2 Ensure cumulative degradation is correctly applied (10 -> 20 -> 30) for each of the 5 types.
- [x] 3.3 Implement the new CSV structure for `resultados_robustez.csv` that compares original and degraded performance in a single row.

## 4. Execution and Validation

- [x] 4.1 Update the final stdout summary to report execution time and pair connectivity statistics.
- [x] 4.2 Verify that all 4 CSV files match the requested format.
- [x] 4.3 Ensure the experiment is reproducible across different runs with the same seeds.
