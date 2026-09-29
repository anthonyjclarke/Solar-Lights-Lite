# SolarLights Lite - engineering review

Revision 0.5 live project status | 27-Sep-2026 | Active bench development

> **Historical evidence, not the current programming procedure.** This report
> preserves dated commands, port names and machine-specific results so the test
> history remains auditable. For a clean iMac or MacBook setup and all current
> build, upload and serial-monitor steps, use
> [`firmware/lite_controller/PROGRAMMING.md`](../firmware/lite_controller/PROGRAMMING.md).

> **v0.5 integration status.** The current test configuration reuses the D1 Mini
> and Q2/R8/R9/R10 as a receive-only, inverted UART monitor (Arduino D1/TX to D1
> Mini D6). It has not added current, energy, panel-voltage or temperature
> measurement hardware. The dated v0.4 evidence below remains historical evidence;
> it is not a test result for this new telemetry path.

**The rebuild has a useful architecture, but the supplied design is not yet build-ready.** A small independent controller and sleeping Wi-Fi telemetry are sensible. Reuse the existing panel and a protected TP4056 module, after resolving its input supply and confirming the actual module. Use reduced brightness from dusk to dawn, as requested during this review.

The drawings in `docs/` supersede the old assembly instructions. The old KiCad files remain evidence of the reviewed design, not a fabrication release. No hardware was connected, programmed, measured, or ordered by this assistant. Later user-reported and recorded programming/measurement results are documented in the dated addenda below.

## What the reference files establish

- Panel photograph: AS102-0712A, Pmax 1.2 W, Vmp 7 V, **Imp 0.17 A**, Voc 7.6 V, Isc 0.19 A, at 25 C standard test conditions. Isc is not the normal charging-current rating.
- Charger photograph: protected six-terminal 4056-family module; chip marking appears to be **TC4056**, not proof of a genuine Top Power TP4056. The filename `TP4046.jpg` is misleading. The board schematic and maximum ratings must be identified from the actual module.
- Original light schematic: LDR/transistor switch with a variable series LED resistance. Retain or replace the current limiting; removing the transistor board does not establish that the LED string has its own resistors.
- Original ESPHome: 10 minutes awake per approximately 190-minute cycle. At an illustrative 80 mA awake and 0.2 mA asleep, this is about **105 mAh/day** before other loads. Short wakes can help substantially; 200 mA lighting for 14 h is still **2,800 mAh/night**.
- User inventory: 16 MHz Pro Mini, assorted MOSFETs, multiple TP4056 modules; reuse the existing solar charging arrangement initially. Exact MCU marking, MOSFETs, regulators, cells, and LED characteristics remain unconfirmed.

## Findings and disposition

