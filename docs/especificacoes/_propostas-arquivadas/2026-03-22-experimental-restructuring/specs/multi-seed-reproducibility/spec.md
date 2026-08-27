## ADDED Requirements

### Requirement: Multiple Seeds
The system SHALL iterate over a fixed set of seeds {42, 123, 456, 789, 1011} for each map.

#### Scenario: Seeded execution
- **WHEN** the experiment starts for a map
- **THEN** it iterates 5 times, seeding `srand()` with each value in the set.
