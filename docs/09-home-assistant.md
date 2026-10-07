# 09 – Home Assistant and ESPHome telemetry

**Files:** [`firmware/esphome/`](../firmware/esphome/) (D1 Mini profiles) and
[`homeassistant/`](../homeassistant/) (package and dashboards).
**Hardware:** [07 – Module E: telemetry hardware](07-build-telemetry.md).

The lights run without any of this. Telemetry lets you watch the controller
work, calibrate it, prove it over a two-week soak, and then keep an eye on it in
service.

**What you will learn:** ESPHome configuration and secrets, parsing a serial
protocol in an ESPHome lambda, deep sleep with an OTA escape hatch, Home
Assistant packages, helpers, automations and sections dashboards.

---

## The tiers

| Tier | Controller build | ESPHome profile                          | D1 Mini power |
| :--- | :--------------- | :--------------------------------------- | :------------ |
| 0    | `standalone`     | None                                     | –             |
| 1    | `advanced`       | `solar-lights-advanced-telemetry.yaml`   | Micro-USB     |
| 2    | `production`     | `solar-lights-production-telemetry.yaml` | U3 (battery)  |

**Tier 1 – Advanced Telemetry** is the commissioning instrument. The D1 Mini
stays awake and publishes every field of every diagnostic line, plus its own
Wi-Fi, heap and uptime. It keeps receiving if Wi-Fi or Home Assistant go down,
and serves its own web page at `http://<D1 IP address>/`. It draws around
70–80 mA continuously, which is why it runs from USB and is never part of the
battery budget.

**Tier 2 – Production Telemetry** is for the finished installation. Once an hour
the D1 Mini wakes, waits up to 20 s for a status line from the controller,
reads the battery voltage, reports, and goes back to deep sleep. Its average
draw is well under 1 mA.

Both profiles use the **same device name (`solar-lights`), entity names and
encryption key**, so moving from Tier 1 to Tier 2 keeps your Home Assistant
history and the same entity IDs.

---

## 1. Install ESPHome

Use either the **ESPHome Device Builder** add-on in Home Assistant
(Settings → Add-ons) or the ESPHome command-line tool. The profiles need
ESPHome 2024.11 or later.

## 2. Add the secrets

In the ESPHome `secrets.yaml` (never in this repository):

| Key                      | Used for                                |
| :----------------------- | :-------------------------------------- |
| `wifi_ssid`              | Your Wi-Fi network                      |
| `wifi_password`          | Your Wi-Fi password                     |
| `esphome_encryption_key` | API key (ESPHome can generate one)      |
| `ota_password`           | Over-the-air update password            |
| `ap_password`            | Tier 1 fallback hotspot (8+ characters) |

## 3. Flash the D1 Mini (Tier 1)

1. Remove the D0 → RST link while flashing over USB.
2. In the ESPHome dashboard create a device, then replace its YAML with
   `solar-lights-advanced-telemetry.yaml`. Keep `name: solar-lights`: the
   dashboards' entity IDs depend on it.
3. **Validate**, then **Install** over USB the first time. Later updates can go
   over Wi-Fi.
4. Adopt the device in Home Assistant (Settings → Devices & services).
5. Flash the controller with the `advanced` build
   ([08 – Firmware](08-firmware.md)).

Within about a minute, **Arduino Diagnostics Fresh** turns on and
**Arduino Diagnostic Line** shows a complete line starting `fw=`.

## 4. Install the Home Assistant package

[`homeassistant/solar_lights_package.yaml`](../homeassistant/solar_lights_package.yaml)
adds:

- `input_boolean.solar_lights_ota`, the helper Tier 2 uses to stay awake for
  updates;
- three example automations: battery low, low-voltage cut-off, and reports
  stopped. They use persistent notifications, so they work without a phone
  app.

Enable packages once in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Copy the file to `/config/packages/`, check the configuration
(Developer tools → YAML) and restart Home Assistant.

## 5. Import a dashboard

