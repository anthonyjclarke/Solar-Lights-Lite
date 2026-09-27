# SolarLights Lite firmware: build, upload and serial diagnostics

This is the **single current procedure** for compiling and programming the
SolarLights Lite Arduino controller. It is written for a clean macOS setup and
does not assume a particular iMac, MacBook, USB port name or programmer serial
number.

The target is the project BTE13-010A Pro Mini with an ATmega328P. Its confirmed
configuration is:

- internal 8 MHz clock;
- brown-out detection at 2.7 V;
- no bootloader;
- application uploads through ISP, not through the UART connector.

The fuse conversion is already complete. Routine firmware updates do **not**
rewrite the fuses.

## 1. Two separate interfaces

Do not confuse programming with serial monitoring:

| Interface | Purpose | Connections |
|---|---|---|
| USBasp or Arduino-as-ISP | Compile output is written into flash | MOSI, MISO, SCK, RESET, VCC, GND |
| USB-UART adapter | Read diagnostic `Serial.print()` output after programming | Pro Mini TX to adapter RX; common GND |

The USB-UART adapter cannot upload to this controller because the chip has no
bootloader. During ISP programming, completely disconnect the UART adapter,
battery, panel, LED string and every other peripheral.

## 2. Firmware folder and important files

Run all commands from this folder:

```bash
cd SolarLights_Lite/firmware/lite_controller
```

| File | Purpose |
|---|---|
| `src/main.cpp` | Arduino hardware, sensing, output and diagnostics |
| `include/schedule.h` | Hardware-independent scheduler |
| `platformio.ini` | Named build/upload environments |
| `test_host/regression.cpp` | Scheduler regression tests |

## 3. macOS prerequisites — check on each Mac

Choose one PlatformIO installation on each Mac:

- If the PlatformIO extension is already installed in VS Code, use its
  **PlatformIO Core CLI** terminal. The extension includes PlatformIO Core; do
  not install a second copy just for this project.
