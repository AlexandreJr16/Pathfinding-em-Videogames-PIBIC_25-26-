## ADDED Requirements

### Requirement: Incremental Map Blockage
The system SHALL apply map blockages in a strictly cumulative and increasing order (10% -> 20% -> 30%).

#### Scenario: Sequential Degradation
- **WHEN** transitioning from a 10% blockage state to a 20% state
- **THEN** all cells blocked at 10% SHALL remain blocked
- **AND** new cells SHALL be added until the 20% target is reached.

### Requirement: Reproducible Randomness for Degradation
The system SHALL use a consistent random seed to ensure that the cumulative sequence of blockages is reproducible for a given map and degradation type.

#### Scenario: Seeded Cumulative State
- **WHEN** the map is degraded to 30% starting from a fixed seed
- **THEN** the resulting map state SHALL be identical every time the same seed and map are used.
