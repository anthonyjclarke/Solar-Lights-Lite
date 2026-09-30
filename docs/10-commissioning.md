# 10 – Commissioning: test gates and final assembly

Never assemble everything and switch on for the first time. Each gate below
adds one thing, tests it, and must pass before the next. The order is chosen
so that a mistake costs a resistor, not a battery.

**What you will learn:** staged power-up, measuring current in circuit,
calibration, and how to decide from evidence that something is ready.

Record your results as you go (a template is at the end). Sheet 5
(`drawings/sheet-5.png`) shows gates 1–7 as a ribbon, and the printable
[controller bench sheet](drawings/controller-bench-sheet.pdf) covers Gate 1.

A note on time: the controller's clock is its watchdog oscillator, which on
the reference board runs about 12 % slow. A "300 s" confirmation therefore
takes about 5.5 real minutes. That is normal.

---

## Gate 0 – Inspection, power off

- Pad labels identified on M1: IN+, IN-, B+, B-, OUT+, OUT-.
- Controller regulator and power LED removed; no short between VCC and GND.
- No external link between B- and OUT-; S1 open; fuses fitted.
- Every connector labelled (colour scheme on sheet 4).

**Pass:** no continuity from VBAT_SYS to GND_LOAD; battery and panel still
disconnected.

---

## Gate 1 – Controller on a bench supply

Set up: controller fuses set and `advanced` build flashed
([08 – Firmware](08-firmware.md)). Current-limited bench supply (200 mA limit)
at 3.80 V to VCC/GND. LED string on R3. Button and LDR fitted. Diagnostics via
Tier 1 or a USB-UART adapter.

| Check                        | Expect                                      |
| :--------------------------- | :------------------------------------------ |
| Reset                        | Field guide, then lines starting `fw=`      |
| `vdd` vs meter               | Within 0.05 V after `BANDGAP_V` calibration |
| D9 PWM frequency             | 1.9–2.0 kHz (confirms 8 MHz clock)          |
| Press D2                     | `cause=BUTTON_TEST output=100%`             |
| LED current, 3.40 V          | About 11 mA (record actual)                 |
| LED current, 3.70 V          | About 15 mA (record actual)                 |
| LED current, 4.20 V          | About 21 mA; over 22 mA → fit 56 Ω          |
| Controller unpowered / reset | String dark                                 |

Measure LED current with a meter in series with the string positive, lights at
100 % (press D2).

**Pass:** calibrated supply reading, correct clock, LED current within the pin's
20 mA working rating (or R3 changed), nothing warm.

---

## Gate 2 – Protected battery

Power down. Connect **one** suitable cell to M1 B+/B-. With S1 open, meter
OUT+/OUT-: correct polarity, roughly the cell voltage. Close S1.

**Pass:** the controller runs from OUT+/OUT- only; `vdd` still matches the
meter; the D2 test works; no unexplained current or heat.

---

## Gate 3 – Light sensor and timing

1. In daylight or room light, confirm `sense=LIGHT` and `next_tick=8s`.
2. Cover the LDR with a light-tight cover. `sense=DARK`, ticks change to 1 s,
   `confirm=DUSK n/300s` counts up.
3. After 300 scheduler seconds: `mode=NIGHT`, output fades up at 2 % per
   second to the night level.
4. Uncover for 300 s: `mode=DAY`, output fades to 0.
5. Brief shadows or a torch flash must not cause a transition.

**Pass:** clean transitions, no flicker around the thresholds. Final threshold
calibration happens in the real location during Gate 7.

---

## Gate 4 – Low-voltage behaviour (bench supply)

Return to the bench supply; never deliberately over-discharge a cell. Cover the
LDR to reach night mode, then:

| Step                         | Expect                                 |
| :--------------------------- | :------------------------------------- |
| Lower VCC to 3.40 V          | Output settles at half the night level |
| Lower VCC to 3.25 V for 30 s | `mode=LVC output=0%`, immediately off  |
| Press D2                     | Lights stay off (`LVC_OFF`)            |
| Raise to 3.80 V, still dark  | Still off                              |
| Uncover the LDR for 300 s    | `mode=DAY`; normal again               |

**Pass:** cut-off, button lockout and daylight-only recovery all behave as
above.

---

## Gate 5 – Charger input and charge current

Test the charger from a current-limited bench supply before the panel is
connected.

- **Option B only:** with U0's output disconnected, feed its input from the
  bench supply and adjust it to 5.00 V. Check it at no load and under load,
  and at the highest input voltage you expect from the panel. With the input
  disconnected, check it does not draw current back from its output (night-time
  reverse leakage).
