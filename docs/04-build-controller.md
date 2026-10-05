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

**Buy the 16 MHz board if that is what you can find.** Most Pro Minis on sale
are the 5 V/16 MHz version; 3.3 V/8 MHz boards are harder to find and cost
more. They use the same ATmega328P chip, and the two versions differ only in
the regulator and the clock part. This build removes the regulator and stops
using the crystal, so after rework and fuse setting both versions behave the
same. What you cannot do is leave a 16 MHz board running at 16 MHz from the
battery; see [Why the controller runs at 8 MHz](#why-the-controller-runs-at-8-mhz).

Check the chip marking says **ATmega328P** or **ATmega328PB**. Many current
clones carry the 328PB, sometimes sold as "ATmega328P". It runs the same
firmware and fuses (this firmware has been run on both chips), and needs only
avrdude's `-p m328pb` part name
([08 – Firmware](08-firmware.md#one-time-preparation-of-a-new-board)). Boards
with an ATmega32U4 (Pro Micro) or ATmega168 are not compatible.

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

## Powering the board: VCC, RAW and the serial header

A Pro Mini has three pins that look like power inputs:

| Pin                        | What it is                      | In this build           |
| :------------------------- | :------------------------------ | :---------------------- |
| `RAW`                      | Input to the on-board regulator | Never connected         |
| `VCC` (top row)            | The chip's supply rail          | The supply goes in here |
| `VCC` on the serial header | Same rail as the top-row `VCC`  | Step 3 check only       |

You may read that "VCC is an output". That is true only when the board is
fed through RAW: the regulator then produces VCC, and the pin can supply
other parts. Feeding VCC directly bypasses the regulator. That is a normal
way to power a Pro Mini, and it is how this build runs, from the protected
battery rail. Once the regulator is removed, VCC is the only way in.

On the reference board, and on standard Pro Mini designs, the top-row `VCC`
pin and the serial header's `VCC` are the same copper. Check yours once with
the board unpowered, in continuity mode: top-row `VCC` to header `VCC` should
beep, and after rework `RAW` to `VCC` should not.

Only one power source at a time, and never 5 V:

| Stage                         | Power source                   | Into         | Regulator      |
| :---------------------------- | :----------------------------- | :----------- | :------------- |
| Step 2 – fuses and flash      | USBasp set to 3.3 V            | `VCC` (ISP)  | Fitted is fine |
| Step 3 – first power-up check | USB-UART adapter set to 3.3 V  | Header `VCC` | Fitted is fine |
| Gate 1 – bench                | Bench supply 3.80 V, 200 mA    | `VCC`        | Removed        |
| Gate 2 onwards                | Battery via M1 OUT+ (VBAT_SYS) | `VCC`        | Removed        |

---

## Build steps

Prove the chip, fuses and firmware first, then do the rework, then decoupling.
Gate 0 confirms the rework before anything goes onto the bench supply.

### 1. Fit headers

Fit headers (or plan direct wiring) for VCC, GND, D1/TX, D2, D7, D9, A1 and
the six ISP pins (VCC, GND, RST, 11, 12, 13).

### 2. Set the fuses and flash the firmware

Follow [08 – Firmware](08-firmware.md):

1. Read the chip signature: `1E 95 0F` (ATmega328P) or `1E 95 16`
   (ATmega328PB, use `-p m328pb`).
2. Set the fuses once: low `0xE2`, high `0xD9`, extended `0xFD`.
3. Build and flash the `advanced` firmware for commissioning.

| Fuse     | Value  | Meaning                                |
| :------- | :----- | :------------------------------------- |
| Low      | `0xE2` | Internal 8 MHz RC oscillator, no ÷8    |
| High     | `0xD9` | No bootloader; SPI programming enabled |
| Extended | `0xFD` | Brown-out detection at 2.7 V           |

### 3. First power-up check

This proves the board before you solder on it.

1. Disconnect the USBasp.
2. Set a USB-UART adapter to **3.3 V**. Connect adapter GND to GND, adapter
   VCC to the serial header's `VCC`, and controller TX to adapter RX. Leave
   the adapter's TX, DTR and CTS open.
3. Run `pio device monitor --baud 9600` from `firmware/controller` and press
   the board's reset button. The banner should show the firmware version and
   the time you built it, followed by `fw=` lines.
4. Meter DC volts across the top-row `VCC` and `GND` pins and compare with
   `vdd=`.

| Check           | Expect                                                 |
| :-------------- | :----------------------------------------------------- |
| Banner          | `Firmware v0.6.0 built <date and time of your build>`  |
| `vdd=` vs meter | Within 0.05 V (calibrate in Gate 1 if not)             |
| `battery=`      | `LOW`: correct on 3.3 V, below the 3.45 V level        |
| First lines     | `cause=STARTUP_TEST`, then `DAY_OFF` or `DUSK_TO_DAWN` |

3.3 V is close to the 3.30 V cut-off, so leave the lighting tests for Gate 1.
`vdd=` around 5 V means the adapter is set to 5 V: disconnect it at once.
When you have finished, disconnect the adapter's VCC. From here on the
adapter is a monitor only (TX → RX and GND).

### 4. Identify the regulator and power LED

1. Photograph the board. With no power applied, use continuity mode to trace
   RAW to the regulator's input and VCC to its output. The regulator is
   usually a SOT-23-5 or SOT-89 part near RAW.
2. Find the power LED: the LED and series resistor connected permanently
   across VCC and GND. The LED on D13 is a different one; leave it.

### 5. Remove them

1. Remove the regulator with hot air, or with plenty of flux and a wide iron
   tip heating all pins together. Removing the power LED (or just its series
   resistor) is enough for the LED branch.
2. Do not remove decoupling capacitors next to the regulator.
3. Check for shorts between VCC and GND, and that RAW no longer connects to
   VCC.
4. Repeat the step 3 check. The same banner shows the rework did no harm.

Why: the regulator and power LED together can draw milliamps continuously,
which is hundreds of times the controller's sleep current. With a 2.7–4.2 V
Li-ion rail the ATmega328P needs no regulator at 8 MHz. The rework must be
done before Gate 0, which checks for it, and Gate 1.

### 6. Fit decoupling

On the carrier, fit C3 (100 µF, 10 V) and C4 (100 nF) across VCC and GND,
close to the board.

---

## Why the controller runs at 8 MHz

A 16 MHz Pro Mini is meant to run from its 5 V regulator. In this build the
chip runs directly from one Li-ion cell, at 2.7–4.2 V, and 16 MHz is not
reliable at those voltages.

**The voltage needed rises with clock speed.** The ATmega328P datasheet's
safe operating area allows 10 MHz from 2.7 V and 20 MHz from 4.5 V, with the
limit rising in a straight line between them. On that line, 16 MHz needs about
**3.8 V**:

| Clock  | Minimum rated supply | Li-ion cell (2.7–4.2 V)         |
| :----- | :------------------- | :------------------------------ |
| 8 MHz  | 2.4 V                | In spec over the whole range    |
| 16 MHz | ~3.8 V               | Out of spec for most of a night |

A cell rests at about 3.6–3.7 V and sinks lower overnight while the lights
draw on it, so a 16 MHz controller would run out of spec for most of every
night. Below its rated voltage an AVR does not stop cleanly: it can misread
flash, execute wrong instructions or corrupt registers, and it gets worse in
the cold. A 16 MHz board often seems fine on a warm bench, then fails at
random on a cold winter night outdoors, which is very hard to diagnose.

**Brown-out protection cannot fix it at 16 MHz.** The 2.7 V brown-out reset
(extended fuse `0xFD`) holds the chip in reset before it leaves its rated
area at 8 MHz. To protect a 16 MHz chip the same way you would need the 4.3 V
brown-out level, which is above a fully charged cell, so the controller would
never run.

**8 MHz also uses less power.** While the lights are on, the controller sleeps
in IDLE mode with its clock running, because Timer1 generates the D9 PWM. The
current it draws in that state rises roughly in proportion to clock speed. At
8 MHz there is still plenty of headroom for the firmware, which spends almost
all of its time asleep.

**Why the internal oscillator and not the crystal.** The 16 MHz crystal could
be divided down to 8 MHz in firmware, but the internal RC oscillator is
simpler. It needs no external parts, behaves the same on every board, whether
it has a crystal or a resonator, and restarts faster when the chip wakes from
power-down. Its accuracy is good enough for the 9600-baud telemetry link.
Setting the fuses is therefore the only change needed. It also clears the
board's bootloader setting; flashing is by ISP only
([why ISP, not a USB-serial upload](08-firmware.md#why-isp-not-a-usb-serial-upload)).

The firmware is built for the 8 MHz clock (PlatformIO board
`pro8MHzatmega328`), so its PWM and serial timing are wrong until the fuses
are set: garbled serial text is the giveaway.

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
| Signature `1E 95 16`               | ATmega328PB: use `-p m328pb`          |
| Serial text is garbage             | Fuses not set: still on 16 MHz clock  |
| High sleep current                 | Regulator or power LED still fitted   |
| D9 PWM not ~1.96 kHz               | Wrong clock (check the fuses)         |
