# Solar Lights Lite – PCB carrier Rev B

Prepared **16-Oct-2026**, TP4056 holes and mounting holes revised **27-Oct-2026**. Status: **fabrication review prototype; physical qualification pending.**

A routed **74 × 51.5 mm** two-layer carrier (3,811 mm², 52 % smaller than Rev A's 8,000 mm²),
all through-hole. It keeps the ATmega328P firmware and direct D9 LED drive, and now also carries the
TP4056 charger. Open `SolarLights_Carrier_RevB.kicad_pro` in **KiCad 10 or later** (built with 10.0.6).

---

## What changed from Rev A

| Change                          | Rev B                                                                      |
|:--------------------------------|:---------------------------------------------------------------------------|
| Module silkscreen               | True-size outlines for M2, M3 and M1 with orientation cues and pin names   |
| Connectors                      | Every Phoenix block is now a 2.54 mm solder-point pair                     |
| Fuses                           | **None.** F2 removed, and cell fuses FB1/FB2 are not part of this build    |
| In-circuit programming          | `JISP1` pads labelled `MISO VCC SCK MOSI RST GND`                          |
| 5 V buck U0                     | External only; two `PV IN` pads accept its 5.00 V output                   |
| TP4056 charger M1               | On the board through six overlay holes; cells land on `CELL` pads          |
| Footprint                       | 74 × 51.5 mm; small parts sit under the modules; M3 antenna overhangs      |

**B– is now on the board.** Rev A deliberately had no cell or charger-input copper. In Rev B `PACK_NEG`
(B–) is its own net and never joins `GND_LOAD`; only M1 **OUT–** is the load return, and M1 **IN–** has no
copper link to OUT– (many modules join them internally: meter yours). `validate.py` enforces both.

The wired-build guides in `docs/` (01–12) are unchanged and still describe fused cells and F2. That is
the module-wired build; this carrier is the fuse-free alternative.

---

## Files

| File                                                | Purpose                                              |
|:----------------------------------------------------|:-----------------------------------------------------|
| `SolarLights_Carrier_RevB.kicad_pro` / `_sch` / `_pcb` | Editable project, schematic and routed PCB        |
| `SolarLights_Carrier_RevB_fabrication_REVIEW.zip`   | Gerbers and drills for a quote or DFM review         |
| `SolarLights_Carrier_RevB_design_REVIEW.zip`        | Portable project with libraries, tools, review files |
| `review/pcb-review.pdf`                             | Layout, actual-size fit template, qualification page |
| `review/fit-sheet-A4.pdf`                           | 1:1 A4 sheet: board overlay and module templates     |
| `review/module-check.png`                           | Module dimensions and assumptions, colour-coded      |
| `review/schematic.pdf`, `pcb-top.png`               | Schematic and KiCad render (modules not modelled)    |
| `review/assembly-bom.csv`                           | Parts, tier population, notes                        |
| `review/validation.json`, `drc.json`, `erc.json`    | Recorded checks (physical testing still pending)     |

---

## Solder points and links

Pad 1 is square. Pairs run left to right, pad 1 on the left.

| Ref        | Pad 1                | Pad 2                 | Use                                             |
|:-----------|:---------------------|:----------------------|:------------------------------------------------|
| `JPV1`     | M1 IN+ (charger 5 V) | M1 IN–                | U0 5.00 V output, or an Option A panel (≤ 6.5 V) |
| `JCELL1`   | B+                   | B–                    | 1S2P pack joined in parallel at the holder      |
| `JS1`      | M1 OUT+              | `VBAT_SYS`            | S1 switch, or a 2-pin header and shunt          |
| `JLED1`    | R3 output            | OUT–                  | Low-power LED string                            |
| `JLDR1`    | D7 supply            | A1 sense              | Remote LDR between the two pads                 |
| `JBUTTON1` | D2                   | OUT–                  | Normally-open test button                       |
| `JU3IN1`   | `VBAT_SYS`           | OUT–                  | U3 input (Tier 2)                               |
| `JU3OUT1`  | U3 3.3 V             | OUT–                  | U3 output; measure before closing JP1           |
| `JP1`      | U3 3.3 V             | ESP 3V3               | Fit header and shunt. Open for USB, closed Tier 2 |
| `JP2`      | D0                   | ESP RST               | Header and shunt. Open to flash                 |
| `JP3`      | `VBAT_SYS`           | R5 input              | Header and shunt. Open if M3 absent or unpowered |

| Tier | Population                                         | JP1               | JP2           | JP3                      |
|:-----|:---------------------------------------------------|:------------------|:--------------|:-------------------------|
| 0    | M2, C3, C4, R3, R4, M1, pads                       | Open              | Open          | Open                     |
| 1    | Add M3, Q2, R5, R8, R9, R10; M3 powered by USB     | **Open**          | Open to flash | Closed while M3 powered  |
| 2    | Add U3 wiring and C2; production firmware          | Closed, USB out   | Closed        | Closed                   |

There is no automatic USB/battery interlock. Remove JP3 if M3 is unpowered, to avoid injection through its ADC.

---

## Modules and silkscreen

The F.Silkscreen shows each module's true outline so a reversed module is obvious.

- **M2 Pro Mini** – 18 × 33.3 mm, pin pitch 2.54 mm, pin 1 about 4.0 mm from the serial end. The heavy edge and the word `SERIAL` with an arrow mark the 6-pin serial end.
  Socket pin names are printed beside every hole. Left row top to bottom: TX RX RST GND D2 D3 D4 D5 D6 D7 D8 D9.
  Right row: RAW GND RST VCC A3 A2 A1 A0 D13 D12 D11 D10 (RAW has no trace).
- **M3 D1 Mini** – 25.6 × 34.2 mm. The antenna end **overhangs the top board edge**, so no copper keepout is
  needed; the open outline marks it. The USB end faces the board and the notch is drawn. Left row: RST A0 D0 D5 D6
  D7 D8 3V3. Right row: TX RX D1 D2 D3 D4 G 5V (5V unconnected).
- **M1 TP4056** – 17.2 × 26.73 mm, USB-C end up, flush with the top edge, pad names printed at each hole.

Turning M2 or M3 by 180° puts signals on wrong pins; follow the outline and cue text.

Parts under the modules (fit needs about 6 mm of height with 8.5 mm sockets): M2 – R3, R4, C4. M3 – R5, R8, R9,
R10, Q2. C2 and C3 stay beside the modules. Keep the area under each module's end zones free of tall parts.

---

## In-circuit programming (ISP)

`JISP1` is a 2 × 3 header footprint (fit a pin header), standard AVR order: 1 MISO, 2 VCC, 3 SCK, 4 MOSI,
5 RST, 6 GND. D13/D12/D11 and RST reach only the header and M2.

- **Open S1 first.** VCC is wired to `VBAT_SYS`. S1 sits between M1 OUT+ and `VBAT_SYS`, so with it open a programmer
  that supplies target power cannot back-feed the cells. With S1 closed, set the programmer to **no target power**.
- Use the programmer's **3.3 V** signalling; 5 V into a 3.0–4.2 V target exceeds the AVR's VCC + 0.5 V pin limit.
- Fuse programming still follows the controller guide (`docs/04`, `docs/08`).

---

## TP4056 module M1

Geometry is measured from the module in hand: **17.2 × 26.73 mm, IN holes 14 mm apart, IN/OUT rows 22 mm apart,
IN row 1.5 mm from the USB end, hole 1.2 mm**. The bottom row is **OUT– 3.45 B– 7.45 B+ 3.10 OUT+** (centres, mm),
taken from fit-sheet and ruler photos; the vendor drawing's 2.54 / 8.92 / 2.54 mm does not match this module.
The module's IN– is joined to OUT– internally and B– is not, so the carrier adds no link and keeps B– on its own net.
Mounting: a short wire or cut lead through each module hole and the matching carrier hole, soldered both sides,
module standing ~2 mm proud. Check it first with `review/fit-sheet-A4.pdf` printed at 100 %.

Before soldering M1 in: replace the PROG resistor for 100–150 mA (guide 03 step 2). The module's USB-C is wired to
`IN+`: never plug USB while a panel or U0 is connected. Cell wires go to `JCELL1`; match and pre-balance the cells
first (guide 03 step 3). The DW01A/8205A protects only the OUT side. The `PACK_POS`/`PACK_NEG` copper between `JCELL1` and M1 is
upstream of it and unfused, so a bridge or moisture there shorts the cells directly: inline cell fuses at the
holder and conformal coating close that gap without a board change.

---

## Assumptions and open measurements

| Item                              | Needed                                                       |
|:----------------------------------|:-------------------------------------------------------------|
| TP4056 B– / B+ holes              | Re-measured; confirm they centre on the 27-Oct fit sheet     |
| Pro Mini row spacing, body        | 15.24 mm and 18 × 33 mm assumed; serial-header end clearance |
| Heights under the modules         | About 6 mm free assumed; check with your sockets             |
| LED peak current                  | 47 Ω predicts 21.3 mA at 4.2 V; qualify to ≤ 20 mA or fit 56 Ω |

CAD rules: clearance 0.25 mm; signal tracks 0.30 mm; power tracks 0.80 mm; copper-to-edge 0.50 mm; vias 0.80/0.40 mm.
Three 3.2 mm mounting holes at (3.5, 47.5), (71.3, 48.0), (52.8, 31.5) mm, with no copper within 3 mm of their
centres (room for an M3 head or standoff); JPV1 pad 2 sits 2.9 mm from H2's centre.

Upload **only the fabrication REVIEW ZIP** for a bare-board quote: 2-layer FR-4, 1.6 mm, 1 oz, PTH, ordinary mask,
top silkscreen, no assembly. Supplier DFM has **not** been run. Do not order until the fit checks are done.

---

## Reproduce

```
tools/run_checks.sh          # generate, polish, ERC, netlist, DRC with parity, validate
```

Then `REPORTLAB_PY=<python with reportlab, pypdfium2> tools/build_outputs.sh` exports the fabrication files, renders
the board and builds the review PDF, the 1:1 fit sheet, the module check and the design zip. The router is a
simple grid router; KiCad DRC is the authority. KiCad libraries are CC-BY-SA-4.0 with the library exception
(see `Carrier.pretty/LICENSE.md`).
