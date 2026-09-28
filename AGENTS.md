# Solar Lights Lite

Solar-charged garden-light controller. The active firmware targets the
ATmega328P BTE13-010A/Pro Mini path at internal 8 MHz.

- PlatformIO: `atmelavr`, Arduino, `pro8` and `pro8_debug`; firmware lives in
  `SolarLights_Lite/firmware/lite_controller/`. It uses Arduino plus AVR sleep,
  watchdog, power, and delay headers; no external PlatformIO libraries are set.
- Keep the existing small C++/Arduino style: fixed-width types, named pin and
  threshold constants, comments for electrical constraints, and hardware-free
  scheduler logic in `include/schedule.h` for host tests.
- Write human-readable dates as `dd-mmm-yyyy` (for example, `27-Sep-2026`).
  Preserve formats emitted by tools in captured or generated evidence, such as
  ERC timestamps and exported netlists.
- Never touch or commit `secrets.h`, credentials, `.env` files, `.pio/`, or
  editor/build output. Preserve user changes outside the requested scope.
- Never commit or push without explicit instruction.

Use [architecture](SolarLights_Lite/docs/ARCHITECTURE.md),
[hardware](SolarLights_Lite/docs/HARDWARE.md), and
[design decisions](SolarLights_Lite/docs/DESIGN_DECISIONS.md) for project context.
