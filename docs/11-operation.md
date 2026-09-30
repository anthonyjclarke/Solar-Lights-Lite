# 11 – Operation and maintenance

Once commissioned, Solar Lights Lite needs no attention day to day. This page
describes normal behaviour, what the button and telemetry tell you, routine
care, and how to diagnose problems.

---

## A normal day

| When                 | What happens                              |
| :------------------- | :---------------------------------------- |
| Power-on or reset    | 10 s flash (self-test)                    |
| Daytime              | Lights off; controller wakes every 8 s    |
| Dusk                 | ~5.5 min of darkness, then a slow fade up |
| Night                | Lights on at the night level              |
| Battery below 3.45 V | Night level halves                        |
| Dawn                 | ~5.5 min of light, then a slow fade off   |
| Battery below 3.30 V | Lights off until daylight and > 3.60 V    |

Brightness falls gently through a long night as the battery voltage drops. This
is by design: the LED string is driven directly, so its current follows the
battery.

## The test button

Press the button at any time to run the lights at the night level for
60 seconds – useful for checking the string in daylight. The button does
nothing while the low-voltage cut-off is active, which is itself a useful
signal: if a press gives no light, the battery is too low.

## What telemetry tells you

| Tier | Where to look                 | Look for                 |
| :--- | :---------------------------- | :----------------------- |
| 0    | The lights themselves         | On at dusk, off at dawn  |
| 1    | Advanced dashboard            | Live state, every change |
| 2    | Production dashboard (hourly) | Battery trend over days  |

The most useful single view is **battery voltage at dawn over a week or
more**. A steady or rising trend means the panel is keeping up; a falling one
means the system is in deficit (see Seasonal care).

---

## Routine care

| Interval      | Task                                        |
| :------------ | :------------------------------------------ |
| Monthly       | Clean the panel; clear leaves and shade     |
| Each season   | Check dawn battery trend; adjust brightness |
| Twice a year  | Check glands, seals and for condensation    |
| Yearly        | Inspect cells, holder, fuses, connections   |
| After a storm | Check the panel mount and the LED cable     |

## Seasonal care

Winter brings shorter days, longer nights and weaker sun, so the same panel
harvests less while the lights use more. If the dawn battery voltage trends
down:

1. Clean and re-aim the panel (steeper tilt for winter).
2. Lower `NIGHT_DUTY_PCT` in `firmware/controller/include/config.h` (for
   example to 60) and reflash.
3. Consider a larger panel (check its Voc against Option A/B in
   [03 – Power](03-build-power.md)).

Remember the charger cannot sense cell temperature: in freezing weather see
[Known limitations](01-design-overview.md#known-limitations).

---

## Troubleshooting

| Symptom                           | Check first                            |
| :-------------------------------- | :------------------------------------- |
| Lights never come on              | S1, fuses, cut-off; LDR seeing a light |
| Lights come on too late or early  | Recalibrate LDR thresholds (doc 06)    |
| Lights on during the day          | LDR shaded, covered or dirty           |
| Lights flicker at dusk            | LDR too close to the LED string        |
| Very dim all night                | Battery low: check dawn voltage trend  |
| Off before dawn most nights       | Energy deficit: see Seasonal care      |
| Button gives no light             | Low-voltage cut-off active             |
| No Tier 2 reports                 | D1 Mini power (U3), D0 → RST, Wi-Fi    |
| Tier 2 D1 Mini awake all the time | OTA helper left on                     |
| Battery voltage reads wrong in HA | Recalibrate the A0 multiplier (doc 09) |

If a problem is not obvious, put the system back into **Tier 1**: reflash the
controller with `advanced`, run the D1 Mini on USB with the Advanced profile
(open the U3 jumper first), and watch every decision the controller makes.
That is exactly what Advanced Telemetry is for.
