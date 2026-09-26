#!/usr/bin/env python3
"""One-page bench sheet for steps 1 and 2 (clock conversion, then string current).
Writes ../../output/pdf/Bench_Steps_1_2.pdf and a PNG preview in ../.
Run with a Python environment containing reportlab and pypdfium2.
"""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import pypdfium2 as pdf

DOC = Path(__file__).resolve().parents[1]
OUT = DOC.parents[1] / 'output/pdf'; OUT.mkdir(parents=True, exist_ok=True)
FN = OUT / 'Bench_Steps_1_2.pdf'
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
c.setFillColor(GREEN); c.setFont('Helvetica-Bold', 8.5); c.drawString(L, y, 'SOLARLIGHTS / REBUILD 2026'); y -= 20
c.setFillColor(INK); c.setFont('Helvetica-Bold', 17); c.drawString(L, y, 'Bench sheet: steps 1 and 2'); y -= 16
c.setFillColor(MUTED); c.setFont('Helvetica', 9.3)
c.drawString(L, y, 'Convert the clock, flash the merged firmware, then measure the string. Rev 0.4 amended, 20 Sep 2026.'); y -= 13
rule()

box(['Before you start',
     'No cells connected for any of this. Use a current-limited bench supply, 200 mA limit, for VCC.',
     'Do not connect the panel or the charger. R3 sits at the board end, not out at the string.',
     'Duty does not limit current: only R3 and the pin do. Verify at 4.20 V and 100% duty.'])

# ---------------------------------------------------------------- step 1
head('1', 'Convert the ATmega328P to internal 8 MHz, BOD 2.7 V   (closes H03)')
txt('Power the board from the ISP or a bench supply, never both. Battery and panel disconnected.', col=MUTED)
y -= 2
row(['Fuse', 'Value', 'Meaning'], [70, 62, 300], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
row(['Low', '0xE2', 'Internal 8 MHz RC, CKDIV8 off, slow rising power'], [70, 62, 300])
row(['High', '0xD9', 'Factory default: SPIEN on, no boot reset vector'], [70, 62, 300])
row(['Extended', '0xFD', 'BOD 2.7 V. avrdude may read it back as 0x05: same three bits'], [70, 62, 300])
y -= 2
txt('avrdude -c usbasp -p m328p -U lfuse:w:0xE2:m -U hfuse:w:0xD9:m -U efuse:w:0xFD:m', size=8.6, col=INK)
txt('Arduino as ISP instead: -c stk500v1 -P /dev/cu.usbmodemXXXX -b 19200', size=8.6, col=MUTED)
txt('Or MiniCore: ATmega328P, Clock "Internal 8 MHz", BOD 2.7 V, Bootloader "No bootloader", Burn Bootloader.', size=8.6, col=MUTED)
y -= 2
txt('Read back and confirm:  avrdude -c usbasp -p m328p -U lfuse:r:-:h -U hfuse:r:-:h -U efuse:r:-:h', size=8.6)
txt('Chip erase removes any bootloader. From here on, upload with the programmer, not over serial.', size=8.6, col=AMBER)
y -= 2
txt('Board work: remove the regulator and the power LED or its series resistor. Feed VCC directly, leave RAW', col=MUTED)
txt('unused, keep the local decoupling. The 16 MHz crystal can stay fitted; it is simply not selected.', col=MUTED)
y -= 3
txt('Pass: fuses read back as written, and the board runs with VCC at 3.3 V.', bold=True)
rule()

# ---------------------------------------------------------------- step 2
head('2', 'Flash the merged firmware and check it thinks straight')
txt('Build with DEBUG_SERIAL 1 and TIME_SCALE 60, F_CPU 8 MHz. Upload with the programmer. Serial at 9600.', col=MUTED)
y -= 2
row(['Check', 'Expect'], [190, 250], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
row(['Serial line per wake', 't=... vdd=3.80 state=... pct=...'], [190, 250])
row(['VCC at 3.80 V', 'vdd within 0.05 V of the meter (set BANDGAP_V = 1.10 x Vmeter / Vreported)'], [190, 250], size=8.4)
row(['D9 PWM frequency', '1.9 to 2.0 kHz, confirming the 8 MHz clock'], [190, 250])
row(['Cover the LDR 5 s', 'state goes to night, pct ramps to 100 (5 s = 5 "minutes" at TIME_SCALE 60)'], [190, 250], size=8.4)
row(['Uncover the LDR', 'state returns to day, pct fades to 0'], [190, 250])
rule()

# ---------------------------------------------------------------- gate 5
head('3', 'Gate 5: string current with R3 = 47 ohm   (settles 47 vs 56 ohm)')
txt('DMM in series with the string positive. Lights at 100% duty (LDR covered). Record what you read:', col=MUTED)
y -= 3
row(['Supply', 'Expect', 'Measured', 'R3 temp', 'Notes'], [62, 62, 80, 66, 170], bold=True, col=MUTED, size=8.5)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
for v, e in [('3.40 V', '11 mA'), ('3.70 V', '15 mA'), ('4.20 V', '21 mA')]:
    row([v, e, '__________', '________', '________________________'], [62, 62, 80, 66, 170], lead=17)
y -= 2
box(['Decision rule',
     'Over 22 mA at 4.20 V: fit 56 ohm and repeat the three readings (expect 18 / 13 / 9 mA).',
     'Within tolerance but too dim from the street at 3 am: keep 47 ohm and accept the 21 mA peak,',
     'or cap commanded duty above 4.0 V in firmware. Tell Claude which and it changes three files.'])
txt('Also confirm: R3 and the D9 pin stay at ambient; the string is dark with M2 unplugged and during reset.', size=8.8, col=MUTED)
y -= 1
txt('Then restore DEBUG_SERIAL 0 and TIME_SCALE 1 before any real-time LVC or overnight test.', size=8.8, bold=True, col=RED)

# ---------------------------------------------------------------- footer
c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(L, 46, R, 46)
c.setFont('Helvetica-Bold', 7.8); c.setFillColor(AMBER)
c.drawString(L, 34, 'NOT RELEASED FOR OUTDOOR ASSEMBLY  |  H01 and H02 remain open before cells are connected')
c.setFont('Helvetica', 7.8); c.setFillColor(MUTED)
c.drawRightString(R, 34, 'docs/tools/make_bench_sheet.py')
c.showPage(); c.save()

page = pdf.PdfDocument(str(FN))[0]
page.render(scale=2).to_pil().save(DOC / 'bench-steps-1-2.png')
print('wrote', FN)
