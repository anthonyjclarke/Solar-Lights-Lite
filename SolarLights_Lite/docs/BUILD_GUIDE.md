# SolarLights Lite - rebuild guide

v0.5 live project status | 27-Sep-2026 | Active bench development

**Goal: reuse the panel, TP4056 modules, 16 MHz Pro Mini and existing lights; run dimly from dusk to dawn with low standby consumption.** Open `ASSEMBLY.html` for the illustrated guide, or print `../../output/pdf/SolarLights_Rev05_Drawings.pdf` at A3 landscape. Review `VALIDATION.md` first. A checklist version of the parts table below is at [SolarLights_Lite_Parts_List.csv](SolarLights_Lite_Parts_List.csv). For a schematic that matches this document part-for-part, see [../kicad_current/](../kicad_current/README.md) - the KiCad folder in ../kicad/ is the frozen Rev 0.3 audit baseline, not this circuit.

> **Release status (27-Sep-2026):** the design remains a staged bench proposal.
> The direct-drive branch is resistor-limited; its normal dusk-to-dawn command is
> 100% duty, producing about 15 mA at 3.7 V with R3 = 47 ohm. Do not apply the
> historical 5% PWM cap language elsewhere in the archived material to this build.

## Confirmed board and available transistors

Use the photographed **BTE13-010A** after its internal-8-MHz conversion. **2N3904 is selected for Q2**; the supplied TO-92 inventory contains no MOSFETs. Q1 is resolved by removing it: the measured string runs at approximately 15 mA directly from D9 through R3 ([measurement](../validation/led-string-measurement.md)). See [board-specific pin map and inventory assessment](BOARD_AND_PARTS.md). A BC337 LED-driver alternative requires a separate circuit decision.

## Proposed assembly

1. Existing panel -> a qualified 5 V regulator -> protected TP4056 input. The old pair of series diodes is removed as a voltage-limiting scheme. A blocking diode may be required by the chosen regulator's reverse-current specification; it is not the voltage regulator.
2. Two matched 4.2 V-charge Li-ion cells in **1S2P** (parallel, not series), each with a positive-terminal fuse, -> charger B+/B-. All loads use OUT+/OUT-. A main load fuse and service switch feed the protected battery rail.
3. The Pro Mini runs from that rail at a verified 8 MHz after removing its regulator and power LED. Switched LDR -> A1; D9 -> R3 47 ohm -> light string positive, string negative to load GND. R3 sets the current; there is no switching device in this build.
4. During development, an always-on Wemos D1 Mini records the Arduino's own diagnostics and its Wi-Fi/battery health in Home Assistant without an Arduino USB connection. It reuses the fitted Q2/R8/R9/R10 status interface as a protected, inverted serial receiver; no INA226, temperature sensor or other telemetry module is required. The separate D1 Mini low-power profile remains the later production reference.

**Read module pad labels, not board positions.** The illustrations are functional terminal maps, not photographs or universal pin layouts. All seven drawings (01-power through 07-current-architecture) were regenerated on 29-Sep-2026 and show the 20-Sep-2026 direct-drive change; if you have an older cached copy open, re-export ASSEMBLY.html or the PDF. If a switching device is reintroduced for a brighter string, its pin order must come from the exact part/package datasheet.

## Parts and selection gates

