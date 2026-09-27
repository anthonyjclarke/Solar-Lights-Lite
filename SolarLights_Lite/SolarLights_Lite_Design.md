> **SUPERSEDED - v0.5 retains the electrical review and adds test-only D1 Mini UART telemetry. Do not assemble from this historical design. See [current build guide](docs/BUILD_GUIDE.md) and [validation report](docs/VALIDATION.md).**

# SolarLights Lite – Parts-Bin Design & Build

Rev 0.2 · 17-Sep-2026 · home-built companion to SolarLights v2 (v2 is unchanged)

Rev 0.2: staged panel plan – build and test on the existing 1.2 W panel, then upgrade the panel only if the winter results call for it.

---

## 1. Overview

Lite keeps what matters from v2 and builds it on perfboard from parts you already have. It's built in two stages:

| Stage | Panel                            | Lights                                 | Buy        |
|:-----:|----------------------------------|----------------------------------------|------------|
|   1   | Existing AS102-0712A 1.2 W (7 V) | 20 % cap, evening only (dusk → ~22:30) | Nothing    |
|   2   | New 6 V 5 W panel (§8)           | Full levels 8–60 %, evening + pre-dawn | Panel only |

Stage 1 is energy-neutral all year but dim in winter. Move to Stage 2 when the field tests in §7 say so – the panel is a straight swap plus one firmware setting.

| Feature                                         | v2 PCB |         Lite        |
|-------------------------------------------------|:------:|:-------------------:|
| Energy-positive in winter                       |   ✓    | ✓ (Stage 1 at 20 %) |
| Dusk/dawn from panel voltage, hysteresis        |   ✓    |          ✓          |
| Evening + pre-dawn schedule (solar midnight)    |   ✓    |          ✓          |
| Battery-aware brightness, fades, 3.30 V cut-off |   ✓    |          ✓          |
| Lights run with WiFi/HA down                    |   ✓    |          ✓          |
| HA: battery V/%                                 |   ✓    |          ✓          |
| HA: lights on, charging                         |   ✓    |          ✓          |
| HA: panel V, temperature, light level           |   ✓    |          –          |
| MPPT charger                                    |   ✓    |          –          |
| Temperature charge inhibit                      |   ✓    |          –          |
| Custom PCB / SMD soldering                      |  Yes   |          No         |

Design choices, driven by what you have:

| Block       | Lite choice                                | Why                                                  |
|-------------|--------------------------------------------|------------------------------------------------------|
| Charger     | Your TP4056 + DW01A board, 2 series diodes | Already built; diodes keep a cold panel under 8 V    |
| Controller  | Arduino Pro Mini 3.3 V, modified           | Familiar Arduino tooling; µA sleep once modified     |
| Light sense | Panel divider on A0 (LDR option on A1)     | Your LDR idea kept as a switchable option            |
| LED switch  | Logic-level N-MOSFET from the parts box    | Replaces the two 2N2222s; fully on at 3 V gate drive |
| Telemetry   | Your Wemos D1 Mini, hourly deep sleep      | Same HA device you have now, far shorter wakes       |

---

## 2. Parts

### 2.1 From the parts box

