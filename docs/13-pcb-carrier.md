# 13 – PCB carrier

**Design files:** [`hardware/pcb-rev-b/`](../hardware/pcb-rev-b/) (KiCad 10).
**Fit check:** [`fit-sheet-A4.pdf`](../hardware/pcb-rev-b/review/fit-sheet-A4.pdf).
**Review pack:** [`pcb-review.pdf`](../hardware/pcb-rev-b/review/pcb-review.pdf).

The carrier PCB replaces the perfboard from guides 04–07. The Pro Mini (M2)
and D1 Mini (M3) plug into sockets, and the TP4056 charger (M1) solders
directly onto the board. Every external connection is a 2.54 mm pin header.
The circuit, firmware and ESPHome configuration are the same as in the wired
build, so modules A–F, tiers 0/1/2 and gates 0–8 all still apply.

**What you will learn:** how to read a two-layer board, check that a board
fits before you order it, order bare boards from a fabrication service,
assemble through-hole parts in a sensible order, and test a populated board
before any module goes in.

![Rev B carrier with pin headers fitted, angled view](images/pcb/carrier-angled.png)

*Rev B rendered with every pin header and passive part fitted. The three
modules are not drawn: M2 and M3 plug into the black sockets, and M1 sits
inside the outline at top right.*

---

## The board at a glance

| Item              | Rev B                                             |
|:------------------|:--------------------------------------------------|
| Size              | 74 × 51.5 mm, two layers, 1.6 mm FR-4, 1 oz       |
| Parts             | All through-hole; no SMD soldering                |
| M2 Pro Mini       | Two 12-way sockets, serial-header end up          |
| M3 D1 Mini        | Two 8-way sockets; antenna overhangs the top edge |
| M1 TP4056         | Six wire links through overlay holes, USB-C up    |
| External links    | Eight 2-pin headers along the bottom edge         |
| Tier links        | JP1–JP3, 2-pin headers with shunts                |
| Programming       | `JISP1` 2 × 3 AVR ISP header                      |
| Mounting          | Three 3.2 mm holes, no copper near them           |

The silkscreen shows each module's true outline, with its pin names beside
every socket hole. That makes a reversed module easy to spot. Turning M2 or
M3 through 180° puts signals on the wrong pins, so always match the module
to the outline and the `SERIAL END` / `ANTENNA END` marks.

![Rev B carrier, top view](images/pcb/carrier-top.png)

---

## Design decisions

- **B– is not ground.** On the board, `PACK_NEG` (B–) is its own net and
  never joins `GND_LOAD`. Only M1 OUT– is the load return, exactly as in
  guide 03.
- **The antenna overhangs the board.** M3's antenna end sticks out past the
  top edge, so there is no copper under it. The cost is that M3's
  micro-USB faces into the board. A right-angle micro-USB adapter, or
  ESPHome over-the-air updates, avoids the tight spot above JP2/JP3.
