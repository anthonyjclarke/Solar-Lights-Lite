# 02 – Parts, tools, skills and safety

Everything here is a common hobby module or through-hole part. A printable
checklist version of the parts list, with a "have it?" column, is in
[`parts-list.csv`](parts-list.csv). Reference designators match the drawings,
the wire schedule and the KiCad schematic.

---

## Parts by module

### Module A – power, charging and battery

| Ref     | Part                           | Notes                              |
| :------ | :----------------------------- | :--------------------------------- |
| PV1     | Solar panel, ~1–2 W            | Reference: AS102-0712A 1.2 W       |
| U0      | 5 V buck module, e.g. MP1584EN | Option B panels only (Voc > 6.5 V) |
| M1      | Protected TP4056-family module | Six pads: IN, B, OUT (± each)      |
| BT1/BT2 | Matched 18650 Li-ion cells × 2 | 1S2P, in an insulated holder       |
| FB1/FB2 | 1 A fuse + holder × 2          | One per cell positive lead         |
| F2      | 1 A fuse + holder              | After M1 OUT+                      |
| S1      | SPST service switch            | Breaks the whole protected rail    |

### Module B – controller

| Ref | Part                            | Notes                            |
| :-- | :------------------------------ | :------------------------------- |
| M2  | ATmega328P Pro Mini-class board | Reference: BTE13-010A clone      |
| C3  | 100 µF electrolytic, 10 V       | Across VCC/GND at the controller |
| C4  | 100 nF ceramic                  | Across VCC/GND at the controller |

### Module C – lighting

| Ref  | Part                              | Notes                              |
| :--- | :-------------------------------- | :--------------------------------- |
| R3   | 47 Ω, ¼ W                         | At the controller end; 56 Ω option |
| JLED | Low-power LED string              | ~2.5–3 V forward, ≤ 20 mA total    |
| –    | 2-way screw terminal or connector | Outdoor cable to the string        |

### Module D – light sensor and button

| Ref  | Part                      | Notes                        |
| :--- | :------------------------ | :--------------------------- |
| LDR1 | Light-dependent resistor  | Typical 5–10 kΩ (light) type |
| R4   | 47 kΩ                     | LDR divider lower resistor   |
| SW1  | Momentary push button, NO | D2 to ground; test button    |

### Module E – telemetry (optional)

| Ref | Part                        | Notes                              |
| :-- | :-------------------------- | :--------------------------------- |
| M3  | Wemos D1 Mini (ESP8266)     | Any common clone                   |
| U3  | TPS63802 buck-boost, 3.3 V  | e.g. HL802A breakout, 3.3 V jumper |
| C2  | 470 µF electrolytic, 10 V   | At U3 input                        |
| Q2  | 2N3904 NPN (or BC547–BC550) | Serial inverter; check E-B-C order |
| R8  | 47 kΩ                       | Controller TX to Q2 base           |
| R9  | 100 kΩ                      | Q2 base to emitter                 |
| R10 | 10 kΩ                       | Q2 collector pull-up to 3V3        |
| R5  | 220 kΩ                      | Battery sense to D1 Mini A0        |

### Module F – enclosure and assembly

| Item                            | Notes                                 |
| :------------------------------ | :------------------------------------ |
| Weatherproof box (IP65 or so)   | Shaded position, room to service      |
| Cable glands × 3                | Panel, LED string, LDR                |
| Perfboard / stripboard carrier  | Sockets for M1, M2, M3, U3            |
| Female headers, screw terminals | Modules must stay replaceable         |
| Standoffs, cable ties, labels   | Label every connector (sheet 4)       |
| Clear window or light pipe      | So the LDR sees the sky, not the LEDs |

---

## Parts to avoid

- **AMS1117 or other linear regulators for U0.** A linear regulator turns the
  difference between panel and 5 V into heat – about 30 % of a 1.2 W panel's
  output – and drops out of regulation in weak light.
- **TPS63802 for U0.** Its 5.5 V input limit is below a typical panel's
  open-circuit voltage.
- **A second board that is not an ATmega328P** (for example a Pro Micro with an
  ATmega32U4). The firmware uses 328P-specific registers, interrupts and ADC
  channels; it is not a drop-in replacement.
- **Unknown or unmatched cells in parallel.** See Safety below.

---

## Tools

| Tool                               | Used for                            |
| :--------------------------------- | :---------------------------------- |
| Temperature-controlled iron        | All soldering                       |
| Flux, braid or hot air             | Removing the Pro Mini regulator/LED |
| Multimeter                         | Every test gate                     |
| Current-limited bench supply       | Controller tests without a battery  |
| USBasp programmer (or an Uno/Nano) | ISP flashing and one-time fuses     |
| Computer with PlatformIO, avrdude  | Building and flashing firmware      |
| Home Assistant + ESPHome           | Telemetry tiers 1 and 2             |
| USB-UART adapter, 3.3 V (optional) | Wired serial monitor alternative    |
| Power profiler (optional)          | Sleep and LED current measurements  |

A current-limited bench supply is the single most useful tool here: it lets you
test the controller and the LED string across the whole battery range, and
simulate a flat battery, without risking a lithium cell.

---

## What you will learn

| Area             | Skills                                       |
| :--------------- | :------------------------------------------- |
| Soldering        | Through-hole, SMD rework, perfboard layout   |
| Electronics      | Dividers, LED current, transistor inverters  |
| Power            | Li-ion charging, protection, fusing, budgets |
| Microcontrollers | Fuses, ISP, sleep modes, watchdog, ADC, PWM  |
| Firmware         | C++ on AVR, host unit tests, build profiles  |
| ESPHome          | UART parsing, deep sleep, OTA, secrets       |
| Home Assistant   | Dashboards, packages, helpers, automations   |
| Test discipline  | Staged power-up and acceptance gates         |

---

## Safety

Lithium-ion cells store a lot of energy. Treat every step that involves them
with care.

- **Never connect cells in series to a 1S charger**, and never bridge the
  module's B- to OUT-: that bypasses the protection circuit.
- **Only parallel matched cells**: same type, age, capacity and state of
  charge. Voltage equality alone does not prove two cells are safe to join.
  If in doubt, use a purpose-made protected 1S2P pack.
- **Fuse each cell** before the parallel junction (FB1/FB2). A single fuse
  after the junction cannot stop one cell feeding a fault in the other.
- **Do not solder to bare cell cans.** Use holders or pre-tabbed cells.
- **Do not short the pack to test protection.** Use a current-limited supply
  or an electronic load.
- **Never charge below 0 °C** and keep cells shaded and away from the charger
  and resistors. The charger module does not measure cell temperature.
- **Supervise charging** until Gate 5 and Gate 6 of
  [10 – Commissioning](10-commissioning.md) have passed.

### A note on reclaimed cells

Reclaimed cells, such as those from disposable vapes, can be usable, but their
history, condition, chemistry and suitability are unknown. They have worked
well with TP4056-family chargers in this project, but that is experience, not a
safety guarantee or a recommendation. Inspect and test cells properly, do your
own research, and if there is any doubt, use purpose-bought rechargeable cells.