| ID | Priority | Finding | Required disposition |
|---|---|---|---|
| H01 | Blocker | Two series diodes are not a voltage regulator. Forward drop depends on current; cold/no-load Voc is not bounded by subtracting 1 V. TP4056 absolute max 8 V is a stress limit, not a design target. | Add qualified 5 V input conditioning for the retained charger. Inspect actual chip ratings. Validate full-battery/no-load and cold-panel conditions. |
| H02 | Blocker | No TP4056 PROG resistor/current is specified. A common 1 A module can collapse a 170 mA panel; ordinary buck regulators can also cycle in weak light. | Start with a verified 100-150 mA charge setting, test weak-light restart and measure net harvest. A genuine TP4056 uses approximately 1,200/R(kohm) mA: 12k -> 100 mA; 8.2k -> 146 mA. Do not assume clone equivalence. |
| H03 | Blocker | User has a 16 MHz board; supplied firmware assumes 8 MHz. Stock 16 MHz is not guaranteed across a 1S discharge range. A build flag does not change the oscillator. | Convert verified ATmega328P to internal 8 MHz using ISP, BOD 2.7 V, remove regulator/power LED, then verify timing. Alternative: known 8 MHz board. |
| H04 | Blocker | LED string peak current and resistance are unknown. PWM reduces average current, not pulse amplitude. | Establish safe current at 4.20 V with a current-limited supply before connecting cells. Fit Rlim as measured; never default to 0 ohms. |
| H05 | High | Battery into the D1 Mini 5V pin can work on some boards, but LDO dropout/board differences mean low-battery radio operation is unverified. More capacitance does not fix insufficient DC headroom. | Prefer a qualified low-quiescent 3.3 V buck-boost supply into 3V3 with the onboard LDO isolated. Direct battery-to-5V remains an optional measured variant, not a guarantee. Never connect 4.2 V to 3V3. |
| H06 | High | D8 100k/220k divider gives 2.27 V at 3.30 V battery. ESP8266 VIH at 3.3 V is 2.475 V minimum. | Replace with a small NPN inverter, pull up collector to ESP 3V3, invert D5 in YAML. Avoids battery-domain logic-high ambiguity. |
| H07 | High | IRLZ44N/IRLB8721 cannot be declared fully enhanced at 3 V solely because they are described as logic-level. | Identify part; require RDS(on) specification at 2.5-3 V or bench qualify at minimum supply. AO3400A on a breakout is a documented example; it is not pin-compatible with a TO-220. |
| H08 | High | Firmware LVC stops only the LEDs. D1 Mini and other loads keep discharging until hardware protection trips. | Confirm hardware pack protection. Consider a higher-threshold disconnect for telemetry; this is especially important if resets cause repeated radio wakes. |
| H09 | High | TP4056 is not a load-sharing charger. Continuous system load contributes to the measured charge current and can delay termination; sunlight loss can produce repeated restart cycles. | Measure charge termination with telemetry on/off and weak-light transitions. Disable daytime LED tests during the termination test. Retained TP4056 is a qualified compromise, not equivalent to a solar power-path charger. |
| H10 | High | Board thermal regulation measures the charger die, not the cells. Typical modules disable TEMP sensing. | Qualify cell-temperature charging limits from the actual cell datasheet and provide temperature inhibit for unattended outdoor use. Do not accept a cool charger as proof that the cells are safe. |
| H11 | Check | Ground concern is module-dependent. Supplier Sunrom 5163 schematic explicitly joins IN- and OUT-, with B- behind protection FETs. Initial suspicion of an automatic protection bypass was not confirmed. | Map the actual board with power removed; never externally join B- to OUT-. The revised drawing keeps the panel return at IN- and load return at OUT- without an extra link. |
| H12 | Medium | CHRG diode can leave reverse leakage, logic-low margin, powered/unpowered behaviour and physical solder access unresolved. | Omit charging telemetry in the initial assembly. Charging LED is not a measurement of net cell current. Add an isolated interface later if needed. |
| H13 | Medium | Panel sensing depends on charger loading; divider can inject current into an unpowered MCU. LDR also needs shading from the light string. | Reuse a switched LDR for this proposal. Do not fit the old raw-panel divider. Measure dusk/dawn thresholds in situ. |
| H14 | Medium | “Energy-neutral all year”, 26-night autonomy, and fixed winter harvest were unsupported. Half-covering a series-cell panel is not a linear half-power winter simulation. | Use measured charge and load energy; log real winter performance. No fixed autonomy without measured usable capacity. |
| H15 | Medium | Solar-midnight timing is not a civil-time clock, particularly with daylight saving and sensor offsets. 1.96 kHz PWM does not guarantee camera flicker freedom. | Dusk-to-dawn mode removes the clock-time dependency. Test the actual light and any camera. |
| H16 | Medium | Identical netlists do not validate module internals, ratings, footprints or manufacturability. Several footprints are absent; generic MOSFET pin numbering is not interchangeable. | Keep legacy KiCad on hold. Create a carrier PCB only after physical modules and footprints are frozen. |

