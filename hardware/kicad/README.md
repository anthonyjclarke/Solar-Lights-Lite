# KiCad schematic

`SolarLights_Lite.kicad_sch` is the complete Solar Lights Lite circuit on one A3
sheet, drawn as six functional blocks:

1. Solar input, charger and cells
2. Battery rail (fuse and service switch)
3. LED output (direct PWM drive through R3)
4. Controller (Pro Mini)
5. Telemetry (Wemos D1 Mini and the Q2 serial receiver)
6. Telemetry 3.3 V supply (U3)

Blocks connect by net label: `VBAT`, `3V3_TEL`, `PWM`, `UART_TX`, `BTN`,
`LDR_PWR`, `LDR_SENSE`, `BATT_BUS`, `BATT-` and `D1_D6`. U0 is drawn for
Option B panels; with an Option A panel, wire PV1 straight to M1 IN. U3 OUT is
shown connected to the D1 Mini 3V3 pin, which is the Tier 2 arrangement; in
Tier 1 that link is open and the D1 Mini runs from USB.

This is a wiring schematic for module-level assembly on perfboard. It has no
footprints or layout and is not a fabrication package.

---

## Files

| File                           | Contents                                     |
| :----------------------------- | :------------------------------------------- |
| `SolarLights_Lite.kicad_sch`   | Editable schematic (KiCad 7 format or later) |
| `SolarLights_Lite.pdf`         | A3 PDF export; no KiCad needed               |
| `SolarLights_Lite_preview.png` | Raster preview                               |
| `SolarLights_Lite.kicad_sym`   | Custom module symbols                        |
| `tools/gen_lite_sch.py`        | Generator for the schematic                  |
| `tools/lite_parts.json`        | Part and net data emitted by the generator   |

---

## Checks and exports

With KiCad installed, `kicad-cli` (in the KiCad application folder, or on
`PATH` on Linux) exports and checks the sheet:

```bash
kicad-cli sch export pdf -o SolarLights_Lite.pdf SolarLights_Lite.kicad_sch
kicad-cli sch erc SolarLights_Lite.kicad_sch
```

ERC currently reports four items, none of them wiring faults: GND has no
`PWR_FLAG`; the `Q_NPN_BCE` symbol is not in KiCad 10's `Device` library; and
two `Battery_Cell` symbols differ from KiCad 10's library copies.

## Regenerating

The generator reads KiCad 7-format stock symbols (it uses `Q_NPN_BCE`, which
KiCad 10 no longer ships). Point `KICAD_LIBS` at a KiCad 7 symbol library
folder containing `Connector_Generic`, `Device`, `Switch` and `power`:

```bash
KICAD_LIBS=/path/to/kicad7-symbols python3 tools/gen_lite_sch.py
```

Then re-export the PDF and preview, and compare netlists before and after to
confirm connectivity.
