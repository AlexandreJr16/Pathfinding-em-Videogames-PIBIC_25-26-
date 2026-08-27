## 1. Core Logic Refactoring

- [x] 1.1 Modify the robustness testing loop in `src/main.cpp` to store intermediate map states (grid10, grid20, grid30).
- [x] 1.2 Implement the cumulative degradation sequence for each type (Radial, Linear, Sparse, Organic, Stochastic).
- [x] 1.3 Ensure `srand(sementeFixa)` is called before the degradation sequence to maintain consistency.
- [x] 1.4 Implement the incremental target calculation (e.g., `target20 - target10`) when calling degradation functions.

## 2. Fixed Pair Selection

- [x] 2.1 Implement a pre-filtering step that checks `verificaPontosConectados` against the 30% map state for all pairs in the scenario.
- [x] 2.2 Store the filtered set of connected pairs in a separate vector for reuse.
- [x] 2.3 Verify that the original connectivity check (`caminhoManhOrig[i] > 0`) is also included in the filtering logic.

## 3. Benchmarking and Output

- [x] 3.1 Update the benchmarking inner loop to iterate through percentages (10%, 20%, 30%) using the stored grids and filtered pairs.
- [x] 3.2 Remove the redundant `if (valido[i])` check during CSV generation for 10% and 20% levels, or convert it to an assert.
- [x] 3.3 Ensure the `resultados_robustez.csv` is updated with data for all filtered pairs across all levels.

## 4. Verification and Cleanup

- [x] 4.1 Verify that the number of rows in `resultados_robustez.csv` for 10% level matches the number for 30% level for each degradation type.
- [x] 4.2 Verify that the map state is correctly reset to `gridOriginal` after each degradation type is processed.
- [x] 4.3 Ensure no unused connectivity checks remain in the hot loop.
- [x] 4.4 Verify that the code compiles and runs without regression in other modes (baseline, ratio).