| Ref     | Part                                                | Qty | Notes                                               |
|---------|-----------------------------------------------------|----:|-----------------------------------------------------|
| PV      | Solar panel AS102-0712A 1.2 W (Vmp 7 V, Isc 0.19 A) |   1 | Existing panel – Stage 1                            |
| M1      | TP4056 module with DW01A/8205A (6-pad)              |   1 | The board you have now                              |
| M2      | Arduino Pro Mini **3.3 V / 8 MHz**                  |   1 | 5 V/16 MHz version is not suitable on a Li-ion cell |
| M3      | Wemos D1 Mini                                       |   1 | Existing unit                                       |
| Q1      | Logic-level N-FET: IRLZ44N, IRLB8721, AO3400        |   1 | **Not** 2N7000/BS170 (≈1 V drop at 200 mA)          |
| D1 D2   | 1N4001 (or 1N5819 + 1N4001, or 1N5408)              |   2 | Series in PV+; see §3.1                             |
| D3      | BAT43 / BAT85 / 1N5819 Schottky                     |   1 | CHRG sense isolation                                |
| R1      | 1M                                                  |   1 | Panel divider top                                   |
| R2      | 330k                                                |   1 | Panel divider bottom                                |
| R3      | LED current limit, ≥ 1 W                            |   1 | From string test; 0 Ω if the string has resistors   |
| R4      | 100k                                                |   1 | LDR option                                          |
| R5      | 220k                                                |   1 | D1 Mini A0 (reuse existing)                         |
| R6      | 100 Ω                                               |   1 | MOSFET gate                                         |
| R7 R8   | 100k                                                |   2 | Gate pull-down; status divider top                  |
| R9      | 220k                                                |   1 | Status divider bottom                               |
| C1      | 100 nF                                              |   1 | A0 filter                                           |
| C2      | 470–1000 µF 10 V electrolytic                       |   1 | D1 Mini 5V pin (WiFi bursts)                        |
| C3      | 100 µF 10 V electrolytic                            |   1 | Across battery rail near the MOSFET                 |
| F1      | 0.5 A fuse (glass + holder, or PTC)                 |   1 | LED output                                          |
| F2      | 3 A inline fuse                                     |   1 | TP4056 OUT+ → battery rail                          |
| LDR     | Your LDR (optional)                                 |   1 | Only if `SENSOR_LDR 1`                              |
| SW1     | Momentary push button                               |   1 | Test / install                                      |
| JP1 JP2 | 2-pin header + jumper caps                          |   2 | Mode selection                                      |
| BT      | 2 × 18650 + parallel holder                         |   1 | Matched cells                                       |
| –       | Perfboard ~90 × 70 mm, screw terminals ×2, headers  |   – | Pro Mini and D1 Mini on female headers              |
| –       | 3.3 V FTDI/CP2102 adapter                           |   1 | Programming the Pro Mini                            |

### 2.2 To buy

| Item                         | Example                                  | When    | Notes                            |
|------------------------------|------------------------------------------|---------|----------------------------------|
| 18650 cells (if not on hand) | Samsung INR18650-35E pair                | Stage 1 | Genuine, matched                 |
| IP65 box + 2 × M16 glands    | Jaycar/Altronics                         | Stage 1 | Keep out of afternoon sun        |
| Solar panel                  | Waveshare Solar Panel (6V 5W), SKU 16158 | Stage 2 | Only if §7 tests say so – see §8 |

Vendor links are in `../SolarLights_v2/SolarLights_v2_Parts_and_Vendors.md`.

### 2.3 Files in this package

| File                                         | Content                                                              |
|----------------------------------------------|----------------------------------------------------------------------|
| `SolarLights_Lite_Design.md`                 | This document                                                        |
| `SolarLights_Lite_Build.html`                | Schematic, wiring diagram, pin maps, build order (open in a browser) |
| `kicad/SolarLights_Lite.kicad_sch`           | KiCad 7+ schematic – 29 parts, 25 nets, fully wired (Rev 0.3)        |
| `kicad/SolarLights_Lite.kicad_sym`           | Symbols for the TP4056 board, Pro Mini, D1 Mini and LDR              |
| `kicad/SolarLights_Lite.net`                 | Netlist export (checked net-by-net against the design)               |
| `kicad/SolarLights_Lite_Wiring.kicad_sch`    | Same circuit, drawn as the block wiring view (Rev 0.3w) – the KiCad source behind `images/SolarLights_Lite_Wiring.png` |
| `kicad/SolarLights_Lite_Wiring.net`          | Netlist of the wiring view – identical 25 nets                       |
| `kicad/tools/gen_lite_sch.py`, `gen_lite_wiring_sch.py` | Scripts that generate the two sheets                       |
| `images/SolarLights_Lite_Schematic.pdf/.png` | Printable schematic sheet (A3)                                       |
| `images/SolarLights_Lite_Wiring.svg/.png`    | Block wiring picture – every component and connection                |
| `images/SolarLights_Lite_Wiring_Sheet.pdf/.png` | The wiring view printed from KiCad (A3)                            |
| `firmware/lite_controller/`                  | Pro Mini project (`PANEL_STAGE`, `SENSOR_LDR`, host test)            |
| `firmware/esphome/solar-lights-lite.yaml`    | D1 Mini ESPHome config                                               |

