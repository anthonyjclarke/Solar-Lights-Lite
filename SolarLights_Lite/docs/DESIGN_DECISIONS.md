# Design decisions

- The ATmega328P at internal 8 MHz is retained because the firmware uses its
  specific ADC, pin-change interrupt, and timer assumptions. The available
  ATmega32U4 Pro Micro is not a drop-in replacement.
- A switched LDR is the normal dusk/dawn sensor. It avoids depending on panel
  voltage under charger load and removes the need for an RTC or network service.
- D9 drives the measured low-current LED string through a series resistor. PWM
  controls brightness; the resistor and output pin bound peak current.
- The scheduler is separated from the AVR layer for repeatable host regression
  tests. Sleep and watchdog timing minimise controller standby consumption.
- Low-voltage cut-off protects the lighting load in firmware; pack protection and
  charger behaviour remain separate hardware concerns.
- v0.5 reuses the D1 Mini and Q2/R8/R9/R10 as an inverted, receive-only UART
  monitor during development. The Arduino remains autonomous; the D1's
  always-on development profile is intentionally not part of the production
  power budget.

These choices are bounded by the unfinished bench work in `ROADMAP.md`.