| Ref | Part / starting value | Selection or qualification |
|---|---|---|
| PV1 | Existing AS102-0712A 1.2 W panel | Confirm polarity, wiring condition and actual Voc; retain initially. |
| U0 | 5 V input regulator - candidate: MP1584EN adjustable buck module (in hand), trimmed to 5 V | Rated above measured cold Voc with margin (target at least 12 V input capability; MP1584EN covers 28 V), output bounded to the selected charger's permitted range across no-load/startup; low input quiescent current; weak-light recovery. **Not** the AMS1117 LDO board also in the kit - a linear regulator wastes ~30% of the panel's tiny budget as heat and drops out of regulation in low light. **Not** the TPS63802/HL802A breakout either - its 5.5 V input ceiling is under the panel's 7.6 V Voc. Candidate accepted 21-Sep-2026, not yet bench-qualified - trim to exactly 5 V and check for night-time reverse leakage before wiring to M1. See [board/parts assessment](BOARD_AND_PARTS.md). |
| M1 | Protected TP4056-family module | Six labelled terminals, identified chip, documented ground topology, adjustable PROG, verified 4.2 V charge voltage. Start 100-150 mA only after verifying programming law. |
| BT1/2 | Matched 18650 pair | Same type, age, chemistry, capacity and state of charge; inspect sleeves/positive insulators. Prefer a preassembled protected 1S2P pack if cell condition is uncertain. Do not solder directly to bare cell cans. |
| FB1/2 | 1 A branch fuses, provisional | At each holder positive, before parallel junction. Check normal inrush, wire/holder ratings and fuse breaking capability. A single downstream fuse cannot interrupt one cell feeding a fault in the other. |
| F2 / S1 | 1 A main fuse / service switch | Fuse after OUT+; switch in series to system rail. Values provisional against actual current and wiring. |
| M2 | Existing 16 MHz Pro Mini (BTE13-010A). A second board found 21-Sep-2026 turned out to be an ATmega32U4 **Pro Micro**, not a Pro Mini - see below, not a drop-in for M2. | Verify ATmega328P marking, remove power LED and onboard regulator, feed from U0/U3's regulated rail, do not use RAW. Convert to internal 8 MHz via ISP, or confirm its existing flash is genuinely running at 8 MHz. See [board/parts assessment](BOARD_AND_PARTS.md). |
| Q1 | Not fitted | Measured string draws approximately 15 mA at 3.7 V through R3, inside the pin rating. See [Q1 disposition](BOARD_AND_PARTS.md). A brighter string reinstates Q1, R6, R7 and F1 together. |
| R6 / R7 | Not fitted | Gate series/pull-down exist only for a MOSFET. With no switch, the pin is low at reset and high-impedance while unpowered, so the string is dark. |
| R3 | 47 ohm, 1/4 W, at the board end | From the measured string: I = (VBAT - 2.56 V) / (R3 + approximately 30 ohm pin resistance). 21/15/11 mA at 4.20/3.70/3.40 V. Fit 56 ohm if you prefer the pin to stay under 20 mA at full charge. Dissipation is under 25 mW. Parallel bare LEDs still require branch ballast, not one common resistor. |
| F1 | Not fitted in the LED branch | The branch is no longer fed from the battery rail; its fault current is bounded by R3 and the pin. The main fuse F2 on OUT+ is unchanged. |
| C3 / C4 | 100 uF / 100 nF across M2 rail | Positive to protected VBAT; at least 6.3 V rating, 10 V preferred for electrolytics. Keep close to controller/driver. |
| LDR1 / R4 | Existing LDR / 100k | D7 -> LDR -> A1 -> R4 -> load GND. Shade from LEDs; weatherproof without obscuring ambient light. |
| SW1 | Momentary normally-open button | D2 to load GND. 60-second test obeys the same 100% direct-drive brightness setting and LVC. |
| U3 | Low-Iq 3.3 V buck-boost - candidate: TPS63802/HL802A breakout (in hand, qty 2), jumper set to 3.3 V | Supplies either D1 profile from the protected rail. Verify 3.0-4.2 V input operation, radio bursts, output stability and reverse-current behaviour. Target >=500 mA transient support and measured total standby <=0.5 mA only applies to the later low-power profile. |
| M3 | Existing Wemos D1 Mini | Use the existing `solar-lights-lite.yaml` for the later hourly deep-sleep profile and `solar-lights-lite-dev-d1.yaml` while testing. In the test profile, D6 receives inverted Arduino diagnostics through Q2; D5 and D8 are left open. |
| C2 | 470 uF / 10 V at U3 input | Observe polarity and the selected converter's required output capacitors. Required for either battery-powered D1 profile. |
| R5 | 220k to D1 Mini A0 | Assumes onboard 220k/100k divider; verify clone. At 4.2 V: ADC core ~0.778 V, A0 header ~2.489 V. Nominal overall gain 5.4; recalibrate it against a meter. |
| Q2 / R8 / R9 / R10 | 2N3904 NPN; 47k / 100k / 10k | **Development profile:** Arduino D1/TX -> R8 -> base; R9 base-emitter; emitter OUT-; collector -> D6 with R10 pull-up to ESP 3V3. This inverts and level-shifts the UART. **Production profile:** restore the original D8 status -> D5 wiring if desired. Verify actual E/B/C pin order. |
| Enclosure | Glands, standoffs, insulated cell holder | Keep cells shaded and separated from charger/resistor heat. Antenna clear of cells, wires and metal. Allow inspection and strain relief. |