Open the schematic with **KiCad 8 or 9**: `File → Open…` → `kicad/SolarLights_Lite.kicad_sch`. It upgrades on first save, and the project symbol library registers itself through `sym-lib-table`.

There are two sheets of the same circuit, and both export the same 25 nets, so either can be the one you carry into a PCB:

- `SolarLights_Lite.kicad_sch` – the engineering sheet, energy flowing left to right.
- `SolarLights_Lite_Wiring.kicad_sch` – the wiring view: modules sit where they do in `images/SolarLights_Lite_Wiring.png`, with the OUT+ battery rail and OUT− ground rail drawn as the two vertical buses down the middle. Use this one when you are wiring the box and want the drawing to match what is in front of you.

(The PNG itself is a picture – it holds no netlist, so the wiring view was redrawn as real KiCad symbols and wires rather than traced from the image.)

The sheet is drawn to follow the energy, left to right:

| Block | Reads                                                                    |
|:-----:|--------------------------------------------------------------------------|
| 1     | Panel → blocking diodes → TP4056 → cells, with the sense divider tapping PV+ |
| 2     | The protected battery rail runs across the top; every load taps off it   |
| 3     | LED driver: fuse, Rlim, string, MOSFET to ground                         |
| 4     | Pro Mini: sense and mode inputs on the left, outputs fanning out right   |
| 5     | D1 Mini: rail, battery divider, lights and charge inputs                 |

Everything is drawn with real wires, junction dots and GND symbols – the only net labels are the optional `LDR_PWR` / `LDR_SENSE` pair. Each of the 25 nets was checked pin-by-pin against the design after export.

---

## 3. Circuit

### 3.1 Panel & charging

```
Panel + ──┬── D1 1N4001 ── D2 1N4001 ──► TP4056 IN+
          │
          └── R1 1M ──┬── Pro Mini A0
                      ├── R2 330k ── GND
                      └── C1 100 nF ── GND
Panel − ─────────────────────────────► TP4056 IN−
```

- **Why the diodes:** the TP4056's absolute max is 8 V. The existing panel's Voc is 7.6 V (the new one 7.2 V ± 5 %), and Voc rises on cold, bright mornings. Two diodes at open circuit drop ~1 V, holding IN+ ≤ ~7 V. They also block reverse leakage at night.
- **Harvest cost:** almost none. A linear charger pulls the panel down to about VBAT + dropout, so the panel runs at its current limit whether or not the diodes are there: ~0.19 A for the existing panel, ~0.85 A for the 6 V 5 W. Near full charge the extra 1.6–1.8 V drop trims the current slightly.
- **Heat:** negligible on the existing panel (~0.15 W per diode). With the 5 W panel it's ~0.75 W per 1N4001 at 0.85 A. Leave long leads, or use 1N5408s (3 A), or 1N5819 + 1N4001 (less drop).
- **Divider tap:** R1 connects to panel + *before* the diodes, so the reading is true panel voltage and draws nothing from the battery.
- **TP4056 heat:** the module dissipates well under 1 W because the panel sits near battery voltage. Mount it where air moves, not against the lid.

### 3.2 Cells & rails

```
TP4056 B+ ── 2 × 18650 (+ in parallel)      TP4056 B− ── 2 × 18650 (−)
TP4056 OUT+ ── F2 3 A ── BATTERY RAIL (perfboard bus)
TP4056 OUT− ──────────── GND RAIL (perfboard bus)
```

- **All loads on OUT+/OUT−**, so the DW01A over-discharge and short protection covers them. Firmware cuts the lights at 3.30 V long before the DW01A's ~2.4 V trip.
- **Cells:** match them to within 0.05 V before joining in parallel.

### 3.3 Arduino Pro Mini (lights controller)

| Mod       | How                                                         | Result                        |
|-----------|-------------------------------------------------------------|-------------------------------|
| Power LED | Remove the LED or its resistor                              | Saves ~1–3 mA                 |
| Regulator | Remove it (or lift its output pin); feed battery to **VCC** | Saves its quiescent current   |
| Brown-out | Stock 3.3 V bootloader fuses set BOD 2.7 V – leave as is    | Clean reset on a dead battery |

