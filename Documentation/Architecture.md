# Architecture

## System Architecture

```mermaid
flowchart TB
    Human[Operator] --> Buttons[Set and Manual/Auto buttons]
    Sensor[HC-SR04] --> MCU[Arduino UNO]
    Buttons --> MCU
    MCU --> LCD[16x2 I2C LCD]
    MCU --> LEDs[Red / Yellow / Green LEDs]
    MCU --> Buzzer[Active buzzer]
    MCU --> Relay[Relay module]
    Relay --> Pump[Pump load]
    MCU -- USB serial, 9600 baud --> Python[Python dashboard or logger]
    Python --> CSV[(water_data.csv)]
```

## Hardware Block Diagram

```mermaid
flowchart LR
    V5[Regulated 5 V logic supply] --> UNO[Arduino UNO]
    UNO -->|D2 trigger / D3 echo| HCSR04[HC-SR04]
    UNO -->|I2C| LCD[16x2 LCD]
    UNO -->|D7| Buzzer[Active buzzer]
    UNO -->|D8 D9 D12| LEDs[Status LEDs]
    UNO -->|D10 D11| Buttons[Set and AUTO/MANUAL inputs]
    UNO -->|D13| Relay[Relay input]
    Relay -. isolated load circuit .-> Pump[Pump]
```

## Software Workflow

```mermaid
flowchart TD
    Start([Application start]) --> Load[Load CSV history]
    Load --> Scan[Scan for Arduino port]
    Scan --> Connect{Serial connected?}
    Connect -- No --> Retry[Show disconnected state and retry]
    Retry --> Scan
    Connect -- Yes --> Read[Read serial line]
    Read --> Parse{Valid 3 or 4 field payload?}
    Parse -- No --> Read
    Parse -- Yes --> Update[Update visual state and KPIs]
    Update --> Append[Append reading to CSV]
    Append --> Read
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as Ultrasonic sensor
    participant A as Arduino UNO
    participant D as Python dashboard
    participant F as CSV file
    U->>A: Echo timing
    A->>A: Convert distance to percentage
    A-->>D: distance, percentage, pump
    D->>D: Validate and clamp values
    D->>F: Append timestamped row
    D-->>D: Refresh gauge, graph, alerts, and KPIs
```

## Dashboard Communication Flow

```mermaid
flowchart LR
    Port[COM port] --> Reader[SerialReader thread]
    Reader --> Queue[Thread-safe UI queue]
    Queue --> Apply[Dashboard._apply_reading]
    Apply --> Visuals[Gauge, tank, pump, LEDs, alerts]
    Apply --> History[30-reading deque]
    Apply --> Logger[DataLogger]
    History --> Graph[Matplotlib trend graph]
    Logger --> File[water_data.csv]
```

## Design Contracts

- Serial speed: `9600` baud.
- Accepted payload: `distance_cm,water_percent,pump_state`.
- Pump state: uppercase `ON` or `OFF` after parsing.
- Percentage range: clamped to `0..100`.
- Dashboard history: maximum 30 readings in memory.
- Low threshold: below 30%.
- Full threshold: 90% or higher.
