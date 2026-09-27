#!/usr/bin/env python3
"""One-page USBasp wiring sheet for the BTE13-010A Pro Mini.
Writes ../../output/pdf/USBasp_Wiring.pdf and a PNG preview in ../.
"""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
import pypdfium2 as pdf

DOC = Path(__file__).resolve().parents[1]
OUT = DOC.parents[1] / 'output/pdf'; OUT.mkdir(parents=True, exist_ok=True)
FN = OUT / 'USBasp_Wiring.pdf'
W, H = A4
INK = HexColor('#173047'); MUTED = HexColor('#516578'); RED = HexColor('#c1363d')
GREEN = HexColor('#008572'); AMBER = HexColor('#ad6200'); LINE = HexColor('#d5e0e6')
BLUE = HexColor('#176eb0'); YEL = HexColor('#b8860b'); GREY = HexColor('#334454')
L, R = 38, W - 38
c = Canvas(str(FN), pagesize=A4)
y = H - 46

def txt(s, size=9.2, col=INK, bold=False, dx=0, lead=13):
    global y
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size); c.setFillColor(col)
    c.drawString(L + dx, y, s); y -= lead

def head(n, s):
    global y
    y -= 6; c.setFillColor(GREEN); c.setFont('Helvetica-Bold', 10.5)
    c.drawString(L, y, f'{n}  {s}'); y -= 16

def rule(gap=8):
    global y
    y -= gap - 5; c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(L, y, R, y); y -= gap

def row(cells, widths, size=9, bold=False, col=INK, lead=13.5, dx=0):
    global y
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size); c.setFillColor(col)
    x = L + dx
    for cell, w in zip(cells, widths):
        c.drawString(x, y, cell); x += w
    y -= lead

# header
c.setFillColor(GREEN); c.setFont('Helvetica-Bold', 8.5); c.drawString(L, y, 'SOLARLIGHTS / REBUILD 2026'); y -= 20
c.setFillColor(INK); c.setFont('Helvetica-Bold', 17); c.drawString(L, y, 'USBasp application-firmware upload'); y -= 16
c.setFillColor(MUTED); c.setFont('Helvetica', 9.3)
c.drawString(L, y, 'Six wires. Every pin you need is on the board\'s top row. Nothing else connected: no FTDI, no battery, no string.'); y -= 14
rule()

# ---- USBasp header drawing
head('1', 'The USBasp 10-pin header, looking at the connector')
bx, by, cw, ch = L + 10, y - 62, 52, 26
names = [('1 MOSI', GREEN), ('2 VCC', RED), ('3 NC', MUTED), ('4 GND', GREY), ('5 RST', AMBER),
         ('6 GND', GREY), ('7 SCK', YEL), ('8 GND', GREY), ('9 MISO', BLUE), ('10 GND', GREY)]
