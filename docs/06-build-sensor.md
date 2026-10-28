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
              R4 22 kΩ
              │
              RV1 50 kΩ trimmer (wiper joined to pin 3)
              │
           GND_LOAD
```

The LDR's resistance rises in the dark. R4 and RV1 form the lower leg of the
divider, 22–72 kΩ. Set to mid-travel, the leg is 47 kΩ, the value the firmware
was calibrated with, and A1 reads as a fraction of VCC:

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
(`LDR_DARK_RATIO`, `LDR_LIGHT_RATIO`). The lower leg sets where they fall, and
RV1 changes it without reflashing: more resistance makes the sensor call
"dark" later (it needs a darker sky). Across RV1's travel, the dark point moves
from an LDR of about 51 kΩ to 168 kΩ.

---

## Build steps

1. Wire D7 → LDR1 → A1, and A1 → R4 (22 kΩ) → RV1 pin 1. Join RV1's wiper
   (pin 2) to pin 3 and take pin 3 to GND_LOAD. RV1 is a 3296W multi-turn
   trimmer, 50 kΩ (marked 503). Before fitting, set it to mid-travel: about
   25 kΩ between pins 1 and 2.
2. Mount the LDR where it sees the sky but **not the LED string**: the lights
   must never be able to convince the sensor it is daytime. A short tube or
   hood around the LDR helps. Check it at night: with the lights on, `ldr=`
   should rise by only a few points and stay well below the light threshold
   (Gate 3, step 6). On the bench, the string raised it by 4.5, 8 and 16
   points in three different positions.
3. Wire SW1, the TEST button, between D2 and GND_LOAD. The firmware enables D2's internal
   pull-up and a pin-change interrupt, so a press wakes the controller
   immediately.

---

## Test gate

**Gate 3** in [10 – Commissioning](10-commissioning.md): cover and uncover the
LDR and confirm the transitions. Test darkness with a truly light-tight cover;
a loose cap can still let through enough light to read about 20 %.

**Calibrate in the final position.** With Advanced Telemetry running, note the
`Arduino LDR` value at the moment you would like the lights to come on. If it
is well above 30 %, the lights will come on later than you want: turn RV1
towards more resistance, which raises the reading, until it sits just below
30 % at that moment. If the lights come on too early, turn it the other way.
Measure between RV1's pins 1 and 2 to find which way your part turns. If RV1's
range is not enough, change `LDR_DARK_RATIO` in `config.h` (keeping
`LDR_LIGHT_RATIO` about 0.3 above it).

Each threshold has a 3 % hysteresis band (`LDR_HYSTERESIS`): once the reading
is DARK it stays DARK until it rises above 33 %, and once LIGHT it stays LIGHT
until it falls below 57 %. Noise near a threshold therefore cannot restart the
300 s confirmation. Even so, the night-time reading should sit clearly below
the dark threshold. A reading that hovers just under it, as indoor room light
can cause, delays dusk; widen the margin rather than relying on the
hysteresis.

---

## What can go wrong

| Symptom                           | Likely cause                     |
| :-------------------------------- | :------------------------------- |
| Lights never come on              | Dark reading stays above 30 %    |
| Lights switch off soon after dusk | LEDs lighting the LDR            |
| Lights on during the day          | LDR shaded or covered            |
| Button does nothing               | Cut-off active, or D2 not to GND |
| Transition takes ~5.5 min         | Normal: 300 s confirmation       |
