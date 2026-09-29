# Development

Run PlatformIO from `SolarLights_Lite/firmware/lite_controller`.

| Environment | Command | Use |
| --- | --- | --- |
| `pro8` | `pio run -e pro8` | Quiet production build |
| `pro8_debug` | `pio run -e pro8_debug` | Bench build with 9600-baud diagnostics |

The target has no bootloader. Do not use PlatformIO's upload target; use the
separate current `avrdude` ISP procedure in `firmware/lite_controller/PROGRAMMING.md`.
That guide also specifies USBasp/Arduino-as-ISP isolation, fuse readback, and serial
monitoring. Normal updates do not write fuses.

## ESPHome development telemetry (D1 Mini)

`firmware/esphome/solar-lights-lite-dev-d1.yaml` turns the existing Wemos D1 Mini
into an always-awake monitor. It receives the debug build's D1/TX output through
the reused Q2/R8/R9/R10 inverter at D6. It only receives data and is for testing
only. When you return to low-power testing, use the separate
`solar-lights-lite.yaml` profile instead.

### 1. Secrets

Add these keys to the ESPHome `secrets.yaml` in Home Assistant (never to this repo):

| Key                      | Use                                          |
|:-------------------------|:---------------------------------------------|
| `wifi_ssid`              | Bench Wi-Fi network                          |
| `wifi_password`          | Bench Wi-Fi password                         |
| `esphome_encryption_key` | API key; reuse the one already adopted in HA |
| `ap_password`            | Fallback AP `telemetry-fallback` (new, 8+)   |

`ap_password` is new in v0.5.3; the build fails until it exists. Reuse the
encryption key the running device already has, or Home Assistant will ask you
to re-enter it.

### 2. Validate and flash

1. In the ESPHome add-on, open (or create) the `telemetry` device and paste in
   the repo YAML. Keep `name: telemetry`: the dashboard's entity IDs depend on it.
2. Choose **Validate**, then **Install**. Use **Wirelessly** (OTA) if the
   `telemetry` device is already online; otherwise use USB.
3. Flash the Pro Mini with the `pro8_debug` build (see `PROGRAMMING.md`). The
   quiet `pro8` build sends no UART data.

### 3. Check it is working

- **D1 Status** is on and **Arduino Diagnostics Fresh** turns on within about 60 s.
- **Arduino Diagnostic Line** shows one complete line, not half of one.
- The ESPHome log should not show repeated `Dropped corrupted UART line`
  warnings; if it does, check Q2 wiring and the shared ground at OUT-.
- The D1 web page (`http://<D1 IP address>/`) lists the same entities if Home
  Assistant is unavailable.
- If Wi-Fi cannot be reached, the D1 raises the `telemetry-fallback` AP but keeps
  receiving UART data; it does not reboot.

### 4. Import the dashboard

In Home Assistant, create a dashboard, open **⋮ → Edit dashboard → ⋮ → Raw
configuration editor**, and replace the contents with
[`solar-lights-lite-dev-dashboard.yaml`](../firmware/esphome/solar-lights-lite-dev-dashboard.yaml).
It uses only built-in cards and expects `*.telemetry_*` entity IDs. If Home
Assistant assigned different IDs when the device was adopted, find-and-replace
the prefix before saving. The dashboard shows controller and receiver health;
it does not measure current, energy or temperature.

For scheduler-only checks, build the host tests in `test_host/` with a C++17 compiler
and include path `../include`; the recorded validation evidence is under `validation/`.
