# Hardware

The supported controller is the BTE13-010A ATmega328P Pro Mini path, confirmed at
internal 8 MHz with 2.7 V brown-out detection and no bootloader. It is powered
from the protected battery rail at VCC; RAW is left disconnected. Routine firmware
updates use ISP, while UART is for diagnostics only.

| Signal | Current wiring intent |
| --- | --- |
| D9 | 47 ohm series resistor to LED string positive; string return to load ground |
| D8 | Production-reference status input only; leave open for the v0.5 D1 UART test profile |
| D1 / TX | v0.5 test profile: 47 kΩ resistor to Q2 base; Q2 collector drives D1 Mini D6 as inverted UART |
| D7 / A1 | Switched LDR supply and LDR divider midpoint |
| D2 | Button to ground, using the internal pull-up |
| D10 / D11 | Reserved and left open |

Bench snapshot: the LDR is **not yet wired**. Panel sense and charger-status inputs
are disconnected in the current revision. The LED string has been measured with a
47 ohm resistor, but installed-cable and temperature behaviour remain unmeasured.
The retained panel/charger path has not been fully qualified; do not treat the
charger module, charge current, or outdoor wiring as verified.

For development, use `firmware/esphome/solar-lights-lite-dev-d1.yaml` with
`pro8_debug`; this is always-on test telemetry, not the final low-power profile.
See `BOARD_AND_PARTS.md` and `BUILD_GUIDE.md` for retained reference detail.
