## Why

The current map degradation methodology generates 10%, 20%, and 30% blockage levels independently, causing selection bias in the origin-destination pairs and leading to invalid comparisons between levels. Additionally, approximately 87% of pairs are discarded in post-processing when forcing intersection of valid pairs, resulting in significant data loss.

## What Changes

- **Cumulative Map Degradation**: Map blockages will be applied incrementally (0% -> 10% -> 20% -> 30%) instead of resetting the map for each level.
- **Fixed and Guaranteed Valid Pairs**: Origin-destination pairs will be selected once based on the most restrictive state (30% blockage), ensuring 100% connectivity across all levels (10%, 20%, and 30%).
- **Optimized CSV Generation**: Redundant connectivity checks for levels < 30% will be removed, as connectivity is guaranteed by the selection process.
- **Consistent Seeding**: The random seed will be managed to ensure reproducibility of the entire cumulative sequence.
- **Preserved Output Format**: The `resultados_robustez.csv` file structure remains unchanged to maintain compatibility with existing analysis tools.

## Capabilities

### New Capabilities
- `cumulative-map-degradation`: Capability to apply blockages incrementally to an existing map state, ensuring that the 20% state contains all 10% blockages, and the 30% state contains all 20% blockages.
- `fixed-pair-selection`: Capability to pre-filter and select origin-destination pairs that remain connected in the most restrictive (30%) map state.

### Modified Capabilities
- (None - this is a new implementation of the robustness testing logic)

## Impact

- `src/main.cpp`: Significant modification of the robustness testing loop to implement cumulative degradation and fixed pair selection.
- `src/map.cpp` / `src/map.h`: Possible addition of helper functions to support incremental degradation if current ones are insufficient.
- `resultados_robustez.csv`: No structural change, but the data will now represent cumulative states and higher pair retention.
