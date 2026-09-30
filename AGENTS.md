# Solar Lights Lite

Solar-charged dusk-to-dawn controller for a low-power LED string, with optional
ESPHome telemetry. See `CLAUDE.md` for the hardware gotchas and rules, and
`docs/01-design-overview.md` for the design.

- Controller firmware: `firmware/controller/` (PlatformIO, `atmelavr`, Arduino
  framework, board `pro8MHzatmega328`; environments `standalone`, `production`,
  `advanced`). It uses Arduino plus AVR sleep, watchdog, power and delay
  headers; no external libraries.
- Keep the small C++/Arduino style: fixed-width types, `constexpr` settings in
  `include/config.h`, comments for electrical constraints, and hardware-free
  scheduler logic in `include/schedule.h` so `test_host/regression.cpp` can
  run it.
- ESPHome profiles in `firmware/esphome/` parse the controller's `key=value`
  telemetry line; change the firmware and both profiles together.
- Write human-readable dates as `dd-mmm-yyyy`. Preserve formats emitted by
  tools in generated files.
- Never touch or commit `secrets.h`, `secrets.yaml`, credentials, `.env`
  files, `.pio/`, `.esphome/` or build output. Preserve user changes outside
  the requested scope.
- Never commit or push without explicit instruction.
