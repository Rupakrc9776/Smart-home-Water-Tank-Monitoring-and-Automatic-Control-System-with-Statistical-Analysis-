# Software

## Runtime Components

| File | Responsibility |
| --- | --- |
| `dashboard.py` | Tk dashboard, serial reader, CSV logger, graph, alerts, exports |
| `dashboard_assets.py` | Canvas drawing helpers and shared color palette |
| `water_logger.py` | Headless serial reader and append-only CSV writer |
| `requirements.txt` | Python dependency constraints |
| `water_data.csv` | Runtime and sample measurements |

## Serial Protocol

The reader uses 9600 baud and ignores malformed lines. Accepted payloads are either:

```text
15,25,ON
```

or the backward-compatible four-field form:

```text
ignored,15,25,ON
```

Distance is parsed as a non-negative floating-point value. Percentage is constrained to 0-100. The pump field is normalized to uppercase and must be `ON` or `OFF`.

## Data Storage

The CSV schema is:

| Column | Meaning |
| --- | --- |
| `Time` | Local time in `HH:MM:SS` format |
| `Distance_cm` | Parsed sensor distance in centimetres |
| `Water_Percent` | Parsed water level from 0 to 100 |
| `Pump` | `ON` or `OFF` |

`DataLogger` creates the parent directory and header when necessary. The logger is append-only; use a copy for analysis or archival processing.

## Threading Model

Serial I/O runs in a daemon thread. Parsed readings are queued back to Tk's event loop before the UI is mutated. This keeps blocking serial reads away from the dashboard event loop and allows the window to remain responsive.

## Compatibility Notes

The dashboard can run with `ttkbootstrap` for the darkly theme. Its import fallback uses the standard Tkinter themed widgets, so syntax and basic startup remain testable even when the optional visual theme is unavailable.