for i, (nm, col) in enumerate(names):
    cx = bx + (i // 2) * cw; cy = by + (0 if i % 2 else ch)
    c.setStrokeColor(LINE); c.setFillColor(white); c.rect(cx, cy, cw - 4, ch - 4, fill=1, stroke=1)
    c.setFillColor(col); c.setFont('Helvetica-Bold', 8.6); c.drawCentredString(cx + (cw - 4) / 2, cy + 9, nm)
c.setFillColor(INK); c.setFont('Helvetica-Bold', 8.4)
c.drawString(bx - 2, by + 2 * ch + 4, 'odd row: 1 3 5 7 9')
c.drawString(bx - 2, by - 12, 'even row: 2 4 6 8 10')
c.setFillColor(MUTED); c.setFont('Helvetica', 8.6)
c.drawString(bx + 5 * cw + 16, by + ch + 12, 'Pin 1 is marked with a dot, a triangle or a')
c.drawString(bx + 5 * cw + 16, by + ch + 1, 'square pad. On a ribbon cable it is the red')
c.drawString(bx + 5 * cw + 16, by + ch - 10, 'stripe. Only 1, 2, 5, 7, 9 and one GND are used.')
y = by - 26

# ---- Pro Mini strip
head('2', 'The Pro Mini top row, board the right way up, FTDI header on the left')
pins = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', '13', '12', '11', '10']
used = {'GND': GREY, 'RST': AMBER, 'VCC': RED, '13': YEL, '12': BLUE, '11': GREEN}
pw = (R - L - 20) / len(pins)
py = y - 30
for i, p in enumerate(pins):
    px = L + 10 + i * pw
    col = used.get(p)
    c.setStrokeColor(LINE if not col else col); c.setLineWidth(1 if not col else 1.6)
    c.setFillColor(HexColor('#f4f1ea') if not col else white)
    c.rect(px, py, pw - 5, 26, fill=1, stroke=1)
    c.setFillColor(col or MUTED); c.setFont('Helvetica-Bold' if col else 'Helvetica', 9)
    c.drawCentredString(px + (pw - 5) / 2, py + 9, p)
c.setFillColor(MUTED); c.setFont('Helvetica', 8.6)
c.drawString(L + 10, py - 13, 'Coloured pins are the six you use. A4 to A7 are the unpopulated holes at the far end; ignore them.')
y = py - 34

# ---- table
head('3', 'The six connections')
row(['USBasp', 'Signal', 'Pro Mini pin', 'Suggested wire'], [90, 90, 130, 140], bold=True, col=MUTED, size=8.6)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
for a, b, d, w, col in [('Pin 1', 'MOSI', '11', 'green', GREEN), ('Pin 9', 'MISO', '12', 'blue', BLUE),
                        ('Pin 7', 'SCK', '13', 'yellow', YEL), ('Pin 5', 'RESET', 'RST', 'orange', AMBER),
                        ('Pin 2', 'VCC', 'VCC', 'red', RED), ('Pin 4, 6, 8 or 10', 'GND', 'GND', 'black', GREY)]:
    row([a, b, d, w], [90, 90, 130, 140], col=col)
c.setFillColor(AMBER); c.setFont('Helvetica-Bold', 8.8)
c.drawString(L, y, 'RESET goes to RST, not to a numbered pin. MOSI and MISO are the pair people swap: 11 out, 12 back.'); y -= 16
rule()

# ---- jumpers and commands
head('4', 'USBasp setup, then the commands')
txt('The target is already converted to internal 8 MHz. Routine application uploads never rewrite its fuses.', col=AMBER, bold=True)
txt('Use a verified target-compatible 3.3 V power and logic configuration for the isolated rebuilt controller.', col=MUTED)
txt('Some clone voltage jumpers change target power but not signal level: verify the actual unit with a meter.', col=MUTED)
txt('JP2 is only for updating the USBasp\'s own firmware. Leave it open.', col=MUTED)
txt('JP3, "slow SCK": fit it if the chip will not answer. Old clone firmware ignores avrdude\'s -B option.', col=MUTED)
y -= 3
txt('Plug the USBasp into the Mac. No driver is needed on macOS. Test first, this writes nothing:', col=INK)
txt('avrdude -c usbasp -p m328p -v', size=8.8, bold=True)
txt('Expect: Device signature = 0x1e950f. Stop if it differs, or reads all 00 / all ff.', size=8.8, col=GREEN)
y -= 3
txt('From SolarLights_Lite/firmware/lite_controller, compile and upload the diagnostic build:', col=INK)
txt('platformio run -e pro8_usbasp_debug', size=8.8, bold=True)
txt('platformio run -e pro8_usbasp_debug -t upload', size=8.8, bold=True)
txt('Use pro8_usbasp instead for the quiet production build. A successful upload must verify flash.', size=8.6, col=MUTED)
rule()

# ---- troubleshooting
head('5', 'If it will not talk')
row(['Message', 'Usual cause'], [250, 230], bold=True, col=MUTED, size=8.6)
c.setStrokeColor(LINE); c.line(L, y + 9, R, y + 9)
for a, b in [('could not find USB device 0x16c0/0x5dc', 'USBasp not enumerated: cable, hub, or a dead clone'),
             ('device signature = 0x000000', 'No power at the target, or a loose wire. Check VCC on the board'),
             ('signature reads as 0xffffff', 'MISO not connected, or MOSI and MISO swapped'),
             ('initialization failed, rc=-1', 'SCK too fast: fit JP3, or try -B 8'),
             ('warning: cannot set sck period', 'Harmless on old clone firmware. Use JP3 instead')]:
    row([a, b], [250, 230], size=8.6)
y -= 2
c.setFillColor(RED); c.setFont('Helvetica-Bold', 8.8)
c.drawString(L, y, 'Never add fuse-write options to a routine application upload. Disconnect ISP before restoring battery power.')

c.setStrokeColor(LINE); c.setLineWidth(0.8); c.line(L, 46, R, 46)
c.setFont('Helvetica-Bold', 7.8); c.setFillColor(AMBER)
c.drawString(L, 34, 'CANONICAL PROCEDURE: firmware/lite_controller/PROGRAMMING.md')
c.setFont('Helvetica', 7.8); c.setFillColor(MUTED)
c.drawRightString(R, 34, 'docs/tools/make_usbasp_sheet.py')
c.showPage(); c.save()
pdf.PdfDocument(str(FN))[0].render(scale=2).to_pil().save(DOC / 'usbasp-wiring.png')
print('wrote', FN)
