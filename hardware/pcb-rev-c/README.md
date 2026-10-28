# Solar Lights Lite – PCB carrier Rev C

Started **28-Oct-2026** from Rev B. Status: **current design; CAD checks pass and fabrication files are exported, not yet ordered. Supplier DFM has not been run.**

Rev C started as a copy of the Rev B layout. [Guide 13](../../docs/13-pcb-carrier.md) describes how to
order, build and test it. The [Rev B README](../pcb-rev-b/README.md) still covers anything not changed
below: tiers, modules, TP4056 geometry and the open measurements.

Open `SolarLights_Carrier_RevC.kicad_pro` in **KiCad 10 or later**.

---

## What changed from Rev B

| Change         | Rev C                                         |
|:---------------|:----------------------------------------------|
| R3 LED feed    | 56 Ω (was 47 Ω): model 19.1 mA peak at 4.2 V  |
| LDR trim       | R4 22 kΩ + RV1 50 kΩ 3296W rheostat           |
| Test button    | On-board 6 × 6 mm tactile SW1 (was pads)      |
| ISP header     | Lies sideways below the Pro Mini; box outline |
| ISP option     | DC3-6P shrouded box header, keyed (optional)  |
| Silkscreen     | Name; GitHub repository up right edge         |
| Bottom row     | LED 17.2, LDR 22.3, U3 IN 36.9, U3 OUT 42.9 mm |
| C3, H1         | C3 to (20.0, 39.0); H1 to (3.5, 48.0) mm      |

**LDR trim.** R4 and RV1 form the lower leg of the LDR divider on A1. RV1 is wired as a rheostat
(wiper joined to pin 3), so the leg runs from 22 kΩ to 72 kΩ, and mid-travel gives the 47 kΩ that
`config.h` assumes. More resistance raises A1, so the lights wait for a darker dusk; less makes them
come on earlier. With the firmware's 0.30 dark ratio, the dusk point moves between an LDR of about
51 kΩ and 168 kΩ, with no reflash. Set RV1 to mid-travel (about 25 kΩ, pin 1 to pin 2) before
fitting. Which way of turning the screw adds resistance has not been checked on the part: confirm
with a meter.

**Button.** SW1 is a 4-pin through-hole 6 × 6 mm tactile switch (tall stem, about 9.5 mm) between
the LDR pads and U3 IN, clear of both modules. It replaces the remote-button solder pads.

**ISP.** `JISP1` now uses KiCad's `IDC-Header_2x03_P2.54mm_Vertical` footprint and lies on its side
below the Pro Mini. Pin 1 is at the lower left, odd pins are along the lower row, and the
silkscreen draws the outline of a DC3-6P box header with its key slot facing the bottom edge. The
outline starts about 0.7 mm below the Pro Mini outline. Fit either a plain 2 × 3 male header or,
optionally, the DC3-6P straight box header (2.54 mm, listed in the BOM as `JISP1 (option)`). The
box keys a 6-pin IDC cable so it cannot go on backwards. The box covers the space beside the pins,
so the pin names are a legend underneath it (`1 MISO 2 VCC / 3 SCK 4 MOSI / 5 RST 6 GND`). Check
that the box's key slot lines up with the cable's key before soldering.

---

## Working on Rev C

The board, schematic, footprints and BOM are generated from `tools/design.py` (placement, nets,
labels) and `tools/footprints.py`. Make layout changes there, not in KiCad, then rerun the checks;
`generate.py` overwrites the KiCad files. `tools/validate.py` holds the design rules (B– isolation,
board area, tier population): update it when a change is deliberate.

```
tools/run_checks.sh          # generate, polish, ERC, netlist, DRC with parity, validate
```

When the checks pass, `REPORTLAB_PY=<python with reportlab, pypdfium2> tools/build_outputs.sh` exports
the fabrication files, review PDFs, fit sheet and design zip. The renders go to `review/renders/`; copy
them to `docs/images/pcb/` for guide 13, then rerun `tools/make_guide.py` from the repository root.

Rev B stays unchanged as the record of the ordered board.
