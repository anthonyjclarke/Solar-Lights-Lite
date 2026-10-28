"""Create a three-page review PDF with an actual-size fit template for Rev C.
Uses exported PCB geometry (fit-geometry.json) and the module envelopes in design.py.
Needs reportlab and pypdfium2 (pip install into a venv); run after export.py and a pcb render.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from design import (ROOT, BW, BH, HOLES, M1_BODY, M2_BODY, M3_BODY, M1_PADS_BOARD)
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
import pypdfium2
OUT = ROOT / 'review'
G = json.loads((OUT / 'fit-geometry.json').read_text()); V = json.loads((OUT / 'validation.json').read_text())
W, H = A4; C = Canvas(str(OUT / 'pcb-review.pdf'), pagesize=A4)
INK = HexColor('#173047'); TEAL = HexColor('#008572'); GRAY = HexColor('#516578'); AMBER = HexColor('#b36b00')
STYLE = ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, textColor=INK)
def para(txt, x, y, width=170 * mm):
    p = Paragraph(txt, STYLE); _, height = p.wrap(width, 600); p.drawOn(C, x, y - height); return y - height - 10
def title(n, caption):
    C.setFillColor(TEAL); C.setFont('Helvetica-Bold', 10); C.drawString(20 * mm, H - 19 * mm, 'SOLAR LIGHTS LITE / PCB REV C')
    C.setFillColor(INK); C.setFont('Helvetica-Bold', 20); C.drawString(20 * mm, H - 31 * mm, caption)
    C.setFillColor(GRAY); C.setFont('Helvetica', 9)
    C.drawString(20 * mm, H - 40 * mm, '28-Oct-2026 | Rev C | CAD checks pass; supplier DFM not run')
    C.setStrokeColor(HexColor('#c6d6df')); C.line(20 * mm, 18 * mm, W - 20 * mm, 18 * mm)
    C.setFont('Helvetica', 8); C.drawString(20 * mm, 12 * mm, 'KiCad 10.0.6 | See README.md for wiring, links and assembly steps')
    C.drawRightString(W - 20 * mm, 12 * mm, str(n))

title(1, 'Carrier with charger: layout')
image = ImageReader(str(OUT / 'pcb-top.png')); iw, ih = image.getSize(); rw = 170 * mm; rh = rw * ih / iw
C.drawImage(image, 20 * mm, H - 48 * mm - rh, width=rw, height=rh)
y = H - 54 * mm - rh
y = para(f'{BW} x {BH} mm carrier (about {BW * BH:,.0f} mm2, under half of Rev A). Pro Mini M2 and optional D1 Mini M3 are '
         'socketed; the TP4056 charger M1, the TEST button SW1 and the RV1 dusk trimmer sit on the board; every external connection is a 2.54 mm solder point. '
         'The image is a KiCad render: modules are not modelled.', 20 * mm, y)
y = para('External: panel, U0 (5 V buck, if needed), U3 (3.3 V buck-boost), cells, S1, the LED string and the LDR. '
         '<b>No fuses.</b> B- is its own net and never joins ground; only M1 OUT- is the load return.', 20 * mm, y)
y = para(f'<b>CAD checks:</b> zero ERC/DRC violations, zero unrouted connections and schematic parity issues; '
         f'{len(V["checks"])} independent/model checks recorded.', 20 * mm, y)
para('<b>Before ordering:</b> print review/fit-sheet-A4.pdf at 100% and lay the real modules on it. Pro Mini, D1 Mini and '
     'the four TP4056 corner holes were confirmed on the 16-Oct fit sheet; the TP4056 B- and B+ holes were re-measured '
     '(3.45 / 7.45 / 3.10 mm) and must now centre on the new sheet. '
     'Also confirm 8.5 mm sockets leave about 6 mm under the modules.', 20 * mm, y)
C.showPage()

title(2, 'Actual-size fit check')
y = H - 50 * mm
y = para('Print at <b>Actual size / 100%</b> (scaling off). Check the 50 mm line, then lay the real modules on the template.', 20 * mm, y)
ox = (W - BW * mm) / 2; oy = H - 78 * mm - BH * mm
def xy(x, yy): return ox + x * mm, oy + (BH - yy) * mm
C.setLineWidth(.35); C.setStrokeColor(INK); C.rect(ox, oy, BW * mm, BH * mm)
def body(b, label, ly=None, col=TEAL):
    x0, y0, x1, y1 = b; C.setStrokeColor(col); C.setDash(2, 2)
    a, bb = xy(x0, y1); C.rect(a, bb, (x1 - x0) * mm, (y1 - y0) * mm); C.setDash()
    C.setFillColor(col); C.setFont('Helvetica-Bold', 6); C.drawCentredString(*xy((x0 + x1) / 2, ly if ly is not None else (y0 + y1) / 2), label)
body(M2_BODY, 'M2 Pro Mini', M2_BODY[3] - 1.3); body(M3_BODY, 'M3 D1 Mini', M3_BODY[3] - 1.3); body(M1_BODY, 'M1 TP4056', col=AMBER)
C.setStrokeColor(INK); C.setFillColor(INK)
for pad in G['pads']:
    x, yy = xy(pad['x'], pad['y']); w = pad['width'] * mm; h = pad['height'] * mm
    if round(pad['angle']) % 180: w, h = h, w
    if pad['ref'].startswith('H'):
        C.circle(x, yy, pad['drill'] * mm / 2); continue
    if pad['rect']: C.rect(x - w / 2, yy - h / 2, w, h)
    else: C.ellipse(x - w / 2, yy - h / 2, x + w / 2, yy + h / 2)
    C.setFillColor(white); C.circle(x, yy, pad['drill'] * mm / 2, fill=1, stroke=1); C.setFillColor(INK)
C.setFont('Helvetica', 5)
for ref in ('JM2L1', 'JM2R1', 'JM3L1', 'JM3R1', 'JISP1', 'M1', 'JP1', 'JP2', 'JP3'):
    p = next(p for p in G['pads'] if p['ref'] == ref and p['pin'] in ('1',))
    x, yy = xy(p['x'] - 1.4, p['y'] - .5); C.drawRightString(x, yy, ref + ' 1')
C.setFont('Helvetica', 8); C.drawCentredString(ox + BW * mm / 2, oy - 5 * mm, f'{BW} x {BH} mm outline; square pads mark pin 1; amber = TP4056 envelope')
cx = ox; cy = oy - 16 * mm; C.setLineWidth(.7); C.line(cx, cy, cx + 50 * mm, cy)
for x in (cx, cx + 50 * mm): C.line(x, cy - 2 * mm, x, cy + 2 * mm)
C.drawCentredString(cx + 25 * mm, cy - 5 * mm, '50 mm calibration line')
y = oy - 30 * mm
for t in ['M2 Pro Mini: rows 15.24 mm apart, pitch 2.54, body 18 x 33.3 mm, pin 1 about 4.0 mm from the serial end; serial header end up (heavy line). Parts under it: R3, R4, C4.',
          'M3 D1 Mini: rows 22.86 mm apart; body 25.6 x 34.2 mm; antenna end overhangs the top edge, USB end faces the board. Parts under it: R5, R8, R9, R10, Q2.',
          '<b>M1 TP4056:</b> 17.2 x 26.73 mm; holes 14 mm apart at the USB end, rows 22 mm apart, bottom holes 3.45 / 7.45 / 3.10 mm (measured); hole 1.2 mm. '
          'See review/fit-sheet-A4.pdf for a 1:1 check.',
          'Parts under a module need under about 6 mm of height with 8.5 mm sockets; C2, C3, RV1 and SW1 stay beside the modules.',
          'ISP lies on its side below the Pro Mini, outlined for an optional DC3-6P box header (key slot down); a plain 2x3 header fits the same holes.',
          'Mounting: 3.2 mm holes at (3.5, 48), (71.3, 48), (52.8, 31.5) mm from the upper-left corner.']:
    y = para(t, 20 * mm, y)
C.showPage()

title(3, 'Qualification and service')
data = [['Tier', 'JP1 power', 'JP2 wake', 'JP3 ADC'], ['0 standalone', 'Open', 'Open', 'Open'],
        ['1 USB telemetry', 'OPEN', 'Open to flash', 'Closed while powered'],
        ['2 battery telemetry', 'Closed; USB absent', 'Closed after flashing', 'Closed']]
table = Table(data, colWidths=[48 * mm, 40 * mm, 40 * mm, 42 * mm], rowHeights=10 * mm)
table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), TEAL), ('TEXTCOLOR', (0, 0), (-1, 0), white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), .3, HexColor('#c6d6df'))]))
table.wrapOn(C, 170 * mm, 100 * mm); table.drawOn(C, 20 * mm, H - 96 * mm)
y = H - 106 * mm
items = [('1. Module fit', 'Measure the TP4056 pad holes first. Verify M2/M3 rows, body outlines and socket height against page 2.'),
         ('2. Charger prep', 'Replace the module PROG resistor for 100-150 mA before soldering it on. Meter IN- to OUT- to see whether the module joins them.'),
         ('3. Unpowered continuity', 'No rail short; B- not joined to ground; S1 open isolates OUT+ from VBAT_SYS; JP1/JP3 isolate their feeds.'),
         ('4. In-circuit ISP', 'Open S1, then program M2 through JISP1. If the programmer supplies VCC it must be set to 3.3 V.'),
         ('5. LED current', 'Record peak current at 100% duty: 3.40 V ____ mA; 3.70 V ____ mA; 4.20 V ____ mA; warm ____ mA. Target <= 20 mA.'),
         ('6. Telemetry and supply', 'Q2 EBC, inverted 9600-baud reception, ADC calibration; U3 output ____ V; sleep current ____ uA.'),
         ('7. Charger and outdoor soak', 'Original Gates 0-8: charge current/termination, cold panel Voc, leakage, temperature limits, energy balance.')]
for heading, body_text in items: y = para('<b>' + heading + '</b><br/>' + body_text, 20 * mm, y)
y = para('<b>Known limits:</b> no fuses (only the module protection), no temperature charge inhibit, no power-path charger, '
         'no automatic USB/U3 interlock, no protection against an LED cable short at D9. USB-C on M1 shares the solar input: never use both.', 20 * mm, y)
para('Builder: ____________________  Date: ____________________<br/>Fit checked: ____  Electrical gates passed: ____  Ordering release: ____', 20 * mm, y)
C.save()
pdf = pypdfium2.PdfDocument(str(OUT / 'pcb-review.pdf'))
for i, page in enumerate(pdf): page.render(scale=1.5).to_pil().save(OUT / f'pcb-review-page-{i + 1}.png')
print('Created 3-page review PDF and rendered all pages for visual QA')
