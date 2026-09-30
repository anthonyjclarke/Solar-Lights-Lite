# 12 – Going further

Solar Lights Lite is deliberately small. These are the natural next steps,
each a project in its own right. None of them is needed for the design as
documented, and each changes the energy budget and the commissioning work.

---

## Brighter lights: add a driver stage

The controller pin can supply about 20 mA. For a brighter string, D9 must drive
a switch that carries the LED current:

- **Logic-level MOSFET** with its on-resistance *specified at 2.5 V gate
  drive* (for example AO3400A on a breakout). "Logic level" on its own is not
  enough: at 3.0–3.3 V many such parts, including the 2N7000, are only partly
  on at LED currents.
- **NPN transistor** such as a BC337, with a base resistor sized for forced
  saturation (base current about a tenth of collector current).

A driver stage also needs a gate or base resistor, a pull-down so the lights
stay off at reset, a current-limiting resistor per LED branch, and a fuse in
the LED branch, because the string is then fed from the battery rail rather
than through the pin. Re-run the energy budget: a 200 mA string for 14 hours
needs 2,800 mAh a night, far beyond a 1–2 W panel.

---

## Better charging

- **Cell-temperature protection.** Add a thermistor on the cells and a
  charger (or cut-off circuit) that stops charging below 0 °C and above about
  45 °C. This is the main requirement for unattended use in cold climates.
- **Power-path charging.** Chargers such as the TI BQ24074 or Microchip
  MCP73871 supply the load and charge the battery separately, and regulate the
  input to suit a solar panel. They are not pin-compatible with TP4056 modules
  and come in small packages, so they suit a custom PCB.

## Measuring energy

The telemetry reports controller state, not energy. An INA219 or INA226
current monitor on the battery lead (read by the D1 Mini over I²C) would add
charge current, load current and daily mAh in and out – turning the soak test
into a true energy balance.

## Time-based schedules

The dusk-to-dawn design deliberately avoids clocks. An "evening and pre-dawn
only" schedule would need real time: a DS3231 RTC on the controller, or a time
sync from the D1 Mini. Watch the added standby current.

## A carrier PCB

Once your modules are fixed, a two-layer carrier board can replace perfboard:
sockets for the Pro Mini and D1 Mini, screw terminals, fuse holders, labelled
rails, test points and footprints for the Q2 interface. Keep the ESP8266
antenna at the board edge, and keep LED return current away from the LDR and
ADC ground. The KiCad schematic in [`hardware/kicad/`](../hardware/kicad/) is
the starting point; it needs footprints and a layout.

## Lower-power telemetry

An ESP32-C3 or similar module has a much lower deep-sleep current than an
ESP8266 D1 Mini and can run directly from a 3.3 V buck-boost. The serial
protocol and Home Assistant side would stay the same.
