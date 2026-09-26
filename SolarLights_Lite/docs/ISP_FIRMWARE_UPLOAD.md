# ISP firmware upload - method and notes (BTE13-010A)

21 September 2026. This is the practical "how to flash this chip" reference. For the
one-time fuse conversion itself (internal 8 MHz, BOD 2.7 V, no bootloader), see
[CLOCK_CONVERSION.md](CLOCK_CONVERSION.md) - that already happened, is confirmed, and
does not need repeating. This doc is about uploading *application firmware*, which
you'll come back to every time the code changes. For the full dated blow-by-blow of
how everything below was actually discovered, see the addenda in
[VALIDATION.md](VALIDATION.md) - this doc is the distilled, current-state version.

## 1. Why ISP, not the CH340 adapter

The fuses were set on 21 Sep 2026 to internal 8 MHz / BOD 2.7 V / **no bootloader**
(BOOTRST=1). That was deliberate, but it has a permanent consequence: **a plain
USB-to-serial adapter (the CH340 board) can never upload new firmware to this chip
again.** Serial upload only works if a bootloader is present to answer the
handshake; there isn't one, and reburning one is a separate, not-yet-done option
(see section 6).

The CH340 adapter still works fine, forever, for **monitoring** - watching
`Serial.print()` output over TX/RX. That only needs the firmware to be running, not
a bootloader. Don't confuse "the monitor works" with "upload still works" - they are
unrelated capabilities that happen to use the same wires.

## 2. Hardware

- **Programmer:** two confirmed working options, machine-dependent - see section 3.
  An Arduino Nano running the `ArduinoISP` sketch (built 21 Sep 2026, proven on the
  MacBook) works everywhere but needs six wires and a second Arduino. A USBasp
  dongle is simpler when it works - it succeeded cleanly on the iMac, but an
  earlier attempt on the MacBook failed with old clone firmware that doesn't
  support avrdude's SCK-period negotiation (see section 5). Try USBasp first if you
  have one; fall back to Arduino-as-ISP if it won't sync.
- **Wiring (6 wires):** MOSI->11, MISO->12, SCK->13, RESET->RST, VCC->VCC, GND->GND.
  Full pin map and photos: [BOARD_AND_PARTS.md](BOARD_AND_PARTS.md).
- **Isolation rule:** nothing else may be connected to the Pro Mini while
  programming - no CH340/FTDI adapter, no battery, no LED string. Having the CH340
  connected at the same time as the ISP programmer has caused comms failures in this
  project (contention on shared lines). Fully unplug it first.

## 3. The confirmed-working upload method

`firmware/lite_controller/platformio.ini` has an `[env:pro8_isp]` environment:
`upload_protocol = stk500v1`, `upload_speed = 19200`, no hardcoded port (it differs
per machine, and sometimes per replug - find it with `ls /dev/cu.usbserial-*` and
identify which one is the Nano, not any other serial device).

**Two-step method - proven twice, 21 Sep 2026:**
```
pio run -e pro8_isp
avrdude -c stk500v1 -P /dev/cu.usbserial-XXXX -b 19200 -p m328p -v \
  -U flash:w:.pio/build/pro8_isp/firmware.hex:i
```
(substitute the real port). First command compiles only; second flashes and
verifies using your **system** avrdude - see section 4 for why that distinction
matters.

`platformio.ini` also has an `upload_command` override so a plain
`pio run -t upload` *should* do both steps in one, using the system avrdude
automatically. **This override has not itself been bench-tested** - if it fails,
fall back to the two-step method above, which has.

**Alternative: USBasp, direct - proven once, iMac, 21 Sep 2026:**
```
pio run -e pro8_isp
avrdude -c usbasp -p m328p -v -U flash:w:.pio/build/pro8_isp/firmware.hex:i
```
No `-P` needed - USBasp is a direct USB device, not a serial port. This is
simpler than the six-wire ArduinoISP method when your USBasp supports it. If you
hit `cannot set sck period` / `target does not answer`, that particular USBasp's
firmware doesn't support SCK negotiation - see section 5 for the fix (a physical
jumper, not an avrdude flag), or just switch to the ArduinoISP method above.

## 4. The avrdude nuance - there are two different avrdudes on this machine

This is the thing most likely to bite you again if you forget it:

- **PlatformIO bundles its own avrdude** as part of the `atmelavr` platform package.
  As of 21 Sep 2026 this was **version 6.3.0** (`tool-avrdude @ 1.60300.200527`,
  visible in the `PACKAGES` section of any `pio run` build log). This is what
  `pio run -t upload` uses by default - a separate binary from whatever `avrdude`
  resolves to in a terminal.
- **System avrdude**, installed separately via Homebrew on the iMac
  (`brew install avrdude`), was **version 8.3** as of 21 Sep 2026. This is what runs
  when you type `avrdude` directly in a terminal.