- **There are no fuses on the board.** Fit the cell fuses FB1/FB2 inline at
  the cell holder as in [guide 03, step 3](03-build-power.md#3-prepare-the-cells).
  The copper between `JCELL1` and M1 is upstream of the module's protection,
  so a bridge there shorts the cells directly. For F2, fit a 1 A inline fuse
  in the S1 lead.
- **Small parts sit under the modules.** R3, R4 and C4 are under M2; R5, R8,
  R9, R10 and Q2 are under M3. With 8.5 mm sockets there is about 6 mm of
  room, so keep these parts seated flat and low.
- **U0 and U3 stay off the board.** Each one connects through its own pair of
  pins: `PV` for U0's 5 V output and `U3 IN` / `U3 OUT` for U3.

![Rev B carrier, bottom view](images/pcb/carrier-bottom.png)

*Bottom view, mirrored as seen from underneath.*

---

## Connections

Pin 1 of every pair is on the left, on the square pad.

| Header     | Pin 1         | Pin 2       | Connects to                        |
|:-----------|:--------------|:------------|:-----------------------------------|
| `JLED1`    | LED +         | –           | Low-power LED string               |
| `JLDR1`    | D7 supply     | A1 sense    | Remote LDR across the two pins     |
| `JBUTTON1` | D2            | –           | Normally-open test button          |
| `JU3IN1`   | `VBAT_SYS`    | –           | U3 input (Tier 2)                  |
| `JU3OUT1`  | U3 3.3 V      | –           | U3 output (Tier 2)                 |
| `JS1`      | M1 OUT+       | `VBAT_SYS`  | S1 service switch                  |
| `JCELL1`   | B+            | B–          | Fused 1S2P cells                   |
| `JPV1`     | Charger 5 V   | Charger –   | U0 output, or an Option A panel    |

| Tier | Fit                                       | JP1             | JP2           | JP3                  |
|:-----|:------------------------------------------|:----------------|:--------------|:---------------------|
| 0    | M1, M2, C3, C4, R3, R4, headers           | Open            | Open          | Open                 |
| 1    | Add M3, Q2, R5, R8, R9, R10               | **Open**        | Open to flash | Closed while powered |
| 2    | Add C2 and U3 wiring; production firmware | Closed, no USB  | Closed        | Closed               |

There is no automatic interlock between USB and battery power. Never close
JP1 while M3 is powered from USB. Remove JP3 whenever M3 is unpowered.

---

## Before you order

1. Print [`fit-sheet-A4.pdf`](../hardware/pcb-rev-b/review/fit-sheet-A4.pdf)
   at **100 %** (scaling off) and check the 50 mm calibration line.
2. Lay the real M2, M3 and M1 on the sheet. Every pin and hole should sit
   on its printed mark, with the D1 Mini's antenna end up and the TP4056's
   USB-C end up.
3. Upload `SolarLights_Carrier_RevB_fabrication_REVIEW.zip` only. The
   options are 2 layers, FR-4, 1.6 mm, 1 oz copper, HASL (lead-free if
   offered), any mask colour, top silkscreen, no assembly.
4. Compare the fabrication service's preview with
   [the top render](images/pcb/carrier-top.png): outline, three mounting holes,
   pad names and the square pin-1 pads.

---

## Parts for the board

The [assembly BOM](../hardware/pcb-rev-b/review/assembly-bom.csv) lists every
reference with its tier. In addition to the values already in
[guide 02](02-parts-and-tools.md):

| Part                                 | Qty | For                      |
|:-------------------------------------|:----|:-------------------------|
| 1 × 12 female socket, 8.5 mm         | 2   | M2 Pro Mini              |
| 1 × 8 female socket, 8.5 mm          | 2   | M3 D1 Mini (Tiers 1, 2)  |
| 1 × 2 male header, 2.54 mm           | 11  | Eight pairs, JP1–JP3     |
| 2 × 3 male header, 2.54 mm           | 1   | `JISP1`                  |
| 2.54 mm shunt                        | 3   | JP1–JP3                  |
| Tinned wire or cut resistor leads    | 6   | M1 links                 |
| M3 standoffs and screws              | 3   | Mounting                 |

---

## Assembly

Solder from the lowest parts to the tallest, so each part is held flat by
the bench while you solder it. Check each joint for a shiny fillet on both
sides of the board.

### 1. Resistors

Fit R3 (47 Ω), R4 (47 k) and, for Tiers 1 and 2, R5 (220 k), R8 (47 k),
R9 (100 k) and R10 (10 k). Seat them flat and trim the leads short:
they sit under the modules. Keep two or three cut leads for M1.

### 2. Small capacitor and transistor

Fit C4 (100 nF). For Tiers 1 and 2, fit Q2 (2N3904) with its flat face
matching the outline and E on the square pad. Push it down until the body
is about 2 mm above the board, so M3 clears it.

### 3. Electrolytic capacitors

Fit C3 (100 µF) and, for Tier 2, C2 (470 µF). The stripe marks the
negative lead; the `+` on the silkscreen marks the positive pad.

### 4. Pin headers

Fit the eight bottom-edge pairs, JP1–JP3 and `JISP1`. Tack one pin, check
the header is square to the board, then solder the rest. For a permanent
outdoor install, you can solder the cell, PV and S1 wires straight into the
pads instead.

### 5. Module sockets

Plug the sockets onto the modules' own pins, set the modules in place, and
tack the corner pins. This keeps the rows parallel at the right spacing.
Remove the modules, then solder every socket pin. Fit the M3 sockets only
for Tiers 1 and 2.

### 6. TP4056 charger M1

1. Replace the PROG resistor for 100–150 mA
   ([guide 03, step 2](03-build-power.md#2-set-the-charge-current)) before
   fitting the module.
2. Meter the module: IN– to OUT– is usually joined, and B– must not be
   joined to OUT–.
3. Push a cut lead through each of the six module holes and its carrier hole.
   Stand the module about 2 mm proud, with USB-C at the top edge.
4. Solder each link on both boards, then trim it.

### 7. Inspect and clean

Inspect every joint with a loupe, especially between the close pins of M1's
bottom row (OUT–, B–, B+, OUT+). Clean off flux. A conformal coating over
the bottom side, away from the sockets and headers, protects the unfused
cell copper from moisture.

---

## Test before the modules go in

With M2 and M3 out and nothing connected, measure with a meter:

- [ ] No short between `VBAT_SYS` (`JS1` pin 2) and any `–` pin.
- [ ] No short between B+ and B– at `JCELL1`.
- [ ] B– (`JCELL1` pin 2) is **not** joined to any `–` pin.
- [ ] `JS1` pin 1 and pin 2 are not joined: S1 open isolates the rail.
- [ ] JP1 and JP3 pins are not joined without their shunts.
- [ ] M2 socket VCC to `VBAT_SYS`, and M2 socket GND to `–`, are continuous.

Then fit M2 (serial-header end up) and program it in circuit through
`JISP1`. Open S1 first. Use 3.3 V signalling, and either set the programmer
to supply no power or keep S1 open while it does
([guide 08](08-firmware.md#wire-the-programmer)).

From here, follow the gates in [commissioning](10-commissioning.md) exactly
as for the wired build: Gate 0 inspection, Gate 1 on a bench supply, and so on.
For Tiers 1 and 2, fit M3 antenna end up, matching the outline.

---

## What can go wrong

| Symptom                                   | Likely cause                                          |
|:------------------------------------------|:------------------------------------------------------|
| Programmer cannot read the signature      | M2 reversed; S1 closed with programmer power; 5 V I/O |
| D1 Mini or U3 damaged                     | M3 turned 180°, or JP1 closed with USB connected      |
| Battery reading wrong or stuck            | JP3 open, or R5 / R9 values swapped                   |
| No telemetry lines                        | Q2 reversed (E must be on the square pad)             |
| Module will not seat                      | Q2, C4 or a resistor standing too tall under it       |
| Cells drain with the switch open          | Bridge between B+ / B– copper; clean and re-inspect   |
| IDC programming cable will not fit        | 2 × 3 IDC plug clashes with M2's socket: use leads    |

---

## Rev A

[`hardware/pcb-rev-a/`](../hardware/pcb-rev-a/) is an earlier 100 × 80 mm
carrier. It has screw terminals and fuse F2 on the board, but M1 and the
cell fuses stay off it. Rev B is the board to build. Rev A remains for reference.
