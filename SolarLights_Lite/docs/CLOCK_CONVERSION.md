# Step 1 in full: converting the ATmega328P to internal 8 MHz

Rev 0.4 amended, 20 September 2026. Written for someone who has never touched AVR fuses.
Read this once before starting; the whole job takes about 20 minutes.

---

## 1. What this actually is

An ATmega328P has three configuration bytes called **fuses**. They are not part of your
sketch and a normal upload never touches them. The chip reads them at every reset to
decide things like which clock source to use and at what supply voltage it should refuse
to run. They keep their values with the power off, forever, until deliberately rewritten.

Right now your board's fuses say "use the external 16 MHz crystal". We want them to say
"use the internal 8 MHz oscillator, and shut down below 2.7 V".

Fuses cannot be changed over the USB/serial path you normally upload with. They are
written over **ISP** (In-System Programming), a four-wire SPI connection plus power and
ground, using a separate piece of hardware called a **programmer**. The board being
programmed is called the **target**.

| Term | Meaning |
|---|---|
| Fuse | A configuration byte inside the chip: clock source, brown-out level, reset behaviour |
| ISP / ICSP | In-System Programming: writing the chip over SPI while it sits in circuit |
| Programmer | The hardware that does it: a USBasp, a USBtinyISP, or another Arduino running the ArduinoISP sketch |
| Chip erase | Writing fuses erases the flash first. Any bootloader present is lost, deliberately |
| BOD | Brown-out detection: the chip halts below a set voltage instead of misbehaving |
| Bootloader | The small program that normally receives sketches over serial. We will not have one after this |

---

## 2. What you need

- **A programmer.** A USBasp costs a few dollars, but you almost certainly do not need to
  buy one: any spare Uno, Nano or Mega can be a programmer by loading the **ArduinoISP**
  sketch that ships with the Arduino IDE (File > Examples > 11.ArduinoISP).
- **Six jumper wires**, and a **10 uF capacitor** if you use an Arduino as the programmer.
- **The target board**, your BTE13-010A Pro Mini, with nothing else connected. No battery,
  no panel, no LED string.

Do the fuse change **before** removing the board's regulator and power LED. It is easier
to power the board through its normal path while programming, and the board mods are a
one-way trip.

---

## 3. Wiring

Six connections. The Pro Mini's six-pin ICSP header, if fitted, is numbered 1 MISO,
2 VCC, 3 SCK, 4 MOSI, 5 RESET, 6 GND. If it has no header, the same signals appear on
D12, D11, D13, RST, VCC and GND.

| Signal | Target (Pro Mini) | Uno as programmer | USBasp 10-pin |
|---|---|---|---|
| MISO | D12 (ICSP 1) | D12 | 9 |
| MOSI | D11 (ICSP 4) | D11 | 1 |
| SCK | D13 (ICSP 3) | D13 | 7 |
| RESET | RST (ICSP 5) | **D10** | 5 |
| VCC | VCC (ICSP 2) | 5V | 2 |
| GND | GND (ICSP 6) | GND | 10 |

Note the asymmetry: the programmer's D10 drives the target's RESET. Everything else is
like-to-like.

**If you use an Arduino as the programmer**, do this in order:

1. Upload the ArduinoISP sketch to the Uno, on its own, before wiring anything.
2. Then fit a **10 uF capacitor between the Uno's RESET and GND**, negative leg to GND.
   This stops the Uno resetting itself when avrdude opens the serial port. Without it you
   get "not in sync" errors. Remove it when you want to reprogram the Uno itself.
3. Then wire the six connections above and plug the Uno into the Mac.

### Your USBasp, on your board

Printable version with the header drawn out: `../../output/pdf/USBasp_Wiring.pdf`.

The USBasp's 10-pin header uses the standard AVR ISP layout. Odd numbers are one row,
even the other, and pin 1 carries a dot, a triangle or a square pad (the red stripe on a
ribbon cable):

```
  1 MOSI   3 NC    5 RST   7 SCK   9 MISO
  2 VCC    4 GND   6 GND   8 GND  10 GND
```

Every pin you need on the BTE13-010A is in its top row, which reads, left to right with
the FTDI header on the left: RAW, GND, RST, VCC, A3, A2, A1, A0, 13, 12, 11, 10.

