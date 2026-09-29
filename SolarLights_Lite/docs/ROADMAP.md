# Roadmap

## Current state (as built, 30-Sep-2026)

The whole v0.5 circuit is wired per the drawings: the internal-8-MHz ATmega328P
controller, the LED string on a measured 47 ohm series resistor, the switched LDR
on D7/A1, and the D1 Mini development telemetry. The panel/charger path, pack and
telemetry are built but not qualified, and the LDR thresholds are not calibrated.
No outdoor or seasonal performance is verified.

## Before outdoor assembly

- Calibrate the switched LDR in its final position; confirm dusk/dawn
  thresholds and light-string isolation.
- **Open item – U0:** choose the production panel, then select and fit the 5 V
  input regulator (MP1584EN if the 7.6 V Voc panel is kept). The bench currently
  uses a 5 V panel straight into M1.
- For the production profile, unplug the D1 micro-USB, connect U3 OUT to the D1
  3V3 pin, and qualify radio bursts and standby current on the battery.
- Qualify charger input conditioning, charge current/termination, weak-light
  recovery, actual module topology, and cell-temperature limits.
- Measure installed LED current and sleep current across the battery-voltage range;
  verify low-voltage cut-off and recovery.
- Complete protected-pack wiring and real panel tests, then log at least two weeks
  including overcast conditions and later winter behaviour.
- Use the v0.5 D1 Mini UART telemetry only as a development aid after the
  lighting and charging path pass their acceptance tests; return to the
  low-power D1 profile before measuring final energy use. Any carrier PCB
  remains optional follow-on work.
