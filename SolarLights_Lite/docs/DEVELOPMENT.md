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

For scheduler-only checks, build the host tests in `test_host/` with a C++17 compiler
and include path `../include`; the recorded validation evidence is under `validation/`.