- **Sleep current:** ~5–10 µA with the watchdog running.
- **While lit:** ~1 mA in IDLE sleep, because the PWM timer must keep running. That's ~6 mAh a night, about 1 % of the LED load.
- **Supply range:** the ATmega328P at 8 MHz runs from 2.7–5.5 V, so a 3.0–4.2 V cell is well inside it.
- **Battery voltage:** measured against the internal 1.1 V bandgap, so no divider is needed. Calibrate `BANDGAP_V` once with a multimeter.

### 3.4 Light sensing – panel (default) or LDR

| Option               | Wiring                     |   Idle current | Pros / cons                                       |
|----------------------|----------------------------|---------------:|---------------------------------------------------|
| Panel (default)      | R1/R2 on A0                | 0 (from panel) | Weatherproof, can't see its own lights            |
| LDR (`SENSOR_LDR 1`) | D7 → LDR → A1 → 100k → GND |     0 (D7 off) | Your original idea; needs shading from the string |

The LDR version fixes the weaknesses of the old transistor circuit:
- **Switched divider:** D7 powers the divider only for ~5 ms per reading, so there's no 2 mA standing current.
- **Hysteresis and debounce:** the switching thresholds (`LDR_DARK` 0.30 / `LDR_LIGHT` 0.60) and a 5-minute debounce in firmware stop flicker at dusk.
- **Clean switching:** the MOSFET switches hard, so there's no linear region and no heat.

### 3.5 LED driver

```
BATTERY RAIL ── F1 0.5 A ── R3 Rlim ──► LED string + ── string ── LED string − ──► Q1 drain
Pro Mini D9 ── R6 100 Ω ──► Q1 gate ── R7 100k ── GND           Q1 source ── GND
C3 100 µF across rail/GND near Q1
```

- **PWM:** D9 (Timer1) is set to ~1.96 kHz – no visible flicker, even on camera.
- **Brightness:** chosen at dusk from battery voltage – 60 / 45 / 30 / 15 / 8 %. Stage 1 caps this at 20 %. Compensation keeps it steady as the battery sags (`LED_VF`).

### 3.6 Wemos D1 Mini (reporting only)

```
BATTERY RAIL ──► D1 5V (C2 470 µF to GND)      GND RAIL ──► D1 G
BATTERY RAIL ── R5 220k ──► D1 A0             D1 D0 ── link ── D1 RST
Pro Mini D8 ── R8 100k ──┬──► D1 D5           TP4056 CHRG (pin 7) ◄── D3 cathode
                         R9 220k ── GND       D3 anode ──► D1 D6 (internal pull-up)
```

- **Lights-on signal:** Pro Mini D8 reaches the D1's D5 at ≤ 2.9 V through the divider, drawing current only while lit.
- **Charging signal:** D3 stops the TP4056's LED supply (up to panel voltage) feeding back into D6. While charging, CHRG pulls D6 low.
- **Current:** wakes hourly for ~15 s. Clone D1 Minis sleep at roughly 0.08–0.3 mA – measure yours. A board drawing more than 0.5 mA is worth swapping.

### 3.7 Perfboard layout

- **Bus strips:** run the battery and GND rails as two long strips down the board centre, charger at one end.
- **Loads:** put the MOSFET, fuse, Rlim and screw terminal together at the LED end.
- **Modules:** mount the Pro Mini and D1 Mini on female headers so they can be removed for programming. Leave the Pro Mini's FTDI header reachable.
- **Heat:** keep the diodes and TP4056 away from the cells.

---

## 4. Energy budget*

| Item (mAh/day)                           | Stage 1<br>June | Stage 2<br>June | Stage 2<br>Dec |
|------------------------------------------|----------------:|----------------:|---------------:|
| LED string (host sim)                    |             203 |             540 |            275 |
| Pro Mini (~1 mA while lit, µA otherwise) |               5 |               6 |              3 |
| D1 Mini (24 × 15 s × 75 mA + sleep)      |              15 |              15 |             15 |
| TP4056/DW01A standby, dividers           |             < 1 |             < 1 |            < 1 |
| **Total use**                            |       **≈ 225** |       **≈ 560** |      **≈ 295** |

