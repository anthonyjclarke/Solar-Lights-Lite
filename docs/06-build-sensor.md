# 06 – Module D: light sensor and test button

**Drawing:** sheet 2 (`drawings/sheet-2.png`). **Wiring:** nets `LDR_POWER`,
`LDR_SENSE` and `TEST`.

The light sensor decides when it is dusk and dawn; the button gives you a
60-second test at any time of day.

**What you will learn:** voltage dividers, ratiometric ADC readings, switching
a sensor's supply from a GPIO pin to save power, hysteresis and debouncing,
and pin-change interrupts.

---

## How the sensor works

```
D7 ──> LDR1 ──┬──> A1
              │
              R4 47 kΩ
              │
           GND_LOAD
```

The LDR's resistance rises in the dark. With R4 = 47 kΩ, A1 reads as a fraction
of VCC:

| A1 reading | Meaning                | LDR resistance |
| :--------- | :--------------------- | :------------- |
| Below 30 % | Dark                   | Above ~110 kΩ  |
| 30–60 %    | In between (no change) | ~31–110 kΩ     |
| Above 60 % | Light                  | Below ~31 kΩ   |

Because D7 and the ADC reference are both VCC, the reading does not depend on
battery voltage. D7 is switched on for a few milliseconds per wake, so the
divider draws nothing between readings. A reading must stay dark (or light) for
300 scheduler seconds – about 5.5 minutes on the reference board – before the
controller changes state, and the gap between 30 % and 60 % stops it
hunting at dusk.

The thresholds live in `firmware/controller/include/config.h`
(`LDR_DARK_RATIO`, `LDR_LIGHT_RATIO`). R4 sets where they fall: a larger R4
makes the sensor call "dark" later (it needs a darker sky).

---

## Build steps

1. Wire D7 → LDR1 → A1, and A1 → R4 (47 kΩ) → GND_LOAD.
2. Mount the LDR where it sees the sky but **not the LED string**: the lights
   must never be able to convince the sensor it is daytime. A short tube or
   hood around the LDR helps.
3. Wire SW1 between D2 and GND_LOAD. The firmware enables D2's internal
   pull-up and a pin-change interrupt, so a press wakes the controller
   immediately.

---

## Test gate

**Gate 3** in [10 – Commissioning](10-commissioning.md): cover and uncover the
LDR and confirm the transitions. Test darkness with a truly light-tight cover;
a loose cap can still let through enough light to read about 20 %.

**Calibrate in the final position.** With Advanced Telemetry running, note the
`Arduino LDR` value at the moment you would like the lights to come on. If it
is well above 30 %, the lights will come on later than you want: raise
`LDR_DARK_RATIO` in `config.h` (keeping `LDR_LIGHT_RATIO` about 0.3 above it),
or fit a smaller R4. If the lights come on too early, do the opposite.

---

## What can go wrong

| Symptom                           | Likely cause                     |
| :-------------------------------- | :------------------------------- |
| Lights never come on              | Dark reading stays above 30 %    |
| Lights switch off soon after dusk | LEDs lighting the LDR            |
| Lights on during the day          | LDR shaded or covered            |
| Button does nothing               | Cut-off active, or D2 not to GND |
| Transition takes ~5.5 min         | Normal: 300 s confirmation       |
