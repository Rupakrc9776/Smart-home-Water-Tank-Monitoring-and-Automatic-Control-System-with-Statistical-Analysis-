# Contributing

Thank you for improving the **SMART HOME WATER TANK MONITORING AND AUTOMATIC CONTROL SYSTEM WITH STATISTICAL ANALYSIS**.

## Before Opening a Change

1. Search existing issues and pull requests.
2. Describe the hardware, firmware, or software behavior you intend to change.
3. For hardware changes, include the affected pin, voltage, load, and safety considerations.
4. Keep runtime behavior compatible unless the change is explicitly a breaking release.

## Development Checks

```powershell
python -m py_compile dashboard.py dashboard_assets.py water_logger.py
python -m pip check
```

Test serial parsing with both valid and malformed payloads. Do not test a relay-connected pump without an approved isolation and load procedure.

## Pull Requests

- Use a focused title and explain the user-visible effect.
- Link the issue or test record.
- Include screenshots for dashboard changes.
- Include before/after wiring diagrams for hardware changes.
- Update the relevant documentation and test matrix.
- Do not commit credentials, private serial logs, or generated runtime screenshots.

Contributors retain responsibility for validating changes against their local hardware.