| Panel (TP4056)           | Harvest June<br>mAh/day | Stage 1 use | Stage 2 use |
|--------------------------|------------------------:|------------:|------------:|
| Existing 1.2 W           |                     380 |        59 % |       147 % |
| Existing 1.2 W, shaded ½ |                     190 |       118 % |           – |
| 6 V 5 W                  |                   1,700 |           – |        33 % |
| 6 V 5 W, shaded ½        |                     850 |           – |        66 % |

\* Estimates for Sydney. Harvest ≈ panel current × peak sun hours (June 2.5, Dec 5.5) × 0.8. Stage 1 = 20 % evening only; Stage 2 = 45 % evening + pre-dawn. Autonomy from full: Stage 1 ~26 nights, Stage 2 ~10 nights. Brightness steps down automatically as the battery falls, so a deficit shows as dimmer lights, not a dead pack.

**What this means:** the existing panel is fine for Stage 1 unless its spot is shaded. Stage 2 brightness on the existing panel would run a winter deficit of ~200 mAh/day – which is why the panel upgrade is tied to the tests in §7.

---

## 5. Firmware

### 5.1 Pro Mini – `firmware/lite_controller`

| Setting (`src/main.cpp`)         |     Default | Change when                                                   |
|----------------------------------|------------:|---------------------------------------------------------------|
| `SENSOR_LDR`                     |           0 | Using the LDR instead of the panel                            |
| `DEBUG_SERIAL`                   |           0 | Bench: 1 prints a status line per wake (9600 baud)            |
| `TIME_SCALE`                     |           1 | Bench: 60 runs the schedule 60× faster                        |
| `PANEL_STAGE`                    |           1 | 1 = existing panel (20 % cap, no pre-dawn); 2 = 6 V 5 W panel |
| `PANEL_DARK_V` / `PANEL_LIGHT_V` |   1.5 / 3.0 | Lights switch too early or late                               |
| `LDR_DARK` / `LDR_LIGHT`         | 0.30 / 0.60 | LDR option tuning                                             |
| `BANDGAP_V`                      |        1.10 | Battery reading ≠ multimeter                                  |
| `LED_VF`                         |         2.9 | From your string test                                         |

Schedule, levels and cut-offs live in `include/schedule.h` (`Config`). It's the same logic as v2 and can be tested on a Mac:

```
cd firmware/lite_controller/test_host
c++ -std=c++17 -I../include sim.cpp -o sim && ./sim
```

Checked so far:
- **Compile:** avr-gcc with the Arduino AVR core – Stage 1 and Stage 2 builds 7.2 kB flash; the debug + LDR build is 8.6 kB.
- **Host sim:** winter nights switch on at 17:15 (confirmed 5 min later) and off at 22:30, with pre-dawn 05:30 → dawn. Low battery cuts out at 3.25 V after 30 s and recovers next day. All-night mode tested too. The Stage 1 profile holds 20 % and skips pre-dawn: 203 mAh/night.
- **Not yet run on hardware.**

**Firmware servicing:** the controller has no bootloader, so the FTDI/UART adapter is monitoring-only. Use the consolidated [firmware programming procedure](firmware/lite_controller/PROGRAMMING.md) for PlatformIO builds, USBasp or Arduino-as-ISP uploads, verification and serial diagnostics.

### 5.2 D1 Mini – `firmware/esphome/solar-lights-lite.yaml`

- **Cycle:** wakes hourly, publishes, then deep-sleeps; a 45 s failsafe forces sleep if HA never connects.
- **Entities:** Battery Voltage, Battery Level, Lights On, Charging, WiFi Signal.
- **OTA:** turn on `input_boolean.solar_lights_ota`, wait for the next wake, then flash.
- **Status:** passes `esphome config`.

---

## 6. Build & bench tests (Stage 1)

