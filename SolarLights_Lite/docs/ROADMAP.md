# Roadmap

## Current bench state

The controller can be built for the internal-8-MHz ATmega328P path, and the LED
string has a measured 47 ohm series-resistor configuration. The LDR is **not yet
wired**. The panel/charger path, final pack wiring, and optional telemetry have not
been qualified. No outdoor or seasonal performance is verified.

## Before outdoor assembly

- Wire and calibrate the switched LDR in its final position; confirm dusk/dawn
  thresholds and light-string isolation.
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
