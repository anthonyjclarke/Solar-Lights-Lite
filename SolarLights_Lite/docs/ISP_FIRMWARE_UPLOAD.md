# Firmware programming has moved

The old programming procedure in this location mixed dated iMac/MacBook test
results, USBasp instructions, Arduino-as-ISP instructions and obsolete
environment names.

Use the single current procedure in the firmware folder:

**[Firmware build, USBasp upload and serial diagnostics](../firmware/lite_controller/PROGRAMMING.md)**

That guide starts from a clean macOS environment and covers:

- PlatformIO and avrdude prerequisites;
- Intel and Apple Silicon checks;
- production and diagnostic builds;
- USBasp wiring, signature check, upload and verification;
- Arduino-as-ISP fallback;
- receive-only UART diagnostics;
- read-only fuse verification and troubleshooting.

Do not use historical commands from `validation/` as the current procedure.