- For a standalone Terminal installation, follow PlatformIO's
  [official Core installer](https://docs.platformio.org/en/latest/core/installation/methods/installer-script.html).
  Its current macOS quick install is:

  ```bash
  curl -fsSL -o get-platformio.py \
    https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py
  python3 get-platformio.py
  ```

Install a current system `avrdude`, then verify the commands in the same
terminal that will be used for programming:

```bash
command -v platformio || command -v pio
command -v avrdude
platformio --version
avrdude -?
uname -m
```

`pio` is only a shorter alias for `platformio`. The commands below use the full
name so the instructions are unambiguous. If PlatformIO was installed by its
VS Code extension and is not on the normal shell path, either use a PlatformIO
terminal or invoke:

```bash
~/.platformio/penv/bin/platformio
```

Homebrew provides a current standalone `avrdude`:

```bash
brew install avrdude
```

The project deliberately calls the system `avrdude` for uploads. This avoids a
previous verification failure seen with an old PlatformIO-bundled avrdude.

### Apple Silicon compiler check

On an Apple Silicon Mac, a downloaded Intel-only AVR compiler may fail with:

```text
Bad CPU type in executable
```

Inspect it with:

```bash
uname -m
file ~/.platformio/packages/toolchain-atmelavr/bin/avr-g++
```

If the Mac reports `arm64` and the compiler reports `x86_64`, the immediate
compatibility fix is Apple's Rosetta translator:

```bash
softwareupdate --install-rosetta
```

Follow the prompts, then rerun the compile. Apple documents this command in
[Using Intel-based apps on a Mac with Apple silicon](https://support.apple.com/en-au/102527).
Prefer a native PlatformIO AVR toolchain when one is available; Rosetta support
is a compatibility bridge, not a firmware requirement. Do not treat this as a
firmware error, and do not copy one Mac's `.platformio` package cache to another
Mac with a different architecture.

Before touching the target, make sure a clean compile succeeds on the Mac being
used.

## 4. Choose exactly one environment

| Environment | Programmer | Serial diagnostics | Normal use |
|---|---|---:|---|
| `pro8_usbasp` | USBasp | Off | Production build; default |
| `pro8_usbasp_debug` | USBasp | 9600 baud | Bench testing with expanded diagnostics |
| `pro8_arduinoisp` | Arduino running ArduinoISP | Off | Production fallback |
| `pro8_arduinoisp_debug` | Arduino running ArduinoISP | 9600 baud | Diagnostic fallback |

The debug and production builds use identical controller logic. The debug build
adds rate-limited serial text and consumes roughly 1 mA more. Use production for
sleep-current measurements and final deployment.

## 5. Compile only

For the normal USBasp production build:

```bash
platformio run -e pro8_usbasp
```

For the USBasp diagnostic build:

```bash
platformio run -e pro8_usbasp_debug
```

A successful build ends with `SUCCESS`. The firmware image is written to:

```text
.pio/build/<environment>/firmware.hex
```

For example:

```text
.pio/build/pro8_usbasp_debug/firmware.hex
```

Do not proceed to an upload if compilation failed or the expected `.hex` file
does not exist.

## 6. USBasp wiring — preferred upload method

The USBasp 10-pin numbers below use the standard AVR ISP header. Verify pin 1
from the mark on the actual programmer or cable; never infer orientation from a
photograph alone.

| Signal | USBasp 10-pin | Pro Mini target |
|---|---:|---|
| MOSI | 1 | D11 |
| VCC | 2 | VCC |
| RESET | 5 | RST |
| SCK | 7 | D13 |
| MISO | 9 | D12 |
| GND | 4, 6, 8 or 10 | GND |

Visual references:

- [USBasp wiring PNG](../../docs/usbasp-wiring.png)
- [Printable USBasp wiring PDF](../../../output/pdf/USBasp_Wiring.pdf)
- [BTE13-010A board pin map](../../docs/BTE13-010A-pin-map.png)

### USBasp power and isolation

1. Unplug the battery, solar input, LED string and UART adapter.
2. Confirm the target is not receiving power from anywhere else.
3. Set the USBasp target voltage to a target-compatible level. The rebuilt
   controller is an 8 MHz battery-domain design; use a verified 3.3 V-compatible
   programmer/logic configuration unless the actual programmer and isolated
   target have been deliberately qualified otherwise.
4. Verify VCC-to-GND polarity and voltage with a meter before attempting ISP.
5. Connect the six ISP signals above.
6. Leave any USBasp self-programming jumper open. Use its physical slow-SCK
   jumper only if the target will not answer.

Some clone USBasp voltage jumpers switch target power but not logic voltage.
Confirm the behaviour of the actual unit; a label alone is not proof.

## 7. USBasp preflight, upload and verification

With the target isolated and wired, first read the device signature without
writing anything:

```bash
avrdude -c usbasp -p m328p -v
```

The expected ATmega328P signature is:

```text
0x1e950f
```

Stop if the signature differs or reads `00 00 00` / `ff ff ff`.

Upload a production build in one command:

```bash
platformio run -e pro8_usbasp -t upload
```

Upload the diagnostic build instead:

```bash
platformio run -e pro8_usbasp_debug -t upload
```

The `platformio.ini` upload command uses the system `avrdude` and performs flash
verification. A successful run must report a completed write and verification.

If a build already exists and a direct manual upload is needed, use the matching
environment folder. Diagnostic example:

```bash
avrdude -c usbasp -p m328p -v \
  -U flash:w:.pio/build/pro8_usbasp_debug/firmware.hex:i
```

Never upload a `.hex` from a differently named environment by accident.

After verification:

1. Unplug the USBasp from USB.
2. Disconnect all six ISP wires from the target.
3. Restore the normal battery/controller wiring.
4. Reconnect the receive-only UART monitor only if using a debug build.

## 8. Arduino-as-ISP fallback

Use this only when the available USBasp cannot communicate reliably.

Prepare an Uno/Nano-class programmer by loading the standard `ArduinoISP`
example. After that upload, connect a 10 uF capacitor from programmer RESET to
GND, negative lead to GND, to prevent the programmer itself auto-resetting.

| Signal | ArduinoISP board | Pro Mini target |
|---|---|---|
| MOSI | D11 | D11 |
| MISO | D12 | D12 |
| SCK | D13 | D13 |
| RESET | D10 | RST |
| VCC | target-compatible supply | VCC |
| GND | GND | GND |

Find the programmer's current port after plugging it in:

```bash
ls /dev/cu.usbserial-* /dev/cu.usbmodem* 2>/dev/null
```

Do not put a saved machine-specific port in `platformio.ini`; macOS port names
can change after replugging or between computers.

Compile and upload the diagnostic fallback, substituting the actual port:

```bash
platformio run -e pro8_arduinoisp_debug
platformio run -e pro8_arduinoisp_debug -t upload \
  --upload-port /dev/cu.usbserial-XXXX
```

Production uses `pro8_arduinoisp` in the same commands. Do not pass `-B` to a
stock ArduinoISP sketch; it does not implement avrdude's SCK-duration command.

## 9. Serial diagnostics after upload

Disconnect the ISP programmer first. Power the controller from its normal
protected battery output. For the photographed UART adapter, connect only:

| Pro Mini | UART adapter |
|---|---|
| TX | RX |
| GND / OUT- | GND |

Leave UART `DTR`, `TX`, `VO` and `CTS` open. Never connect UART `VO` while the
battery powers the Pro Mini. Keep the adapter itself powered by USB while its RX
is connected, or disconnect the signal so an unpowered adapter cannot be
back-fed.

Find the UART port and start a 9600-baud monitor:

```bash
ls /dev/cu.usbserial-* /dev/cu.usbmodem* 2>/dev/null
platformio device monitor --baud 9600 --port /dev/cu.usbserial-XXXX
```

On reset, the debug firmware prints a one-time field guide followed by live,
rate-limited diagnostic lines. The production build intentionally prints
nothing.

## 10. Optional read-only fuse check

Routine uploads do not need fuse changes. To confirm the existing values with a
USBasp, use this read-only command:

```bash
avrdude -c usbasp -p m328p \
  -U lfuse:r:-:h -U hfuse:r:-:h -U efuse:r:-:h
```

Expected values are low `0xE2`, high `0xD9`, extended `0xFD`. Some avrdude
versions display the implemented extended-fuse bits as `0x05`; that represents
the same BOD setting. Do not add fuse-write options to a normal application
upload.

## 11. Troubleshooting

| Symptom | Check |
|---|---|
| `Bad CPU type in executable` | Host/toolchain architecture mismatch; see the Apple Silicon check in section 3 |
| USBasp `cannot set sck period` | Old/clone programmer firmware; fit the physical slow-SCK jumper or use Arduino-as-ISP |
| `target does not answer` | Pin-1 orientation, MOSI/MISO, RESET, common ground, target VCC and slow SCK |
| Signature `00 00 00` | Target unpowered, reset/wiring fault, or stale state; fully remove power and reconnect |
| Signature is not `0x1e950f` | Wrong target or wiring; stop without writing |
| Repeatable flash verification mismatch | Confirm the command is using the system `avrdude`, then rebuild cleanly |
| Serial text is unreadable at 9600 | Check the actual 8 MHz clock and confirm the debug environment was flashed |
| No serial text | Production build flashed, TX/RX reversed, no common OUT- ground, or wrong port |
| Controller behaves differently while connected | Check for two power sources; UART power must remain disconnected |

## 12. Clean rebuild and final checklist

If build artifacts are suspect:

```bash
platformio run -e pro8_usbasp_debug -t clean
platformio run -e pro8_usbasp_debug
```

Before every upload:

- correct environment selected;
- expected `.hex` path exists;
- battery, panel, LEDs and UART fully disconnected;
- exactly one target power source;
- programmer voltage and pin 1 verified;
- signature is `0x1e950f`;
- flash write and verification both complete;
- ISP disconnected before normal power and serial monitoring return.

For firmware behaviour and test expectations, continue with the project
[assembly and staged diagnostics guide](../../docs/ASSEMBLY.html#staging).
