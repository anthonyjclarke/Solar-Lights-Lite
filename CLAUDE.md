# Solar Lights Lite

The active controller is `SolarLights_Lite/firmware/lite_controller`: an
ATmega328P BTE13-010A/Pro Mini target at internal 8 MHz, built with PlatformIO
environments `pro8` and `pro8_debug`. It has no bootloader; routine flashing is
ISP-only (see `PROGRAMMING.md`). Do not port it to the available ATmega32U4 Pro
Micro without redesigning its AVR-specific ADC, interrupt, and timer assumptions.

As built (30-Sep-2026): the whole v0.5 circuit is wired per the drawings
(`docs/sheet-1.png`..`sheet-7.png`). D9 drives the LED string through 47 ohm;
D7 -> LDR -> A1 -> R4 47k -> OUT- is the dusk/dawn sensor (R4 was 100k until
30-Sep-2026: too little dark margin at 30%); D1/TX feeds the Q2 UART
inverter to D1 Mini D6; D8 is open in v0.5; D2 is the button. Bench power: U0 is
not fitted (open item until the production panel is chosen) and a 5 V panel feeds
M1 IN directly; U3 is a TPS63802 breakout at 3.3 V with VIN on VBAT_SYS. The always-on bench D1
Mini runs from its own micro-USB, so U3 OUT must be off its 3V3 pin (never both);
production D1 runs from U3 only. The WDT scheduler clock runs ~12% slow vs real
time (measured 30-Sep-2026); do not rely on `time=` for wall-clock durations. Panel/charger qualification, LDR threshold calibration,
and outdoor validation are incomplete.

Do not commit secrets, credentials, `.env` files, `.pio/`, or editor/build output.
Write human-readable dates as `dd-mmm-yyyy`; retain machine-mandated date formats
inside captured tool output and generated evidence.
Use `SolarLights_Lite/docs/` as the shared source of truth, especially
`ARCHITECTURE.md`, `HARDWARE.md`, and `ROADMAP.md`.
