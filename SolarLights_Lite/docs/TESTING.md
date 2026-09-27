# Testing

Host regression coverage exercises debounce, a 14-hour dusk-to-dawn cycle, startup
and button caps, low-voltage cut-off/recovery, low-battery dimming, slow watchdog
wakes, and the shipped all-night default. It validates scheduler behaviour only;
it does not validate AVR registers, ADC settling, timing, sleep current, wiring,
or component temperatures.

Bench testing should use an isolated current-limited supply before cells or panel:

1. Build and ISP-program the `pro8_debug` image; verify supply-voltage reporting
   through the v0.5 D1 Mini Home Assistant telemetry, without an Arduino USB-UART
   connection.
2. Sweep 3.3–4.2 V and confirm LED current at 3.40, 3.70, and 4.20 V.
3. Wire the LDR, then cover/uncover it to verify the five-minute transition delay.
4. Verify the button and low-voltage cut-off/recovery conditions.
5. Qualify the panel/charger and then run outdoor and winter logging.

The current state is not qualified for unattended outdoor operation. Detailed dated
results and acceptance gates remain in `VALIDATION.md` and `BUILD_GUIDE.md`.
