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

For v0.5 bench telemetry, flash
`firmware/esphome/solar-lights-lite-dev-d1.yaml` to the existing Wemos D1 Mini.
It remains awake and receives the debug image's D1/TX output through the reused
Q2/R8/R9/R10 inverter at D6. It is a receive-only, test-only monitor; use the
separate `solar-lights-lite.yaml` profile when returning to low-power testing.

## Home Assistant development dashboard

After the D1 appears in Home Assistant, import
[`solar-lights-lite-dev-dashboard.yaml`](../firmware/esphome/solar-lights-lite-dev-dashboard.yaml)
through a dashboard's raw YAML editor. It is a core-card-only v0.5 bench view for
battery and Arduino voltage, light behaviour, parsed UART state, raw diagnostics,
Wi-Fi, reset cause, heap and uptime. It deliberately does not imply current,
energy or temperature measurement. If Home Assistant assigned different entity IDs
when the ESPHome device was adopted, update those IDs in the example before import.

For scheduler-only checks, build the host tests in `test_host/` with a C++17 compiler
and include path `../include`; the recorded validation evidence is under `validation/`.