| Step | Build                                                               | Test / pass                                                                  |
|-----:|---------------------------------------------------------------------|------------------------------------------------------------------------------|
|   B1 | Flash Pro Mini (`DEBUG_SERIAL 1`, `TIME_SCALE 60`, `PANEL_STAGE 1`) | Serial shows `vdd≈3.80` on a 3.8 V bench supply                              |
|   B2 | Remove Pro Mini LED + regulator                                     | Sleep current ≤ 10 µA (day state, 8 s wakes)                                 |
|   B3 | Add MOSFET, R6/R7, F1, R3, string                                   | Button → 30 % for 60 s; Q1 cool; no flicker                                  |
|   B4 | Add R1/R2/C1 on A0                                                  | Panel input 6 → 1 V: on after 5 "min" at 20 %; 3.5 V: off after 5 "min"      |
|   B5 | Lower supply to 3.25 V at night                                     | Lights off after 30 s; back on only after daylight + > 3.60 V                |
|   B6 | TP4056 + diodes + cells + existing panel                            | In sun: CHRG LED on, charge current 0.12–0.19 A; IN+ ≤ 7 V with battery full |
|   B7 | D1 Mini + D0–RST, flash YAML                                        | HA shows battery (±0.05 V vs meter), Lights On, Charging                     |
|   B8 | Reflash Pro Mini (`DEBUG 0`, `TIME_SCALE 1`, `PANEL_STAGE 1`)       | Self-test flash at power-up; first evening switches correctly                |

---

## 7. Field tests (Stage 1, existing panel)

### 7.1 Test plan

| Test | Dates             | Method                                                        | Pass                                                              |
|------|-------------------|---------------------------------------------------------------|-------------------------------------------------------------------|
| F1   | Install night     | Watch dusk and ~22:30; check HA                               | On within 10 min of dark at 20 %; off ~22:15 (1st night fallback) |
| F2   | First 14 days     | Log battery at ~07:00 and ~16:00 from HA history              | Back to ≥ 4.10 V most afternoons; no LVC                          |
| F3   | 14 days, Oct–Nov  | **Winter emulation:** cover ½ the panel with opaque card/tape | Battery at dusk flat or rising over 14 days; no LVC               |
| F4   | 01-Jun-2027–31-Aug-2027 | Real winter; weekly check of the dusk battery trend           | Dusk battery ≥ 3.70 V; no LVC nights                              |
| F5   | Any time          | Lights On = off at the 19:00 report while it's dark           | Never happens (it means LVC or a fault)                           |

- **Why F3 works:** spring sun (~5 PSH) with half the panel covered gives about the same daily harvest as an uncovered panel in June. You get a winter answer in November instead of waiting until next July.
- **Reading the trend:** "battery at dusk" is the Battery Voltage report just before the lights come on – the fullest the battery gets that day. A falling dusk voltage week over week means more is being used than collected.

### 7.2 Home Assistant alert (optional)

```yaml
alias: Solar Lights – battery low
triggers:
  - trigger: numeric_state
    entity_id: sensor.solar_lights_battery_voltage
    below: 3.5
actions:
  - action: notify.notify
    data:
      message: "Solar Lights battery {{ states('sensor.solar_lights_battery_voltage') }} V"
```

Add a history graph card with *Battery Voltage*, *Lights On* and *Charging* for the weekly check.

### 7.3 Decision – upgrade the panel?

Buy the Stage 2 panel if **any** of these happen during F3 or F4:

| #   | Trigger                                                      |
|-----|--------------------------------------------------------------|
| 1   | Dusk battery voltage falls > 0.05 V/week for 2 weeks running |
| 2   | Any LVC night (F5)                                           |
| 3   | Battery Level at dusk < 40 % on 5+ days in a month           |
| 4   | Stage 1 brightness (20 %, no pre-dawn) isn't enough for you  |

If none trigger through F4, stay on Stage 1 – it's working as designed.

---

## 8. Stage 2 – panel upgrade

### 8.1 Panel to buy

