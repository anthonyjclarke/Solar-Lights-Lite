# 08 – Controller firmware: build, fuses, flash and diagnostics

The controller firmware is in [`firmware/controller/`](../firmware/controller/).
It is built with PlatformIO and flashed over ISP with a standalone copy of
`avrdude`. The board has no bootloader, so there is no USB upload.

**What you will learn:** AVR fuses and ISP programming, PlatformIO build
environments, low-power AVR techniques (power-down sleep, watchdog wake,
pin-change interrupts, bandgap voltage measurement, hardware PWM), and testing
embedded logic on a desktop computer.

---

## Source layout

| File                       | Purpose                                    |
| :------------------------- | :----------------------------------------- |
| `include/config.h`         | Every tuneable value: pins, levels, timing |
| `include/schedule.h`       | Hardware-free dusk-to-dawn scheduler       |
| `src/main.cpp`             | AVR layer: ADC, PWM, sleep, telemetry      |
| `test_host/regression.cpp` | Scheduler tests that run on a computer     |
| `platformio.ini`           | One build environment per telemetry tier   |

---

## Build environments

| Environment  | Telemetry output                   | Use with      |
| :----------- | :--------------------------------- | :------------ |
| `advanced`   | Field guide, then full diagnostics | Tier 1, bench |
| `production` | One compact status line every ~8 s | Tier 2        |
| `standalone` | None; serial port powered down     | Tier 0        |

All three run identical lighting logic. Commission with `advanced`; deploy
with `production` (or `standalone` if you have no telemetry).

---

## Install the tools

