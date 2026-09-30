#!/usr/bin/env python3
"""One-page printable controller bench sheet: flash, prove the controller, measure the LED string.
Writes docs/drawings/controller-bench-sheet.pdf and a PNG preview beside it.
Run with a Python environment containing reportlab and pypdfium2.
"""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import pypdfium2 as pdf

DOC = Path(__file__).resolve().parents[1] / 'docs' / 'drawings'
OUT = DOC; OUT.mkdir(parents=True, exist_ok=True)
FN = OUT / 'controller-bench-sheet.pdf'
W, H = A4
INK = HexColor('#173047'); MUTED = HexColor('#516578'); RED = HexColor('#c1363d')
GREEN = HexColor('#008572'); AMBER = HexColor('#ad6200'); LINE = HexColor('#d5e0e6')
L, R = 38, W - 38
c = Canvas(str(FN), pagesize=A4)
y = H - 46

def txt(s, size=9.2, col=INK, bold=False, dx=0, lead=13):
    global y
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size); c.setFillColor(col)
    c.drawString(L + dx, y, s); y -= lead

def rule(gap=7):
    global y
    y -= gap - 4; c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(L, y, R, y); y -= gap

def head(n, s):
    global y
    y -= 4
    c.setFillColor(GREEN); c.setFont('Helvetica-Bold', 10.5); c.drawString(L, y, f'{n}  {s}')
    y -= 15

def row(cells, widths, size=9, bold=False, col=INK, lead=13.5):
    global y
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size); c.setFillColor(col)
    x = L
    for cell, w in zip(cells, widths):
        c.drawString(x, y, cell); x += w
    y -= lead

def box(lines, col=AMBER, pad=6):
    global y
    h = 11.5 * len(lines) + 2 * pad
    c.setFillColor(HexColor('#fdf6ec')); c.setStrokeColor(col); c.setLineWidth(1)
    c.rect(L, y - h + 10, R - L, h, fill=1, stroke=0)
    c.setLineWidth(2.5); c.line(L, y - h + 10, L, y + 10)
    yy = y
    for i, s in enumerate(lines):
        c.setFont('Helvetica-Bold' if i == 0 else 'Helvetica', 9); c.setFillColor(HexColor('#3a362f'))
        c.drawString(L + pad + 4, yy, s); yy -= 11.5
    y = yy - 12

# ---------------------------------------------------------------- header
c.setFillColor(GREEN); c.setFont('Helvetica-Bold', 8.5); c.drawString(L, y, 'SOLAR LIGHTS LITE / PRINTABLE SHEET'); y -= 20
c.setFillColor(INK); c.setFont('Helvetica-Bold', 17); c.drawString(L, y, 'Controller bench sheet'); y -= 16
c.setFillColor(MUTED); c.setFont('Helvetica', 9.3)
c.drawString(L, y, 'Flash the advanced build, prove the controller, then measure the LED string. Gate 1 of docs/10-commissioning.md.'); y -= 13
rule()

box(['Before you start',
     'No cells connected for any of this. Use a current-limited bench supply, 200 mA limit, for VCC.',
     'Do not connect the panel or the charger. R3 sits at the board end, not out at the string.',
     'Duty does not limit current: only R3 and the pin do. Verify at 4.20 V and 100% duty.'])

# ---------------------------------------------------------------- step 1
head('1', 'Flash the advanced build')
txt('Fuses are set once per board (internal 8 MHz, BOD 2.7 V, no bootloader). Routine flashing never writes them.', col=AMBER, bold=True)
txt('Disconnect cells, panel, UART and LED string. Power from one verified target-compatible ISP source only.', col=MUTED)
y -= 2
row(['Action', 'Command / pass result'], [152, 300], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
row(['Open firmware folder', 'cd firmware/controller'], [152, 300], size=8.6)
row(['Check the target', 'avrdude -c usbasp -p m328p -v   -> signature 0x1e950f'], [152, 300], size=8.6)
row(['Compile advanced build', 'pio run -e advanced   -> SUCCESS'], [152, 300], size=8.6)
row(['Upload and verify', 'standalone current avrdude; never pio -t upload'], [152, 300], size=8.6)
y -= 2
txt('Disconnect all ISP wires before normal power returns. USB-UART is monitoring-only: target TX -> adapter RX,', size=8.6)
txt('OUT-/GND -> adapter GND; leave adapter VO/VCC, TX, DTR and CTS open. Monitor at 9600 baud.', size=8.6)
y -= 3
txt('Tool setup, fuses, Arduino-as-ISP fallback and troubleshooting: docs/08-firmware.md', bold=True)
rule()

# ---------------------------------------------------------------- step 2
head('2', 'Check the controller on a current-limited bench supply')
txt('Read the diagnostics through Tier 1 telemetry or a USB-UART adapter (RX and GND only) at 9600 baud.', col=MUTED)
y -= 2
row(['Check', 'Expect'], [190, 250], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
row(['Startup after reset', 'One-time field guide, then rate-limited named diagnostic fields'], [190, 250])
row(['VCC at 3.80 V', 'vdd within 0.05 V of the meter (config.h BANDGAP_V = 1.10 x Vmeter / Vreported)'], [190, 250], size=8.2)
row(['D9 PWM frequency', '1.9 to 2.0 kHz, confirming the 8 MHz clock'], [190, 250])
row(['Pull D2 to GND', 'cause=BUTTON_TEST, output=100%, button timer counts down'], [190, 250], size=8.4)
row(['Cover / uncover LDR', 'DUSK / DAWN confirmation reaches 300 s before mode changes'], [190, 250])
rule()

# ---------------------------------------------------------------- gate 5
head('3', 'LED string current with R3 = 47 ohm')
txt('Meter in series with the string positive, lights at 100% duty (press D2 or cover the LDR). Expect = model:', col=MUTED)
y -= 3
row(['Supply', 'Expect', 'Measured', 'R3 temp', 'Notes'], [62, 62, 80, 66, 170], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
for v, e in [('3.40 V', '11 mA'), ('3.70 V', '15 mA'), ('4.20 V', '21 mA')]:
    row([v, e, '__________', '________', '________________________'], [62, 62, 80, 66, 170], lead=17)
y -= 2
box(['Decision rule',
     'Over 22 mA at 4.20 V: fit 56 ohm and repeat the three readings (expect about 18 / 13 / 9 mA).',
     'Too bright or want longer run time: lower NIGHT_DUTY_PCT in config.h. Too dim: this design is at',
     'its limit; a brighter string needs a driver stage (docs/12-going-further.md).'])
txt('Also confirm: R3 and the D9 pin stay at ambient; the string is dark with M2 unplugged and during reset.', size=8.8, col=MUTED)
y -= 1
txt('For deployment, build pio run -e production (or standalone) and flash its .hex the same way.', size=8.2, bold=True, col=RED)

# ---------------------------------------------------------------- footer
c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(L, 46, R, 46)
c.setFont('Helvetica-Bold', 7.8); c.setFillColor(AMBER)
c.drawString(L, 34, 'REV 0.6  |  NO CELLS, PANEL OR CHARGER CONNECTED FOR THESE STEPS')
c.setFont('Helvetica', 7.8); c.setFillColor(MUTED)
c.drawRightString(R, 34, 'make_bench_sheet.py')
c.showPage(); c.save()

page = pdf.PdfDocument(str(FN))[0]
page.render(scale=2).to_pil().save(DOC / 'controller-bench-sheet.png')
print('wrote', FN)
