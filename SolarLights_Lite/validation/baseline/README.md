# SolarLights 2026 – Lite

Parts-bin build of the Solar Front Lights redesign.
Folder: `~/PlatformIO/Projects/SolarLights_2026_Lite` · sibling: `../SolarLights_2026_v2`
Last updated 19 Sep 2026.

---

## Layout

| Path                                          | Content                                                   |
|-----------------------------------------------|-----------------------------------------------------------|
| `SolarLights_Lite/SolarLights_Lite_Design.md` | Design, staged panel plan, bench + field tests            |
| `SolarLights_Lite/SolarLights_Lite_Build.html`| Schematic, wiring diagram, pin maps, build order          |
| `SolarLights_Lite/kicad/`                     | Two KiCad sheets, symbols, netlists, generator scripts    |
| `SolarLights_Lite/images/`                    | Schematic PDF/PNG, wiring picture SVG/PNG, wiring sheet   |
| `SolarLights_Lite/firmware/lite_controller/`  | Pro Mini PlatformIO project (`PANEL_STAGE`, host test)    |
| `SolarLights_Lite/firmware/esphome/`          | D1 Mini ESPHome config                                    |
| `v1_reference/`                               | Original v1 schematic, YAML and photos                    |
| `Claude outputs/`                             | Older delivered copies – superseded, safe to delete       |

Two sheets of the same circuit, both verified 25/25 nets:

| Sheet                             | Use                                                     |
|-----------------------------------|---------------------------------------------------------|
| `SolarLights_Lite.kicad_sch`      | Engineering view – energy flows left to right           |
| `SolarLights_Lite_Wiring.kicad_sch`| Wiring view – module layout, OUT+/OUT− rails as buses  |

---

## Status

| Item          | State                                                             |
|---------------|-------------------------------------------------------------------|
| Design        | Rev 0.2 – Stage 1 on the existing 1.2 W panel, Stage 2 panel swap |
| Schematic     | Rev 0.3 / 0.3w – both sheets verified 25/25 nets                  |
| Pro Mini fw   | Compiles (~7.2 kB); host-simulated; not yet on hardware           |
| ESPHome       | Validates; not yet flashed                                        |
| Build         | Not started                                                        |

---

## Open items

- Build Stage 1 and run bench tests B1–B8.
- Field tests F1–F3 (Oct–Nov), then decide on the Waveshare 6 V 5 W panel (SKU 16158).
- Measure the LED string and set `R3` (Rlim) plus the current cap in the firmware.
- Decide whether to keep the LDR (fitted DNP) or run on the panel-voltage sense alone.

Note, 20 September 2026: `SolarLights_Lite/SolarLights_Lite_Build.html` and
`SolarLights_Lite/images/` listed above were moved to `_archive/` during a folder tidy.
They were superseded documentation, not evidence; the firmware and YAML snapshots in this
directory are untouched.