1. **PlatformIO.** Install the PlatformIO extension for VS Code, or PlatformIO
   Core ([installation guide](https://docs.platformio.org/en/latest/core/installation/)).
   Check `pio --version` in the PlatformIO terminal.
2. **avrdude, version 7 or later, installed separately.** PlatformIO bundles an
   older avrdude that is not reliable with this setup, so do not use
   `pio run -t upload`.
   - macOS: `brew install avrdude`
   - Linux: your distribution's `avrdude` package, if it is version 7 or later;
     otherwise build or download it from the
     [AVRDUDE project](https://github.com/avrdudes/avrdude/releases).
   - Windows: download the release from the
     [AVRDUDE project](https://github.com/avrdudes/avrdude/releases), extract
     the whole folder (including `avrdude.conf`) and add it to `PATH`. A USBasp
     also needs a libusb driver (for example installed with Zadig).
3. Check `avrdude --version` in the same terminal you will flash from.

---

## Wire the programmer

Disconnect the battery, panel, LED string, telemetry and any USB-UART adapter
first. The controller must have exactly one power source: the programmer.

| USBasp 10-pin | Signal | Pro Mini |
| :------------ | :----- | :------- |
| 1             | MOSI   | 11       |
| 2             | VCC    | VCC      |
| 5             | RESET  | RST      |
| 7             | SCK    | 13       |
| 9             | MISO   | 12       |
| 4, 6, 8 or 10 | GND    | GND      |

Set the USBasp to **3.3 V** and confirm with a meter: some clones switch target
power but not logic level. Printable sheets: [USBasp wiring](drawings/usbasp-wiring.pdf)
and the [board map](drawings/BTE13-010A-pin-map.pdf).

---

## One-time preparation of a new board

Run these from any folder. None of them are needed again for routine updates.

**1. Read the signature** (writes nothing):

```bash
avrdude -c usbasp -p m328p -v
```

The device signature must be `0x1e950f`. Stop if it differs or reads all
`00` or all `ff`.

**2. Save the existing fuses**, in case you ever want the board back as it
was:

```bash
avrdude -c usbasp -p m328p -U lfuse:r:-:h -U hfuse:r:-:h -U efuse:r:-:h
```

**3. Write the Solar Lights fuses:**

```bash
avrdude -c usbasp -p m328p -U lfuse:w:0xE2:m -U hfuse:w:0xD9:m -U efuse:w:0xFD:m
```

| Fuse     | Value  | Effect                                       |
| :------- | :----- | :------------------------------------------- |
| Low      | `0xE2` | Internal 8 MHz RC oscillator, no clock ÷8    |
| High     | `0xD9` | Start at address 0 (no bootloader), ISP kept |
| Extended | `0xFD` | Brown-out reset at 2.7 V                     |

Fuses are persistent configuration bits, separate from the program. Type the
values carefully: a wrong clock-source value can leave the chip needing an
external clock or a high-voltage programmer to recover. Some avrdude versions
show the extended fuse as `0x05`; that is the same setting with the unused
bits hidden.

The first firmware flash erases the chip, which also removes any Arduino
bootloader. The board will no longer accept serial uploads; that is expected.

---

## Build and flash

From `firmware/controller`:

```bash
pio run -e advanced
```

The build must end in `SUCCESS` and produce `.pio/build/advanced/firmware.hex`.
Then flash it:

```bash
avrdude -c usbasp -p m328p -v -U flash:w:.pio/build/advanced/firmware.hex:i
```

Success needs both the write and the verify to pass. Unplug the programmer and
remove all six ISP wires before reconnecting normal power.

For deployment, build and flash `production` (or `standalone`) the same way,
replacing `advanced` in both commands. Routine updates never write fuses.

### Arduino as ISP (fallback)

If you have no USBasp, an Uno or Nano can act as the programmer:

1. Upload the `ArduinoISP` example sketch to it.
2. Fit a 10 µF capacitor from its RESET to GND (stops it auto-resetting).
3. Wire programmer D11 → target 11, D12 → 12, D13 → 13, D10 → target RST,
   plus VCC and GND. A 5 V Uno drives 5 V logic, so power the target from the
   Uno's 5 V pin: that is within the ATmega328P's rating **only while the
   controller is isolated** from the battery rail, LDR, LED string and D1 Mini.
4. Replace `-c usbasp` with `-c stk500v1 -P <port> -b 19200` in every command,
   for example `-P /dev/ttyACM0`, `-P /dev/cu.usbmodem1101` or `-P COM5`. Do
   not add `-B`; the stock sketch ignores it.

---

## Reading the diagnostics

With the `advanced` build, the controller prints a one-time field guide at
reset, then a line whenever something changes, every 10 s while a transition,
test or cut-off is being timed, and every 60 s otherwise. The `production`
build prints a shorter line every 8 scheduler seconds.

Two ways to read it:

- **Tier 1 Advanced Telemetry** (recommended): the D1 Mini decodes every line
  into Home Assistant ([09 – Home Assistant](09-home-assistant.md)).
- **A 3.3 V USB-UART adapter**: connect only controller TX → adapter RX and
  GND → adapter GND; leave the adapter's VCC, TX, DTR and CTS open (sheet 5).
  Then run `pio device monitor --baud 9600` from `firmware/controller`.

### Line format

Every line is space-separated `key=value` pairs starting with `fw=`. Both
ESPHome profiles parse these keys; if you rename one, update both YAML files.

| Key         | Example        | Meaning                                |
| :---------- | :------------- | :------------------------------------- |
| `fw`        | `0.6.0`        | Firmware version (`config.h`)          |
| `time`      | `1234s`        | Scheduler seconds since reset          |
| `vdd`       | `3.912V`       | Controller supply (= battery rail)     |
| `battery`   | `OK`           | Band: OK, MID, LOW, CRITICAL           |
| `ldr`       | `12.4%`        | A1 as a percentage of VCC              |
| `sense`     | `DARK`         | DARK, MID or LIGHT                     |
| `mode`      | `NIGHT`        | DAY, NIGHT or LVC (cut-off)            |
| `night`     | `YES`          | Dusk confirmed, dawn not yet           |
| `output`    | `100%`         | D9 PWM duty                            |
| `cause`     | `DUSK_TO_DAWN` | Why the output has its value           |
| `raw`       | `127`          | A1 ADC count (advanced only)           |
| `ldr_v`     | `0.485V`       | A1 volts (advanced only)               |
| `confirm`   | `DUSK 40/300s` | Transition progress (advanced only)    |
| `lvc`       | `0/30s`        | Time below cut-off (advanced only)     |
| `button`    | `59s`          | Test time left (advanced only)         |
| `next_tick` | `1s`           | Next watchdog interval (advanced only) |

| `cause`           | Meaning                            |
| :---------------- | :--------------------------------- |
| `STARTUP_TEST`    | 10 s flash after reset             |
| `BUTTON_TEST`     | 60 s test after a D2 press         |
| `DAY_OFF`         | Daylight, lights off               |
| `FADE_TO_DAY_OFF` | Dawn confirmed, fading out         |
| `DUSK_TO_DAWN`    | Night, full night level            |
| `LOW_BATT_NIGHT`  | Night, below 3.45 V: level halved  |
| `LOW_VOLT_BLOCK`  | Test refused: supply below cut-off |
| `LVC_OFF`         | Low-voltage cut-off active         |

---

## Tuning and calibration

All settings are in `include/config.h`. The ones you are most likely to change:

| Setting           | Default | Effect                              |
| :---------------- | :------ | :---------------------------------- |
| `NIGHT_DUTY_PCT`  | 100     | Night brightness and energy use     |
| `LDR_DARK_RATIO`  | 0.30    | Dusk threshold (A1 fraction)        |
| `LDR_LIGHT_RATIO` | 0.60    | Dawn threshold (A1 fraction)        |
| `LOW_BATT_V`      | 3.45    | Below this, night level halves      |
| `LVC_OFF_V`       | 3.30    | Cut-off voltage (after 30 s)        |
| `LVC_RESUME_V`    | 3.60    | Recovery voltage (in daylight)      |
| `BANDGAP_V`       | 1.10    | Supply measurement calibration      |
| `TIME_SCALE`      | 1       | Bench only: 60 runs time 60× faster |

**Calibrate the supply reading** once per board, in Gate 1: power the
controller from a bench supply at about 3.8 V, compare `vdd` with a meter, set
`BANDGAP_V = 1.10 × Vmeter / Vreported`, then rebuild and reflash. The
thresholds above all depend on this reading.

---

## Host tests

The scheduler has no hardware dependencies, so its behaviour is tested on any
computer with a C++17 compiler. From `firmware/controller/test_host`:

```bash
c++ -std=c++17 -Wall -Wextra -Werror -I../include regression.cpp -o regression && ./regression
```

It must print `PASS`. The tests cover dusk/dawn confirmation, a 14-hour night,
test-level caps, cut-off and recovery, low-battery dimming, slow ticks and the
shipped defaults. They do not test registers, ADC settling, sleep current or
wiring: that is what commissioning is for.

---

## Troubleshooting

| Symptom                                | Meaning / action                         |
| :------------------------------------- | :--------------------------------------- |
| `pio: command not found`               | Use the PlatformIO terminal              |
| `Bad CPU type` on an Apple-silicon Mac | AVR toolchain needs Rosetta 2            |
| avrdude path contains `.platformio`    | Wrong avrdude: use the standalone one    |
| `cannot set sck period`                | Old USBasp firmware: fit slow-SCK jumper |
| `target does not answer`               | Pin 1, MOSI/MISO, RST, VCC, slow SCK     |
| Signature not `0x1e950f`               | Wrong chip or wiring: stop               |
| Verification mismatch                  | Check avrdude version, retry once        |
| Serial text unreadable                 | Fuses not set (still 16 MHz)             |
| No serial output at all                | `standalone` build, or TX/GND wiring     |
