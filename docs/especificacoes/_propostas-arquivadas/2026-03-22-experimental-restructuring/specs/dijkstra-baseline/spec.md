## ADDED Requirements

### Requirement: Dijkstra Baseline
The system SHALL compute the optimal path length for each problem using Dijkstra (A* with h=0).

#### Scenario: Optimal path calculation
- **WHEN** calculating the ratio for a formula
- **THEN** it first runs A* with a constant zero heuristic to find the true shortest path length.
