## ADDED Requirements

### Requirement: Pre-filtering of Connected Pairs
The system SHALL identify valid origin-destination pairs by checking connectivity in the most restrictive (30%) map state.

#### Scenario: Selection from 30% State
- **WHEN** a map has been degraded to its 30% blockage level
- **THEN** the system SHALL filter the list of candidate pairs (from the scenario file) to keep only those that are connected in this state.

### Requirement: Reuse of Fixed Pairs
The system SHALL use the exact same set of pre-filtered pairs for all benchmarking levels (10%, 20%, and 30%) for a given map and degradation type.

#### Scenario: Consistent Pairs Across Levels
- **WHEN** benchmarking the 10% and 20% levels
- **THEN** the system SHALL use the same set of pairs that were validated at the 30% level.

### Requirement: Removal of Redundant Connectivity Checks
The system SHALL NOT perform additional connectivity checks during the execution of pathfinding for 10% and 20% levels if the pairs were already validated at 30%.

#### Scenario: Guaranteed Connectivity
- **WHEN** executing A* on a 10% or 20% degraded map using pairs validated at 30%
- **THEN** the pathfinding MUST succeed (or find a path) without needing a prior connectivity check for that specific level.
