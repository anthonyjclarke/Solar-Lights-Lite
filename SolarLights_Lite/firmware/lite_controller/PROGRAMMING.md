# SolarLights Lite firmware: build, flash and serial diagnostics

This is the single current procedure for the BTE13-010A Arduino controller.
It applies to an Intel Mac, an Apple-silicon Mac and Windows. It deliberately
uses `pio` to **build** and a separately installed, current `avrdude` to
**flash**. Do not use `pio -t upload` for this project.

## Read this first: what the fuses mean

**Fuses are persistent configuration bits inside the ATmega328P.** They are
not part of the Arduino firmware. They select fundamental hardware behaviour:
the clock source, brown-out protection and whether a bootloader receives a
reset before the application.

This controller's fuses have already been independently confirmed as:

| Setting | Value | Consequence |
|---|---:|---|
| Low fuse | `0xE2` | Internal 8 MHz clock |
| High fuse | `0xD9` | No bootloader; application starts directly |
| Extended fuse | `0xFD` (`0x05` may be displayed) | 2.7 V brown-out detection |

Do **not** burn a bootloader or add fuse-write (`lfuse:w`, `hfuse:w`,
`efuse:w`) options during ordinary updates. A normal flash command writes only
the application and leaves these settings alone.

There is no bootloader, so the USB-UART board is **monitoring only**. Firmware
is flashed over ISP with either a USBasp or a second Arduino running ArduinoISP.

## 1. What connects when

| Job | Interface | Connections |
|---|---|---|
| Flash firmware | USBasp or ArduinoISP | MOSI, MISO, SCK, RESET, VCC, GND |
| Read diagnostics | USB-UART adapter | Target TX to adapter RX; common GND |

During ISP work, disconnect the UART adapter, battery, panel, LED string and
all other peripherals. The target must have exactly one power source.

## 2. Project folder and build profiles

Run commands from this folder:

```text
SolarLights_Lite/firmware/lite_controller
```

| Profile | Command | Purpose | Firmware image |
|---|---|---|---|
| Production | `pio run -e pro8` | Quiet, low-power firmware | `.pio/build/pro8/firmware.hex` |
| Diagnostic | `pio run -e pro8_debug` | Same logic plus 9600-baud diagnostics | `.pio/build/pro8_debug/firmware.hex` |

The diagnostic build adds rate-limited `Serial` output and roughly 1 mA of
current. Use it for the bench; use production for sleep-current measurement and
deployment. The profiles set `DEBUG_SERIAL` explicitly, so the production image
remains quiet even if the source-file default is changed for ad-hoc testing.

## 3. Prepare the computer

`pio` is the command supplied by PlatformIO. Some installations also provide a
`platformio` command; this project documents and uses `pio` because it is the
reliable command in the PlatformIO terminal. Verify the two required tools:

```text
pio --version
avrdude --version
```

### Intel Mac

1. Install PlatformIO Core or use the PlatformIO terminal supplied by the VS
   Code extension. PlatformIO's [official installation guide](https://docs.platformio.org/en/latest/core/installation/)
   covers both routes.
2. Install a current standalone avrdude, outside PlatformIO:

   ```bash
   brew install avrdude
   ```

3. Confirm `pio --version` and `avrdude --version` work in the terminal where
   you will compile and flash.

### Apple-silicon Mac (M1, M2, M3, M4 and later)

Follow the Intel-Mac steps, then check the AVR compiler:

```bash
uname -m
file ~/.platformio/packages/toolchain-atmelavr/bin/avr-g++
```

If the Mac reports `arm64` and the compiler reports `x86_64`, PlatformIO's AVR
toolchain needs Apple's Intel-translation layer. Install it once, follow the
prompts, then rerun the build:

```bash
softwareupdate --install-rosetta
```

