# Troubleshooting

## COM Port Issues

- Check Windows Device Manager for the Arduino entry and note its COM number.
- Close Arduino Serial Monitor and any other application using the port.
- Enter the port manually in the dashboard and select **RECONNECT**.
- Try a known-good USB data cable and a direct USB port.

## Serial Permission Errors

- Close competing serial applications.
- Disconnect and reconnect the board.
- Confirm the selected port belongs to the intended controller.
- On managed machines, ask the administrator to permit access to the USB serial device.

## LCD Address Problems

- Confirm SDA and SCL wiring for the Arduino UNO.
- Run an I2C scanner and record the detected address.
- Match the firmware configuration to the detected address.
- Check contrast adjustment and common ground.

## Relay Problems

- Test the relay input LED with the pump disconnected.
- Confirm the relay module logic level and coil supply.
- Verify D13 is not shorted and that the firmware's active level matches the module.
- Inspect contact wiring and rating before connecting the pump.

## Sensor Noise

- Mount the HC-SR04 perpendicular to the water surface.
- Keep the transducer clear of tank walls, pipes, and splashing water.
- Add a mechanically stable bracket and repeat calibration.
- Investigate large jumps in raw distance before changing software thresholds.

## Dashboard Errors

- Run from the repository root so local imports resolve correctly.
- Confirm the virtual environment is active.
- Delete or move a malformed CSV copy only after preserving the original data.
- Check that the display driver supports Tkinter on the target Python installation.

## Python Library Errors

```powershell
python -m pip install -r requirements.txt
python -m pip check
```

If `ttkbootstrap` is unavailable, the dashboard includes a standard Tkinter fallback. Missing `pyserial`, `matplotlib`, or `Pillow` must still be corrected for the full feature set.
