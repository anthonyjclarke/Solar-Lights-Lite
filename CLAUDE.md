# Solar Lights Lite

The active controller is `SolarLights_Lite/firmware/lite_controller`: an
ATmega328P BTE13-010A/Pro Mini target at internal 8 MHz, built with PlatformIO
environments `pro8` and `pro8_debug`. It has no bootloader; routine flashing is
ISP-only (see `PROGRAMMING.md`). Do not port it to the available ATmega32U4 Pro
Micro without redesigning its AVR-specific ADC, interrupt, and timer assumptions.

Current bench snapshot: D9 drives the LED string through 47 ohm; D1/TX feeds the
Q2 UART inverter to D1 Mini D6; D8 is open in v0.5; D2 is the button. The
switched D7/A1 LDR is not yet wired. Panel/charger qualification, complete
wiring, and outdoor validation are incomplete.

Do not commit secrets, credentials, `.env` files, `.pio/`, or editor/build output.
Write human-readable dates as `dd-mmm-yyyy`; retain machine-mandated date formats
inside captured tool output and generated evidence.
Use `SolarLights_Lite/docs/` as the shared source of truth, especially
`ARCHITECTURE.md`, `HARDWARE.md`, and `ROADMAP.md`.
