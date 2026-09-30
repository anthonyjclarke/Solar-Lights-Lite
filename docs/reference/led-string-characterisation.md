# Reference LED string characterisation

This is the measurement behind the R3 value and the lighting model in
[05 – Low-power lighting](../05-build-lighting.md). Repeat it for your own
string: it takes ten minutes and tells you whether 47 Ω is right.

---

## Method

A current-limited bench supply that also measures current (a power profiler
works well) feeds the string through a single 47 Ω resistor: supply positive →
47 Ω → string positive, string negative → supply ground. Room temperature,
string out of its enclosure.

## Results

| Supply | Measured | Across 47 Ω | Implied string voltage |
| :----- | -------: | ----------: | ---------------------: |
| 3.40 V |    18 mA |      0.85 V |                 2.55 V |
| 3.70 V |    24 mA |      1.13 V |                 2.57 V |
| 4.20 V |    35 mA |      1.65 V |                 2.55 V |

A straight line through the three points has a slope of 47 Ω (the resistor
alone) and an intercept of 2.56 V. Across the battery range the string behaves
as a fixed 2.56 V drop with no significant internal resistance:

```
I = (V − 2.56 V) / R_series
```

The model gives 17.9, 24.3 and 34.9 mA against the measured 18, 24 and 35 mA.

## From bench to circuit

On the bench the supply connects directly to the resistor. In the finished
build the current comes through the controller's D9 pin, which adds roughly
30 Ω of its own output resistance. That is why the same 47 Ω gives about
21 / 15 / 11 mA in circuit rather than 35 / 24 / 18 mA. The in-circuit figures
are a model until you measure them in Gate 1 of
[10 – Commissioning](../10-commissioning.md).

The reference string was accepted as bright enough at about 15 mA, which is
comfortably inside the pin's 20 mA working rating, so no driver transistor is
needed.

## What this does not cover

- **Temperature.** LED forward voltage falls as they warm, so current rises
  slightly on a hot night.
- **Branch sharing.** If a string is built from parallel LEDs, one shared
  resistor does not guarantee each branch its share.
- **The installed cable.** Long thin cable adds a small voltage drop.
