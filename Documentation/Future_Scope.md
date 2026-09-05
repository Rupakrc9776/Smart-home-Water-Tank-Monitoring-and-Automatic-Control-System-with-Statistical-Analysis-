# Future Scope

The following improvements are suitable for a subsequent release and should be designed with hardware safety and data integrity in mind:

- Add the reviewed Arduino firmware source and automated compile validation.
- Replace fixed thresholds with a validated configuration file and visible audit trail.
- Add sensor filtering, confidence indicators, and outlier reporting.
- Persist data in SQLite or a time-series database while retaining CSV export.
- Generate daily and weekly statistical reports with pump duty-cycle analysis.
- Add configurable desktop notifications for low water, sensor failure, and communication loss.
- Support multiple tanks and controller identities.
- Add calibration workflows for tank geometry and sensor offsets.
- Provide a secure web or mobile view for remote status access.
- Add watchdog behavior, dry-run protection, and fail-safe relay defaults.
- Package the dashboard for controlled Windows deployment.
