# Release Notes

## v1.0 - Mini Project Submission

### Summary

Initial publication of the **SMART HOME WATER TANK MONITORING AND AUTOMATIC CONTROL SYSTEM WITH STATISTICAL ANALYSIS** repository as a B.Tech Electrical Engineering mini project.

### Included

- Python desktop dashboard with serial connection handling.
- Headless serial logger.
- CSV logging with distance, percentage, pump state, and timestamp.
- Live tank, gauge, pump, alert, and trend visualizations.
- Average, maximum, minimum, and pump activation indicators.
- Hardware pin contract and calibration guidance.
- Architecture diagrams and operator documentation.
- GitHub contribution, security, issue, and CI configuration.

### Validation

- Python modules compile successfully.
- Parser contract and thresholds are documented.
- Hardware relay, LCD, sensor, and end-to-end pump tests remain environment-dependent.

### Known Repository Limitation

The original Arduino `.ino` source referenced by the project brief is not present in this workspace. Add the reviewed firmware under `Arduino_Code/` before treating the release as a complete firmware artifact.
