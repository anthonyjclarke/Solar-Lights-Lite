"""1:1 print sheet for checking real modules against the proposed Rev B geometry.
Page 1: the board with module bodies, pin holes, mounting holes and the solder row.
Page 2: each module as a full-size template to lay the real part on.
Print on A4 at 100% (Actual size). Needs reportlab. Output: review/fit-sheet-A4.pdf
Geometry matches the regenerated Rev B board (design.py).
"""
import json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, HexColor
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / 'review'
G = json.loads((OUT / 'fit-geometry.json').read_text())
W, H = A4
BW, BH = 74.0, 51.5
# --- proposed module geometry (mm) ---
PM_W, PM_L, PM_ROW, PM_P1 = 18.0, 33.3, 15.24, 4.0   # pin 1 from serial end: photo estimate (+/-0.3)
WM_W, WM_L, WM_ROW, WM_P1 = 25.6, 34.2, 22.86, 9.0
TP_W, TP_L = 17.2, 26.73
TP_X = {'-IN': 1.6, '+IN': 15.6, 'OUT-': 1.6, 'B-': 5.05, 'B+': 12.50, 'OUT+': 15.6}
TP_Y = {'-IN': 1.5, '+IN': 1.5, 'OUT-': 23.5, 'B-': 23.5, 'B+': 23.5, 'OUT+': 23.5}
TP_HOLE = 1.2
TP_LABEL_DY = {'-IN': 3.2, '+IN': 3.2, 'OUT-': 6.2, 'B-': -2.6, 'B+': -2.6, 'OUT+': 6.2}   # +ve = below the hole, -ve = above
PM_L_NAMES = ['TX', 'RX', 'RST', 'GND', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
PM_R_NAMES = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', 'D13', 'D12', 'D11', 'D10']
WM_L_NAMES = ['RST', 'A0', 'D0', 'D5', 'D6', 'D7', 'D8', '3V3']
WM_R_NAMES = ['TX', 'RX', 'D1', 'D2', 'D3', 'D4', 'G', '5V']
M2_ORG = (2.0, 2.0); M3_X = 23.0; M3_PIN1_Y = 1.7; M1_ORG = (53.0, 1.0)
HOLES = [(3.5, 47.5), (71.3, 48.0), (52.8, 31.5)]
KEEP_REFS = ('JLED1', 'JLDR1', 'JBUTTON1', 'JU3IN1', 'JU3OUT1', 'JS1', 'JCELL1', 'JPV1', 'JP1', 'JP2', 'JP3')

C = Canvas(str(OUT / 'fit-sheet-A4.pdf'), pagesize=A4)
GRAYL = HexColor('#9aa5ae')
class Frame:
    def __init__(self, ox, oy): self.ox, self.oy = ox, oy
    def p(self, x, y): return (self.ox + x) * mm, H - (self.oy + y) * mm
def txt(t, x, y, size=6, anchor='l', bold=False, col=black):
    C.setFillColor(col); C.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    {'l': C.drawString, 'c': C.drawCentredString, 'r': C.drawRightString}[anchor](x, y, t)
def ln(f, x0, y0, x1, y1, w=.3, dash=None, col=black):
    C.setStrokeColor(col); C.setLineWidth(w); C.setDash(dash) if dash else C.setDash()
    a = f.p(x0, y0); b = f.p(x1, y1); C.line(*a, *b); C.setDash()
def box(f, x0, y0, x1, y1, w=.4, dash=None, col=black):
    ln(f, x0, y0, x1, y0, w, dash, col); ln(f, x1, y0, x1, y1, w, dash, col); ln(f, x1, y1, x0, y1, w, dash, col); ln(f, x0, y1, x0, y0, w, dash, col)
def hole(f, x, y, d=1.0, square=False, cross=1.6):
    cx, cy = f.p(x, y); C.setStrokeColor(black); C.setLineWidth(.25)
    if square: C.rect(cx - d / 2 * mm, cy - d / 2 * mm, d * mm, d * mm)
    else: C.circle(cx, cy, d / 2 * mm)
    C.setLineWidth(.15); C.line(cx - cross * mm, cy, cx + cross * mm, cy); C.line(cx, cy - cross * mm, cx, cy + cross * mm)
def ruler(f, w, h, y_axis_left=True):
    C.setStrokeColor(GRAYL); C.setLineWidth(.15)
    for i in range(0, int(w) + 1):
        t = 1.6 if i % 10 == 0 else .8 if i % 5 == 0 else .4
        ln(f, i, 0, i, -t, .15, col=GRAYL)
        if i % 10 == 0: txt(str(i), f.p(i, 0)[0], f.p(i, -2.4)[1], 5, 'c', col=GRAYL)
    for j in range(0, int(h) + 1):
        t = 1.6 if j % 10 == 0 else .8 if j % 5 == 0 else .4
        ln(f, 0, j, -t, j, .15, col=GRAYL)
        if j % 10 == 0: txt(str(j), f.p(-2.0, j)[0], f.p(0, j + .6)[1], 5, 'r', col=GRAYL)
def header(n, title, sub):
    txt('SOLAR LIGHTS LITE / REV B  -  FIT SHEET (matches the regenerated board)', 15 * mm, H - 14 * mm, 8, 'l', True)
    txt(title, 15 * mm, H - 22 * mm, 14, 'l', True); txt(sub, 15 * mm, H - 28 * mm, 8)
    txt('PRINT AT 100% (Actual size, Scale: None, no fit-to-page). The bar below must measure exactly 100 mm.', 15 * mm, 24 * mm, 8, 'l', True)
    ox = 15 * mm; C.setLineWidth(.8); C.line(ox, 18 * mm, ox + 100 * mm, 18 * mm)
    for i in (0, 50, 100): C.line(ox + i * mm, 16.5 * mm, ox + i * mm, 19.5 * mm)
    txt('100 mm', ox + 50 * mm, 13.5 * mm, 7, 'c'); txt(f'{n}/2', W - 15 * mm, 13.5 * mm, 8, 'r')

# ---------------- page 1: board ----------------
header(1, 'Board overlay 1:1', 'Lay the real modules on this sheet. Pin holes are centred on cross-hairs. Square = pin 1.')
f = Frame(68, 80)
box(f, 0, 0, BW, BH, .9)
ruler(f, BW, BH)
for x, y in HOLES:
    cx, cy = f.p(x, y); C.setLineWidth(.4); C.circle(cx, cy, 1.6 * mm); C.setLineWidth(.15)
    C.line(cx - 2.2 * mm, cy, cx + 2.2 * mm, cy); C.line(cx, cy - 2.2 * mm, cx, cy + 2.2 * mm)
txt('3.2 mm holes', f.p(HOLES[1][0], HOLES[1][1] + 3.6)[0], f.p(0, HOLES[1][1] + 3.6)[1], 5, 'c')
# M2 Pro Mini
x0, y0 = M2_ORG; lx = x0 + (PM_W - PM_ROW) / 2; rx = x0 + (PM_W + PM_ROW) / 2
box(f, x0, y0, x0 + PM_W, y0 + PM_L, .5, [2, 1.5]); ln(f, x0, y0, x0 + PM_W, y0, 1.2)
txt('M2 PRO MINI', f.p(x0 + PM_W / 2, y0 + PM_L + 2.6)[0], f.p(0, y0 + PM_L + 4.0)[1], 6, 'c', True)
txt('SERIAL END', f.p(x0 + PM_W / 2, y0)[0], f.p(0, y0 - 1.0)[1], 5, 'c', True)
for i in range(12):
    y = y0 + PM_P1 + 2.54 * i
    hole(f, lx, y, 1.0, i == 0); hole(f, rx, y, 1.0, i == 0)
    txt(PM_L_NAMES[i], f.p(lx + 1.3, y)[0], f.p(0, y - .6)[1], 4.5); txt(PM_R_NAMES[i], f.p(rx - 1.3, y)[0], f.p(0, y - .6)[1], 4.5, 'r')
# M3 D1 Mini (antenna end overhangs the top edge)
lx3, rx3 = M3_X + (WM_W - WM_ROW) / 2, M3_X + (WM_W + WM_ROW) / 2; top = M3_PIN1_Y - WM_P1
box(f, M3_X, top, M3_X + WM_W, top + WM_L, .5, [2, 1.5])
ln(f, M3_X, 0, M3_X + WM_W, 0, .3, [.6, .6], GRAYL)
txt('M3 D1 MINI', f.p(M3_X + WM_W / 2, top + WM_L + 2.6)[0], f.p(0, 29.4)[1], 6, 'c', True)
txt('ANTENNA END (overhangs top edge)', f.p(M3_X + WM_W / 2, top + 1.6)[0], f.p(0, top + 3.4)[1], 5, 'c', True)
for i in range(8):
    y = M3_PIN1_Y + 2.54 * i
    hole(f, lx3, y, 1.0, i == 0); hole(f, rx3, y, 1.0, i == 0)
    txt(WM_L_NAMES[i], f.p(lx3 + 1.3, y)[0], f.p(0, y - .6)[1], 4.5); txt(WM_R_NAMES[i], f.p(rx3 - 1.3, y)[0], f.p(0, y - .6)[1], 4.5, 'r')
# M1 TP4056 (USB-C end flush with the top edge): rotate vendor frame 90 deg clockwise
box(f, M1_ORG[0], M1_ORG[1], M1_ORG[0] + TP_W, M1_ORG[1] + TP_L, .5, [2, 1.5]); ln(f, M1_ORG[0], M1_ORG[1], M1_ORG[0] + TP_W, M1_ORG[1], 1.2)
txt('M1 TP4056 (USB-C up)', f.p(M1_ORG[0] + TP_W / 2, M1_ORG[1] + TP_L + 2.6)[0], f.p(0, M1_ORG[1] + TP_L + 9.5)[1], 6, 'c', True)
for n in TP_X:
    bx, by = M1_ORG[0] + TP_W - (TP_W - TP_X[n]), M1_ORG[1] + TP_Y[n]
    hole(f, bx, by, TP_HOLE, n == '+IN')
    txt(n, f.p(bx, by)[0], f.p(0, by + TP_LABEL_DY[n] - .5)[1], 4.5, 'c', True)
# solder row and links
for p in G['pads']:
    if p['ref'] in KEEP_REFS: hole(f, p['x'], p['y'], 1.0, p['pin'] == '1', 1.2)
txt('SOLDER ROW: LED, LDR, BUTTON, U3 IN, U3 OUT, S1, CELL, PV  |  links JP3 JP2 JP1 above it', f.p(BW / 2, 0)[0], f.p(0, BH + 5)[1], 5.5, 'c')
txt('Not drawn: ISP header, C2, C3 and the resistors / Q2 / C4 under the modules (positions move when regenerated).', f.p(BW / 2, 0)[0], f.p(0, BH + 9)[1], 5.5, 'c')
y = H - 162 * mm
for t in ['Board 74 x 51.5 mm; origin is the upper-left corner, x right, y down.',
          'Dashed boxes are true module bodies. M3 sticks out above the top edge: its antenna is off the board.',
          'M1 TP4056: USB-C end flush with the top edge; IN holes at the top, OUT/B holes at the bottom.',
          'AMBER ASSUMPTIONS (mark them as you check): Pro Mini pin 1 at 4.0 mm from the serial end (photo estimate);',
          'D1 Mini pin 1 at 9.0 mm from the antenna end; rows 15.24 and 22.86 mm; TP4056 hole 1.2 mm.',
          'Mark any hole that does not line up and send me the offset.']:
    txt(t, 15 * mm, y, 8); y -= 5 * mm
C.showPage()

# ---------------- page 2: module templates ----------------
header(2, 'Module templates 1:1', 'Lay each real module on its template. Holes sit on cross-hairs; record any offset.')
# TP4056
f = Frame(20, 55)
box(f, 0, 0, TP_W, TP_L, .7); ruler(f, TP_W, TP_L)
box(f, 3.4, -2.2, 13.8, 0, .4, [1.5, 1])
txt('USB-C', f.p(TP_W / 2, -.8)[0], f.p(0, -.8)[1], 5, 'c')
for n in TP_X:
    hole(f, TP_X[n], TP_Y[n], TP_HOLE, n == '+IN', 2.0)
    txt(n, f.p(TP_X[n], 0)[0], f.p(0, TP_Y[n] + TP_LABEL_DY[n] - .5)[1], 5, 'c', True)
txt('TP4056 charger', f.p(TP_W / 2, 0)[0], f.p(0, TP_L + 5)[1], 7, 'c', True)
txt('17.2 x 26.73, USB end up', f.p(TP_W / 2, 0)[0], f.p(0, TP_L + 9)[1], 6, 'c')
# Pro Mini
f = Frame(70, 55)
lxp, rxp = (PM_W - PM_ROW) / 2, (PM_W + PM_ROW) / 2
box(f, 0, 0, PM_W, PM_L, .7); ruler(f, PM_W, PM_L); ln(f, 0, 0, PM_W, 0, 1.4)
for i in range(12):
    y = PM_P1 + 2.54 * i
    hole(f, lxp, y, 1.0, i == 0, 1.6); hole(f, rxp, y, 1.0, i == 0, 1.6)
    txt(PM_L_NAMES[i], f.p(lxp + 1.3, y)[0], f.p(0, y - .6)[1], 4.5); txt(PM_R_NAMES[i], f.p(rxp - 1.3, y)[0], f.p(0, y - .6)[1], 4.5, 'r')
txt('SERIAL END', f.p(PM_W / 2, 0)[0], f.p(0, -1.2)[1], 5, 'c', True)
txt('Pro Mini', f.p(PM_W / 2, 0)[0], f.p(0, PM_L + 5)[1], 7, 'c', True)
txt('33.3 x 18.0, serial end up', f.p(PM_W / 2, 0)[0], f.p(0, PM_L + 9)[1], 6, 'c')
# D1 Mini
f = Frame(118, 55)
lxw, rxw = (WM_W - WM_ROW) / 2, (WM_W + WM_ROW) / 2
box(f, 0, 0, WM_W, WM_L, .7); ruler(f, WM_W, WM_L)
ln(f, 0, 7.3, WM_W, 7.3, .3, [1.5, 1]); txt('ANTENNA', f.p(WM_W / 2, 0)[0], f.p(0, 3.8)[1], 5.5, 'c', True)
for i in range(8):
    y = WM_P1 + 2.54 * i
    hole(f, lxw, y, 1.0, i == 0, 1.6); hole(f, rxw, y, 1.0, i == 0, 1.6)
    txt(WM_L_NAMES[i], f.p(lxw + 1.3, y)[0], f.p(0, y - .6)[1], 4.5); txt(WM_R_NAMES[i], f.p(rxw - 1.3, y)[0], f.p(0, y - .6)[1], 4.5, 'r')
txt('micro-USB', f.p(WM_W / 2, 0)[0], f.p(0, WM_L - 1.5)[1], 5.5, 'c', True)
txt('D1 Mini', f.p(WM_W / 2, 0)[0], f.p(0, WM_L + 5)[1], 7, 'c', True)
txt('34.2 x 25.6, antenna end up', f.p(WM_W / 2, 0)[0], f.p(0, WM_L + 9)[1], 6, 'c')
# TP4056 coordinate table
y = H - 128 * mm
txt('TP4056 hole centres (mm): u from the USB end, v from the +IN / OUT+ edge', 15 * mm, y, 8, 'l', True); y -= 5.5 * mm
for n in ['+IN', '-IN', 'OUT+', 'B+', 'B-', 'OUT-']:
    txt(f'{n:<5}  u {TP_Y[n]:>5.2f}   v {TP_W - TP_X[n]:>5.2f}', 15 * mm, y, 8); y -= 4.6 * mm
y -= 3 * mm
for t in ['Pin pitch 2.54 mm; Pro Mini pin 1 4.0 mm from the serial end; D1 Mini pin 1 9.0 mm from the antenna end.',
          'Rulers along the left and top edges are in mm from each module corner.']:
    txt(t, 15 * mm, y, 8); y -= 5 * mm
C.save()
print('Wrote review/fit-sheet-A4.pdf')
