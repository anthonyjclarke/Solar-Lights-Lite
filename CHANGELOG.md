# Changelog

Notable changes to Solar Lights Lite. For an introduction to the project, start
with [README.md](README.md).

---

## [Unreleased]

### Added

- `tools/make_layouts.py`: breadboard and perfboard layout drawings of the
  whole system (`docs/drawings/breadboard-layout.*`, `perfboard-layout.*`),
  placed to keep hookup wire to a minimum. Both layouts are checked against
  `docs/netlist.json` when generated; perfboard traces are routed on the
  0.1 in grid.
- Both layouts linked from guides 04 and 07 and shown in `docs/ASSEMBLY.html`
  (breadboard under Module B, perfboard under Module E).

- Guide 04 explains why the controller runs at 8 MHz: the ATmega328P speed
  versus voltage limit, why brown-out protection cannot cover 16 MHz, IDLE
  current, and the choice of internal oscillator over crystal. It also states
  that the widely sold 5 V/16 MHz Pro Mini is a suitable board. Guide 01 links
  to it.
- Guide 08 explains why the controller is flashed over ISP rather than through
  a USB-serial (FTDI) adapter and bootloader. Fuses need ISP, the factory
  16 MHz bootloader fails at 8 MHz, and ISP avoids a start-up delay, DTR
  wiring and back-feeding the battery. Guide 04 links to it.

- Controller reset banner (`advanced` and `production` builds): firmware
  version, build date and time, telemetry profile and clock setting.

- ATmega328PB support documented after a bench dry run on a new board. That
  board read signature `1E 95 16`, and the firmware ran unchanged. Guides 08
  and 04, the USBasp sheet and the controller bench sheet now accept either
  signature, use `-p m328pb` for the 328PB, and warn against `-F`.
- Guide 08 lists typical factory fuses for a 16 MHz Pro Mini (`0xFF`/`0xDA`/
  `0xFD`) and a troubleshooting row for `vdd=` reading about 5 V (supply
  set to 5 V). It also covers powering the bare controller from a USB-UART
  adapter's 3.3 V VCC pin for a quick check after flashing.
- Guide 04 has a new "Powering the board" section covering VCC, RAW and the
  serial header, with a table of the power source at each stage. Its build
  steps are reordered: headers, then fuses and flash, then a new first
  power-up check (3.3 V adapter into the header VCC; banner and `vdd` against
  a meter), then the regulator and power LED rework (checked again
  afterwards), then decoupling. The rework is now consistently required
  before Gate 0 and Gate 1. Guides 08 and 10, the controller bench sheet and
  the board map (serial-header pins, header VCC on the same rail) match.

- `docs/reference/ProMini-328PB-front.jpeg`: photo of the second tested
  board, a blue ATmega328PB Pro Mini clone. Guide 04 describes it and adds
  a test to tell its two LEDs apart (the power LED is the one that stays lit
  while the firmware runs). On this board the power LED is the red one beside
  the regulator, drawing about 1.8 mA (about 43 mAh a day). Guide 04 also
  estimates the power LED's daily drain in general.

### Changed

- Advanced ESPHome profile: "Arduino Diagnostics Fresh" now allows 180 s
  without a report, up from 90 s. An overnight v0.6 run lost 6 of 897 lines,
  each leaving a gap of about 140 s, and every lost line briefly showed the
  link as down. One lost line is now tolerated; two in a row still show it.
- Watchdog drift documented as chip-dependent, typically 10–20 % slow (12 %
  and 16 % measured), in `config.h` and guides 01 and 10.
- Gate 3 adds a lit-LDR check: with the lights on at night the LDR may rise
  only a few percent and must stay well below the light threshold. Guide 06
  adds the same check, and Gate 3 notes that an indoor bench sees room
  lights.
- Advanced ESPHome profile: the battery ADC takes 4 samples per 10 s read
  and averages the last six readings (one minute), replacing 16 samples per
  read. The 16-sample read blocked the ESPHome loop for about 66 ms and
  triggered "took a long time" warnings. The production profile is unchanged:
  it reads once per hourly wake, so a moving average would not survive deep
  sleep.
- The `advanced` build's reset output is reorganised: banner, active settings,
  then an aligned field guide, ending with `Live diagnostics`. No reset line
  starts with `fw=`, so the ESPHome profiles are unaffected.
- `tools/make_guide.py` shows a figure's "Printable PDF" link only when that
  PDF exists.
- `tools/make_guide.py` now also prefixes links to a heading in the same guide,
  so they work in `docs/ASSEMBLY.html`.

---

## [0.6.0] 30-09-2026

A restructure from a development record into a build-and-operate package. The
circuit is unchanged; the controller firmware and both D1 Mini profiles change
behaviour and must be reflashed together.

### Added

- Numbered documentation set in `docs/`: design overview, parts/tools/safety,
  one build guide per module (A–E), firmware, Home Assistant, commissioning
  gates 0–8 with final assembly (module F), operation and maintenance, and
  going further.
- Controller one-time fuse procedure for a new board (low `0xE2`, high `0xD9`,
  extended `0xFD`).
- `firmware/controller/include/config.h` holding every tuneable value,
  including a firmware version reported as `fw=` in every telemetry line.
