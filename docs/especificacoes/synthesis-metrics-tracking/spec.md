## ADDED Requirements

### Requirement: Record Synthesis Data
The system SHALL record the genetic algorithm's initial population size, generation count, total synthesis time, best formula string, and final fitness.

#### Scenario: Synthesis record creation
- **WHEN** the genetic algorithm finishes evolving a heuristic for a map
- **THEN** it writes a single row to `resultados_sintese.csv` with the synthesis metadata.
