# User-reported BTE13-010A programming result

Recorded 19 September 2026. Source: user report, not a tool-observed flash operation.

- Project target: Arduino Pro Mini ATmega328P 3.3 V / 8 MHz.
- Upload speed corrected from 19200 to 57600 baud.
- CH340 serial port: cu.usbserial-210 (normally /dev/cu.usbserial-210 on macOS).
- Readable serial monitor setting: 38400 baud.
- Device signature: 0x1e950f (ATmega328P).
- Firmware size written: 6488 bytes.
- Upload and flash verification: successful.
- User explicitly reports clock verification; the provided excerpt does not include fuse readback or a frequency measurement.

```text
SolarLights Lite
t=1 vdd=3.379 state=0 pct=5
t=2 vdd=3.379 state=0 pct=5
t=3 vdd=3.379 state=0 pct=5
t=4 vdd=3.379 state=0 pct=5
t=5 vdd=3.379 state=0 pct=5
t=6 vdd=3.379 state=0 pct=5
t=7 vdd=3.379 state=0 pct=5
t=8 vdd=3.379 state=0 pct=5
t=9 vdd=3.379 state=0 pct=5
```

## Accepted evidence

The serial programming path works, the chip responds with the expected signature, the flash verifies, and firmware starts and produces plausible ADC/scheduler output. Programmer availability is no longer a blocker. Keep the working bootloader/upload path; do not erase it simply to repeat the earlier proposed no-bootloader procedure.

In this workspace's scheduler, state=0 is DAY. The first nine seconds at pct=5 match the capped startup self-test. At t=10 the startup test ends; under continuing daylight the normal fade reaches zero on subsequent steps. These lines alone do not test a whole night, dusk/dawn sensing, physical LED current, low-voltage cutoff or voltage calibration. The t field is watchdog-based elapsed logic time, not a measured CPU-frequency result.

## Attached working files resolve the baud discrepancy

The user supplied the actual `platformio.ini` and `main.cpp`; unmodified snapshots are in `user-working-upload/`. Compared with the project source, the working main.cpp enables DEBUG_SERIAL and changes Serial.begin from 9600 to **19200**. The supplied PlatformIO configuration targets `pro8MHzatmega328`, uploads at 57600 on `/dev/cu.usbserial-210`, and monitors at **38400**. No clock-prescaler change occurs in the supplied main.cpp.

**Conclusion: successful programming and startup are confirmed by the user; actual 8 MHz operation is not established. The twofold runtime baud difference strongly indicates a 16 MHz CPU running code compiled for 8 MHz**, consistent with the photographed crystal. This is an inference from the supplied files and reported output, not a direct fuse or frequency measurement. Actual build overrides/framework changes or a different flashed binary could change the interpretation; no build log or binary was supplied.

The installed PlatformIO board manifest declares F_CPU=8000000L. Arduino AVR HardwareSerial::begin uses F_CPU to calculate the UART divisor. For Serial.begin(19200), U2X mode gives UBRR=51:

| Actual CPU clock | UART baud with this divisor | D9 PWM with this code |
|---|---:|---:|
| 8 MHz | 19,230.8 (monitor 19200) | 1,960.8 Hz |
| 16 MHz | 38,461.5 (monitor 38400) | 3,921.6 Hz |

UART = actual CPU clock / (8 * (51+1)); phase-correct 8-bit Timer1 PWM = actual CPU clock / (8 * 510). A 16 MHz physical clock also halves CPU-cycle-based delays relative to this build's assumptions. The watchdog is a separate oscillator, so its approximately one-second log ticks do not prove an 8 MHz CPU clock. ADC prescaling and sample-settling delays also warrant checking after clock correction.

### Next verification and correction

1. Retain the successful upload configuration as evidence; do not promote its 38400 monitor workaround as proof of correct 8 MHz operation.
2. Read actual clock-source/divider/brownout fuses with an appropriate programmer, or measure D9 PWM while the lights/test are active. An ordinary firmware upload does not apply the board manifest's bootloader fuse values.
3. If still on the 16 MHz crystal, configure internal 8 MHz and the intended brownout setting using the actual device/programmer. Preserve backups and decide deliberately whether to retain a compatible bootloader or use ISP-only uploads. Bootloader baud settings may change after a clock change; current upload success does not determine the new settings.
4. With a genuine 8 MHz runtime and the supplied Serial.begin(19200), use a 19200 monitor. The project production source remains DEBUG_SERIAL=0, with 9600 if debug is enabled; neither source was silently replaced.
5. Recheck PWM, voltage calibration, real-time LVC and current consumption. Do not release the present clock/build mismatch for low-voltage outdoor service merely because the flash verifies.

Evidence inspected locally: PlatformIO atmelavr `boards/pro8MHzatmega328.json`, Arduino AVR `cores/arduino/HardwareSerial.cpp` and `wiring.c`. These support the calculations; the uploaded binary itself has not been inspected.