| Item           | Recommended                                     | Alternative (local stock)                                   |
|----------------|-------------------------------------------------|-------------------------------------------------------------|
| Model          | Waveshare **Solar Panel (6V 5W)**               | Waveshare **Monocrystalline silicon solar panel (5.5V 6W)** |
| Part no.       | Waveshare SKU **16158**                         | Core Electronics **WS-24166**                               |
| Power          | 5.0 W ± 5 %                                     | 6 W                                                         |
| Vmp / Voc      | 6.0 V / 7.2 V ± 5 %                             | 5.5 V / 7.2 V ± 5 %                                         |
| Imp / Isc      | 833 mA / 916 mA ± 5 %                           | 1,000 mA / 1,090 mA ± 5 %                                   |
| Build          | 156 mono cell, toughened glass, aluminium frame | Mono, toughened glass                                       |
| Output         | DC plug 3.5 × 1.35 mm                           | Micro-USB on 3 m lead                                       |
| Price          | US$10.99 (plus shipping)                        | A$34.90 inc GST                                             |
| Source         | waveshare.com/solar-panel-6v-5w.htm             | core-electronics.com.au (search WS-24166)                   |
| Harvest, June* | ≈ 1,700 mAh/day                                 | ≈ 2,000 mAh/day (TP4056 limits at ~1 A)                     |

\* Via TP4056, good aspect. Prices and stock as listed on 17-Sep-2026.

Notes:
- **Connector:** cut off the DC plug or micro-USB and wire the leads to the PV screw terminal. On the WS-24166 the USB VBUS (red) is + and GND (black) is −. Confirm polarity with a meter in sun.
- **Diodes for the 5.5 V panel:** use 1N5819 + 1N4001 (~1.2 V total) rather than 2 × 1N4001, so the lower Vmp still tops the battery up fully.
- **Mounting:** both are larger and heavier than the 110 × 110 mm panel. Allow a sturdier bracket, facing north at ~50° tilt.
- **Other 6 V panels:** any 5–6 W panel with Voc ≤ 7.5 V works the same. Avoid "12 V" panels (Voc ~21 V) – they would destroy the TP4056.

### 8.2 Swap procedure

| Step | Action                                                                       | Check                                             |
|-----:|------------------------------------------------------------------------------|---------------------------------------------------|
|   S1 | In sun, measure the new panel: Voc and short-circuit current (meter on 10 A) | Voc ≤ 7.6 V; Isc ≥ 0.8 A                          |
|   S2 | Cover the old panel; disconnect it at the PV terminal                        | Lights/controller unaffected (battery powered)    |
|   S3 | For WS-24166 only: swap D1/D2 to 1N5819 + 1N4001                             | Diode orientation: bands towards TP4056 IN+       |
|   S4 | Connect the new panel (+ to diodes, − to IN−)                                | In sun: CHRG LED on; charge 0.7–1.0 A             |
|   S5 | Pull the Pro Mini, reflash with `PANEL_STAGE 2` (FTDI, batteries out)        | Self-test flash at power-up                       |
|   S6 | Optional: fit D11 jumper to cap at 30 %                                      | –                                                 |
|   S7 | Re-run B6 (charging), F1 (first night) and 14 days of F2                     | Dusk battery flat or rising; pre-dawn window runs |

No other hardware changes are needed:
- **Panel divider:** R1/R2 reads up to ~10 V safely.
- **D1 Mini:** its configuration is unchanged.

---

## 9. Timeline (indicative)

| Dates               | Activity                                        |
|---------------------|-------------------------------------------------|
| 01-Oct-2026–31-Oct-2026            | Build, bench tests B1–B8, install, F1           |
| Oct–Nov             | F2 (14 days) then F3 winter emulation (14 days) |
| Late Nov            | Decision point 1 – buy panel now if F3 fails    |
| Dec–May             | Normal running (summer surplus)                 |
| 01-Jun-2027–31-Aug-2027   | F4 real winter monitoring                       |
| Any trigger in §7.3 | Stage 2 panel swap (§8), then F1/F2 re-check    |

---

## 10. Upgrade path to v2

Lite is a working subset of v2, so parts can be swapped one at a time:

| Upgrade                     | Swap                                       | Gain                       |
|-----------------------------|--------------------------------------------|----------------------------|
| Bigger panel                | Existing 1.2 W → 6 V 5 W (§8)              | ×4–5 energy                |
| More harvest                | TP4056 + diodes → CN3791 MPPT module       | +30–40 % energy            |
| Panel/temp data in HA       | D1 Mini → ESP32-C3 power-gated by Pro Mini | Full v2 telemetry          |
| Hot-weather charging safety | NTC on cells + inhibit (v2 §5.1)           | Stops charging above 45 °C |
| Smaller, tidier             | v2 PCB                                     | One board, SMD             |
