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

As built (30-Sep-2026): the whole v0.5 circuit, including the switched LDR
(D7 -> LDR -> A1 -> R4 47k -> OUT-), is wired per sheets 1–7. Panel sense and
charger-status inputs are disconnected by design in this revision. The LDR
dusk/dawn thresholds are not yet calibrated for its final position.

R4 was changed from 100k to 47k on 30-Sep-2026 without reprogramming. The
firmware's fixed A1-ratio thresholds (dark < 0.30, light > 0.60) therefore now
correspond to an LDR above about 110k for dark and below about 31k for light;
with 100k they were about 233k and 67k. At 100k the dark room overnight read
about 50% (LDR ~100k) and dusk never confirmed. Bench readings with 47k: fully
covered 9.1% (raw 93, LDR ~470k), 92% in room daylight. A loose cap gave only
~19%, so test darkness with a light-tight cover. Dusk and dawn both confirmed.

The watchdog "seconds" run about 12% slow against real time (measured
30-Sep-2026 at both the 1 s and 8 s ticks). The 300 s dusk/dawn confirmation
therefore takes about 5.6 real minutes, and scheduler `time=` drifts about 3 h per
day. This does not matter in dusk-to-dawn mode; it would matter for any future
fixed-duration evening window.

Bench power arrangement (30-Sep-2026):

- **U0 (5 V input regulator): not fitted – open item.** A 5 V bench panel feeds
  M1 IN+/IN- directly. U0 is chosen once the production panel is confirmed;
  MP1584EN remains the candidate if the 7.6 V Voc AS102-0712A panel is kept.
- **U3 (D1 Mini 3.3 V supply): fitted.** TPS63802 buck-boost breakout set to
  3.3 V; VIN on VBAT_SYS, GND on OUT-.

D1 Mini (M3) power, by profile:

| Profile              | D1 Mini powered from          | U3 OUT -> D1 3V3 |
| -------------------- | ----------------------------- | ---------------- |
| Bench (always-on)    | Its own micro-USB             | Disconnected     |
| Production (battery) | U3 3.3 V out only             | Connected        |

The bench arrangement keeps the always-on D1 from draining the battery
overnight. Never have micro-USB and U3 OUT on the D1 3V3 rail at the same time:
the D1's onboard regulator and U3 would drive the same rail. In both profiles D1
G stays on OUT-, which is the shared UART reference.

Production (battery-only) wiring: VBAT_SYS -> C2 470 µF -> U3 VIN; U3 GND ->
OUT-; U3 3.3 V out -> D1 3V3 pin and R10; D1 5V pin and USB not connected; D1 G
-> OUT-; A0 <- R5 220k <- VBAT_SYS; D0 -> RST for deep-sleep wake. The D1's
onboard regulator stays fitted but unused. The LED string has been measured with a
47 ohm resistor, but installed-cable and temperature behaviour remain unmeasured.
The retained panel/charger path has not been fully qualified; do not treat the
charger module, charge current, or outdoor wiring as verified.

For development, use `firmware/esphome/solar-lights-lite-dev-d1.yaml` with
`pro8_debug`; this is always-on test telemetry, not the final low-power profile.
See `BOARD_AND_PARTS.md` and `BUILD_GUIDE.md` for retained reference detail.