Create a dashboard (Settings → Dashboards → Add dashboard), open it, choose
**Edit dashboard → Raw configuration editor**, and paste one of:

| Dashboard                             | Use                                 |
| :------------------------------------ | :---------------------------------- |
| `dashboard-advanced-telemetry.yaml`   | Tier 1: commissioning and soak test |
| `dashboard-production-telemetry.yaml` | Tier 2: day-to-day and 7-day trends |

Both use built-in cards only. If Home Assistant assigned different entity IDs,
find-and-replace `solar_lights_` before saving.

---

## Moving from Tier 1 to Tier 2

Do this only after the soak test (Gate 7) has passed.

1. Flash the controller with the `production` build.
2. With the D1 Mini still on USB, install
   `solar-lights-production-telemetry.yaml` over Wi-Fi.
3. Unplug USB. Close the U3 OUT → 3V3 jumper. Fit the D0 → RST link.
4. Watch for the first hourly report; then complete Gate 8.

To go back to Tier 1 (for example to recalibrate), reverse the steps: open the
U3 jumper **before** plugging in USB.

### Updating a sleeping D1 Mini (Tier 2)

Turn on **Solar Lights stay awake for OTA** (`input_boolean.solar_lights_ota`).
At its next wake the D1 Mini stays awake; install the update, then turn the
helper off and it resumes its hourly sleep. To reach it sooner, press its reset
button.

---

## Entities

| Entity (name in ESPHome)              | Tier 1 | Tier 2 | Notes                    |
| :------------------------------------ | :----: | :----: | :----------------------- |
| Battery Voltage / Battery Level       | ✓      | ✓      | D1 Mini A0, calibrated   |
| Arduino VDD                           | ✓      | ✓      | Controller's own reading |
| Arduino Mode / Night / Output Cause   | ✓      | ✓      | Scheduler state          |
| Arduino Light Duty / Lights Commanded | ✓      | ✓      | D9 PWM duty              |
| Arduino LDR / Light Sense             | ✓      | ✓      | Light sensor             |
| Arduino Battery Band / Firmware       | ✓      | ✓      |                          |
| Arduino Diagnostic Line               | ✓      | ✓      | Latest raw line          |
| Arduino Diagnostics Fresh             | ✓      | ✓      | Tier 2: line this wake   |
| Arduino LDR Raw / LDR Voltage         | ✓      |        | Advanced detail          |
| Arduino Transition Confirmation       | ✓      |        | Dusk/dawn progress       |
| Arduino LVC Elapsed / Button Test     | ✓      |        | Timers (see guide 11)    |
| D1 WiFi Signal                        | ✓      | ✓      |                          |
| D1 Status, IP, SSID, uptime, heap     | ✓      |        | Receiver health          |

Telemetry reports what the controller measures and decides. It does not
measure panel voltage, charge or load current, energy or temperature; use a
meter or power profiler for those.

---

## Calibrating the battery reading

In Gate 7, compare **Battery Voltage** with a meter across VBAT_SYS and GND at a
few battery levels. Set the multiplier in both profiles:

```
new multiplier = old multiplier × meter volts / reported volts
```

The nominal value is 5.4 (R5 220 kΩ plus the D1 Mini's 220 kΩ/100 kΩ divider);
the reference build calibrated to 5.21. **Arduino VDD** is a useful
cross-check, since it measures the same rail independently.

---

## Troubleshooting

| Symptom                                | Check                                   |
| :------------------------------------- | :-------------------------------------- |
| Diagnostics Fresh stays off            | Controller build, Q2 wiring, grounds    |
| `Dropped corrupted UART line` warnings | Q2 pin order, shared GND_LOAD           |
| Home Assistant asks for the key again  | Encryption key changed between profiles |
| Tier 2 device never reports            | D0 → RST link, U3 jumper, Wi-Fi reach   |
| Tier 2 stays awake                     | OTA helper still on                     |
| Entities `unavailable` in Tier 1       | D1 Mini USB power or Wi-Fi              |
