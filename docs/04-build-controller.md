# 04 – Module B: controller

**Drawings:** sheet 2 (`drawings/sheet-2.png`) and the board map
(`drawings/BTE13-010A-pin-map.png`). **Reference photos:**
[`reference/`](reference/). **Layouts:** the whole system on a
[breadboard](drawings/breadboard-layout.png) (bench build) or a
[perfboard carrier](drawings/perfboard-layout.png) (final build).

The controller is an ATmega328P Pro Mini-class board, modified to run straight
from the battery and to sleep at microamp levels. It runs the lights on its
own; nothing else in the system is required for the lights to work.

**What you will learn:** SMD rework (removing a regulator and an LED),
identifying a board from its silkscreen and tracks, what AVR fuses are, ISP
programming, and why clock speed and supply voltage are linked.

---

## Choosing a board

Any ATmega328P Pro Mini-class board works: 3.3 V/8 MHz or 5 V/16 MHz, genuine
or clone. The reference build uses a **BTE13-010A** clone with a 16 MHz
crystal. Whatever the board, the same fuse settings switch it to the
ATmega328P's internal 8 MHz oscillator, so the crystal or resonator no longer
matters and can stay fitted.

Check the chip marking says **ATmega328P**. Boards with an ATmega32U4 (Pro
Micro) or ATmega168 are not compatible.

---

## Pin map

| Pin   | Connection                     | Module |
| :---- | :----------------------------- | :----- |
| VCC   | VBAT_SYS (protected battery)   | A      |
| GND   | GND_LOAD (M1 OUT-)             | A      |
| RAW   | Not connected                  | –      |
| D9    | R3 47 Ω → LED string +         | C      |
| D7    | LDR supply (switched)          | D      |
| A1    | LDR / R4 midpoint              | D      |
| D2    | Test button to GND_LOAD        | D      |
| D1/TX | R8 47 kΩ → Q2 base (telemetry) | E      |
| 11–13 | ISP only (MOSI, MISO, SCK)     | –      |
| RST   | ISP only                       | –      |

D0, D3–D6, D8, D10 and A0, A2–A7 are unused; the firmware drives unused
digital pins low and disables unused analog input buffers.

---

## Build steps

### 1. Identify the regulator and power LED

1. Photograph the board. With no power applied, use continuity mode to trace
   RAW to the regulator's input and VCC to its output. The regulator is
   usually a SOT-23-5 or SOT-89 part near RAW.
2. Find the power LED: the LED and series resistor connected permanently
   across VCC and GND. The LED on D13 is a different one; leave it.

### 2. Remove them

1. Remove the regulator with hot air, or with plenty of flux and a wide iron
   tip heating all pins together. Removing the power LED (or just its series
   resistor) is enough for the LED branch.
2. Do not remove decoupling capacitors next to the regulator.
3. Check for shorts between VCC and GND afterwards.

Why: the regulator and power LED together can draw milliamps continuously,
which is hundreds of times the controller's sleep current. With a 2.7–4.2 V
Li-ion rail the ATmega328P needs no regulator at 8 MHz.

### 3. Fit headers and decoupling

1. Fit headers (or plan direct wiring) for VCC, GND, D1/TX, D2, D7, D9, A1 and
   the six ISP pins (VCC, GND, RST, 11, 12, 13).
2. On the carrier, fit C3 (100 µF, 10 V) and C4 (100 nF) across VCC and GND,
   close to the board.

### 4. Set the fuses and flash the firmware

Follow [08 – Firmware](08-firmware.md):

1. Read the chip signature (`0x1e950f`).
2. Set the fuses once: low `0xE2`, high `0xD9`, extended `0xFD`.
3. Build and flash the `advanced` firmware for commissioning.

| Fuse     | Value  | Meaning                                |
| :------- | :----- | :------------------------------------- |
| Low      | `0xE2` | Internal 8 MHz RC oscillator, no ÷8    |
| High     | `0xD9` | No bootloader; SPI programming enabled |
| Extended | `0xFD` | Brown-out detection at 2.7 V           |

Why 8 MHz: the ATmega328P is only rated for 16 MHz above about 3.8 V, and a
Li-ion cell spends every night below that. At 8 MHz it is rated down to 2.7 V,
which matches the brown-out setting.

---

## Test gates

The controller is proven on a current-limited bench supply in **Gate 1**, then
on the protected battery in **Gate 2**
([10 – Commissioning](10-commissioning.md)). The printable
[controller bench sheet](drawings/controller-bench-sheet.pdf) covers Gate 1.

---

## What can go wrong

| Symptom                            | Likely cause                          |
| :--------------------------------- | :------------------------------------ |
| Programmer cannot see the chip     | Wiring, pin 1 orientation, or no VCC  |
| Signature `0x000000` or `0xffffff` | No target power, or MISO/MOSI swapped |
| Serial text is garbage             | Fuses not set: still on 16 MHz clock  |
| High sleep current                 | Regulator or power LED still fitted   |
| D9 PWM not ~1.96 kHz               | Wrong clock (check the fuses)         |