| USBasp | Signal | Pro Mini pin |
|---|---|---|
| 1 | MOSI | 11 |
| 9 | MISO | 12 |
| 7 | SCK | 13 |
| 5 | RESET | RST |
| 2 | VCC | VCC |
| 4, 6, 8 or 10 | GND | GND |

RESET goes to the pin marked RST, not to a numbered pin. MOSI and MISO are the pair that
get swapped: 11 is the one going out to the chip, 12 is the one coming back.

Jumpers on the USBasp: leave the 5 V setting (your board is the 16 MHz version, so it
programs at 5 V), leave JP2 alone, and keep JP3 "slow SCK" handy in case the chip does not
answer. Old clone firmware ignores avrdude's `-B` option, so JP3 is the real slow-clock
control. Nothing else may be connected to the Pro Mini while you do this: no FTDI adapter,
no battery, no LED string. The USBasp powers the board through pin 2.

**If your USBasp has a 3.3/5 V jumper**, set it to match the target. A 5 V Pro Mini
programs at 5 V. If you have already removed the regulator and are feeding VCC from a
3.3 V supply, program at 3.3 V instead, and make sure the programmer's logic is also
3.3 V.

---

## 4. The three fuse values, and what each bit means

We are writing **low = 0xE2**, **high = 0xD9**, **extended = 0xFD**.

**Low fuse 0xE2 - the clock**

| Bit | Value | Meaning |
|---|---|---|
| CKDIV8 | 1 (off) | Do not divide the clock by 8. Leave it off, or you get 1 MHz |
| CKOUT | 1 (off) | Do not output the clock on a pin |
| SUT1:0 | 10 | Slow rising power start-up delay, the safe choice on a battery |
| CKSEL3:0 | 0010 | Internal 8 MHz RC oscillator. This is the bit that does the job |

**High fuse 0xD9 - the factory default, unchanged**

| Bit | Value | Meaning |
|---|---|---|
| RSTDISBL | 1 (off) | Reset pin stays a reset pin. **Never program this to 0**: it disables ISP for good |
| DWEN | 1 (off) | debugWIRE off |
| SPIEN | 0 (on) | ISP enabled. Leave it |
| WDTON | 1 (off) | Watchdog not forced on; the firmware controls it |
| EESAVE | 1 (off) | EEPROM is erased on chip erase. Use 0xD1 instead if you ever need to preserve it |
| BOOTSZ, BOOTRST | 00, 1 | Start at address 0, no jump to a bootloader |

**Extended fuse 0xFD - brown-out**

| Value | BOD level |
|---|---|
| 0xFF | Disabled |
| 0xFE | 1.8 V |
| **0xFD** | **2.7 V - what we want** |
| 0xFC | 4.3 V |

Only three bits of this byte exist, so **avrdude often reads it back as 0x05**. That is
the same value, not a failed write.

Why 2.7 V: it is below your 3.30 V firmware cut-off, so it never interferes with normal
operation, but it halts the chip before a collapsing cell can make it execute nonsense or
corrupt its own flash.

**The two ways to lock yourself out**, so you can avoid both:

- Programming RSTDISBL to 0. Recovery needs a high-voltage programmer.
- Selecting an external clock source that is not present (for example CKSEL = 0000 with no
  signal on XTAL1). Recovery needs a clock injected into XTAL1.

Neither can happen if you use exactly the three values above.

---

## 5. Doing it - the IDE way (no command line)

The Arduino IDE can write these fuses for you if you install **MiniCore** (Boards Manager,
search "MiniCore" by MCUdude).

1. Tools > Board > MiniCore > **ATmega328**
2. Tools > Clock > **Internal 8 MHz**
3. Tools > BOD > **2.7 V**
4. Tools > Bootloader > **No bootloader**
5. Tools > Variant > 328P / 328PA, Tools > Programmer > **Arduino as ISP** (or USBasp)
6. Tools > **Burn Bootloader**

Despite the menu name, with "No bootloader" selected this writes fuses and no bootloader.
It is exactly the three values in section 4.

---

## 6. Doing it - the avrdude way (recommended, because you see what happened)

On macOS, avrdude comes with the Arduino IDE:

```
~/Library/Arduino15/packages/arduino/tools/avrdude/*/bin/avrdude
```

