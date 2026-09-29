# Current-build schematic – v0.5 reference, 28-09-2026

This is the schematic for the direct-drive core circuit retained by the v0.5
review, including the 20-09-2026 direct-drive change. It is a **new, separate
project** from `../kicad/` on purpose – that folder holds the original Rev 0.3
circuit, frozen as an audit baseline. Nothing there was touched or overwritten
to produce this project.

## Layout and connectivity

The current sheet is arranged as six dashed, numbered functional blocks:

1. Solar input, charger and cells
2. Battery rail
3. LED output
4. Controller – Pro Mini
5. Telemetry – D1 Mini
6. Telemetry 3.3 V supply

The short italic caption in each block records its role. Inter-block connections
use net labels instead of sheet-long wires: `VBAT`, `3V3_TEL`, `PWM`, `UART_TX`,
`BTN`, `LDR_PWR`, `LDR_SENSE`, `BATT_BUS`, `BATT-`, and `D1_D6`. The layout
uses a 2.54 mm grid and the generator rejects diagonal wires, eliminating the
previous off-grid endpoint warnings. This is a legibility rework only; circuit
connectivity is unchanged except for the intentional D8 no-connect below.

The Pro Mini now visibly includes an open `D8` pin. The earlier committed symbol
omitted that pin even though the firmware and documentation already specified
that `D8` was open. Its intentional single-pin net is
`unconnected-(M2-D8_open-PadD8)`.

## What changed vs. the Rev 0.3 baseline

- **U0**, a 5 V input regulator, replaces the old two-diode panel-voltage-limiting
  scheme. It is an open item and not fitted: the bench uses a 5 V panel straight into M1
  until the production panel is chosen – see `../docs/BUILD_GUIDE.md`. It is **not**
  the TPS63802/HL802A breakout below; its 5.5 V input ceiling is under the
  panel's 7.6 V Voc.
- **FB1 / FB2** give each cell its own fuse off the shared charger B+ node
  (1S2P), instead of one fuse downstream of both cells.
- **S1** is a service switch in series with the main fuse F2.
- **Q1, R6, R7 and F1 are not fitted.** D9 drives R3 (47R) directly into the
  LED string – see `../validation/led-string-measurement.md` and the Q1
  disposition note in `../docs/BOARD_AND_PARTS.md`.
- Q2 (2N3904) + R8/R9/R10 is the protected v0.5 receive-only UART interface:
  Arduino D1/TX feeds D1 Mini D6 through the inverted level shifter. D8 and D5
  are open in this development configuration; see `../docs/BUILD_GUIDE.md`.
- **U3**, a low-Iq 3.3 V supply, feeds the D1 Mini and the R10 pull-up directly,
  instead of running the D1 Mini from raw `VBAT`. The TPS63802/HL802A breakout
  is fitted, set to 3.3 V, with VIN on `VBAT`. The schematic shows the production
  connection. On the bench the always-on D1 Mini runs from its micro-USB and U3 OUT
  is disconnected from `3V3_TEL`, so U3 is not yet qualified as the D1's supply.
- The old panel-sense divider (R1/R2/C1) and A0 wiring, the D10/D11 mode
  jumpers (JP1/JP2), and the CHRG-to-D1-Mini diode (D3) are absent because they
  are not used in the current firmware or build guide.
- The switched LDR (LDR1/R4) is fitted by default, not optional/DNP as it was
  in Rev 0.3.

## Verification

On 28-09-2026, KiCad 10.0.6 exported netlists from `HEAD` and this working
sheet. Comparing each net's sorted reference/pin set while ignoring net names
found 26 identical sets. The only additional set is the intended `M2.D8`
single-pin no-connect. No connected net changed.

KiCad 10.0.6 also supports `kicad-cli sch erc`. The current ERC result is four
non-layout violations:

- one `power_pin_not_driven` error for GND, because no `PWR_FLAG` is fitted;
- one `lib_symbol_issues` warning because KiCad 10's `Device` library no longer
  contains `Q_NPN_BCE`; and
- two `lib_symbol_mismatch` warnings because the embedded `Battery_Cell`
  symbols differ from KiCad 10's library copies.

There are no off-grid endpoint violations. These ERC findings are retained
engineering follow-ups, not evidence that the layout rework changed a circuit.

## Files

- `SolarLights_Lite_Current.kicad_sch` – editable KiCad v0.5 sheet.
- `SolarLights_Lite_Current.pdf` – A3 PDF export; no KiCad installation needed
  to view it.
- `current_preview.png` – quick raster preview.
- `tools/gen_lite_sch_current.py` – regenerates the schematic and the project
  support files.
- `tools/lite_parts_current.json` – emitted part/net data for future diffs.

## Regenerating with KiCad 10

KiCad 10.0.6 can open the current sheet and provide netlist, PDF and ERC
exports. The generator itself deliberately parses the older KiCad 7 stock symbol
format, however; it expects `Q_NPN_BCE`, which KiCad 10's `Device` library no
longer supplies. Do not point `KICAD_LIBS` at KiCad 10's stock-symbol directory.

For a repeatable regeneration today, provide a KiCad 7-format snapshot of the
required stock libraries and point `KICAD_LIBS` at that directory before running
the generator:

```sh
KICAD_LIBS=/path/to/kicad7-symbol-snapshot \
  python3 tools/gen_lite_sch_current.py
```

The snapshot needs the stock symbols referenced by the generator, including
`Connector_Generic`, `Device`, `Switch` and `power`. A practical robust follow-up
is to extract and normalise the embedded stock-symbol copies from the committed
`.kicad_sch` into a version-controlled KiCad 7-format snapshot, then have the
generator load that snapshot. That change is intentionally not implemented here.

After generation, use KiCad 10's CLI for checks and exports, for example:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch erc \
  SolarLights_Lite_Current.kicad_sch
```

## Still first-pass

The current sheet has a netlist comparison and an ERC record, but it is not a
fabrication or outdoor-release package. Resolve the power-flag and library
follow-ups, assign and verify footprints, and complete the hardware validation
gates in `../docs/VALIDATION.md` before treating it as build-ready.
