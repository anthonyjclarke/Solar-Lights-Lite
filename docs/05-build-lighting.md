# 05 – Module C: low-power lighting

**Drawing:** sheet 2 (`drawings/sheet-2.png`). **Wiring:** nets `PWM` and
`LED_POS`, plus `JLED.-` on `GND_LOAD`.

This module is a single resistor and a string of LEDs, which makes it the best
place in the project to learn how LED current really works.

**What you will learn:** LED forward voltage, why a series resistor sets
current, what PWM does and does not change, how much current a
microcontroller pin can safely supply, and how to measure it.

---

## What kind of lights

This controller drives a **low-power LED string directly by PWM from pin D9**.
There is no MOSFET or transistor between the pin and the lights, so the string
must be one that is happy at 20 mA or less in total, from a 3–4.2 V supply,
through a series resistor.

Suitable: small "fairy" or garden LED strings with a forward voltage around
2.5–3 V, or a handful of individual LEDs, each with its own resistor.

**Not suitable:** mains lights, 12 V garden lights, conventional or legacy
light fittings, or any string that expects its own driver or battery box. For
those, see the driver stage in [12 – Going further](12-going-further.md).

---

## How the current is set

An LED string behaves roughly like a fixed voltage drop. The reference string
measured 2.56 V with almost no change across the battery range, so:

```
I = (VBAT − Vstring) / (R3 + Rpin)
```

`Rpin` is the ATmega328P's own output resistance, roughly 30 Ω at these
currents (a typical datasheet characteristic, not a guaranteed value). With
R3 = 47 Ω the model predicts:

| Battery | R3 = 47 Ω | R3 = 56 Ω |
| :------ | --------: | --------: |
| 4.20 V  |     21 mA |     18 mA |
| 3.70 V  |     15 mA |     13 mA |
| 3.40 V  |     11 mA |      9 mA |

These are predictions. Gate 1 measures the real current through the pin; the
reference string's own characterisation is in
[`reference/led-string-characterisation.md`](reference/led-string-characterisation.md).

**PWM** switches D9 fully on and off about 1,960 times a second. The duty
cycle sets the average current and the brightness; the peak current in each
pulse is still set by R3 and the pin. That is why the firmware's
`NIGHT_DUTY_PCT` is a brightness and energy setting, not a safety limit.

---

## Build steps

1. Fit R3 (47 Ω) on the carrier, **at the controller end**, from D9 to the
   LED output terminal. The outdoor cable should always be on the far side of
   the resistor.
2. Connect the LED string's positive lead to the R3 terminal and its negative
   lead to GND_LOAD.
3. If your string is made of parallel LEDs without their own resistors, it
   needs one resistor per branch; a single shared resistor does not balance
   them.

---

## Test gate

**Gate 1** in [10 – Commissioning](10-commissioning.md) measures the string
current at 3.40, 3.70 and 4.20 V at 100 % duty. If it exceeds 22 mA at 4.20 V,
fit 56 Ω and measure again. Also confirm that R3 and the controller stay at
room temperature, and that the string is dark with the controller unpowered
and during reset.

---

## What can go wrong

| Symptom                        | Likely cause                           |
| :----------------------------- | :------------------------------------- |
| Very dim at 3.4 V              | Expected: brightness tracks battery    |
| Over 22 mA at 4.20 V           | String Vf lower than reference: 56 Ω   |
| Uneven brightness              | Parallel LEDs sharing one resistor     |
| Visible flicker on camera      | 1.96 kHz PWM banding; normal to eye    |
| Lights on while controller off | Wiring fault: D9 must be the only feed |
