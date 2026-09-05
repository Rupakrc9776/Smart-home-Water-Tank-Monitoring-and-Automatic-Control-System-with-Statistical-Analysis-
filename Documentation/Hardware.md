# Hardware

## Components and Roles

| Component | Role | Engineering note |
| --- | --- | --- |
| Arduino UNO | Controller and USB serial endpoint | Use a regulated logic supply and common ground |
| HC-SR04 | Water-surface distance sensor | Mount vertically and keep the beam clear of obstructions |
| Relay module | Pump switching interface | Check coil voltage and contact rating |
| 16x2 I2C LCD | Local status display | Confirm the module address during commissioning |
| Active buzzer | Audible low-water warning | Drive within the module's voltage/current limits |
| Red LED | Low-level state | Use a current-limiting resistor |
| Yellow LED | Intermediate state | Use a current-limiting resistor |
| Green LED | Full/healthy state | Use a current-limiting resistor |
| Push buttons | Setpoint and mode inputs | Use the firmware's pull-up/pull-down policy |
| Breadboard and jumpers | Prototype interconnect | Do not use as a permanent mains installation |

## Wiring Contract

| Pin | Signal |
| --- | --- |
| D2 | HC-SR04 Trigger |
| D3 | HC-SR04 Echo |
| D7 | Active buzzer |
| D8 | Red LED |
| D9 | Yellow LED |
| D10 | Set button |
| D11 | Green LED |
| D12 | Manual / Auto button |
| D13 | Relay module input |

The 16x2 I2C LCD uses the Arduino I2C pins, normally A4/SDA and A5/SCL on an UNO. Confirm the LCD module's pinout and address before applying power.

## Working Principle

The HC-SR04 emits an ultrasonic pulse and measures the return time. The controller converts the measured distance into a tank-level percentage using the calibrated empty and full distances. The controller updates the LCD and indicators, decides the pump state according to its configured operating mode, and reports a newline-terminated reading over USB serial.

The dashboard interprets values below 30% as low water and values at or above 90% as full. The Python application displays the reported pump state; the firmware remains the authority for physical relay control.

## Calibration Process

1. Measure the sensor-to-water distance at the known empty reference.
2. Measure the sensor-to-water distance at the known full reference.
3. Record the usable range and account for the sensor's minimum measurement distance.
4. Test at low, intermediate, and full reference levels.
5. Confirm the reported percentage and LED state at each reference.
6. Record the calibration date, tank dimensions, and firmware revision in the project report.

## Safety Precautions

- Keep mains wiring physically separated from Arduino and breadboard wiring.
- Use a correctly rated, enclosed relay or contactor for the pump.
- Add appropriate fusing and overcurrent protection.
- Never handle exposed conductors while the pump circuit is energized.
- Test automatic switching with the pump disconnected before connecting the load.
- Protect the electronics from water ingress and condensation.
- Use a qualified electrician for permanent installations.
