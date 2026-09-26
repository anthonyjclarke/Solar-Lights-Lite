# Changelog

All notable project milestones are recorded here. This file is a development
timeline; for an introduction to the project and its current architecture, start
with [README.md](README.md).

## [0.4.0] - 2026-09-27

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

## [0.4] - 2026-09-21

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

## [0.4] - 2026-09-20

### LED measurement and direct-drive revision

- Measured the LED string at a 2.56 V drop with no significant dynamic resistance.
- Chose a reduced-current direct-drive branch: D9 through R3 = 47 ohm, with an
  illustrative current of about 15 mA at 3.7 V.
- Removed Q1, R6, R7, and the LED-branch fuse from the current design because the
  branch is limited by R3 and the controller pin.
- Updated the firmware's normal night setting to 100% command duty; in this design
  duty is brightness control and R3 sets the current limit.

## [0.4] - 2026-09-19

### Engineering review baseline

- Started the Rev 0.4 rebuild review around safer panel input conditioning, reduced
  energy use, direct verification of the controller clock, and staged validation.
- Recorded the original KiCad sheets and legacy firmware/configuration as audit
  evidence rather than a fabrication release.
- Established the core acceptance gates for charger programming, battery protection,
  LED current, controller power, telemetry load, and real-world solar performance.

[0.4.0]: https://github.com/anthonyjclarke/Solar-Lights-Lite/releases/tag/v0.4.0