TP4056 limits/current/termination: [Top Power datasheet](https://www.toppwr.com/uploadfile/file/20240307/65e993d6379ea.pdf). Module topology: [Sunrom module schematic](https://www.sunrom.com/p/lithum-battery-charger-with-protection-microusb). GPIO thresholds: [Espressif ESP8266EX datasheet, electrical characteristics](https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf). Clock/supply constraints: [Microchip ATmega328P](https://www.microchip.com/en-us/product/atmega328p). MOSFET example: [AOS AO3400A](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a). LDO example: [Richtek RT9013](https://www.richtek.com/assets/product_file/RT9013/DS9013-10.pdf). These are component/design sources, not identification of the user's clones.

## Software review and changes

Baseline source snapshots are in `validation/baseline/`. Revised code is a proposal matched to the new drawings.

- Uniform dusk-to-dawn mode defaults to a **5% maximum commanded duty**, dropping to 2% below 3.45 V. The 8-bit PWM uses floor division: 5% becomes 12/255 = 4.71%. `PANEL_STAGE=2` now selects a 10% all-night profile only after energy measurements justify it; it is not automatic approval of a panel swap.
- Removed voltage compensation that could double actual duty as the cell discharged. This deliberately allows brightness to fall with battery voltage.
- Startup and button tests obey the same cap. Low-voltage startup does not flash the lights. Confirmed LVC turns PWM off immediately, without a fade; it still requires 30 seconds below 3.30 V and recovery above 3.60 V in confirmed daylight.
- LDR is the default (`SENSOR_LDR=1`). D10/D11 are reserved and open in Rev 0.4. No RTC, Wi-Fi or HA is needed to run the lights.
- D5 uses an inverted NPN interface. Removed the unqualified CHRG/D6 input. Added OTA helper state handling and a bounded initial wait for its state; helper OFF allows sleep again. The 45-second sleep fallback remains. OTA ON intentionally increases consumption; it is not unattended operating mode.
- Battery percentage remains an approximate voltage-derived indication, not coulomb-counted state of charge. Calibrate voltage first. The 5.21 multiplier is preserved from the user's previous calibration; nominal resistors imply 5.4. Wi-Fi wake current and voltage sag affect the reading.

## Executed checks

| Check | Result | Evidence |
|---|---|---|
| Original references | Panel/charger photos and rendered original circuit inspected | `v1_reference/` |
| Fresh KiCad netlist exports | Both have 25 nets; connectivity identical | `validation/netlist-comparison.json`, two exported XML files |
| Engineering ERC | 1 error, 167 warnings | `validation/legacy-erc.txt` |
| Wiring ERC | 1 error, 169 warnings | `validation/legacy-wiring-erc.txt` |
| ERC meaning | Undriven power pin is a modelling issue; most warnings are off-grid endpoints, plus dangling wire endpoint(s). Do not confuse them with 168 physical circuit faults. | Full reports retained without exclusions added |
| Original host simulation | Compiled and ran; reproduces 203 mAh/day evening-only estimate under its idealised assumptions | `validation/legacy-simulation.txt` |
| Revised regression | Eight assertion groups pass, compiled with warnings-as-errors and address/undefined-behaviour sanitizers | `validation/regression-results.txt` |
| AVR firmware build | See `validation/avr-build.txt`; original PlatformIO toolchain cannot execute on this Mac (Bad CPU type) | No on-device result inferred from host tests |
| ESPHome schema | See `validation/esphome-config.txt` | Dummy secrets only; no flash/connection to hardware |
| User hardware upload/startup | User reports 6,488 bytes verified, signature 0x1e950f; startup log supplied | `validation/user-hardware-upload.md`; attached source requests 19200 but monitor needs 38400: likely 16 MHz runtime / 8 MHz build |
| Complete circuit and weather | NOT TESTED | Bench/field acceptance plan in build guide |

The host tests cover dusk debounce and reset, a 14-hour night, daylight shutdown, startup/button cap, LVC delay and immediate shutdown, recovery lockout, low-battery startup, dimming, slow ticks, and evening fallback. They do not emulate AVR registers, ADC settling, oscillator drift, sleep current, EMI or Wi-Fi behaviour.

## Board and inventory follow-up

User photos identify the board as BTE13-010A with a 16 MHz crystal. The linked BTE13-010 reference was retrieved via HTTP; its HTTPS endpoint failed. The A-revision still requires chip-signature and regulator/LED trace checks. Q2 is now selected as 2N3904 from the inventory; no MOSFET occurs in that list, so Q1 remains open. S9013 is corrected to NPN in a separate reviewed copy. See [BOARD_AND_PARTS.md](BOARD_AND_PARTS.md) for the pin map, evidence and BJT alternative tradeoffs. No hardware was modified.

## Decision before assembly

Programming access is user-confirmed. Verify/correct the likely 16 MHz runtime / 8 MHz build mismatch and select suitable LED-switch parts, actual charger topology/PROG value, and any available 5 V regulator and 3.3 V converter. Then select the two power modules and measure the LED string. The illustrated wiring is concrete at the named-terminal level, but amber modules and Rlim are explicitly not selected parts. This is a review package, not permission to substitute arbitrary modules.

**2N7000 follow-up:** You confirmed this MOSFET separately. It is not selected for the present 200 mA pulse LED driver at battery-level gate drive. See [board/parts assessment](BOARD_AND_PARTS.md) for the datasheet basis and reduced-current alternative.

---

## Addendum - 20-Sep-2026: measured string and direct pin drive

New evidence: [validation/led-string-measurement.md](../validation/led-string-measurement.md).
The user measured the string on a Nordic Power Profiler Kit II through one 47 ohm series
resistor: 18, 24 and 35 mA at 3.40, 3.70 and 4.20 V. That fits I = (V - 2.56 V) / 47 ohm,
so the string is a 2.56 V drop with no significant dynamic resistance in this range, and
the series resistor alone sets the current. The user then chose approximately 15 mA as
the working brightness.

| Finding | Status after this measurement |
|---|---|
| H04 LED string current unknown | **Closed** for this string, at room temperature, 3.4-4.2 V, with R3 fitted. Temperature coefficient, per-branch distribution and the installed cable run remain unmeasured. |
| H07 MOSFET enhancement at 3 V | **Not applicable** to this build. At 15 mA the branch is driven from D9 through R3 with no switching device, so there is no gate to qualify. The finding returns intact if a brighter string is fitted later. |
| All others | Unchanged. H01, H02, H03, H05, H06, H08 to H16 remain open. |

Consequential changes, all reversible:

- R3 is 47 ohm at the board end, 56 ohm if the pin is to stay under 20 mA at full charge.
  Q1, R6, R7 and the LED branch fuse F1 are not fitted. See the Q1 disposition in
  [BOARD_AND_PARTS.md](BOARD_AND_PARTS.md).
- Firmware night duty becomes 100%, because duty is now brightness only: peak current is
  bounded by R3 and the pin, not by the commanded percentage. The Rev 0.4 reasoning for a
  5% hard cap was that the peak was unbounded; that reason is gone, the cap mechanism is
  not. Removing voltage compensation remains right: current now falls with cell voltage by
  construction, from 21 mA at 4.20 V to 11 mA at 3.40 V.
- A short across the outdoor run is bounded to roughly 55 mA by R3 plus the pin's own
  resistance. That is above the 40 mA absolute maximum: bounded, not protected.

Not tested, and not claimed: outdoor temperature behaviour, the installed cable run, the
actual harvest, and everything the Rev 0.4 acceptance gates still require before assembly.
Drawings 02-controller.svg and 04-assembly.svg have not been regenerated and still show
the MOSFET driver.

Update 29-Sep-2026: all seven drawings, including 02-controller.svg and 04-assembly.svg,
have since been regenerated and show D9 driving the string through R3 with no MOSFET.


---

## Addendum - 21-Sep-2026: second board identified as ATmega32U4 (Pro Micro), corrected

**Supersedes the addendum this replaces, filed earlier the same day.** That entry
assumed the "8 MHz" board was a second Pro Mini (ATmega328P). The user's photos show
otherwise: it is silkscreened **"Pro Micro"**, carries an **ATmega32U4-MU**, has a
micro-USB connector, and its 8.000 MHz crystal is genuine - but the pin labels (RAW,
GND, RST, VCC, A3-A0, 15, 14, 16, 10 / TX0, RXI, GND, GND, 2-9) and the MCU itself are
a different chip family from the BTE13-010A, not a same-chip alternative.

| Finding | Status after this |
|---|---|
| H03 16 MHz vs 8 MHz firmware mismatch | **Still open.** This board's clock is genuinely 8 MHz, but it does not satisfy H03's "known 8 MHz board" alternative as simply as a same-chip Pro Mini would, because the firmware is written against ATmega328P registers that do not all exist on ATmega32U4 (below). The BTE13-010A path (convert to internal 8 MHz, or confirm its existing flash is genuinely 8 MHz) remains the closer-to-done route for M2. |
| All others | Unchanged. |

**Concretely, `firmware/lite_controller/src/main.cpp` will not build or run correctly
on this chip as it stands:**

- `PCICR |= _BV(PCIE2); PCMSK2 |= _BV(PCINT18);` and `ISR(PCINT2_vect)` (button wake
  on D2) use the PCINT2/PORTD group. **ATmega32U4 has no PCIE2, PCMSK2, PCINT18 or
  PCINT2_vect** - it has a single pin-change group, PCINT0, covering PB0-PB7 only.
  This alone fails to compile against a 32U4 target without moving the button to a
  PORTB-mapped pin and rewriting the ISR.
- `adcRaw(0)` and `adcRaw(1)` (panel/LDR sense) and `adcRaw(0x0E)` (`readVcc()`,
  internal 1.1 V bandgap read) are ATmega328P ADMUX channel numbers. On ATmega32U4,
  A0-A3 sit on ADC7-ADC4 (not ADC0-ADC3), and the internal bandgap reference needs a
  different MUX value plus the ADCSRB MUX5 bit that this code never sets. Unmodified,
  it would sample the wrong physical pins and return a meaningless "Vcc".
- `DIDR0 = _BV(ADC0D) | _BV(ADC1D)` disables digital buffers on ADC0/ADC1 (PF0/PF1 on
  the 32U4) - pins this board most likely doesn't even route to the header - instead
  of the ones actually in use.
- `TCCR1B` PWM-prescaler poke for D9 (the ~1.96 kHz figure used in the 20-Sep-2026 LED
  measurement) assumes D9 drives Timer1/OC1A, as it does on the 328P. Genuine
  SparkFun Pro Micro pinouts also route D9 to OC1A, so this may carry over, but it is
  **not verified for this specific clone's silkscreen** and should not be assumed.
- `platformio.ini`'s `[env:pro8]` targets `board = pro8MHzatmega328` - the wrong MCU
  entirely; a 32U4-targeted board definition and its native-USB (Caterina-style)
  upload flow would replace the current serial-bootloader-at-57600 profile.

**Net effect:** this board is a real, useful part - genuine 8 MHz, native USB (no
separate FTDI/CH340 adapter needed to program it), a fine controller in its own
right - but it is not a lower-risk swap-in for M2 the way a real Pro Mini/328P at
8 MHz would have been. Using it here means porting the ADC/bandgap channel logic,
the button-wake interrupt and vector, and the PlatformIO board target, then
re-verifying the D9 timer mapping and the ~1.96 kHz PWM figure on the actual chip -
materially more work than the clock-only check a same-family board would need.

**Recommendation:** keep M2 on the ATmega328P path - either the BTE13-010A after
confirming/completing its 8 MHz conversion, or a genuine Pro Mini/328P at 8 MHz if
one turns up - and set the Pro Micro aside as a spare controller for some other
project, unless a firmware port to ATmega32U4 is something you actually want to take
on.

This does not change M1/U0/U3/charging, Q1, the LED drive, or the LDR wiring. See
[BUILD_GUIDE.md](BUILD_GUIDE.md) for the corresponding M2 row.

---

## Addendum - 21-Sep-2026: BTE13-010A fuses set to internal 8 MHz, BOD 2.7 V

Bench result. USBasp on this board failed to initialise ("cannot set sck period" /
"target does not answer") - consistent with old clone firmware, per the known-issues
table in `CLOCK_CONVERSION.md`. Switched to an Arduino as ISP (`stk500v1` at 19200
baud) instead, which worked.

```
avrdude -c stk500v1 -P /dev/cu.usbserial-A98B3PDH -b 19200 -p m328p \
  -U lfuse:w:0xE2:m -U hfuse:w:0xD9:m -U efuse:w:0xFD:m
```

Write and independent read-back both confirmed lfuse 0xE2, hfuse 0xD9, efuse 0xFD -
exactly the pass values `CLOCK_CONVERSION.md` section 9 specifies. hfuse 0xD9 has
BOOTRST=1 (no bootloader, reset vector at 0x0000) and efuse 0xFD sets BOD to 2.7 V, so
this is confirmed as the intended ISP-only, no-bootloader, internal-8-MHz, BOD-2.7-V
configuration - not just "a fuse write happened".

| Finding | Status after this |
|---|---|
| H03 16 MHz vs 8 MHz firmware mismatch | **Fuse portion of the disposition executed** on the BTE13-010A: internal 8 MHz oscillator and BOD 2.7 V are now the chip's actual configuration, signature/fuse-verified. Not yet closed - the clock still needs to be proved in practice (see below), the application firmware still needs to be uploaded via ISP (the old serial bootloader path no longer exists on this chip), and the board's onboard regulator/power LED are still fitted. |
| All others | Unchanged. |

**Consequence: the working 57600-baud serial upload path recorded earlier no longer
applies to this chip.** BOOTRST=1 means there is no bootloader; every future firmware
update goes through ISP (the same wiring just used), not the CH340 serial adapter,
unless a bootloader is deliberately reburned later.

**Still to do, per `CLOCK_CONVERSION.md` section 9 and `BUILD_GUIDE.md`:**

- Build and upload the actual SolarLights Lite firmware (PlatformIO `pro8`
  environment or equivalent MiniCore no-bootloader build) via this same ISP
  connection - fuses alone don't put the application on the chip.
- Cheap independent clock check: a 1000 ms-delay blink, timed against a watch -
  should blink at 1 s, not 2 s.
- Once the project firmware is running: confirm D9 PWM is approximately 1.96 kHz
  (scope or frequency counter).
- Only after that: remove the board's onboard regulator and power LED, per the
  documented order in `CLOCK_CONVERSION.md` ("do the fuse change before removing the
  board's regulator and power LED") - both are still fitted right now.

This does not change M1/U0/U3/charging, Q1, the LED drive, or the LDR wiring.

---

## Addendum - 21-Sep-2026: chip still running pre-conversion firmware

Clarified with the user after an apparent contradiction: a serial monitor session
over the CH340 adapter showed clean "SolarLights Lite" / `t=.../vdd=.../state=.../
pct=` output, which looked like it could mean a serial upload still worked. It does
not. Timeline, confirmed by the user:

- A few days ago: old firmware uploaded to this same Pro Mini via the CH340 adapter,
  through whatever bootloader was on the chip at the time (the user has no other Pro
  Mini board - this is the same physical chip throughout).
- 21-Sep-2026: ISP fuse write (internal 8 MHz / BOD 2.7 V / no bootloader) done on
  this chip via a self-built Arduino Nano as ISP. No firmware upload has happened via
  ISP yet.

**Why the old firmware is still running:** the fuse write never touched flash memory
- only a chip-erase or a flash write does that, and neither has happened. Arduino
bootloader uploads always place the application at 0x0000; the bootloader itself
lived higher in flash and only grabbed the reset vector via BOOTRST. Setting
BOOTRST=1 today made the reset vector point straight at 0x0000 instead of detouring
through the bootloader first - so the same old application, still physically present
from days ago, now just runs directly. The bootloader is bypassed, not erased, and
permanently unreachable now regardless.

**Confirmed practical consequence: the CH340/serial path can upload monitor output
forever (TX/RX only, no bootloader needed) but can never again upload new firmware**
- attempting it reproduces the `stk500_getsync()` failure already seen. All future
firmware changes go through ISP with the Nano-as-ISP programmer, unless a bootloader
is deliberately reburned later (offered to the user, not yet decided).

**The chip has not yet received the current Rev 0.4 firmware.** What is running is
pre-conversion code. The actual ISP upload of the reviewed source is still the next
step:

```
pio run -e pro8_isp -t upload --upload-port /dev/cu.usbserial-XXXX
```

(port specific to the Nano-as-ISP on whichever machine is being used - see
`platformio.ini`).

---

## Addendum - 21-Sep-2026: ISP link recovered after a cold power cycle

After the ISP fuse write, the Nano-as-ISP link to this same chip went from working
(fuse write + independent read-back both clean) to consistently reading
`Device signature = 00 00 00` - reproducible across avrdude re-runs, isolating the
CH340 adapter, re-seating all six ISP wires, and confirming target power with a
meter. None of those fixed it.

What did: a full power-down of the target board (not just avrdude's own reset
toggle) followed by reconnecting. The next attempt read back the correct
`1E 95 0F` signature immediately.

Working theory, not fully confirmed: fuse changes only take effect at the next
reset, so the successful write session ran while the chip was still on its old,
faster clock (the board's original external crystal). Once actually power-cycled
onto the newly active fuses - internal 8 MHz oscillator, SUT `10` ("slowly rising
power", up to a 65 ms startup delay per `CLOCK_CONVERSION.md`) - the target may have
been left in a stale or partially-started state that a simple reset toggle did not
clear, while a genuine cold power-down did. This is offered as the likely
explanation, not a proven root cause; if `00 00 00` recurs after a future power
cycle, that theory would need revisiting rather than assumed.

**Practical takeaway for future sessions: if the ISP link stops answering after a
fuse change, a full power-down/power-up of the target - not just re-running
avrdude - is a cheap first thing to try**, before assuming a wiring fault.

Next step (unchanged from the previous addendum): upload the actual Rev 0.4
firmware via `pio run -e pro8_isp -t upload --upload-port /dev/cu.usbserial-XXXX`.

---

## Addendum - 21-Sep-2026: Rev 0.4 firmware genuinely on the chip; root-caused the upload tool

**Milestone: the actual reviewed Rev 0.4 firmware is now written and verified on the
BTE13-010A**, replacing the pre-conversion code that had been running until this
point. 4250/4250 bytes written and verified clean.

Getting there took one more real fault, separate from the earlier signature-read
issue and its own root cause:

`pio run -e pro8_isp -t upload` reproducibly failed flash verification at the exact
same byte and exact same value on two separate attempts (`0x0006: 0x3e != 0x7e`),
including after cables were swapped for different ones - ruling out a marginal
physical connection, since real electrical noise would not land on the identical
byte twice. Root cause: **PlatformIO's bundled `tool-avrdude` (6.3.0)** has some
incompatibility writing/verifying flash against this ArduinoISP/stk500v1 setup.
Running the identical `.hex` file through the system-installed `avrdude` (8.3)
instead - same port, same protocol, same speed - wrote and verified cleanly, twice:

```
avrdude -c stk500v1 -P /dev/cu.usbserial-XXXX -b 19200 -p m328p -v \
  -U flash:w:.pio/build/pro8_isp/firmware.hex:i
```

`platformio.ini`'s `[env:pro8_isp]` now has an `upload_command` override pointing
plain `pio run -t upload` at the system avrdude instead of the bundled one. This
override has not itself been bench-tested yet - the two-step method above (build
with `pio run -e pro8_isp`, then flash with that explicit avrdude command) is the
one actually proven twice and is the fallback if the override misbehaves.

**Two separate issues now resolved on this chip today, for the record:**
1. Signature read `00 00 00` after the fuse write -> fixed by a full power-cycle of
   the target (previous addendum).
2. Flash write/verify failing under PlatformIO's bundled avrdude -> fixed by using
   the system avrdude directly (this addendum).

**Still open, per the original wiring-order step 4 acceptance gate:** confirm D9 PWM
is approximately 1.96 kHz, and the 1000 ms-blink watch-timed sanity check, before
removing the board's onboard regulator and power LED.

The dated observations above remain evidence only. The machine-independent current procedure is consolidated in [the firmware programming guide](../firmware/lite_controller/PROGRAMMING.md); this file remains the dated, blow-by-blow record.

### Addendum - 21-Sep-2026: USBasp works cleanly on the iMac

On the iMac (`AnthonysiMac5K4`), direct USBasp upload of the same Rev 0.4 firmware succeeded on the first attempt, using the system avrdude (8.3, Homebrew-installed):

```
avrdude -c usbasp -p m328p -v -U flash:w:.pio/build/pro8_isp/firmware.hex:i
```

Signature read correctly (`1E 95 0F`), chip auto-erased, 4250 bytes written and verified in one pass - no SCK-negotiation error, no JP3 jumper needed.

**This does not contradict the earlier USBasp failure** (`cannot set sck period` / `target does not answer`, logged under the MacBook-based troubleshooting earlier today) - that was on a different machine with what appears to be older/clone USBasp firmware not supporting SCK-period negotiation. The USBasp used here on the iMac evidently either has different (newer/compatible) firmware, or the default SCK rate happened to suit this target without negotiation being invoked. The two findings describe two different physical programmers, not a contradiction.

**Practical effect:** the iMac now has a working USBasp path as a simpler alternative to Arduino-as-ISP (no six-wire ISP link to a Nano, no ArduinoISP sketch) - both confirmed independently against the same Rev 0.4 `.hex`, which is good corroborating evidence the build itself is solid. The Arduino-as-ISP method remains the documented fallback if this particular USBasp is ever swapped for a clone with the older firmware.
