# Architecture

The active firmware is in `firmware/lite_controller/`. `src/main.cpp` owns AVR
setup, ADC reads, GPIO, PWM, watchdog wakeups, button interrupts, and sleep.
`include/schedule.h` contains the hardware-independent light scheduler so it can
be exercised by the host tests in `test_host/`.

Each wake measures controller supply voltage and the selected light sensor. With
the current configuration, D7 briefly powers the LDR divider and A1 is sampled.
The scheduler debounces dark/light for five minutes, controls dusk-to-dawn output,
applies low-voltage cut-off, and handles the startup and button test intervals.

The controller wakes every second while lit, fading, or confirming a transition;
otherwise it uses an eight-second watchdog wake and power-down sleep. PWM requires
idle sleep while the LEDs are on. The optional ESPHome configuration is separate
under `firmware/esphome/` and is not required for the light controller.
