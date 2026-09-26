# Solar Lights Lite

**Rev 0.4 proposal, 19 September 2026, amended 27 September. Hardware is not yet validated or released for outdoor assembly.**

This repository captures the reviewed rebuild of a small solar light system: a
1.2 W panel, protected TP4056-family charger, ATmega328P controller, direct-drive
LED string, and optional Wi-Fi telemetry. It is an engineering review and staged
bench-build package, **not** a PCB fabrication release or an outdoor-ready design.

**20 September amendment.** The LED string was measured (2.56 V drop, no significant dynamic resistance), the user chose approximately 15 mA, and at that current the string runs straight from D9 through R3 = 47 ohm with no Q1, R6, R7 or LED-branch fuse. Firmware night duty becomes 100% because duty is now brightness only. This closes H04 and makes H07 not applicable; every other finding stands. See [the measurement](SolarLights_Lite/validation/led-string-measurement.md), the [Q1 disposition](SolarLights_Lite/docs/BOARD_AND_PARTS.md) and the addendum in [VALIDATION.md](SolarLights_Lite/docs/VALIDATION.md).

The current proposal follows your clarified goal: **dim dusk-to-dawn lighting**, reusing the existing 1.2 W panel, a protected TP4056 module and your 16 MHz Pro Mini (converted to 8 MHz using ISP).

## Board and inventory follow-up

Your photographed **BTE13-010A** is the chosen controller. You report successful upload and verification of 6,488 bytes with signature 0x1e950f; programming access is confirmed. The attached working source requests 19200 baud but is readable at 38400: this strongly indicates a 16 MHz runtime with an 8 MHz build. The clock still needs direct verification/correction. **Q2: 2N3904** from your inventory. The inventory contains BJTs, not MOSFETs; Q1 is now removed rather than selected (see the 20 September amendment above). [Board-specific pin map and parts assessment](SolarLights_Lite/docs/BOARD_AND_PARTS.md) includes the S9013 polarity correction and a BC337 alternative discussion.

## Start here

- [Illustrated assembly guide](SolarLights_Lite/docs/ASSEMBLY.html): clear power, controller, telemetry and enclosure drawings.
- [Printable A3 schematic and assembly sheets](output/pdf/SolarLights_Rev04_Drawings.pdf).
- [Build guide and parts list](SolarLights_Lite/docs/BUILD_GUIDE.md): clock conversion, terminal wiring, component selection, energy budget and bench tests.
- [Engineering validation](SolarLights_Lite/docs/VALIDATION.md): findings, primary sources, executed checks and remaining limitations.
- [Wire-by-wire CSV](SolarLights_Lite/docs/wire-schedule.csv) and [external terminal netlist](SolarLights_Lite/docs/reviewed-netlist.json).

![Assembly placement proposal](SolarLights_Lite/docs/sheet-4.png)

## Review result

The old two-diode solar-input protection is not a guaranteed voltage limit. The charger current, LED peak current, MOSFET suitability and D1 Mini supply require qualification. Your 16 MHz Pro Mini needs a real clock conversion; selecting an 8 MHz compiler target is insufficient.

The new drawings show a retained TP4056 charger with a **qualified 5 V input regulator**, a switched LDR, MOSFET LED driver, and optional separately regulated Wi-Fi telemetry. Amber blocks remain unselected pending your available parts. Confirm cell-temperature charging protection before unattended installation.

The current firmware uses **100% command duty from dusk to dawn** because the
measured direct-drive branch is resistor-limited to approximately 15 mA at 3.7 V;
duty now controls brightness rather than providing the original current safety cap.
Low-voltage dimming and cutoff remain active. ESPHome uses an NPN lights-status
interface and omits the unqualified CHRG wire. These firmware changes match Rev 0.4
wiring, not the legacy diagrams.

## Validation evidence

- Both old KiCad sheets freshly export identical 25-net connectivity. They still show the MOSFET driver and remain on hold as evidence, not a release.
- ERC: 1 error + 167 warnings / 1 error + 169 warnings, mainly off-grid endpoints. Not electrically signed off.
- Revised host regression: eight groups pass with address/undefined-behaviour sanitizers.
- Revised ESPHome: schema valid under 2026.9.0 with dummy secrets.
- AVR build was verified through the reviewed ISP path: the Rev 0.4 image (4,250 bytes) was written and verified on the BTE13-010A. PlatformIO's bundled avrdude 6.3.0 remains unsuitable for this programmer setup; system avrdude 8.3 or the documented USBasp method was used. See [validation evidence](SolarLights_Lite/docs/VALIDATION.md) and the [ISP upload guide](SolarLights_Lite/docs/ISP_FIRMWARE_UPLOAD.md).

Logs and original source snapshots are under [validation/](SolarLights_Lite/validation/). No battery, programmer or live Home Assistant connection was used.

## Repository release notes, 27 September 2026

- The repository is intentionally rooted here; `SolarLights_Lite/` holds the active
  design, firmware and validation record.
- The five SVG assembly sheets and printable Rev 0.4 drawing set were regenerated
  on 27 September and identify the build as an unreleased proposal.
- Hidden OS metadata and generated PlatformIO build artefacts are excluded from Git.
- Historical material is retained in `_archive/` and `v1_reference/` for traceability;
  it is clearly labelled and must not be used to assemble the current revision.

## Folder tidy, 20 September 2026

Superseded material moved to `_archive/`: the Rev 0.3 build page and its pictures and
generator, the old delivered copies, the regenerable KiCad exports and the PlatformIO
cache. Nothing current links to any of it, and the folder can be deleted whenever you
like. See [_archive/README.md](_archive/README.md).

## File status

| Location | Status |
|---|---|
| `SolarLights_Lite/docs/` | Current Rev 0.4 review and assembly proposal |
| `output/pdf/` | Current printable vector drawings |
| `SolarLights_Lite/firmware/` | Revised software proposal; requires new wiring and verified 8 MHz hardware |
| `SolarLights_Lite/kicad/` | Legacy Rev 0.3 audit sources; **not a PCB fabrication release** |
| Old `SolarLights_Lite_Design.md`, `SolarLights_Lite_Build.html`, `images/` | Superseded documentation and exports |
| `v1_reference/` | Original source material, preserved |
| `Claude outputs/` | Earlier historical copies, preserved |

To complete hardware selection: identify suitable LED-switch parts, regulator modules, TP4056 chip/PROG resistor and LED string characteristics. The documentation includes a module-carrier PCB path once those parts are proven.

**2N7000 follow-up:** You confirmed this MOSFET separately. It is not selected for the present 200 mA pulse LED driver at battery-level gate drive. See [board/parts assessment](SolarLights_Lite/docs/BOARD_AND_PARTS.md) for the datasheet basis and reduced-current alternative.
