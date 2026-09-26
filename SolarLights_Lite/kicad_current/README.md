# Current-build schematic - Rev 0.4b, 21 September 2026

This is the schematic for the circuit as it stands today: the Rev 0.4 review
plus the 20 September direct-drive change. It is a **new, separate project**
from `../kicad/` on purpose - that folder holds the original Rev 0.3 circuit,
frozen as an audit baseline (see `../kicad/README.md` and `../docs/VALIDATION.md`
finding H16, "keep legacy KiCad on hold"). Nothing there was touched or
overwritten to produce this.

## What changed vs. the Rev 0.3 baseline

- **U0**, a 5 V input regulator, replaces the old two-diode panel-voltage-limiting
  scheme. Still not selected - see `BUILD_GUIDE.md`. **Not** the TPS63802/HL802A
  breakout below; its 5.5 V input ceiling is under the panel's 7.6 V Voc.
- **FB1 / FB2** give each cell its own fuse off the shared charger B+ node
  (1S2P), instead of one fuse downstream of both cells.
- **S1** is a new service switch in series with the main fuse F2.
- **Q1, R6, R7, F1 are not fitted.** D9 drives R3 (47R) directly into the LED
  string - see `../validation/led-string-measurement.md` and the "Q1
  disposition" note in `BOARD_AND_PARTS.md`.
- The **D8 status interface** is now Q2 (2N3904) + R8/R9/R10, an NPN inverter,
  not the old two-resistor divider.
- **U3**, a low-Iq 3.3 V supply, now feeds the D1 Mini and the R10 pull-up
  directly, instead of running the D1 Mini off raw VBAT. Candidate as of
  21 Sep 2026: the TPS63802/HL802A breakout (on hand, qty 2), jumper set to
  3.3 V - not yet bench-qualified. See `../docs/BOARD_AND_PARTS.md`.
- The old panel-sense divider (R1/R2/C1) and A0 wiring, the D10/D11 mode
  jumpers (JP1/JP2), and the CHRG-to-D1-Mini diode (D3) are gone - none of
  them are used in the current firmware or build guide.
- The switched LDR (LDR1/R4) is now fitted by default, not the optional/DNP
  part it was in Rev 0.3.

Every part and net here was checked against `../docs/BUILD_GUIDE.md`'s
"Parts and selection gates" table and against a `kicad-cli sch export netlist`
pass (no accidental shorts, and only the intentionally-unused pins - M1.CHRG,
M2.A0/D10/D11, M3.D6 - show up unconnected).

## Files

- `SolarLights_Lite_Current.kicad_sch` - open this in KiCad 7.
- `SolarLights_Lite_Current.pdf` - A3 PDF export, no KiCad needed to view it.
- `current_preview.png` - quick raster preview.
- `tools/gen_lite_sch_current.py` - regenerates the `.kicad_sch` from scratch
  (same pattern as `../kicad/tools/gen_lite_sch.py`). Needs KiCad's symbol
  libraries (`KICAD_LIBS`, default `/usr/share/kicad/symbols`) and KiCad 7's
  `kicad-cli` for exports.
- `tools/lite_parts_current.json` - the part/net table the script emits, for
  diffing against a future revision.

## Still first-pass

This was built in one sitting and passed a netlist check, but it has **not**
been through ERC (KiCad 7's `kicad-cli` doesn't have an `erc` subcommand -
that arrived in KiCad 8) and no footprints have been assigned beyond what
Rev 0.3 already had. Treat it as a correct connectivity reference, not a
release package - the same caveat `../docs/VALIDATION.md` applies to
everything else in this review.