These are genuinely different binaries and can behave differently against the same
hardware. **Confirmed 21 Sep 2026:** PlatformIO's bundled 6.3.0 reproducibly failed
flash verification against this exact Nano-as-ISP/stk500v1 setup - the *same* byte
and *same* mismatched values on two separate attempts, even after the ISP cables
were swapped for different ones (which rules out a flaky physical connection - real
noise would not land on the identical byte twice). The system 8.3 avrdude wrote and
verified the identical `.hex` file cleanly, twice, over the same wiring.

**Takeaway: if a PlatformIO upload fails verification in a way that looks
consistent/repeatable rather than random, try the same `.hex` through the system
avrdude directly (section 3's second command) before assuming a hardware fault.**

Check what's installed on either machine with `avrdude -v` (system) and by reading
the `PACKAGES` line of a `pio run` build log (PlatformIO's bundled version) - don't
assume they match.

## 5. Known gotchas, in the order they were hit (21 Sep 2026)

| Symptom | Cause | Fix |
|---|---|---|
| USBasp: `cannot set sck period` / `target does not answer` (MacBook, 21 Sep) | That specific USBasp's old/clone firmware doesn't support avrdude's SCK-period negotiation command - not a universal USBasp problem, a different USBasp on the iMac worked cleanly the same day | Fit the physical slow-SCK jumper on that dongle if it has one, or switch to Arduino-as-ISP (`stk500v1`) |
| `pio run -t upload` gives `stk500_getsync()` failures, every time | It ran the `pro8` environment (serial-bootloader protocol) instead of `pro8_isp` (ISP protocol) - two different environments in `platformio.ini`, and the bottom-of-window VS Code environment picker or a bare `pio run` can default to the wrong one | Always specify `-e pro8_isp` explicitly, or confirm the environment picker shows it. `default_envs = pro8_isp` is now set in `platformio.ini` so a bare upload can't silently pick the dead bootloader profile |
| `avrdude -B ...` with ArduinoISP gives `cannot get into sync` / `cannot set Parm_STK_SCK_DURATION` | The stock ArduinoISP sketch does not implement the STK500 SCK-duration command at all; asking for it breaks the *entire* handshake, not just the clock speed | Don't pass `-B` when the programmer is ArduinoISP. To genuinely slow the SPI clock, edit the `SPI_CLOCK` line inside the ArduinoISP sketch itself (e.g. `#define SPI_CLOCK (1000000/128)`) and reflash the Nano |
| Device signature reads `00 00 00`, reproducibly, right after a fuse change | avrdude's own reset toggle is not the same as a genuine cold power-down; the chip was left in a stale state after the fuse write took effect on the next reset | Fully power the target board off and back on - not just re-run avrdude |
| Flash verify fails at the same byte and same value on repeat attempts, even with fresh wiring | PlatformIO's bundled avrdude (6.3.0) - see section 4 | Use the system avrdude directly, or the `upload_command` override (untested by itself) |
| Anything behaving strangely with both a CH340 adapter and the ISP programmer connected | Contention on shared reset/serial lines | Always fully disconnect the CH340 before using ISP |

## 6. Current chip state, 21 September 2026

- **Fuses confirmed:** lfuse `0xE2`, hfuse `0xD9`, efuse `0xFD` - internal 8 MHz, BOD
  2.7 V, no bootloader. Read back independently, not just assumed from the write.
- **Rev 0.4 firmware confirmed uploaded and verified** - 4250/4250 bytes, via the
  method in section 3.
- **The CH340 adapter still works for serial monitoring only.** Never for uploads,
  unless a bootloader is deliberately reburned (not currently planned, but discussed
  as an option - see the relevant `VALIDATION.md` addendum).
- **Still open before removing the board's onboard regulator and power LED**
  (deliberately left fitted this whole time, per `CLOCK_CONVERSION.md` section 8):
  confirm D9 PWM reads approximately 1.96 kHz on a scope or frequency counter, and a
  1000 ms-delay blink sketch times out at 1 s (not 2 s) against a watch. Both are
  cheap, informal cross-checks of the actual running clock, on top of the fuse
  read-back.

## 7. If coming back to this after a break

- **Port names are not stable** across machines, or even across replugs on the same
  machine. Always re-check with `ls /dev/cu.usbserial-*` and identify which one is
  actually the Nano-as-ISP, not some other serial device that happens to be plugged
  in.
- **Never connect the CH340 adapter and the ISP programmer at the same time.**
- **The `pro8` (serial-bootloader) environment is dead for this chip** and stays
  dead unless a bootloader is deliberately reburned.
- If a PlatformIO upload fails in a way that looks repeatable (not random), suspect
  the bundled avrdude first - see section 4 - before re-wiring anything.
- `VALIDATION.md`'s dated addenda have the full story if anything here seems to
  contradict what actually happened; this doc is the summary, that file is the
  record.