**Not fitted:** old panel divider R1/R2/C1, CHRG diode D3 and its former D6 input,
and D10/D11 mode jumpers. The v0.5 development UART is the only D6 connection:
Q2 collector to D1 Mini D6. Reference designators intentionally follow the earlier
build where possible.

## Firmware programming status

The BTE13-010A is confirmed at internal 8 MHz with BOD 2.7 V and no bootloader. Application uploads therefore use ISP; the UART adapter is monitoring-only. All current compile, USBasp, Arduino-as-ISP and 9600-baud diagnostic instructions are consolidated in [the firmware programming guide](../firmware/lite_controller/PROGRAMMING.md). Dated serial-bootloader and machine-specific experiments remain under `validation/` as evidence, not procedure.

## Second board identified as a Pro Micro (ATmega32U4), 21-Sep-2026

The "8 MHz" board found in the kit turned out, from photos, to be silkscreened
**Pro Micro** with an **ATmega32U4-MU** - a genuinely different chip family, not a
second Pro Mini. It does not satisfy H03 as simply as a same-chip 8 MHz Pro Mini
would: `firmware/lite_controller/src/main.cpp` pokes ATmega328P-specific registers
that do not exist on the 32U4 (the PCINT2/D2 button-wake interrupt, in particular,
would not compile - the 32U4 only has one pin-change group, limited to PORTB), and
its ADC channel numbers and internal-bandgap read would sample the wrong pins on
this chip. Full detail and the exact lines involved are in the dated addendum in
`VALIDATION.md`. Using this board for M2 would mean porting that logic and the
PlatformIO board target to ATmega32U4, not just verifying a clock and a pinout.

**M2 stays on the ATmega328P path** - the confirmed internal-8-MHz BTE13-010A.
The Pro Micro is a genuinely useful board (native USB,
no separate FTDI adapter needed to program it) but is better kept as a spare for a
future project than adopted here.

## Controller preparation and servicing

The one-time clock/fuse conversion is complete and must not be repeated during routine updates; [CLOCK_CONVERSION.md](CLOCK_CONVERSION.md) now records status only. Remove or isolate the onboard regulator and power LED/resistor, preserve local decoupling, feed protected battery voltage to VCC and leave RAW disconnected. Verify D9 PWM is approximately 1.96 kHz during a partial-duty test. For every subsequent firmware build, upload, verification and serial-monitor session, follow [PROGRAMMING.md](../firmware/lite_controller/PROGRAMMING.md).

## Wiring order and acceptance gates