Add `-C ~/Library/Arduino15/packages/arduino/tools/avrdude/*/etc/avrdude.conf` if it
complains about a missing config, or install your own with `brew install avrdude`.

**Test the connection first.** Nothing is written by this command:

```
avrdude -c stk500v1 -P /dev/cu.usbmodemXXXX -b 19200 -p m328p -v
```

For a USBasp instead: `avrdude -c usbasp -p m328p -v`, with no port or baud.

Find your port with `ls /dev/cu.*`. A good result reports:

```
Device signature = 0x1e950f (probably m328p)
```

That is the same signature your successful 6,488-byte upload reported, so you know the
chip and the wiring are both right. It also prints the current fuses - write them down.

**Write the fuses:**

```
avrdude -c stk500v1 -P /dev/cu.usbmodemXXXX -b 19200 -p m328p \
  -U lfuse:w:0xE2:m -U hfuse:w:0xD9:m -U efuse:w:0xFD:m
```

**Read them back:**

```
avrdude -c stk500v1 -P /dev/cu.usbmodemXXXX -b 19200 -p m328p \
  -U lfuse:r:-:h -U hfuse:r:-:h -U efuse:r:-:h
```

Expect `0xe2`, `0xd9`, `0xfd` (or `0x05` for the last one).

The moment the low fuse is written the chip switches to its internal oscillator. It keeps
talking to the programmer because ISP runs from the target's own clock and avrdude's SCK
is slow enough for both speeds.

---

## 7. After the fuse change

- **The bootloader is gone.** Uploading over the FTDI/serial adapter will no longer work.
  From now on: Sketch > **Upload Using Programmer**, or
  `avrdude ... -U flash:w:firmware.hex:i`. The six ISP wires stay on the bench.
- **Baud rates now behave.** The 19200-versus-38400 confusion was the 8 MHz build running
  on a 16 MHz chip. Build and chip now agree, so the sketch's 9600 really is 9600.
- **The crystal can stay** on the board. It is simply no longer selected.

> For the ongoing method of uploading application firmware via ISP after this conversion - including the two avrdude-versions gotcha discovered 21 Sep 2026 - see [ISP_FIRMWARE_UPLOAD.md](ISP_FIRMWARE_UPLOAD.md). This page covers the one-time fuse change only.

## 8. Board modifications, after the fuses

1. Photograph the board first, both sides, at high resolution.
2. Remove the **power LED or its series resistor** - the one permanently tied to VCC. The
   D13 LED is a different branch and stays.
3. Remove the **regulator**. Feed your supply into **VCC**, never RAW.
4. Keep the local decoupling capacitors.

## 9. Proving it worked

| Check | How | Pass |
|---|---|---|
| Fuses | Read back as above | 0xE2 / 0xD9 / 0xFD (or 0x05) |
| Clock speed | Blink sketch with 1000 ms delays, timed against a watch | 1 s, not 2 s |
| Clock speed, properly | Scope or frequency meter on D9 once the project firmware runs | 1.9 to 2.0 kHz |
| Serial | Monitor at 9600 with DEBUG_SERIAL 1 | Readable text, not garbage |
| Low voltage | Bench supply at 3.3 V on VCC | Runs normally |

## 10. When it goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| `Device signature = 0x000000` | No power, RESET not driven, or MISO/MOSI swapped | Recheck the six wires; confirm VCC at the target |
| `avrdude: stk500_recv(): programmer is not responding` | Wrong port, wrong baud, or the ISP Arduino is auto-resetting | Use `-b 19200`; fit the 10 uF capacitor on the programmer's RESET |
| Works at 5 V, fails at 3.3 V | SCK too fast for a slow target | Add `-B 8`, or fit the USBasp slow-clock jumper |
| Signature reads, fuse write refused | Lock bits set | `-e` chip erase clears lock bits, then rewrite |
| Chip silent after a fuse write | Wrong CKSEL, or RSTDISBL programmed | Inject a clock on XTAL1, or high-voltage programming |

## 11. The shortcut

If there is a **genuine 3.3 V / 8 MHz Pro Mini** in your parts bin, use that instead and
skip this entire page. It is the same ATmega328P already fused for internal-or-8 MHz
operation at this voltage range. You would still remove its power LED and regulator, and
still verify the D9 PWM frequency, but finding H03 closes without touching a fuse.
