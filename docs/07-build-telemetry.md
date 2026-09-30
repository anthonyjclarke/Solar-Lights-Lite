# 07 – Module E: telemetry hardware

**Drawings:** sheet 6 (Tier 1, `drawings/sheet-6.png`) and sheet 3 (Tier 2,
`drawings/sheet-3.png`). **Wiring:** nets `UART_*`, `ESP_3V3`, `ADC_BATT` and
`WAKE`. **Software:** [09 – Home Assistant](09-home-assistant.md).

Telemetry is optional: skip this module for a standalone (Tier 0) build. It is
strongly recommended while commissioning, because it turns the controller's
diagnostics into live Home Assistant entities without a cable on the
controller.

**What you will learn:** serial (UART) signalling, level shifting and
inverting with a single transistor, buck-boost converters, ADC dividers,
ESP8266 deep sleep and wake-on-reset, and keeping two power domains apart.

---

## One harness, two tiers

The same wiring serves both telemetry tiers. Only the D1 Mini's power source
and the firmware change.

| Connection                 | Tier 1 Advanced   | Tier 2 Production |
| :------------------------- | :---------------- | :---------------- |
| Controller D1/TX → Q2 → D6 | Fitted            | Fitted            |
| VBAT_SYS → R5 → A0         | Fitted            | Fitted            |
| D1 Mini G → GND_LOAD       | Fitted            | Fitted            |
| D1 Mini power              | Its own micro-USB | U3 OUT → 3V3 pin  |
| U3 OUT → D1 Mini 3V3       | **Disconnected**  | Connected         |
| D0 → RST                   | Optional          | Fitted            |
| Controller firmware        | `advanced`        | `production`      |
| ESPHome profile            | Advanced          | Production        |

**Never power the D1 Mini from USB and U3 at the same time**: its onboard
regulator and U3 would both drive the 3V3 rail. Fit a jumper or a two-pin
plug in U3 OUT so switching tiers is a clean, visible change.

---

## The serial receiver (Q2)

```
Controller D1/TX ── R8 47 kΩ ──┬── Q2 base (2N3904)
                               R9 100 kΩ
                               │
GND_LOAD ──────────────────────┴── Q2 emitter

D1 Mini 3V3 ── R10 10 kΩ ──┬── Q2 collector
                            └── D1 Mini D6
```

The controller's TX swings between 0 V and the battery voltage (up to 4.2 V),
which is too high for the ESP8266's 3.3 V inputs. Q2 turns each TX high into a
collector low at D1 Mini logic levels, and each TX low into a high through R10.
The signal arrives inverted, so the ESPHome profiles declare D6 as
`inverted: true`. The D1 Mini's TX is never connected: the link is receive-only
and the D1 Mini cannot affect the controller.

R9 holds Q2 off whenever the controller's TX is low, released or unpowered. A
serial line idles high, so with the `advanced` build Q2 conducts between lines
(about 0.4 mA, mostly from the USB-powered D1 Mini). The `production` build
enables its serial port only while sending and parks TX low in between, so in
Tier 2 the link draws nothing between messages.

**Check the transistor's pin order.** 2N3904 and BC547-family parts come in
different E-B-C orders depending on the maker. Confirm with a datasheet or a
diode test before soldering.

---

## Battery sense

`VBAT_SYS → R5 220 kΩ → A0`. The D1 Mini already has a 220 kΩ/100 kΩ divider on
A0, so the total ratio is about 5.4. Clone boards vary; calibrate the ESPHome
multiplier against a meter in Gate 7.

---

## U3 – 3.3 V supply for Tier 2

The battery rail runs from 4.2 V down to about 3.0 V, crossing 3.3 V along the
way. A buck-only regulator cannot hold 3.3 V below that; a buck-boost can. The
TPS63802 breakout draws about 20–30 µA quiescent and handles the ESP8266's
radio bursts comfortably.

1. Set the breakout's output jumper to 3.3 V and **measure it** before
   connecting anything.
2. Wire VIN to VBAT_SYS (with C2, 470 µF, close to VIN) and GND to GND_LOAD.
3. Take U3 OUT to a jumper or plug that goes to the D1 Mini 3V3 pin. Leave it
   open for Tier 1.

The D1 Mini's own regulator stays fitted; in Tier 2 it is simply unused
because nothing feeds its 5V pin.

---

## Build steps

1. Build the Q2 receiver (Q2, R8, R9, R10) on the carrier near the D1 Mini.
2. Controller D1/TX → R8; Q2 collector → D1 Mini D6; R10 to D1 Mini 3V3.
3. R5 from VBAT_SYS to D1 Mini A0.
4. D1 Mini G to GND_LOAD (never to B-).
5. Fit U3 and C2; U3 OUT to the D1 Mini 3V3 pin **through an open jumper**.
6. Fit a removable link from D1 Mini D0 to RST (needed for Tier 2 deep-sleep
   wake; remove it when flashing the D1 Mini over USB).

Then flash the D1 Mini and set up Home Assistant:
[09 – Home Assistant](09-home-assistant.md).

---

## Test gates

The receiver is exercised from Gate 1 onwards if you commission with Tier 1.
**Gate 7** covers A0 calibration and service outages; **Gate 8** covers the
switch to Tier 2 and its standby current
([10 – Commissioning](10-commissioning.md)).

---

## What can go wrong

| Symptom                        | Likely cause                        |
| :----------------------------- | :---------------------------------- |
| No controller data in HA       | Controller running `standalone`     |
| Garbled or dropped lines       | Q2 pin order, or grounds not common |
| Battery voltage wildly off     | Multiplier not calibrated           |
| D1 Mini resets on radio bursts | U3 output not 3.3 V, or C2 missing  |
| D1 Mini never wakes (Tier 2)   | D0 → RST link missing               |
| Cannot flash D1 Mini over USB  | D0 → RST link fitted: remove it     |