| Step | Work with power removed unless stated | Pass before proceeding |
|---|---|---|
| 1 | Photograph/label M1 pads; inspect traces and continuity with cells/panel removed. | Identify B+, B-, OUT+, OUT-, IN+, IN-. B- and OUT- are protection-separated; a conductive MOSFET path when powered is not proof they are the same net. If unsure, obtain actual board schematic. |
| 2 | Qualify U0 separately on a current-limited source emulating the panel. | 5 V output within charger specification at load/no-load, startup and maximum panel voltage. Test low-current source limits/cloud transitions. Do not use cells for this test. |
| 3 | Identify PROG and set conservative charge current. Test charger with a suitable battery simulator or supervised known cell. | Correct charge voltage/current, thermal behaviour and termination. Do not assume CHRG LED proves termination or net charging. |
| 4 | Program M2 using the canonical firmware procedure and add C3/C4. Use a 3.8 V current-limited bench supply for functional testing after the programmer is removed. | Battery estimate within +/-0.05 V after calibration; supply sweep 3.3-4.2 V; sleep target <=20 uA excluding regulator/other boards. |
| 5 | Add R3 from D9 to the string, string return to load GND. No Q1, R6, R7 or F1. | Measure string current at 3.40, 3.70 and 4.20 V at 100% duty on a current-limited supply: expect approximately 11, 15 and 21 mA with 47 ohm. Anything above 22 mA at 4.20 V means fit 56 ohm. Pin and resistor cool. Lights dark with M2 unplugged and at reset. |
| 6 | Fit switched LDR and test button. | Cover/uncover: transition after 5-minute persistence; threshold gap prevents flicker. Lights remain on throughout the night. Button never exceeds cap. |
| 7 | Sweep supply below 3.30 V for >30 s. | LED turns fully off when LVC confirms; button cannot relight; battery recovery alone in darkness does not relight; daylight + >3.60 V restores operation. Hardware protection remains a separate test. |
| 8 | Assemble fused pack using suitably matched/charged cells; connect pack to M1, then loads. | Never parallel unequal/unknown cells directly. Voltage equality alone does not establish health or safe equalisation current. Do not short the pack to test protection; use a current-limited simulator/load. |
| 9 | Add the always-on D1 Mini test telemetry before final assembly. Flash `firmware/esphome/solar-lights-lite-dev-d1.yaml`; flash M2 with `pio run -e pro8_debug`. | D1 stays online with Wi-Fi/HA absent; it receives a complete Arduino line at least every 60 s when stable; no Arduino USB-UART adapter is attached. Q2's emitter connects only to OUT- / GND_LOAD. |
| 10 | Compare the D1 A0 battery voltage and parsed Arduino VDD with a meter at 3.30, 3.70 and 4.20 V. | Both values are within the stated calibration accuracy. A known light test reports `output=100%`; the D1 reports it as `Arduino Lights Commanded`. The TP4056 CHRG LED is not a current measurement. |
| 11 | Run Wi-Fi unavailable, HA unavailable and OTA tests. | D1 remains running and retains serial diagnostics while services are unavailable; no brownout loop. It reconnects after an AP/HA restart and accepts an OTA update without losing the Arduino UART interface. |
| 12 | Complete real-sun/shade tests with the qualified panel path. | Charge termination with telemetry attached; automatic weak-light recovery; acceptable cell and component temperatures. Qualify cell-temperature inhibit before unattended installation. |
| 13 | Log at least 14 days including overcast weather, then actual winter. | Record daily charge/load mAh or Wh, dusk/dawn voltages, light usefulness, temperatures and LVC events. No promise of year-round operation from a short sunny test. |

For bench debugging build `pio run -e pro8_debug`. Each reset prints a one-time field guide before the rate-limited 9600-baud data. The D1 development image receives that data through its protected software UART and publishes the raw line plus parsed values to Home Assistant. Build `pio run -e pro8` for final controller sleep-current tests; it intentionally emits no serial telemetry. Do not use `pio -t upload`: flashing is performed separately with a current system `avrdude`. Exact operating-system setup, commands and isolation rules are only in [PROGRAMMING.md](../firmware/lite_controller/PROGRAMMING.md).

## Development telemetry station (Wemos D1 Mini)

