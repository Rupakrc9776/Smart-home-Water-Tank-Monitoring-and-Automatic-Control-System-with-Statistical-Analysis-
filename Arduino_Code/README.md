# Arduino Code

This directory is the intended home for the Arduino UNO firmware for the **SMART HOME WATER TANK MONITORING AND AUTOMATIC CONTROL SYSTEM WITH STATISTICAL ANALYSIS**.

## Firmware Contract

The Python applications expect 9600 baud and a newline-terminated CSV payload:

```text
<distance_cm>,<water_percent>,<pump_state>
```

Example:

```text
15,25,ON
```

The working UNO firmware is [Smart_Water_Tank.ino](Smart_Water_Tank.ino). Do not infer a production wiring or pump-safety policy from this documentation alone.

See [../Documentation/Hardware.md](../Documentation/Hardware.md) for the verified pin assignment and calibration guidance.
