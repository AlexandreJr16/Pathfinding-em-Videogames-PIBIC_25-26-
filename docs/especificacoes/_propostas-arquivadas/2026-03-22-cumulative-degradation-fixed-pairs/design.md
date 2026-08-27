## Context

The current pathfinding robustness experiments suffer from selection bias because each degradation level (10%, 20%, 30%) is generated independently, and origin-destination pairs are validated for connectivity only at the current level. This means a pair used at 10% might be blocked at 20%, making direct comparisons impossible. Approximately 87% of pairs are lost during intersection in post-processing.

## Goals / Non-Goals

**Goals:**
- Ensure that the 20% blockage state is a superset of the 10% state, and 30% is a superset of 20%.
- Use a single, fixed set of origin-destination pairs for all degradation levels (10%, 20%, 30%).
- Maximize the number of usable pairs by selecting them based on the most restrictive (30%) state.
- Guarantee 100% connectivity for all benchmarking runs without redundant checks.

**Non-Goals:**
- Modifying the A* algorithm, heuristics, or the CSV output columns.
- Changing the command-line arguments or parameters.

## Decisions

### 1. Sequential Degradation Pipeline
For each degradation type (Radial, Linear, etc.), we will perform a "Dry Run" degradation sequence to generate the intermediate map states.
- **Rationale**: To determine which pairs are valid in the most restrictive state, we must reach the 30% level first.
- **Workflow**:
    1. Reset `grid` to `gridOriginal`.
    2. Seed `srand(sementeFixa)`.
    3. Call degradation function to reach 10%, save as `grid10`.
    4. Call degradation function to reach 20%, save as `grid20`.
    5. Call degradation function to reach 30%, save as `grid30`.

### 2. Pre-filtering Pairs at 30%
Before running any benchmarks, we will iterate through the scenario file and test connectivity against `grid30`.
- **Rationale**: Since 30% is the most restrictive state, any pair connected at 30% is guaranteed to be connected at 0%, 10%, and 20% given the cumulative nature of the degradation.
- **Alternative considered**: Filtering at each level and taking the intersection. This is what's currently being done (manually in post-processing) and it's inefficient.

### 3. Benchmarking Loop Restructuring
The benchmarking loop will iterate through the saved `grid10`, `grid20`, and `grid30` states using the `filteredScenario`.
- **Rationale**: Ensures that every row in the CSV for a given degradation type uses the exact same subset of problems, allowing for direct statistical comparison of performance degradation.

### 4. Memory Management for Grids
Map states (grids) will be stored in a `std::map<double, std::vector<std::vector<bool>>>` or similar structure during the processing of each degradation type.
- **Rationale**: Maps are small enough that storing 3-6 versions in memory is negligible.

## Risks / Trade-offs

- **[Risk]** → Increased memory usage if maps were extremely large.
- **Mitigation** → Map sizes in this project are standard game maps; memory is not a constraint.
- **[Risk]** → The current `degradaMapa*` functions might not perfectly support incremental additions if they have internal state or assumptions.
- **Mitigation** → We will pass `target - current` to these functions or modify them as requested to handle incremental targets.
