# _archive - safe to delete

Moved here on 20-Sep-2026 while tidying the project. Nothing in this folder is
part of the current build, and nothing in the live folders links to it. Drag the whole
folder to the Trash whenever you like.

| Item | What it was |
|---|---|
| `SolarLights_Lite_Build.html` | Rev 0.3 build page. The design it shows is superseded; the text record survives in `SolarLights_Lite/SolarLights_Lite_Design.md` |
| `images/` | Rev 0.3 exports: schematic, wiring picture, wiring-view sheet, 5 V panel hookup |
| `tools/` | The generator that drew the pictures in `images/` |
| `Claude outputs/` | Three delivered copies of Rev 0.2/0.3 files, all superseded |
| `kicad-exports/` | PDF, PNG and SVG exports of the two legacy KiCad sheets. Regenerate any time from the sources in `SolarLights_Lite/kicad/` with `kicad-cli sch export pdf` / `svg` |
| `pio-cache/` | PlatformIO build cache |
| `_to_delete/` | Leftover from the earlier overwrite; the zip has already been deleted |

The current build lives in `SolarLights_Lite/docs/`, `SolarLights_Lite/validation/` and
`output/pdf/`. The KiCad sources stay in `SolarLights_Lite/kicad/` as the review's
evidence of the reviewed design.
