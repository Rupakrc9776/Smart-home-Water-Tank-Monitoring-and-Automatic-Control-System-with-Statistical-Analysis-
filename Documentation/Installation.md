# Installation

## Prerequisites

- Windows 10 or later.
- Python 3.13 recommended.
- Arduino IDE for firmware upload.
- A USB data cable and an available COM port.
- Low-voltage test hardware assembled according to the reviewed circuit diagram.

## Python Environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify the interpreter and package installation:

```powershell
python --version
python -m pip check
python -m py_compile dashboard.py dashboard_assets.py water_logger.py
```

## Hardware Bring-Up

1. Inspect the wiring with power disconnected.
2. Confirm common ground for the low-voltage modules.
3. Confirm the HC-SR04 trigger and echo lines are on D2 and D3.
4. Confirm relay input is on D13 and that the pump load is isolated.
5. Upload the working Arduino firmware from `Arduino_Code/`.
6. Open the Arduino serial monitor only for a brief protocol check, then close it before starting Python.

## First Run

```powershell
python dashboard.py
```

The dashboard scans for a likely Arduino port. If no port is found, type the port identifier, such as `COM5`, into the port field and select **RECONNECT**. The application creates `water_data.csv` with the required header when needed.

For a terminal-only logger:

```powershell
python water_logger.py
```

Press `Ctrl+C` to stop the logger cleanly.

## Clean Installation Check

A clean installation is ready when the dashboard starts without an import error, the COM port is detected or can be entered manually, a valid payload updates the level display, and a new CSV row contains all four expected columns.