- Three controller build environments, one per telemetry tier:
  `standalone`, `production` and `advanced`.
- `production` build: a compact status line every 8 scheduler seconds, with
  the serial port powered only while sending and TX held low in between.
- Tier 2 production telemetry reads that line during each hourly wake, using
  the same Q2 harness as Tier 1; no rewiring between tiers.
- `homeassistant/solar_lights_package.yaml`: OTA helper plus battery-low,
  cut-off and reports-stopped automations.
- `homeassistant/dashboard-production-telemetry.yaml`.
- `LICENSE`: the whole project is dedicated to the public domain under
  CC0 1.0.
- Host test for the fast-tick rule; UART parsing checked against sample lines.

### Changed

- Repository flattened: `docs/`, `firmware/`, `hardware/kicad/`,
  `homeassistant/` and `tools/` at the root.
- Scheduler simplified to dusk-to-dawn only: states are `DAY`, `NIGHT` and
  `LVC`; the output cause `ALL_NIGHT` is now `DUSK_TO_DAWN`.
- Controller: unused analog inputs A0–A5 have their digital buffers disabled;
  RX has its pull-up enabled; D8 is no longer driven.
- ESPHome: both profiles use device name `solar-lights` with identical entity
  names, an OTA password (`ota_password` secret), a new `Arduino Firmware`
  sensor, and only accept lines that start with `fw=`.
- Drawings regenerated with module and tier titles; sheet 3 now shows Tier 2
  on the shared serial harness. Files renamed under `docs/drawings/`.
- KiCad project renamed to `hardware/kicad/SolarLights_Lite.*`; title block,
  notes and the D1 Mini supply pin (now `3V3`, previously labelled `5V`)
  corrected. Connectivity is unchanged.
- Parts list, wire schedule and netlist regenerated with module and tier notes.
- `docs/ASSEMBLY.html` is now generated from guides 01–12 by
  `tools/make_guide.py`: one visual page with every drawing inline beside its
  module, plus the wire schedule and parts checklist.

### Removed

- Superseded designs, review reports, dated addenda, legacy KiCad baseline,
  archived exports, original v1 files and machine-specific tool captures.
  All remain available at tag `v0.5.5-history`.
- Unused firmware paths: panel-voltage sensing, mode jumpers and the
  evening/pre-dawn schedule.

### Upgrading an existing 0.5 installation

No wiring changes are needed and the lighting behaviour is unchanged. Upgrade
the controller first, then the D1 Mini, so telemetry is never interrupted.

1. **Back up.** Read the controller's current firmware
   (`avrdude -c usbasp -p m328p -U flash:r:solarlights-v0.5-backup.hex:i`),
   copy the D1 Mini's YAML out of ESPHome, and export the dashboard's raw
   configuration.
2. **Controller.** Build in `firmware/controller` (the old `pro8_debug` is now
   `advanced`; the old silent `pro8` is now `standalone`) and flash
   `.pio/build/advanced/firmware.hex` over ISP. Do not write fuses: an already
   converted board keeps its settings. The 0.5 D1 Mini profile still reads the
   new lines; `mode` now reports `DAY`/`NIGHT`/`LVC` and the night cause is
   `DUSK_TO_DAWN`, so update any automation that tests the old values.
3. **D1 Mini.** Install `solar-lights-advanced-telemetry.yaml` with
   `name: telemetry` and `friendly: Telemetry` in its substitutions, so the
   device keeps its network name and Home Assistant keeps its existing
   `*.telemetry_*` entity IDs. Keep the same `esphome_encryption_key`, and add
   an `ota_password` secret (the first wireless install still works because
   the running firmware has no password yet). Renaming an existing device to
   `solar-lights` is not recommended: the first wireless install would look
   for `solar-lights.local`, and Home Assistant would keep the old entity IDs
   while creating new ones, leaving a mix.
4. **Home Assistant.** The existing dashboard keeps working. To use the new
   dashboards or package, replace `solar_lights_` with `telemetry_` in them
   first (but keep `input_boolean.solar_lights_ota` as it is). If that helper
   already exists under Settings → Helpers, remove the `input_boolean:` block
   from the package.
5. **Rollback** at any point: reflash `solarlights-v0.5-backup.hex` and
   reinstall the saved YAML. The complete 0.5 source is at tag
   `v0.5.5-history`.

---

## Pre-release history (0.2 – 0.5.5)

Development between 17-Sep-2026 and 30-Sep-2026 took the design from a
parts-bin concept to the built v0.5 circuit: an engineering review of the
original design, conversion of the BTE13-010A to internal 8 MHz with ISP-only
programming, measurement of the LED string and removal of the MOSFET driver in
favour of direct pin drive through a 47 Ω resistor, a switched LDR (R4 changed
from 100 kΩ to 47 kΩ for dark margin), the TPS63802 telemetry supply, and the
always-on D1 Mini serial telemetry with its Home Assistant dashboard. The full
record – review findings, dated measurements, superseded drawings and the
original design – is preserved at tag `v0.5.5-history`.

[0.6.0]: https://github.com/anthonyjclarke/Solar-Lights-Lite/compare/v0.5.5-history...v0.6.0
