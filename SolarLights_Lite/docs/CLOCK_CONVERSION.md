# Clock and fuse status — conversion complete

The BTE13-010A ATmega328P has already been converted and independently read
back with:

| Setting | Confirmed value |
|---|---|
| Clock | Internal 8 MHz |
| Low fuse | `0xE2` |
| High fuse | `0xD9` |
| Extended fuse | `0xFD` (`0x05` may be displayed for the same implemented bits) |
| Brown-out detection | 2.7 V |
| Bootloader | None |

This conversion is not a routine build step and must not be repeated for normal
firmware updates. Application uploads do not write fuses.

The single current procedure for compiling, uploading with USBasp or
Arduino-as-ISP, checking the existing fuses read-only, and monitoring serial is:

**[Firmware build, upload and diagnostics](../firmware/lite_controller/PROGRAMMING.md)**

The dated discovery and fuse-write evidence remains in
[VALIDATION.md](VALIDATION.md) as history. It is not the current operating
procedure.
