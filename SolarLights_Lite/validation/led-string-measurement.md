# LED string measurement - 20-Sep-2026

Measured by the user with a Nordic Power Profiler Kit II as the supply and current
meter, a single 47 ohm resistor in series between supply positive and string positive,
string negative to supply ground. Room temperature, out of the enclosure.

| Supply V | Measured mA | V across 47 ohm | Implied string V |
|---|---:|---:|---:|
| 3.40 | 18 | 0.85 | 2.55 |
| 3.70 | 24 | 1.13 | 2.57 |
| 4.20 | 35 | 1.65 | 2.55 |

A straight line through the three points has a slope of 47 ohm, that is the series
resistor alone, and an intercept of 2.56 V. Over this range the string behaves as a
fixed 2.56 V drop with no significant dynamic resistance:

    I = (V - 2.56 V) / R_series

Model against the measurements: 17.9, 24.3 and 34.9 mA versus 18, 24 and 35.

## What this closes

- H04, for this string, at room temperature, between 3.4 and 4.2 V, with a series
  resistor fitted. Peak current is set by R_series. PWM duty changes the average only.
- It makes the switch selection question (H07) moot at the chosen brightness: see
  the Q1 disposition in [BOARD_AND_PARTS.md](../docs/BOARD_AND_PARTS.md).

## What it does not establish

- Temperature coefficient. Forward voltage falls as the LEDs warm, so current rises.
  Not measured; the outdoor range is wider than the bench.
- Per-branch distribution. One common resistor was used. If the string contains
  parallel bare LEDs, individual branch currents were not measured.
- Ageing, moisture ingress, or the voltage drop of the installed outdoor cable run.
- Instrument accuracy was taken as given. No second meter was used to cross-check.

## Brightness decision

The user viewed the string at these levels and accepted approximately 15 mA, which is
the reduced-peak case anticipated in BOARD_AND_PARTS.md: a lower peak permits a lighter
drive. At 15 mA no switching device is needed at all.
