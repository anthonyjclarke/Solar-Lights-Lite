# 03 – Module A: power, charging and battery

**Drawing:** sheet 1 (`drawings/sheet-1.png`). **Wiring:** nets `PV_*`,
`CHARGE_*`, `CELL*`, `PACK_*`, `PROTECTED_POS`, `FUSED_POS`, `VBAT_SYS`,
`GND_LOAD` in [`wire-schedule.csv`](wire-schedule.csv).

This module turns sunlight into a protected battery rail. It has no firmware,
and it is the part of the build most worth doing slowly.

**What you will learn:** how a linear Li-ion charger works and how to set its
current, why a solar panel's open-circuit voltage matters, how protection
circuits separate the cell from the load, how to fuse parallel cells, and how
to qualify a module you did not design.

---

## How it fits together

```
PV1 ──(Option B: U0 5 V buck)──> M1 IN+/IN-
                                  M1 B+/B-  <── FB1/FB2 ── BT1 ∥ BT2 (1S2P)
                                  M1 OUT+ ── F2 1 A ── S1 ── VBAT_SYS (+)
                                  M1 OUT- ─────────────────── GND_LOAD (−)
```

- **VBAT_SYS** is the protected, fused, switched positive rail. Every load
  (controller, U3, battery sense) connects here.
- **GND_LOAD** is M1 OUT-. Every load ground connects here. It is the only
  ground used in the rest of the build.
- **B- is not ground.** It sits behind the module's protection MOSFETs. Never
  connect anything to B- except the cells, and never link B- to OUT-.

---

## Choose your solar input: Option A or Option B

The TP4056 family is rated for a 4–8 V input, and 8 V is an absolute maximum,
not a design target. A panel's open-circuit voltage (Voc) rises in cold
weather and appears whenever the battery is full and the charger stops drawing
current. So the choice depends on the panel's **measured, cold, no-load** Voc:

| Panel Voc (cold, no load) | Option | Solar input                  |
| :------------------------ | :----- | :--------------------------- |
| 6.5 V or less             | A      | Panel straight to M1 IN+/IN- |
| Above 6.5 V               | B      | Panel → U0 5 V buck → M1 IN  |

The 6.5 V line leaves margin below the charger's absolute maximum; check it
against the datasheet of the chip actually on your module. A nominal "5 V"
panel is usually Option A. The reference 1.2 W panel (Vmp 7 V, Voc 7.6 V) is
Option B.

**U0 for Option B** must be a switching buck converter rated well above the
panel's cold Voc. The MP1584EN module (4.5–28 V in) is a good fit. It does not
ship set to 5 V: adjust it before it ever sees the charger.

Series diodes are **not** a substitute for either option: their drop depends on
current, so at no load they limit almost nothing.

---

## Build steps

### 1. Identify the charger module

1. Photograph both sides of M1. Read the pad labels: IN+, IN-, B+, B-, OUT+,
   OUT-. Work from the labels, not from pad positions in any drawing.
2. Read the chip markings. TP4056, TC4056 and similar parts behave alike but
   are not guaranteed identical; find the datasheet for yours.
3. With nothing connected, check with a meter whether IN- and OUT- are joined
   on the board (on many modules they are). Do not add any external link
   either way.

### 2. Set the charge current

Most modules ship with the PROG resistor set for about 1 A, which is far more
than a 1–2 W panel can supply; the charger would pull the panel voltage down
and stall. For a genuine TP4056 the charge current is about 1200 / R(kΩ) mA:

| PROG resistor | Charge current            |
| :------------ | :------------------------ |
| 12 kΩ         | ~100 mA                   |
| 8.2 kΩ        | ~146 mA                   |
| 1.2 kΩ        | ~1 A (typical as shipped) |

Replace the PROG resistor (a small SMD part next to the chip) for 100–150 mA.
Confirm the result by measurement in Gate 5; a clone may not follow the
formula exactly.

### 3. Prepare the cells

1. Choose two matched 18650 cells (see Safety in
   [02 – Parts, tools, skills and safety](02-parts-and-tools.md#safety)).
2. Charge or discharge each to the same voltage (within 0.05 V) separately
   before joining them.
3. Fit a 1 A fuse in each cell's positive lead (FB1, FB2), then join the two
   fused leads to M1 B+. Join both negatives to M1 B-.

### 4. Build the protected rail

1. M1 OUT+ → F2 (1 A) → S1 → **VBAT_SYS**.
2. M1 OUT- → **GND_LOAD**.
3. Leave S1 open until the controller is ready (Gate 2).

### 5. Connect the solar input

- **Option A:** panel + to M1 IN+, panel − to M1 IN-.
- **Option B:** first set U0 to 5.00 V on a current-limited supply with its
  output disconnected (Gate 5), then panel → U0 IN, U0 OUT → M1 IN.

Do the panel connection last, after Gate 5 has passed on a bench supply.

---

## Test gates

This module is qualified by **Gate 0** (inspection), **Gate 2** (protected
battery), **Gate 5** (charger input and charge current) and **Gate 6** (solar
panel) in [10 – Commissioning](10-commissioning.md).

---

## What can go wrong

| Symptom                            | Likely cause                              |
| :--------------------------------- | :---------------------------------------- |
| No voltage at OUT+ with cells in   | Protection tripped; briefly charge        |
| Charger LED on, battery not rising | Charge current higher than panel can give |
| Module hot in sun                  | Charge current set too high               |
| Battery drains at night            | Reverse leakage into panel or U0          |
| One cell warmer than the other     | Unmatched cells: stop and separate        |

A charger's LED is not a measurement. Use a meter in series with B+ to see the
real charge current.