This is a host-toolchain compatibility issue, not a controller or firmware
fault. Apple documents Rosetta installation [here](https://support.apple.com/en-au/102527).
Do not copy another Mac's `.platformio` package cache.

### Windows 10 or 11

1. Install the PlatformIO VS Code extension, then open its **PlatformIO Core
   CLI** terminal. Confirm `pio --version` works there.
2. Download the current Windows binary from the [official AVRDUDE releases](https://github.com/avrdudes/avrdude/releases).
   Extract the entire release folder (including `avrdude.conf`) to a stable
   location such as `C:\\Tools\\avrdude`, and add that folder to `PATH`.
3. Open a new PlatformIO terminal and run `avrdude --version`.
4. If avrdude cannot see a USBasp, install the USBasp's required libusb-compatible
   driver for that programmer. The exact driver depends on the USBasp clone;
   do not change drivers for unrelated USB serial adapters.

The current AVRDUDE project explicitly publishes Windows binaries, and Homebrew
currently publishes current Intel and Apple-silicon macOS bottles. [AVRDUDE releases](https://github.com/avrdudes/avrdude/releases) · [Homebrew avrdude](https://formulae.brew.sh/formula/avrdude)

## 4. Compile — do this before connecting the target

For a first bench session, compile diagnostics:

```bash
pio run -e pro8_debug
```

The output must end in `SUCCESS` and create:

```text
.pio/build/pro8_debug/firmware.hex
```

For the final quiet firmware, substitute `pro8`:

```bash
pio run -e pro8
```

**Do not run `pio -t upload`.** PlatformIO's bundled avrdude is older and can
select an invalid packaged configuration. The reported command must instead be
the externally installed `avrdude` below.

## 5. USBasp — preferred flashing method

### Wiring

Verify pin 1 from the mark on the actual USBasp/cable, not a photograph.

| USBasp 10-pin | Signal | BTE13-010A Pro Mini |
|---:|---|---|
| 1 | MOSI | D11 |
| 2 | VCC | VCC |
| 5 | RESET | RST |
| 7 | SCK | D13 |
| 9 | MISO | D12 |
| 4, 6, 8 or 10 | GND | GND |

Use a verified 3.3 V-compatible target-power and logic configuration. Some
USBasp clone jumpers alter target power but not logic level, so confirm the
actual VCC with a meter. Leave the USBasp self-programming jumper open. Fit its
physical slow-SCK jumper only if the target does not answer.

Visual references: [USBasp wiring PNG](../../docs/usbasp-wiring.png) ·
[printable USBasp wiring PDF](../../../output/pdf/USBasp_Wiring.pdf) ·
[BTE13-010A board pin map](../../docs/BTE13-010A-pin-map.png).

### Preflight and flash

With the target isolated and wired, read its signature first. This does not
write anything:

```bash
avrdude -c usbasp -p m328p -v
```

The required signature is `0x1e950f`. Stop if it is different, all `00`, or all
`ff`.

Flash the diagnostic image:

```bash
avrdude -c usbasp -p m328p -v \
  -U flash:w:.pio/build/pro8_debug/firmware.hex:i
```

Flash the production image:

```bash
avrdude -c usbasp -p m328p -v \
  -U flash:w:.pio/build/pro8/firmware.hex:i
```

On Windows, use the same command in the PlatformIO terminal, replacing the
image path slashes if preferred:

```powershell
avrdude -c usbasp -p m328p -v -U flash:w:.pio\build\pro8_debug\firmware.hex:i
```

Success requires both a completed write and successful verification. Then unplug
the USBasp and remove all six ISP wires before restoring normal power.

## 6. Arduino-as-ISP fallback

Use this only if the available USBasp cannot communicate reliably.

1. Load the standard `ArduinoISP` example onto an Uno/Nano-class programmer.
2. Fit a 10 uF capacitor from the programmer's RESET to GND (negative lead to
   GND) after uploading the example; it prevents that programmer auto-resetting.
3. Wire programmer D11 to target D11, D12 to D12, D13 to D13, D10 to target
   RST, target-compatible VCC to VCC, and GND to GND.
4. Compile with `pio run -e pro8_debug` or `pio run -e pro8`.

Find the programmer port:

```bash
# macOS
find /dev -maxdepth 1 -name 'cu.usb*' -print
```

```powershell
# Windows PowerShell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Name
```

Flash diagnostic firmware, substituting the actual port:

```bash
# macOS example
avrdude -c stk500v1 -P /dev/cu.usbmodemXXXX -b 19200 -p m328p -v \
  -U flash:w:.pio/build/pro8_debug/firmware.hex:i
```

```powershell
# Windows example
avrdude -c stk500v1 -P COM5 -b 19200 -p m328p -v -U flash:w:.pio\build\pro8_debug\firmware.hex:i
```

Do not pass `-B` to the stock ArduinoISP sketch; it does not implement avrdude's
SCK-duration command.

## 7. Serial diagnostics after flashing

Disconnect the ISP programmer first and power the controller normally. On the
photographed USB-UART adapter connect only:

| Pro Mini | UART adapter |
|---|---|
| TX | RX |
| GND / OUT- | GND |

Leave UART `DTR`, `TX`, `VO` and `CTS` open. Never connect UART `VO` while the
battery powers the Pro Mini. Keep the adapter powered by USB while its RX is
connected, or disconnect the signal to prevent back-feeding an unpowered adapter.

Start a 9600-baud monitor for a debug build:

```bash
# macOS
pio device monitor --baud 9600 --port /dev/cu.usbserial-XXXX
```

```powershell
# Windows
pio device monitor --baud 9600 --port COM5
```

On reset, the debug image prints a one-time field guide, then rate-limited live
diagnostics. Production firmware intentionally prints nothing.

## 8. Optional read-only fuse check

This confirms the existing configuration without changing it:

```bash
avrdude -c usbasp -p m328p \
  -U lfuse:r:-:h -U hfuse:r:-:h -U efuse:r:-:h
```

Expect low `0xE2`, high `0xD9`, extended `0xFD`. Some avrdude releases display
the implemented extended-fuse bits as `0x05`; this represents the same setting.

## 9. Troubleshooting

| Symptom | Meaning / action |
|---|---|
| `pio: command not found` | Use the PlatformIO Core CLI terminal, or complete the official PlatformIO Core installation. Do not substitute `platformio` for `pio`. |
| `Bad CPU type in executable` on Apple silicon | Install Rosetta as shown above, then rebuild. |
| Old avrdude version or a path under `.platformio` | Stop. Close `pio -t upload`; use the separately installed current avrdude command. |
| USBasp `cannot set sck period` | Old clone firmware; fit its physical slow-SCK jumper or use Arduino-as-ISP. |
| `target does not answer` | Check pin-1 orientation, MOSI/MISO, RESET, shared GND, VCC and slow SCK. |
| Signature is not `0x1e950f` | Wrong target or wiring; stop without writing. |
| Flash verification mismatch | Confirm external current avrdude is running, then rebuild and retry once. |
| Serial text unreadable | Confirm the 8 MHz target and the `pro8_debug` image. |
| No serial output | Production image flashed, TX/RX reversed, missing common OUT- ground, or wrong port. |

## 10. Final checklist

- `pio run -e pro8_debug` ended in `SUCCESS`.
- The correct `.hex` path exists.
- Battery, panel, LEDs and UART are disconnected during ISP.
- Exactly one target power source is present.
- USBasp voltage and pin 1 are verified.
- Signature is `0x1e950f`.
- External avrdude reports both write and verification success.
- ISP is disconnected before normal power and UART monitoring return.

For firmware behaviour and staged hardware validation, use the
[assembly and diagnostics guide](../../docs/ASSEMBLY.html#staging).
