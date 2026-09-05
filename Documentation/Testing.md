# Testing

Testing is divided into software checks, protocol checks, and hardware commissioning. The table records the expected engineering baseline; rerun hardware cases after every wiring or firmware change.

| Test Case | Expected | Actual | Status |
| --- | --- | --- | --- |
| Python syntax compilation | All Python entry points compile | `dashboard.py`, `dashboard_assets.py`, and `water_logger.py` compile | PASS |
| Empty CSV initialization | Header is created with four columns | `DataLogger` creates the documented header | PASS |
| Valid 3-field payload | Distance, level, and pump are accepted | Parser accepts `15,25,ON` | PASS |
| Valid legacy 4-field payload | Leading field is ignored | Parser accepts backward-compatible format | PASS |
| Invalid pump state | Payload is rejected | Values other than `ON` or `OFF` return no reading | PASS |
| Percentage bounds | Level remains between 0 and 100 | Parser clamps values to the supported range | PASS |
| Low-water indication | Red state and buzzer warning below 30% | Dashboard logic applies `< 30` threshold | PASS |
| Full-tank indication | Green state at 90% or above | Dashboard logic applies `>= 90` threshold | PASS |
| Pump activation count | Count increments on OFF-to-ON transition | Dashboard tracks transition state | PASS |
| Port unavailable | UI remains responsive and retries | Serial reader reports disconnected state | PASS |
| CSV append | Valid readings create timestamped rows | Logger writes the four-column schema | PASS |
| HC-SR04 empty reference | Stable calibrated empty percentage | Execute with installed tank hardware | PENDING HARDWARE |
| Relay isolation | Pump switches without unsafe exposure | Execute with qualified electrical review | PENDING HARDWARE |
| LCD address | Text renders at configured I2C address | Execute against the installed LCD | PENDING HARDWARE |
| End-to-end pump cycle | Low state starts and full state stops pump | Execute with approved firmware and safe test load | PENDING HARDWARE |

## Reproducible Software Check

```powershell
python -m py_compile dashboard.py dashboard_assets.py water_logger.py
python -m pip check
```

Hardware results should include firmware revision, tank dimensions, sensor mounting distance, COM port, date, and operator initials.
