## ADDED Requirements

### Requirement: Comparison Rows
The system SHALL log each robustness measurement as a comparison between the original map's performance and the degraded map's performance in a single CSV row.

#### Scenario: Robustness comparison row
- **WHEN** the experiment runs on a degraded map
- **THEN** it retrieves the corresponding performance data from the original map state (baseline) and writes both to the same CSV row.
