# Changelog

All notable project milestones are recorded here. This file is a development
timeline; for an introduction to the project and its current architecture, start
with [README.md](README.md).

## [0.5.0] - 27-Sep-2026

### Development telemetry

- Reworked telemetry around the existing Wemos D1 Mini; no INA226, temperature
  probe, ESP32-C3 or other new telemetry module is required.
- Added an always-on D1 Mini ESPHome profile that captures the Arduino's
  rate-limited 9600-baud diagnostic lines and publishes parsed controller state
  to Home Assistant.
- Reused Q2/R8/R9/R10 as the protected, inverted UART receiver on D6. The
  parsed `output=` value replaces the separate D8-to-D5 light-status wire while
  developing.
- Added a sixth illustrated assembly sheet for the test-only D1 telemetry
  topology; retained the original D1 Mini deep-sleep configuration as the
  production reference.

### Documentation

- Promoted active documentation, visual assembly assets and current firmware
  labels to v0.5.
- Documented the no-purchase measurement boundary: controller diagnostics,
  battery voltage and D1 health are visible; panel voltage, current, energy and
  temperature still need instruments or added hardware.

## [0.4.0] - 27-Sep-2026

### Repository release

- Created the public Git repository and the `v0.4.0` annotated release tag.
- Added repository hygiene for macOS metadata, PlatformIO caches, local secrets,
  and common development artefacts.
- Regenerated the five current Rev 0.4 visual assembly sheets and printable drawing set.
- Consolidated the current direct-drive design status in the root documentation.

### Documentation

- Reworked the README as a newcomer-oriented project overview.
- Moved dated project history into this changelog.
- Added a project hero illustration and a system-architecture diagram.

## [0.4] - 21-Sep-2026

### Controller and programming

- Confirmed the BTE13-010A target as an ATmega328P and configured it for internal
  8 MHz operation with 2.7 V brownout detection and no bootloader.
- Wrote and verified the reviewed firmware image through ISP.
- Documented the reliable system-avrdude and USBasp upload paths after PlatformIO's
  bundled avrdude showed repeatable verification failures with the ArduinoISP setup.
- Identified a second board as an ATmega32U4 Pro Micro rather than a drop-in spare
  for the ATmega328P controller.

### Hardware direction

- Selected the MP1584EN as a candidate solar-input regulator pending bench qualification.
- Selected the TPS63802/HL802A breakout as the optional telemetry-supply candidate,
  also pending bench qualification.
- Created the separate `kicad_current` project to reflect the current direct-drive
  circuit while preserving the older KiCad design as an audit baseline.

## [0.4] - 20-Sep-2026

### LED measurement and direct-drive revision

- Measured the LED string at a 2.56 V drop with no significant dynamic resistance.
- Chose a reduced-current direct-drive branch: D9 through R3 = 47 ohm, with an
  illustrative current of about 15 mA at 3.7 V.
- Removed Q1, R6, R7, and the LED-branch fuse from the current design because the
  branch is limited by R3 and the controller pin.
- Updated the firmware's normal night setting to 100% command duty; in this design
  duty is brightness control and R3 sets the current limit.

## [0.4] - 19-Sep-2026

### Engineering review baseline

- Started the Rev 0.4 rebuild review around safer panel input conditioning, reduced
  energy use, direct verification of the controller clock, and staged validation.
- Recorded the original KiCad sheets and legacy firmware/configuration as audit
  evidence rather than a fabrication release.
- Established the core acceptance gates for charger programming, battery protection,
  LED current, controller power, telemetry load, and real-world solar performance.

[0.4.0]: https://github.com/anthonyjclarke/Solar-Lights-Lite/releases/tag/v0.4.0