- **Charge current:** with a partly discharged cell on B+/B-, supply 5.0 V to
  M1 IN. Measure current into B+. It should match the PROG setting
  (100–150 mA).
- **Termination:** charge to completion with the controller connected. The
  cell should finish at 4.15–4.20 V and current should taper off.
- **Temperature:** module and cell stay comfortably warm at most.

**Pass:** correct input voltage, charge current as set, termination near
4.2 V with the load connected, acceptable temperatures. A charger LED alone is
not a pass.

---

## Gate 6 – Solar panel

Power down, then connect the panel (Option A to M1 IN, Option B to U0 IN).

- In full sun, measure panel voltage, M1 input voltage and charge current.
- Shade the panel, then unshade it: charging must resume on its own.
- At night, check that no current flows from the battery back towards the
  panel.

**Pass:** charging in sun, automatic recovery from shade, no night-time drain,
nothing hot.

---

## Module F – Final assembly

With gates 0–6 passed, move everything into the enclosure (sheet 4):

- Socket every module so it can be replaced. Keep cells in an insulated
  holder, shaded, and away from the charger module and R3.
- Separate the D1 Mini's antenna from the cells, wiring and any metal.
- Mount the LDR where it sees the sky and cannot see the LED string.
- Use cable glands for the panel, LED string and LDR, with strain relief.
- Assemble the pack with both matched, fused cells (Gate 2 used one).
- Leave the lid off, or easy to open, until Gate 7 has passed.

---

## Gate 7 – Soak test with Advanced Telemetry (14 days)

Run the complete system in its real location with Tier 1 telemetry and the
[Advanced dashboard](../homeassistant/dashboard-advanced-telemetry.yaml) for at
least 14 days, including overcast weather.

Before starting:

- Calibrate the D1 Mini's battery reading at three voltages
  ([09 – Home Assistant](09-home-assistant.md#calibrating-the-battery-reading)).
- Calibrate the LDR thresholds in place
  ([06 – Sensor](06-build-sensor.md#test-gate)).
- Turn Wi-Fi off, then Home Assistant off: the D1 Mini keeps receiving and
  reconnects afterwards. Install an OTA update: the controller link survives.

During the soak, watch:

- Battery voltage at dawn each day: it must not trend down day after day.
- Dusk and dawn times: sensible, no flicker, no daytime switching.
- No `LVC` events, no unexplained resets (`Arduino Scheduler Time` restarting).

**Pass:** no progressive energy deficit, no cut-off events, no reset loops, no
unsafe temperatures. If the battery trends down, lower `NIGHT_DUTY_PCT`, improve
the panel position or size, and repeat.

---

## Gate 8 – Production switch-over

1. Flash the controller with `production` (or `standalone`).
2. Move the D1 Mini to Tier 2
   ([09 – Home Assistant](09-home-assistant.md#moving-from-tier-1-to-tier-2)).
3. Measure the whole system's current from the battery in daylight, between
   D1 Mini wakes. Planning targets: controller about 20 µA or less; U3 and the
   sleeping D1 Mini together 0.5 mA or less.
4. Confirm hourly reports arrive and the lights still run dusk to dawn.

**Pass:** standby current within your energy budget; reports arriving; lights
unaffected.

---

## Production readiness checklist

- [ ] Gates 0–8 passed and recorded
- [ ] LED current measured in circuit at 4.20 V (≤ 22 mA)
- [ ] Charge current and termination measured with the load connected
- [ ] 14-day soak with no downward battery trend
- [ ] LDR thresholds calibrated in the final position
- [ ] Enclosure sealed, glands tight, cells insulated and shaded
- [ ] Cold-weather charging risk addressed for your climate
      ([Known limitations](01-design-overview.md#known-limitations))
- [ ] Production firmware and profile installed; tier jumpers correct

---

## Results template

| Gate | Date | Key measurements            | Pass? |
| :--- | :--- | :-------------------------- | :---- |
| 0    |      |                             |       |
| 1    |      | vdd cal; I at 3.4/3.7/4.2 V |       |
| 2    |      |                             |       |
| 3    |      | Dark / light readings       |       |
| 4    |      |                             |       |
| 5    |      | Charge mA; end voltage      |       |
| 6    |      | Sun mA; night leakage       |       |
| 7    |      | Dawn voltage trend          |       |
| 8    |      | Standby µA                  |       |
