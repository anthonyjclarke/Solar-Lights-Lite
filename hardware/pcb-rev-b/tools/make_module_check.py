"""Draw the module geometry Rev B will be built from, for the user to check against
the real parts BEFORE the board is regenerated. Green = given by the user / vendor
drawing, amber = assumed or read off a drawing, red = open question.
Needs reportlab and pypdfium2. Output: review/module-check.pdf and .png.
Text sizes are in paper millimetres; coordinates inside a panel are module millimetres.
"""
import json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor, white
import pypdfium2
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / 'review'
G = json.loads((OUT / 'fit-geometry.json').read_text())
GREEN = HexColor('#0a7a3d'); AMBER = HexColor('#c77700'); RED = HexColor('#c0152f')
INK = HexColor('#173047'); GRAY = HexColor('#7d8a96'); PAD = HexColor('#e0b000'); BLUEFILL = HexColor('#e8f3ff')
MM = 2.8346457

# ---------------- proposed geometry (mm) ----------------
TP_W, TP_L = 17.2, 26.73                                  # width: vendor; length: measured by you (vendor said 28)
TP_X = {'-IN': 1.6, '+IN': 15.6, 'OUT-': 1.6, 'B-': 5.05, 'B+': 12.50, 'OUT+': 15.6}   # from left edge, USB end up
TP_Y_IN, TP_Y_OUT = 1.5, 23.5                              # from the USB end; rows 22 mm apart (measured, vendor said 23)
TP_HOLE, TP_PAD = 1.2, 2.2                                # hole 1.2 inferred from your 7.7 mm; pad assumed
PM_W, PM_L, PM_ROW, PM_P1 = 18.0, 33.3, 15.24, 4.0
PM_L_NAMES = ['TX', 'RX', 'RST', 'GND', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
PM_R_NAMES = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', 'D13', 'D12', 'D11', 'D10']
WM_W, WM_L, WM_ROW, WM_P1 = 25.6, 34.2, 22.86, 9.0
WM_L_NAMES = ['RST', 'A0', 'D0', 'D5', 'D6', 'D7', 'D8', '3V3']
WM_R_NAMES = ['TX', 'RX', 'D1', 'D2', 'D3', 'D4', 'G', '5V']
M1_ORG = (53.0, 1.0)                                      # board position of the TP4056 outline corner (USB end at top edge)

C = Canvas(str(OUT / 'module-check.pdf'), pagesize=(420 * MM, 297 * MM))
CUR = [1.0]
def at(x, y, s=1.0):
    CUR.append(s); C.saveState(); C.translate(x * MM, (297 - y) * MM); C.scale(s * MM, -s * MM)
def done(): CUR.pop(); C.restoreState()
def text(t, x, y, size=2.2, col=INK, anchor='l', bold=False, mono=False):
    if len(CUR) == 1:
        at(0, 0, 1); text(t, x, y, size, col, anchor, bold, mono); done(); return
    C.setFillColor(col); C.setFont('Courier-Bold' if (mono and bold) else 'Courier' if mono else 'Helvetica-Bold' if bold else 'Helvetica', size / CUR[-1] * MM)
    C.saveState(); C.translate(x, y); C.scale(1 / MM, -1 / MM)
    {'l': C.drawString, 'c': C.drawCentredString, 'r': C.drawRightString}[anchor](0, 0, t); C.restoreState()
def line(x0, y0, x1, y1, col=INK, w=.15):
    C.setStrokeColor(col); C.setLineWidth(w); C.line(x0, y0, x1, y1)
def rect(x0, y0, x1, y1, col=INK, w=.25, dash=None, fill=None):
    C.setStrokeColor(col); C.setLineWidth(w); C.setDash(dash) if dash else C.setDash()
    if fill is not None: C.setFillColor(fill)
    C.rect(x0, y0, x1 - x0, y1 - y0, stroke=1, fill=0 if fill is None else 1); C.setDash()
def hole(x, y, d, pad, col=INK, square=False):
    C.setFillColor(PAD); C.setStrokeColor(col); C.setLineWidth(.15)
    if square: C.rect(x - pad / 2, y - pad / 2, pad, pad, fill=1)
    else: C.circle(x, y, pad / 2, fill=1)
    C.setFillColor(white); C.circle(x, y, d / 2, fill=1)
def dim_h(x0, x1, y, label, col, below=False):
    line(x0, y, x1, y, col)
    for x in (x0, x1): line(x, y - .7, x, y + .7, col)
    text(label, (x0 + x1) / 2, y + (2.0 if below else -0.7) * (1 / CUR[-1]) * 1.5, 2.3, col, 'c', True)
def dim_v(y0, y1, x, label, col, side='l'):
    line(x, y0, x, y1, col)
    for y in (y0, y1): line(x - .7, y, x + .7, y, col)
    text(label, x - 0.6 if side == 'l' else x + 0.6, (y0 + y1) / 2 + .5, 2.3, col, 'r' if side == 'l' else 'l', True)

text('Solar Lights Lite Rev B: module geometry (board regenerated with these values)', 12, 13, 5, INK, 'l', True)
text('Compare each drawing with the real module.   GREEN = given by you / vendor drawing.   AMBER = assumed or read off a drawing.   RED = I need your answer.',
     12, 20, 2.6, GRAY)

# ---------------- 1. TP4056 ----------------
ox, oy, S = 30, 62, 2.7
text('1  TP4056 charger module', 12, 30, 3.4, INK, 'l', True)
text('Vendor orientation: USB-C up, +IN / OUT+ on the right', 12, 35, 2.2, GRAY)
at(ox, oy, S)
rect(0, 0, TP_W, TP_L, GREEN, .3, fill=BLUEFILL)
rect(3.4, -1.8, 13.8, 4.8, GRAY, .2, fill=HexColor('#dcdcdc')); text('USB-C', TP_W / 2, 2.2, 2.3, INK, 'c', True)
pts = {'-IN': (TP_X['-IN'], TP_Y_IN), '+IN': (TP_X['+IN'], TP_Y_IN), 'OUT-': (TP_X['OUT-'], TP_Y_OUT),
       'B-': (TP_X['B-'], TP_Y_OUT), 'B+': (TP_X['B+'], TP_Y_OUT), 'OUT+': (TP_X['OUT+'], TP_Y_OUT)}
for n, (x, y) in pts.items():
    hole(x, y, TP_HOLE, TP_PAD, GREEN, square=(n == '+IN'))
text('-IN', -.9, 2.8, 2.2, INK, 'r', True); text('+IN', TP_W + .9, 2.8, 2.2, INK, 'l', True)
text('OUT-', pts['OUT-'][0], TP_Y_OUT + 3.3, 2.0, INK, 'c', True); text('B-', pts['B-'][0] + 1.9, TP_Y_OUT - 1.8, 2.0, INK, 'l', True)
text('B+', pts['B+'][0] - 1.9, TP_Y_OUT - 1.8, 2.0, INK, 'r', True); text('OUT+', pts['OUT+'][0], TP_Y_OUT + 3.3, 2.0, INK, 'c', True)
text('IN- = OUT- (joined)', TP_W / 2, 12.5, 2.0, GREEN, 'c', True); text('B- not joined', TP_W / 2, 15.5, 2.0, GREEN, 'c', True)
dim_h(0, TP_W, -3.2, '17.2', GREEN); dim_h(TP_X['-IN'], TP_X['+IN'], -6.2, '14', GREEN)
dim_v(0, TP_L, -3.0, '26.73', GREEN); dim_v(TP_Y_IN, TP_Y_OUT, -7.6, '22', GREEN)
dim_h(TP_X['OUT-'], TP_X['B-'], TP_L + 3.2, '3.45', GREEN, True)
dim_h(TP_X['B-'], TP_X['B+'], TP_L + 3.2, '7.45', GREEN, True)
dim_h(TP_X['B+'], TP_X['OUT+'], TP_L + 3.2, '3.10', GREEN, True)
dim_v(0, TP_Y_IN, TP_W + 3.2, '1.5', GREEN, 'r'); dim_v(TP_Y_OUT, TP_L, TP_W + 3.2, '3.23', AMBER, 'r')
line(TP_X['B-'] + 1.0, TP_Y_OUT + 3.0, TP_X['B+'] - 1.0, TP_Y_OUT + 3.0, GREEN)
done()
yb = oy + TP_L * S + 24
text('Your markup: length 26.73 (not 28), rows 22 apart (not 23), IN row 1.5, bottom 3.0.', 12, yb, 2.2, GREEN, 'l', True)
text('7.7 mm = gap between the B- and B+ hole edges -> hole about 1.2 mm?', 12, yb + 5, 2.2, RED, 'l', True)
text('Copper pad size not given: 2.2 mm assumed (carrier side is unaffected).', 12, yb + 9, 2.2, AMBER, 'l', True)

# ---------------- 2. Pro Mini ----------------
ox, oy, S = 168, 62, 2.5
text('2  Pro Mini (BTE13-010A clone)', 150, 30, 3.4, INK, 'l', True)
text('Serial end up, as placed on the carrier. Only the two 12-pin rows are used', 150, 35, 2.2, GRAY)
at(ox, oy, S)
rect(0, 0, PM_W, PM_L, GREEN, .3, fill=BLUEFILL)
rect(1.4, .3, PM_W - 1.4, 1.5, GRAY, .15, dash=[.5, .4]); text('6-pin serial header: not on carrier', PM_W / 2, -.8, 1.9, GRAY, 'c')
lx, rx = (PM_W - PM_ROW) / 2, (PM_W + PM_ROW) / 2
for i in range(12):
    y = PM_P1 + 2.54 * i
    hole(lx, y, 1.0, 1.7, AMBER, square=(i == 0)); hole(rx, y, 1.0, 1.7, AMBER, square=(i == 0))
    text(PM_L_NAMES[i], lx + 1.2, y + .45, 1.8, INK, 'l'); text(PM_R_NAMES[i], rx - 1.2, y + .45, 1.8, INK, 'r')
dim_h(0, PM_W, -3.2, '18.0', GREEN); dim_v(0, PM_L, -3.0, '33.3', GREEN)
dim_h(lx, rx, PM_L + 3.2, '15.24', AMBER, True)
dim_v(PM_P1, PM_P1 + 27.94, PM_W + 3.4, '27.94', AMBER, 'r')
dim_v(0, PM_P1, PM_W + 3.4, '4.0 ?', AMBER, 'r'); dim_v(PM_P1 + 27.94, PM_L, PM_W + 3.4, '1.36', AMBER, 'r')
done()
yb = oy + PM_L * S + 24
text('33.3 x 18.0, 27.94 span (2.54 pitch): ticked.  Pin 1 at 4.0 from the serial end.', 150, yb, 2.2, GREEN, 'l', True)
text('Photo of the real board gives 4.0 / 1.36 (sums to 33.3); 3.4 / 2.5 did not. Please re-check.', 150, yb + 5, 2.2, RED, 'l', True)
text('Row spacing 15.24 ticked. Template must be printed at exactly 100%.', 150, yb + 9, 2.2, AMBER, 'l', True)

# ---------------- 3. D1 Mini ----------------
ox, oy, S = 300, 62, 2.5
text('3  Wemos D1 Mini', 285, 30, 3.4, INK, 'l', True)
text('Antenna end up, as placed on the carrier', 285, 35, 2.2, GRAY)
at(ox, oy, S)
rect(0, 0, WM_W, WM_L, GREEN, .3, fill=BLUEFILL)
C.setFillColor(HexColor('#f4d9a8')); C.rect(.4, .3, WM_W - .8, 7.0, fill=1, stroke=0)
text('ANTENNA (off board)', WM_W / 2, 4.4, 2.0, INK, 'c', True)
text('ESP-12 shield', WM_W / 2, 18, 1.9, GRAY, 'c'); text('micro-USB', WM_W / 2, WM_L - 1.5, 2.0, INK, 'c', True)
lx, rx = (WM_W - WM_ROW) / 2, (WM_W + WM_ROW) / 2
for i in range(8):
    y = WM_P1 + 2.54 * i
    hole(lx, y, 1.0, 1.7, AMBER, square=(i == 0)); hole(rx, y, 1.0, 1.7, AMBER, square=(i == 0))
    text(WM_L_NAMES[i], lx + 1.2, y + .45, 1.8, INK, 'l'); text(WM_R_NAMES[i], rx - 1.2, y + .45, 1.8, INK, 'r')
dim_h(0, WM_W, -3.2, '25.6', GREEN); dim_v(0, WM_L, -3.0, '34.2', GREEN)
dim_h(lx, rx, WM_L + 3.2, '22.86', AMBER, True)
dim_v(WM_P1, WM_P1 + 17.78, WM_W + 3.4, '17.78', AMBER, 'r')
dim_v(0, WM_P1, WM_W + 3.4, '9.0 ?', RED, 'r'); dim_v(WM_P1 + 17.78, WM_L, WM_W + 3.4, '7.42', AMBER, 'r')
done()
yb = oy + WM_L * S + 24
text('34.2 x 25.6: given.  Row spacing 22.86 (0.9 in) is standard: assumed.', 285, yb, 2.2, AMBER, 'l', True)
text('Pin 1 (RST, square) centre to antenna-end edge: please measure.', 285, yb + 5, 2.2, RED, 'l', True)

# ---------------- 4. Board overlay ----------------
ox, oy, S = 14, 190, 1.9
BW, BH = 74, 51.5
text('4  Board 74 x 51.5 mm with the new module sizes', 12, 182, 3.4, INK, 'l', True)
text('Dashed = module bodies.  Red = new TP4056 and Pro Mini holes.  Grey = other holes on the current board.', 12, 187, 2.2, GRAY)
at(ox, oy, S)
rect(0, 0, BW, BH, INK, .3, fill=HexColor('#eef5ee'))
rect(2.0, 2.0, 2.0 + PM_W, 2.0 + PM_L, AMBER, .25, [.8, .5]); text('M2 Pro Mini', 11, 1.2, 1.9, AMBER, 'c', True)
rect(23.0, 0, 23.0 + WM_W, 26.9, AMBER, .25, [.8, .5]); text('M3 D1 Mini (top end overhangs the board)', 35.8, 24.9, 1.9, AMBER, 'c', True)
rect(M1_ORG[0], M1_ORG[1], M1_ORG[0] + TP_W, M1_ORG[1] + TP_L, GREEN, .3, [.8, .5])
for p in G['pads']:
    if p['ref'].startswith('H'):
        C.setStrokeColor(INK); C.setLineWidth(.15); C.setFillColor(white); C.circle(p['x'], p['y'], p['drill'] / 2, fill=1); continue
    if p['ref'] in ('JM2L1', 'JM2R1'): continue
    hole(p['x'], p['y'], p['drill'], p['width'], GRAY)
for i in range(12):
    for xx in (2.0 + (PM_W - PM_ROW) / 2, 2.0 + (PM_W + PM_ROW) / 2):
        hole(xx, 2.0 + PM_P1 + 2.54 * i, 1.0, 1.7, RED)
new = {}
for n, (x, y) in pts.items():
    u, v = y, TP_W - x
    bx, by = M1_ORG[0] + TP_W - v, M1_ORG[1] + u; new[n] = (u, v, bx, by)
    hole(bx, by, 1.2, 2.2, RED, square=(n == '+IN'))
    text(n, bx, by + (-2.3 if y < 10 else 3.6), 1.9, RED, 'c', True)
text('TP4056 17.2 x 26.73, USB-C flush with top edge', M1_ORG[0] + TP_W / 2, 31.0, 1.9, GREEN, 'c', True)
done()

# ---------------- legend ----------------
x0, y0 = 190, 190
text('What I will build from (after you confirm)', x0, y0, 3.4, INK, 'l', True)
text('TP4056 hole centres', x0, y0 + 8, 2.4, INK, 'l', True)
text('pad    u(from USB end)  v(from +side edge)  carrier x,y', x0, y0 + 12.5, 2.0, GRAY, 'l', False, True)
for i, n in enumerate(['+IN', '-IN', 'OUT+', 'B+', 'B-', 'OUT-']):
    u, v, bx, by = new[n]
    text(f'{n:<6} {u:>8.1f}        {v:>9.2f}        {bx:>6.2f},{by:>6.2f}', x0, y0 + 17 + i * 4.2, 2.0, AMBER if n.endswith('IN') else GREEN, 'l', False, True)
rows = [(GREEN, 'IN- = OUT- on the module: no extra link on the carrier, JPV1 pad 2 is ground through the module.'),
        (GREEN, 'B- not joined to OUT-: B- stays its own net on the carrier.'),
        (GREEN, 'TP4056 17.2 x 26.73; Pro Mini 33.3 x 18.0 (pin 1 at 4.0 mm); D1 Mini 34.2 x 25.6; side sockets only.'),
        (AMBER, 'Assumed (standard): Pro Mini rows 15.24; D1 Mini rows 22.86; pin pitch 2.54; TP4056 pad 2.2.'),
        (RED, 'CHECK A  Is your 7.7 mm the gap between the B- and B+ hole edges (so hole = 1.2 mm)?'),
        (RED, 'CHECK B  Pro Mini pin 1 at 4.0 / far end 1.36 (from your photo, +/-0.3): please confirm with calipers.'),
        (RED, 'OPEN 3   D1 Mini: pin 1 (RST) centre to antenna-end edge (9.0 assumed). Not on your sheet.'),
        (RED, 'OPEN 4   Socket height (8.5 mm assumed); parts under modules need about 6 mm clear.'),
        (GRAY, 'On regenerate: Pro Mini pins move down 2.0 mm (pin 1 y 6.0); TP4056 body ends at y 27.7; silk shifts.')]
for i, (col, t) in enumerate(rows): text(t, x0, y0 + 48 + i * 5.4, 2.1, col, 'l', col in (RED,))
C.save()
pdf = pypdfium2.PdfDocument(str(OUT / 'module-check.pdf'))
pdf[0].render(scale=2.4).to_pil().save(OUT / 'module-check.png')
print('Wrote review/module-check.pdf and review/module-check.png')
