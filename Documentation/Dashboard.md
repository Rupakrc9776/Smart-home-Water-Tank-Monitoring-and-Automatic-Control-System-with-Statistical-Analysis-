# Dashboard

The dashboard is launched with `python dashboard.py` and is designed for an operator watching one tank and one serial controller.

## Widget Reference

| Widget | Behavior |
| --- | --- |
| Live Water Gauge | Displays the latest clamped percentage and changes color by operating range |
| Circular Gauge | Presents the same level as an animated arc for quick scanning |
| Tank Animation | Animates toward the latest level to make abrupt sensor changes easier to notice |
| Pump Status | Shows reported pump state, relay state, activation count, and last update time |
| Alert Center | Adds timestamped state changes such as low water, tank full, pump running, or pump stopped |
| Live Trend Graph | Plots the latest up to 30 water-percentage readings from the in-memory history |
| CSV Logger | Appends each valid live reading to `water_data.csv` |
| Statistical Analysis Cards | Shows current level, pump state, average, maximum, minimum, and active alert |

## Controls

- **PORT**: optional manual COM port override.
- **RECONNECT**: closes the current serial connection and restarts port handling.
- **CONTROL MODE**: dashboard-side mode label with `AUTO` and `MANUAL` choices. Physical control behavior remains firmware-owned.
- **EXPORT CSV**: copies the current CSV to a chosen destination.
- **SAVE GRAPH PNG**: exports the current trend graph.
- **SCREENSHOT**: captures the dashboard window under `Screenshots/`.
- **CLEAR GRAPH**: clears the current rolling graph history in memory; it does not delete CSV data.
- **EXIT**: stops serial handling and closes the window.

## Operating States

- Below 30%: red state, buzzer warning, and `LOW WATER / BUZZER ACTIVE` alert.
- 30% through 89%: yellow/intermediate state.
- 90% and above: green/full state and `TANK FULL` alert.
- Pump status is taken directly from the valid serial payload.

## Suggested Operator Sequence

1. Start the dashboard with the tank in a known safe condition.
2. Confirm **CONNECTED** and verify the displayed port.
3. Observe distance and percentage at a known reference level.
4. Exercise the pump only after checking relay wiring and load isolation.
5. Use **EXPORT CSV** before closing a test session.
6. Record unusual readings, alarms, and hardware changes in the test log.