`firmware/esphome/solar-lights-lite-dev-d1.yaml` is the maximum capability available
from the existing D1 Mini and fitted resistor/transistor interface. It replaces the
USB serial monitor with Home Assistant entities while the D1 stays awake to hear every
Arduino diagnostic line. It is deliberately excluded from the final battery budget
and must not be mistaken for an outdoor/runtime configuration. The existing
`firmware/esphome/solar-lights-lite.yaml` remains the D1 Mini hourly deep-sleep
reference for the later low-power design.

Secrets, flashing, checks and the dashboard import are covered step by step in
[DEVELOPMENT.md](DEVELOPMENT.md#esphome-development-telemetry-d1-mini).

### Development wiring

1. Keep D1 Mini **GND** on TP4056 **OUT- / GND_LOAD** and power it through the
   qualified U3 3.3 V supply, as in the retained production profile. Do not use B-.
2. Reuse the existing Q2 interface, but move its input from M2 D8 to M2 **D1/TX**
   and move its collector from D1 Mini D5 to **D6**. The final wiring is:
   `M2 D1/TX -> R8 47k -> Q2 base`; `R9 100k base -> OUT-`; `Q2 emitter -> OUT-`;
   `Q2 collector -> D6`; `R10 10k from collector -> ESP 3V3`.
3. Do not connect D1 Mini TX to M2. Q2 makes the receive path safe for the D1's
   3.3 V GPIO and inverts it; the development YAML declares D6 as an inverted,
   9600-baud software UART. Leave D5 and M2 D8 open in this profile.
4. Retain the existing A0 battery divider: `VBAT_SYS -> R5 220k -> A0`. Check the
   D1 clone's onboard divider before trusting the 5.21 multiplier. There is no safe
   additional panel, current, energy or temperature measurement without more hardware.

The configuration publishes the raw Arduino line and its scheduler time, VDD,
LDR ratio/raw/voltage, output duty, LVC progress, test time, battery band,
light sense, scheduler mode, night flag, output cause and transition state. It
also publishes D1 reset cause, heap/fragmentation, Wi-Fi identity/signal and uptime.
These show whether a controller event was real, whether the telemetry unit itself is
healthy, and whether a missing report is an Arduino or network issue.

This no-purchase profile cannot measure charge current, harvested energy, panel
voltage or physical LED current; it reports the controller's command/state, not a
replacement for a current meter. Its useful cross-check is D1 A0 battery voltage
versus Arduino VDD. Record meter values at 3.30, 3.70 and 4.20 V and adjust the
D1 multiplier accordingly.

## Energy budget you can verify

Use battery-side measured currents. Let D be PWM duty fraction, Ipk the maximum string pulse current, H the dark hours, Ictl the controller average while lit, Is the aggregate standby current, N wakes/day, Iw the average **battery-side** wake current and tw seconds/wake:

`Daily use ~= Ipk * D * H + Ictl * H + Is * (24-H) + N * Iw * tw / 3600 + other continuously powered loads`

Avoid counting the same telemetry sleep current twice. The worked table below separately budgets controller and telemetry. These are scenarios, not measured predictions.

Pre-measurement scenarios, kept for the record. They assumed an unbounded 200 mA peak,
which the 20-Sep-2026 measurement replaced; see the measured-string table below.

| Assumption at 14 dark hours | Proposed 5% command | 10% command | Old 100% lighting |
|---|---:|---:|---:|
| LED peak <=200 mA; actual PWM 12/255 or 25/255 | <=132 mAh | <=275 mAh | 2,800 mAh |
| Controller: 1 mA lit + 0.01 mA for 10 h | 14.1 mAh | 14.1 mAh | Not assumed |
| Telemetry: 24 x 15 s x 80 mA battery-side | 8.0 mAh | 8.0 mAh | Original YAML ~101 mAh awake alone |
| Telemetry sleep/converter: 0.2 mA x ~23.9 h | 4.8 mAh | 4.8 mAh | Board-dependent |
| Other standby allowance | 1.0 mAh | 1.0 mAh | Board-dependent |
| **Illustrative total** | **~160 mAh/day** | **~302 mAh/day** | **>2,800 mAh/day** |

### Measured-string scenario, 20-Sep-2026

With R3 fitted, duty no longer bounds current: the resistor does, and 100% duty is the
measured 15 mA at 3.7 V. Fourteen dark hours, same controller and telemetry rows:

| Item | 100% duty, 15 mA | 50% duty |
|---|---:|---:|
| LED branch: 15 mA x 14 h (falls with cell voltage) | 210 mAh | 105 mAh |
| Controller: 1 mA lit + 0.01 mA for 10 h | 14.1 mAh | 14.1 mAh |
| Telemetry: 24 x 15 s x 80 mA battery-side | 8.0 mAh | 8.0 mAh |
| Telemetry sleep/converter: 0.2 mA x ~23.9 h | 4.8 mAh | 4.8 mAh |
| Other standby allowance | 1.0 mAh | 1.0 mAh |
| **Illustrative total** | **~238 mAh/day** | **~133 mAh/day** |

Against the retained-charger scenarios below, 238 mAh/day needs about 3 h of equivalent
full sun at a 100 mA charge setting, or 2 h at 150 mA. That is a scenario built on one
bench measurement and an assumed charge current, not a measured harvest. The 14-day and
winter logging in step 12 is still what decides it.

If sleep consumption is 2 mA instead of 0.2 mA, add about 43 mAh/day. At 45 s per 80 mA wake, wake use is 24 mAh/day instead of 8. At 16 dark hours, LED use at 5% becomes 151 mAh plus controller/telemetry. Firmware caps duty; it cannot cap current without a current sensor.

Retained linear charger scenarios at an ASSUMED 2.5 equivalent full-sun hours and 0.8 daily derating: 100 mA -> 200 mAh/day; 150 mA -> 300 mAh/day; half the actual collected energy ->100/150 mAh/day. These numbers are not a Sydney weather prediction. Input conditioning, charge-current settings, panel I-V curve, shading, thermal limits and full-battery taper determine actual harvest. Never multiply solar-panel watts by hours and divide by battery voltage without modelling the linear-charger losses.

At 5%, the illustrative break-even sun requirement is 160/(100*0.8)=2 h or 160/(150*0.8)=1.33 h. A larger battery helps cloudy-day autonomy but cannot repair a persistent energy deficit. Autonomy = measured usable capacity / measured daily draw; account for cutoff, ageing and temperature. Partial opaque masking of series cells is not a valid linear winter simulator.

## Practical PCB option after bench validation

Start with a two-layer **module carrier**: sockets for the converted Pro Mini and D1 Mini, screw terminals, labelled protected rails, through-hole resistor/capacitor pads, keyed module connectors, fuse holders, MOSFET breakout footprint and test points. This preserves parts-bin assembly and allows replacing an uncertain charger/regulator module. Place fuses at the holder, keep high-current return paths away from ADC ground, and keep the ESP antenna at the carrier edge with copper/module clearance specified by the actual board.

Freeze exact module dimensions, pin maps, transistor pinouts, fuse/wire ratings and enclosure first. Then create footprints, ERC/DRC-clean schematic/layout, dimensioned assembly drawing, BOM, Gerbers and drill files. No fabrication files are released by this review: the legacy KiCad is not a PCB design.

A later integrated board could use a charger with input regulation, power-path management and cell-temperature sensing. [TI BQ24074](https://www.ti.com/product/BQ24074) and [Microchip MCP73871 load-sharing guidance](https://www.microchip.com/en-us/application-notes/an1260) illustrate the architecture. A power-path output may differ from battery voltage, so VCC-based battery sensing must be redesigned. These devices are not pin-for-pin TP4056 substitutions; fine-pitch packages are less convenient for first-time hand assembly.

**2N7000 follow-up:** You confirmed this MOSFET separately. It is not selected for the present 200 mA pulse LED driver at battery-level gate drive. See [board/parts assessment](BOARD_AND_PARTS.md) for the datasheet basis and reduced-current alternative.
