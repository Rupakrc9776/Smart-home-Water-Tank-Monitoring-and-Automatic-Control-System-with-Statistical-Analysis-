# Statistical Analysis

The dashboard presents descriptive statistics over the latest valid readings held in its rolling 30-sample deque. The CSV retains the complete session history for later analysis.

Let the valid water-level samples be $L_1, L_2, ..., L_n$, where each $L_i$ is a percentage in the range 0 to 100.

## Average Water Level

$$
\bar{L} = \frac{1}{n}\sum_{i=1}^{n}L_i
$$

The dashboard reports the arithmetic mean to one decimal place. It is a snapshot of the current rolling window, not a lifetime tank average.

## Maximum Level

$$
L_{max} = \max(L_1, L_2, ..., L_n)
$$

This helps identify the highest observed fill state during the current dashboard history.

## Minimum Level

$$
L_{min} = \min(L_1, L_2, ..., L_n)
$$

A low minimum should be interpreted together with sensor noise, calibration, and whether the pump was running.

## Pump Activation Count

An activation is counted when the dashboard observes a transition from `OFF` to `ON`:

$$
A = \sum_{i=2}^{n} I(P_{i-1}=OFF \land P_i=ON)
$$

where $I(condition)$ is 1 when the condition is true and 0 otherwise. The count resets when the dashboard process restarts and therefore is not a permanent maintenance counter.

## Water Trend Analysis

The live graph plots the ordered percentage series against reading number. A rising sequence generally indicates filling, while a falling sequence generally indicates consumption or drainage. A noisy sequence can indicate turbulence, obstructions, poor sensor mounting, or an unsuitable sample interval.

## Limitations

- The dashboard does not perform outlier rejection beyond payload parsing and percentage clamping.
- Repeated samples at the same second remain separate observations.
- Statistics are based on the loaded rolling history, not necessarily the entire CSV.
- Correlation between pump activity and level change requires offline analysis with aligned timestamps.
