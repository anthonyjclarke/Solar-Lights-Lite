#!/usr/bin/env python3
"""Solar Lights Lite: breadboard and perfboard layout drawings.

Draws the whole system twice, once on a solderless breadboard and once on a
perfboard carrier, with parts placed so that hookup wire is kept to a minimum.
Both layouts are checked against docs/netlist.json before anything is written:
every net must be joined, no two nets may touch and no unused module pin may
be connected. Perfboard solder traces are routed here on the 0.1 in grid.

Run: python3 tools/make_layouts.py   (standard library only)
Writes docs/drawings/breadboard-layout.svg and perfboard-layout.svg, plus PNG
copies when Inkscape is installed.
"""
from pathlib import Path
import heapq, json, math, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'drawings'
NETS = json.loads((ROOT / 'docs' / 'netlist.json').read_text())['nets']
NET_OF = {t: n for n, ts in NETS.items() for t in ts}

INK, MUTED, GREEN, AMBER, RED = '#173047', '#516578', '#008572', '#ad6200', '#c1363d'
FONT = 'Helvetica, Arial, sans-serif'
LOGIC = '#12a37f'
WIRE = {
    'PV_POS': '#1f6fd1', 'PV_RETURN': '#1f6fd1',
    'CHARGE_5V': '#e8772e', 'CHARGE_RETURN': '#e8772e',
    'CELL1_POS': '#7a4bb1', 'CELL2_POS': '#7a4bb1', 'PACK_POS': '#7a4bb1', 'PACK_NEG': '#7a4bb1',
    'PROTECTED_POS': '#d63a3a', 'FUSED_POS': '#d63a3a', 'VBAT_SYS': '#d63a3a',
    'GND_LOAD': '#2a2e33', 'ESP_3V3': '#f0a500', 'WAKE': '#e9c51d', 'ADC_BATT': '#2e86de',
}
STRIPED = {'PV_RETURN', 'CHARGE_RETURN', 'PACK_NEG'}   # minus lead of a same-colour pair


def base(net):
    return net.split(':')[0]


def colour(net):
    return WIRE.get(base(net), LOGIC)


def mix(c, other, a):
    c, o = c.lstrip('#'), other.lstrip('#')
    return '#' + ''.join(f'{round(int(c[i:i + 2], 16) * (1 - a) + int(o[i:i + 2], 16) * a):02x}'
                         for i in (0, 2, 4))


def num(v):
    if isinstance(v, float):
        return f'{v:.3f}'.rstrip('0').rstrip('.')
    return str(v)


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.o = w, h, []

    def raw(self, t):
        self.o.append(t)

    @staticmethod
    def attrs(kw):
        return ''.join(f' {k.rstrip("_").replace("_", "-")}="{num(v)}"'
                       for k, v in kw.items() if v is not None)

    def el(self, tag, **kw):
        self.o.append(f'<{tag}{self.attrs(kw)}/>')

    def rect(self, x, y, w, h, **kw):
        self.el('rect', x=x, y=y, width=w, height=h, **kw)

    def circle(self, cx, cy, r, **kw):
        self.el('circle', cx=cx, cy=cy, r=r, **kw)

    def ellipse(self, cx, cy, rx, ry, **kw):
        self.el('ellipse', cx=cx, cy=cy, rx=rx, ry=ry, **kw)

    def line(self, x1, y1, x2, y2, **kw):
        self.el('line', x1=x1, y1=y1, x2=x2, y2=y2, **kw)

    def path(self, d, **kw):
        self.el('path', d=d, **kw)

    def text(self, x, y, t, size, fill=INK, bold=False, anchor='start', halo=False, **kw):
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        extra = ' font-weight="bold"' if bold else ''
        if halo:
            extra += ' stroke="#ffffff" stroke-width="3" stroke-linejoin="round" paint-order="stroke"'
        self.o.append(f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" fill="{fill}"'
                      f' text-anchor="{anchor}"{extra}{self.attrs(kw)}>{t}</text>')

    def group(self, **kw):
        self.o.append(f'<g{self.attrs(kw)}>')

    def end(self):
        self.o.append('</g>')

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">\n')
        path.write_text(head + '\n'.join(self.o) + '\n</svg>\n')


def rot(u, v, r):
    return {0: (u, v), 90: (-v, u), 180: (-u, -v), 270: (v, -u)}[r % 360]


# ---------------------------------------------------------------- part library
# Each kind is drawn in its own frame, one unit per 0.1 in hole. pins are
# (name, u, v); a name starting with '~' is a pass-through pin (terminal block,
# jumper) that carries whatever net the layout gives it.

LEAD = '#a7abb0'
PAD = '#d9b44a'


def pads(s, pins, r=0.33, fill=PAD, hole='#3a2d10'):
    for _, u, v in pins:
        s.circle(u, v, r, fill=fill, stroke=mix(fill, '#000000', 0.3), stroke_width=0.04)
        s.circle(u, v, r * 0.45, fill=hole)


def k_promini():
    top = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', 'D13', 'D12', 'D11', 'D10']
    bot = ['D1/TX', 'RX', 'RST', 'GND', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
    silk_t = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', '13', '12', '11', '10']
    silk_b = ['TXO', 'RXI', 'RST', 'GND', '2', '3', '4', '5', '6', '7', '8', '9']
    pins = [(n, i, 0) for i, n in enumerate(top)] + [(n, i, 6) for i, n in enumerate(bot)]

    def draw(s):
        s.rect(-3.3, 0.35, 2.3, 5.3, fill='none')
        for k in range(6):
            s.line(-0.6, 0.5 + k, -3.25, 0.5 + k, stroke='#8f949a', stroke_width=0.2, stroke_linecap='round')
        s.rect(-1.25, -0.5, 12.75, 7.0, fill='#1c1f24', stroke='#08090a', stroke_width=0.05, rx=0.15)
        s.rect(-1.2, 0.05, 0.75, 5.9, fill='#101112', rx=0.08)
        s.group(transform='translate(3.4,3) rotate(45)')
        s.rect(-1.25, -1.25, 2.5, 2.5, fill='#8b8f94', rx=0.05)
        s.rect(-1.05, -1.05, 2.1, 2.1, fill='#2a2d31', rx=0.08)
        s.circle(-0.7, -0.7, 0.12, fill='#555a60')
        s.end()
        s.rect(6.2, 2.3, 2.9, 1.4, fill='#c5cad1', stroke='#8a9098', stroke_width=0.05, rx=0.7)
        s.rect(9.7, 2.2, 1.3, 1.6, fill='#cfd2d6', rx=0.12)
        s.rect(10.0, 2.6, 0.7, 0.8, fill='#f2f2f2', rx=0.1)
        s.rect(5.35, 1.55, 0.8, 0.4, fill='#e3dfd3')
        s.rect(5.35, 4.05, 0.8, 0.4, fill='#e3dfd3')
        pads(s, pins)
    # serial header, top to bottom: its VCC is the same rail as top-row VCC
    head = ['DTR', 'TXO', 'RXI', 'VCC', 'GND', 'GND']
    labels = [(t, i, 0.95, 0.36, '#ffffff') for i, t in enumerate(silk_t)] + \
             [(t, i, 5.35, 0.36, '#ffffff') for i, t in enumerate(silk_b)] + \
             [(t, -2.35, k + 0.28, 0.3, RED if t == 'VCC' else MUTED) for k, t in enumerate(head)]
    return dict(pins=pins, body=(-1.25, -0.5, 11.5, 6.5), keep=[(-3.3, 0.3, -1.25, 5.7)], draw=draw, labels=labels)


def k_d1mini():
    left = ['RST', 'A0', 'D0', 'D5', 'D6', 'D7', 'D8', '3V3']
    right = ['TX', 'RX', 'D1', 'D2', 'D3', 'D4', 'G', '5V']
    pins = [(n, 0, i) for i, n in enumerate(left)] + [(n, 9, i) for i, n in enumerate(right)]

    def draw(s):
        s.rect(-0.55, -3.3, 10.1, 13.4, fill='#1f5da8', stroke='#133f73', stroke_width=0.06, rx=0.35)
        s.rect(1.5, -3.15, 6.0, 2.3, fill='#16181b', rx=0.1)
        s.path('M2.1 -1.4 V -2.7 H 2.9 V -1.7 H 3.7 V -2.7 H 4.5 V -1.7 H 5.3 V -2.7 H 6.1 V -1.7 H 6.9',
               fill='none', stroke='#c9a43f', stroke_width=0.16)
        s.rect(1.5, -0.95, 6.0, 6.1, fill='#cfd3d8', stroke='#99a0a8', stroke_width=0.05, rx=0.12)
        s.rect(1.8, -0.65, 5.4, 5.5, fill='none', stroke='#b3b9c0', stroke_width=0.05, rx=0.1)
        s.rect(3.0, 8.75, 3.0, 1.65, fill='#c6cbd0', stroke='#838a92', stroke_width=0.05, rx=0.12)
        s.rect(6.2, 6.0, 1.8, 1.2, fill='#15171a', rx=0.08)
        s.rect(0.9, 7.8, 1.1, 1.1, fill='#d0d3d7', rx=0.1)
        s.circle(1.45, 8.35, 0.3, fill='#23262a')
        pads(s, pins)
    labels = [(t, 1.05, i + 0.12, 0.36, '#ffffff') for i, t in enumerate(left)] + \
             [(t, 7.95, i + 0.12, 0.36, '#ffffff') for i, t in enumerate(right)] + \
             [('ESP8266MOD', 4.5, 2.3, 0.42, '#4d5660')]
    return dict(pins=pins, body=(-0.55, -3.3, 9.55, 10.1), draw=draw, labels=labels)


def k_tp4056():
    pins = [('IN+', 0, 0), ('IN-', 0, 5), ('OUT+', 10, 0), ('B+', 9, 1), ('B-', 9, 4), ('OUT-', 10, 5)]

    def draw(s):
        s.rect(-0.8, -0.85, 11.6, 6.7, fill='#1f62b3', stroke='#123f78', stroke_width=0.06, rx=0.2)
        s.rect(-1.25, 1.35, 2.9, 2.3, fill='#c6cbd1', stroke='#88909a', stroke_width=0.06, rx=0.5)
        s.rect(3.3, 1.6, 2.3, 1.8, fill='#17191c', rx=0.08)
        s.rect(6.9, 1.8, 1.5, 1.4, fill='#17191c', rx=0.06)
        s.rect(6.6, 0.25, 1.2, 0.75, fill='#17191c')
        s.rect(2.2, -0.05, 0.6, 0.4, fill='#ff5b5b')
        s.rect(2.2, 4.65, 0.6, 0.4, fill='#57a6ff')
        for _, u, v in pins:
            s.rect(u - 0.45, v - 0.45, 0.9, 0.9, fill='#dcdcdc', stroke='#9a9a9a', stroke_width=0.04, rx=0.12)
            s.circle(u, v, 0.18, fill='#2a2a2a')
    labels = [('IN+', 1.25, 0.12, 0.38, '#ffffff'), ('IN-', 1.25, 5.12, 0.38, '#ffffff'),
              ('OUT+', 8.6, 0.12, 0.38, '#ffffff'), ('B+', 7.9, 1.12, 0.38, '#ffffff'),
              ('B-', 7.9, 4.12, 0.38, '#ffffff'), ('OUT-', 8.6, 5.12, 0.38, '#ffffff'),
              ('TP4056 + DW01A', 4.8, 4.25, 0.36, '#cfe0f5')]
    return dict(pins=pins, body=(-1.25, -0.85, 10.8, 5.85), draw=draw, labels=labels)


def k_buck():
    pins = [('IN+', 0, 0), ('IN-', 0, 5), ('OUT+', 7, 0), ('OUT-', 7, 5)]

    def draw(s):
        s.rect(-0.8, -0.85, 8.6, 6.7, fill='#25282d', stroke='#0e1012', stroke_width=0.06, rx=0.2)
        s.rect(2.1, 1.0, 2.9, 2.9, fill='#5d636b', rx=0.4)
        s.circle(3.55, 2.45, 0.95, fill='#4b5057')
        s.rect(5.5, 3.2, 1.3, 1.3, fill='#2d6fd6', rx=0.12)
        s.path('M5.85 3.85 H 6.45 M 6.15 3.55 V 4.15', stroke='#ffffff', stroke_width=0.12)
        s.rect(0.9, 3.5, 0.9, 0.8, fill='#111214')
        for _, u, v in pins:
            s.circle(u, v, 0.45, fill='#dcdcdc', stroke='#9a9a9a', stroke_width=0.04)
            s.circle(u, v, 0.2, fill='#2a2a2a')
    labels = [('IN+', 1.1, 0.12, 0.38, '#ffffff'), ('IN-', 1.1, 5.12, 0.38, '#ffffff'),
              ('OUT+', 5.9, 0.12, 0.38, '#ffffff'), ('OUT-', 5.9, 5.12, 0.38, '#ffffff'),
              ('MP1584', 3.5, 5.0, 0.36, '#aab3bd')]
    return dict(pins=pins, body=(-0.8, -0.85, 7.8, 5.85), draw=draw, labels=labels)


def k_hl802():
    pins = [('GND', 0, 0), ('VIN', 0, 2), ('GND', 3, 0), ('VOUT', 3, 2)]

    def draw(s):
        s.rect(-0.55, -0.55, 4.1, 3.1, fill='#1b1c1e', stroke='#000000', stroke_width=0.05, rx=0.12)
        s.rect(0.9, -0.35, 2.2, 1.0, fill='#8d939a', rx=0.12)
        s.rect(1.2, 1.0, 1.6, 1.0, fill='#0c0d0e')
        for _, u, v in pins:
            s.circle(u, v, 0.34, fill=PAD)
            s.circle(u, v, 0.15, fill='#3a2d10')
    labels = [('-', 0.55, -0.02, 0.5, '#ffffff'), ('+', 0.55, 2.2, 0.5, '#ffffff'),
              ('-', 2.45, -0.02, 0.5, '#ffffff'), ('3V3', 2.2, 2.15, 0.3, '#ffffff')]
    return dict(pins=pins, body=(-0.55, -0.55, 3.55, 2.55), draw=draw, labels=labels)


BAND = {0: '#111111', 1: '#7b4a1d', 2: '#d32f2f', 3: '#f57c00', 4: '#fbc02d',
        5: '#388e3c', 6: '#1976d2', 7: '#7b1fa2', 8: '#9e9e9e', 9: '#ffffff'}


def bands(ohms):
    digits = f'{ohms:.0f}'
    mult = len(digits) - 2
    return [BAND[int(digits[0])], BAND[int(digits[1])], BAND[mult], '#c9a13b']


def k_res(span=4, ohms=10000):
    pins = [('1', 0, 0), ('2', span, 0)]

    def draw(s):
        L = min(2.5, span - 0.6)
        c = span / 2
        s.line(0, 0, span, 0, stroke=LEAD, stroke_width=0.12, stroke_linecap='round')
        s.rect(c - L / 2, -0.43, L, 0.86, fill='#dcc28f', stroke='#b3955a', stroke_width=0.05, rx=0.38)
        for i, col in enumerate(bands(ohms)):
            x = c - L / 2 + (0.45 + 0.33 * i if i < 3 else L - 0.55)
            s.rect(x, -0.42, 0.18, 0.84, fill=col)
    return dict(pins=pins, body=(0.8, -0.45, span - 0.8, 0.45), draw=draw, labels=[])


def k_cer(span=2):
    pins = [('1', 0, 0), ('2', span, 0)]

    def draw(s):
        s.line(0, 0, span, 0, stroke=LEAD, stroke_width=0.1)
        s.ellipse(span / 2, 0, 0.75, 0.48, fill='#e3992f', stroke='#b3721a', stroke_width=0.05)
    return dict(pins=pins, body=(span / 2 - 0.75, -0.48, span / 2 + 0.75, 0.48), draw=draw,
                labels=[('104', span / 2, 0.13, 0.36, '#5a3508')])


def k_elec(rad=1.0, pitch=1):
    pins = [('+', 0, 0), ('-', pitch, 0)]
    r = rad

    def draw(s):
        c = pitch / 2
        s.circle(c, 0, r, fill='#1f3f75', stroke='#11274b', stroke_width=0.06)
        a = 0.35 * r
        h = (r * r - a * a) ** 0.5
        s.path(f'M{num(c + a)} {num(-h)} A {num(r)} {num(r)} 0 0 1 {num(c + a)} {num(h)} Z', fill='#b8c6da')
        for k in (-0.35, 0.0, 0.35):
            s.rect(c + a + 0.12, k * r - 0.04, 0.22, 0.08, fill='#1f3f75')
        s.path(f'M{num(c - 0.45 * r)} 0 H {num(c + 0.2 * r)} M {num(c - 0.12 * r)} {num(-0.32 * r)} '
               f'V {num(0.32 * r)}', stroke='#6f86ad', stroke_width=0.06)
    return dict(pins=pins, body=(pitch / 2 - r, -r, pitch / 2 + r, r), draw=draw, labels=[])


def k_to92():
    pins = [('E', 0, 0), ('B', 1, 0), ('C', 2, 0)]

    def draw(s):
        s.path('M-0.1 0.45 H 2.1 A 1.1 1.4 0 0 0 -0.1 0.45 Z', fill='#1d1f22', stroke='#000000',
               stroke_width=0.05)
    return dict(pins=pins, body=(-0.1, -0.95, 2.1, 0.45), draw=draw,
                labels=[('3904', 1.0, -0.1, 0.34, '#d7dade')])


def k_ldr(span=3):
    pins = [('1', 0, 0), ('2', span, 0)]

    def draw(s):
        c = span / 2
        s.line(0, 0, span, 0, stroke=LEAD, stroke_width=0.1)
        s.circle(c, 0, 0.95, fill='#efe9dc', stroke='#b0a58c', stroke_width=0.05)
        s.circle(c, 0, 0.78, fill='#c9582e')
        s.path(f'M{num(c - 0.55)} -0.45 H {num(c + 0.55)} V -0.15 H {num(c - 0.55)} V 0.15 '
               f'H {num(c + 0.55)} V 0.45 H {num(c - 0.55)}', fill='none', stroke='#f3e6c8', stroke_width=0.1)
    return dict(pins=pins, body=(span / 2 - 0.95, -0.95, span / 2 + 0.95, 0.95), draw=draw, labels=[])


def k_tact2():
    pins = [('1', 0, 0), ('2', 0, 3)]

    def draw(s):
        s.line(0, 0, 0, 3, stroke=LEAD, stroke_width=0.14)
        s.rect(-0.85, 0.35, 1.7, 2.3, fill='#2b2d30', stroke='#000000', stroke_width=0.05, rx=0.12)
        s.circle(0, 1.5, 0.62, fill='#6b4a3a', stroke='#3f2a20', stroke_width=0.05)
    return dict(pins=pins, body=(-0.85, 0.35, 0.85, 2.65), draw=draw, labels=[])


def k_tact4():
    # 6 x 6 mm switch: pins 1 and 2 are each a pair joined inside the switch
    pins = [('1', 2, 0), ('1', 2, 3), ('2', 0, 0), ('2', 0, 3)]

    def draw(s):
        for u, v in ((0, 0), (0, 3), (2, 0), (2, 3)):
            s.rect(u - 0.18, v - 0.3, 0.36, 0.6, fill='#b9bdc2')
        s.rect(-0.25, 0.25, 2.5, 2.5, fill='#2c2e31', stroke='#000000', stroke_width=0.05, rx=0.12)
        s.circle(1, 1.5, 0.95, fill='#6b4a3a', stroke='#3f2a20', stroke_width=0.06)
        s.circle(1, 1.5, 0.7, fill='#7d5745')
    return dict(pins=pins, body=(-0.25, 0.25, 2.25, 2.75), draw=draw, labels=[])


def k_term(fill='#2f7fc9'):
    pins = [('~1', 0, 0), ('~2', 2, 0)]

    def draw(s):
        s.rect(-1.0, -1.55, 4.0, 3.0, fill=fill, stroke=mix(fill, '#000000', 0.35), stroke_width=0.06, rx=0.15)
        for u in (0, 2):
            s.rect(u - 0.62, -1.55, 1.24, 0.6, fill=mix(fill, '#000000', 0.55), rx=0.08)
            s.circle(u, 0.3, 0.62, fill='#c3c8ce', stroke='#7e868f', stroke_width=0.05)
            s.line(u - 0.42, 0.3, u + 0.42, 0.3, stroke='#5f666e', stroke_width=0.14)
    return dict(pins=pins, body=(-1.0, -1.55, 3.0, 1.45), draw=draw, labels=[])


def k_jumper():
    pins = [('~1', 0, 0), ('~2', 1, 0)]

    def draw(s):
        s.rect(-0.5, -0.5, 2.0, 1.0, fill='#161718', rx=0.06)
        s.rect(-0.45, -0.42, 1.9, 0.84, fill='#f2c200', stroke='#9c7c00', stroke_width=0.05, rx=0.12)
        s.rect(-0.2, -0.2, 1.4, 0.4, fill='#d4a900', rx=0.08)
    return dict(pins=pins, body=(-0.5, -0.5, 1.5, 0.5), draw=draw, labels=[])


KINDS = dict(promini=k_promini, d1mini=k_d1mini, tp4056=k_tp4056, buck=k_buck, hl802=k_hl802,
             res=k_res, cer=k_cer, elec=k_elec, to92=k_to92, ldr=k_ldr, tact2=k_tact2,
             tact4=k_tact4, term=k_term, jumper=k_jumper)
MODULES = {'promini', 'd1mini', 'tp4056', 'buck', 'hl802'}


class Part:
    def __init__(self, board, ref, kind, x, y, r=0, nets=None, label=None, lab=None, **opt):
        self.board, self.ref, self.kind, self.x, self.y, self.r = board, ref, kind, x, y, r
        self.k = KINDS[kind](**opt)
        self.pins = []            # (terminal or None, (x, y), net or None)
        for i, (name, u, v) in enumerate(self.k['pins']):
            du, dv = rot(u, v, r)
            if name.startswith('~'):
                self.pins.append((None, (x + du, y + dv), nets[i]))
            else:
                term = f'{ref}.{name}'
                self.pins.append((term, (x + du, y + dv), NET_OF.get(term)))
        self.boxes = []
        for u0, v0, u1, v1 in [self.k['body']] + self.k.get('keep', []):
            cs = [rot(u, v, r) for u in (u0, u1) for v in (v0, v1)]
            self.boxes.append((x + min(c[0] for c in cs), y + min(c[1] for c in cs),
                               x + max(c[0] for c in cs), y + max(c[1] for c in cs)))
        self.box = self.boxes[0]
        self.label, self.lab = label, lab

    def draw(self, s):
        b = self.board
        px, py = b.px(self.x, self.y)
        s.group(transform=f'translate({num(px)},{num(py)}) rotate({self.r}) scale({b.P})')
        self.k['draw'](s)
        s.end()
        for t, u, v, size, fill in self.k['labels']:
            du, dv = rot(u, v, self.r)
            lx, ly = b.px(self.x + du, self.y + dv)
            s.text(lx, ly + size * b.P * 0.25, t, size * b.P, fill, True, 'middle')

    def draw_label(self, s):
        if not self.label:
            return
        b = self.board
        x0, y0, x1, y1 = self.box
        gx, gy, anchor = self.lab or ((x0 + x1) / 2, y0 - 0.35, 'middle')
        lx, ly = b.px(gx, gy)
        for i, t in enumerate(self.label.split('\n')):
            plate(s, lx, ly + i * 14, t, anchor, i == 0)


class Board:
    """A hole grid (or a free drawing area when kind == 'free')."""

    def __init__(self, kind, P, ox, oy):
        self.kind, self.P, self.ox, self.oy = kind, P, ox, oy
        self.parts, self.wires = [], []

    def px(self, x, y):
        return self.ox + x * self.P, self.oy + y * self.P

    def node(self, xy):
        return (self.kind, round(xy[0], 3), round(xy[1], 3))

    def add(self, ref, kind, x, y, r=0, **kw):
        p = Part(self, ref, kind, x, y, r, **kw)
        self.parts.append(p)
        return p

    def wire(self, a, b, net, **kw):
        self.wires.append(dict(a=a, b=b, net=net, **kw))


# ------------------------------------------------------------------ checking

class Nets:
    def __init__(self):
        self.parent, self.terms = {}, {}

    def find(self, a):
        self.parent.setdefault(a, a)
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def join(self, a, b):
        self.parent[self.find(a)] = self.find(b)

    def term(self, node, name):
        self.find(node)
        if name:
            self.terms.setdefault(name, []).append(node)

    def check(self, title):
        for nodes in self.terms.values():          # one module pin name = one conductor
            for n in nodes[1:]:
                self.join(n, nodes[0])
        groups = {}
        for t, nodes in self.terms.items():
            groups.setdefault(self.find(nodes[0]), set()).add(t)
        errs = []
        for net, ts in NETS.items():
            missing = [t for t in ts if t not in self.terms]
            if missing:
                errs.append(f'{net} not placed: {missing}')
            roots = {self.find(self.terms[t][0]) for t in ts if t in self.terms}
            if len(roots) > 1:
                errs.append(f'{net} open: {[sorted(groups[r]) for r in roots]}')
        for ts in groups.values():
            nets = sorted({NET_OF[t] for t in ts if t in NET_OF})
            stray = sorted(t for t in ts if t not in NET_OF)
            if len(nets) > 1:
                errs.append(f'short {nets}')
            if nets and stray:
                errs.append(f'{nets} touches unused {stray}')
        if errs:
            raise SystemExit(f'{title} FAILED\n  ' + '\n  '.join(errs))
        print(f'{title}: {len(NETS)} nets match docs/netlist.json')


def overlaps(parts, allow=()):
    bad = []
    for i, a in enumerate(parts):
        for b in parts[i + 1:]:
            if {a.ref, b.ref} in [set(p) for p in allow]:
                continue
            for ax0, ay0, ax1, ay1 in a.boxes:
                for bx0, by0, bx1, by1 in b.boxes:
                    if min(ax1, bx1) - max(ax0, bx0) > 0.05 and min(ay1, by1) - max(ay0, by0) > 0.05:
                        bad.append(f'{a.ref}/{b.ref}')
    return bad


def inside(box, xy, m=0.0):
    return box[0] - m < xy[0] < box[2] + m and box[1] - m < xy[1] < box[3] + m


# ------------------------------------------------------------------- drawing

def round_path(pts, r=14):
    d = f'M{num(pts[0][0])} {num(pts[0][1])}'
    for (ax, ay), (bx, by), (cx, cy) in zip(pts, pts[1:], pts[2:]):
        l1 = max(abs(bx - ax), abs(by - ay)) or 1
        l2 = max(abs(cx - bx), abs(cy - by)) or 1
        k1, k2 = min(r, l1 / 2) / l1, min(r, l2 / 2) / l2
        d += (f' L {num(bx - (bx - ax) * k1)} {num(by - (by - ay) * k1)}'
              f' Q {num(bx)} {num(by)} {num(bx + (cx - bx) * k2)} {num(by + (cy - by) * k2)}')
    return d + f' L {num(pts[-1][0])} {num(pts[-1][1])}'


def wire_path(p1, p2, bend=0.18, via=None, pts=None):
    if pts:
        return round_path([p1] + list(pts) + [p2])
    (x1, y1), (x2, y2) = p1, p2
    if via:
        (cx1, cy1), (cx2, cy2) = via
        return f'M{num(x1)} {num(y1)} C {num(cx1)} {num(cy1)} {num(cx2)} {num(cy2)} {num(x2)} {num(y2)}'
    dx, dy = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) / 2 - dy * bend, (y1 + y2) / 2 + dx * bend
    return f'M{num(x1)} {num(y1)} Q {num(cx)} {num(cy)} {num(x2)} {num(y2)}'


def draw_wire(s, d, net, w, ends=None, width_scale=1.0):
    c = colour(net)
    w = w * width_scale
    s.path(d, fill='none', stroke=mix(c, '#000000', 0.45), stroke_width=w * 1.35, stroke_linecap='round')
    s.path(d, fill='none', stroke=c, stroke_width=w, stroke_linecap='round')
    if base(net) in STRIPED:
        s.path(d, fill='none', stroke='#ffffff', stroke_width=w * 0.28, stroke_dasharray=f'{num(w * 1.2)} {num(w * 0.9)}')
    s.path(d, fill='none', stroke=mix(c, '#ffffff', 0.45), stroke_width=w * 0.22, stroke_linecap='round',
           transform=f'translate(0,{num(-w * 0.18)})', opacity=0.55)
    for x, y in ends or []:
        s.circle(x, y, w * 0.55, fill='#a9aeb4', stroke='#6c7278', stroke_width=0.8)


def textw(t, size, bold=True):
    w = 0.0
    for ch in t:
        if ch in "il.,:;|!' ":
            w += 0.28
        elif ch in 'MWmw':
            w += 0.8
        elif ch.isupper() or ch == '_':
            w += 0.66
        else:
            w += 0.55
    return w * size * (1.05 if bold else 1.0)


def plate(s, x, y, t, anchor='middle', bold=True, size=12):
    w = textw(t, size, bold) + 6
    x0 = {'start': x - 3, 'middle': x - w / 2, 'end': x - w + 3}[anchor]
    s.rect(x0, y - size + 1, w, size + 4, fill='#ffffff', opacity=0.88, rx=3)
    s.text(x, y, t, size, INK if bold else MUTED, bold, anchor)


def tag(s, x, y, t, c):
    w = 6.4 * len(t) + 10
    s.rect(x - w / 2, y - 9, w, 17, fill='#ffffff', stroke=c, stroke_width=1.2, rx=8.5)
    s.text(x, y + 4, t, 10.5, mix(c, '#000000', 0.25), True, 'middle')


def header(s, W, title, sub, sheet):
    s.rect(0, 0, W, s.h, fill='#ffffff')
    s.text(42, 44, 'SOLAR LIGHTS LITE / BUILD LAYOUTS', 15, GREEN, True)
    s.text(42, 84, title, 30, INK, True)
    s.text(42, 112, sub, 15, MUTED)
    s.line(42, 130, W - 42, 130, stroke='#d5e0e6', stroke_width=1)
    s.line(42, s.h - 44, W - 42, s.h - 44, stroke='#d5e0e6', stroke_width=1)
    s.text(42, s.h - 20, 'REV 0.6  |  READ MODULE PAD LABELS, NOT BOARD POSITIONS', 12.5, GREEN, True)
    s.text(W - 42, s.h - 20, sheet, 12.5, MUTED, anchor='end')


def legend(s, x, y, items, title='WIRES'):
    s.text(x, y + 4, title, 11.5, MUTED, True)
    x += 64
    for net, t in items:
        if net == 'TRACE':
            s.line(x, y, x + 30, y, stroke='#8f98a1', stroke_width=5, stroke_linecap='round', opacity=0.7)
        else:
            draw_wire(s, f'M{x} {y} H {x + 30}', net, 5.5)
        s.text(x + 40, y + 4.5, t, 12.5, INK)
        x += 58 + textw(t, 12.5, False)


def notes(s, x, y, w, title, items, c=AMBER, fill='#fffaf0', stroke='#e5c58f'):
    h = 44 + 21 * len(items)
    s.rect(x, y, w, h, fill=fill, stroke=stroke, stroke_width=1.2, rx=12)
    s.text(x + 18, y + 27, title, 15, c, True)
    for i, t in enumerate(items):
        s.text(x + 18, y + 51 + 21 * i, t, 13, INK)
    return h


# off-board items, drawn in page pixels; each returns its terminal positions

def draw_panel(s, x, y, w=230, h=160, box='right'):
    s.rect(x + 4, y + 6, w, h, fill='#dfe4e8', rx=6)
    s.rect(x, y, w, h, fill='#b9c0c8', stroke='#8b949d', stroke_width=1.5, rx=6)
    s.rect(x + 8, y + 8, w - 16, h - 16, fill='#1d3a70')
    cw, ch = (w - 16) / 4, (h - 16) / 3
    for i in range(4):
        for j in range(3):
            cx, cy = x + 8 + i * cw, y + 8 + j * ch
            s.rect(cx + 2, cy + 2, cw - 4, ch - 4, fill='#244a8e', stroke='#2f5aa5', stroke_width=1)
            s.line(cx + cw / 2, cy + 3, cx + cw / 2, cy + ch - 3, stroke='#8fa6cf', stroke_width=0.8)
    bx = x + w - 44 if box == 'right' else x + 4
    s.rect(bx, y + h / 2 - 22, 40, 44, fill='#202226', rx=4)
    ex = x + w - 4 if box == 'right' else x + 4
    return {'+': (ex, y + h / 2 + 11), '-': (ex, y + h / 2 - 11)}


def draw_cells(s, x, y, h=190):
    """Two 18650 cells side by side in an insulated holder, negative ends up."""
    s.rect(x + 4, y + 6, 180, h, fill='#dfe4e8', rx=10)
    s.rect(x, y, 180, h, fill='#26282c', stroke='#101113', stroke_width=1.5, rx=10)
    t = {}
    for i, (ref, wrap) in enumerate((('BT1', '#3f9d5a'), ('BT2', '#2f7dd1'))):
        cx = x + 48 + i * 84
        s.rect(cx - 30, y + 18, 60, h - 36, fill=wrap, stroke=mix(wrap, '#000000', 0.35), stroke_width=1.2, rx=26)
        s.rect(cx - 20, y + 18, 7, h - 36, fill=mix(wrap, '#ffffff', 0.3), rx=3, opacity=0.6)
        s.rect(cx - 13, y + 10, 26, 8, fill='#c8ccd1', rx=2)
        s.rect(cx - 8, y + h - 18, 16, 10, fill='#c8ccd1', rx=3)
        s.text(cx, y + h / 2 - 4, ref, 13, '#ffffff', True, 'middle')
        s.text(cx, y + h / 2 + 12, '18650', 11, '#ffffff', False, 'middle')
        s.text(cx, y + 36, '-', 17, '#ffffff', True, 'middle')
        s.text(cx, y + h - 26, '+', 17, '#ffffff', True, 'middle')
        t[f'{ref}.-'] = (cx, y + 10)
        t[f'{ref}.+'] = (cx, y + h - 8)
    return t


def draw_fuse(s, x, y, ref, vertical=False, flip=False):
    w, h = (22, 64) if vertical else (64, 22)
    s.rect(x - w / 2, y - h / 2, w, h, fill='#1f2124', stroke='#000000', stroke_width=1, rx=10)
    if vertical:
        s.rect(x - 7, y - 16, 14, 32, fill='#e8b830', rx=3)
        a, b = (x, y - h / 2), (x, y + h / 2)
    else:
        s.rect(x - 16, y - 7, 32, 14, fill='#e8b830', rx=3)
        a, b = (x - w / 2, y), (x + w / 2, y)
    s.text(x, y + 4, '1A', 10, '#3a2a00', True, 'middle')
    if flip:
        a, b = b, a
    return {f'{ref}.1': a, f'{ref}.2': b}


def draw_switch(s, x, y, ref):
    s.rect(x - 24, y - 16, 48, 32, fill='#2a2c30', stroke='#000000', stroke_width=1, rx=5)
    s.circle(x, y, 11, fill='#c5cad0', stroke='#7c848d', stroke_width=1)
    s.line(x, y, x + 12, y - 20, stroke='#d9dde1', stroke_width=6, stroke_linecap='round')
    return {f'{ref}.1': (x, y - 16), f'{ref}.2': (x, y + 16)}


def draw_ledstring(s, x, y, w=250, minus_up=False):
    pts = []
    for i in range(29):
        t = i / 28
        pts.append((x + t * w, y + 20 * math.sin(t * 12.5) + 12 * t))
    s.path('M' + ' L '.join(f'{num(a)} {num(b)}' for a, b in pts), fill='none', stroke='#b87333', stroke_width=2)
    for a, b in pts[2::3]:
        s.circle(a, b, 9, fill='#fff3c4', opacity=0.7)
        s.circle(a, b, 4.5, fill='#ffd24a', stroke='#c79a00', stroke_width=1)
    x0, y0 = pts[0]
    s.rect(x0 - 12, y0 - 13, 12, 26, fill='#3b3f45', rx=3)
    up, down = (x0 - 12, y0 - 8), (x0 - 12, y0 + 8)
    return {'JLED.-': up, 'JLED.+': down} if minus_up else {'JLED.+': up, 'JLED.-': down}


def draw_ldr_probe(s, x, y):
    s.circle(x, y, 17, fill='#efe9dc', stroke='#b0a58c', stroke_width=1.2)
    s.circle(x, y, 13, fill='#c9582e')
    s.path(f'M{x - 9} {y - 7} H {x + 9} V {y - 2} H {x - 9} V {y + 3} H {x + 9} V {y + 8} H {x - 9}',
           fill='none', stroke='#f3e6c8', stroke_width=2)
    return {'LDR1.2': (x - 6, y + 17), 'LDR1.1': (x + 6, y + 17)}


def export_png(svg, scale=2):
    png = svg.with_suffix('.png')
    ink = shutil.which('inkscape') or '/Applications/Inkscape.app/Contents/MacOS/inkscape'
    if Path(ink).exists():
        w = int(svg.read_text().split('width="', 1)[1].split('"', 1)[0])
        subprocess.run([ink, str(svg), '--export-type=png', f'--export-filename={png}',
                        f'--export-width={w * scale}', '--export-background=#ffffff'],
                       check=True, capture_output=True)
        return png
    print(f'  (no Inkscape found: {png.name} not written)')
    return None


# ================================================================ breadboard

BB_ROWS = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 7, 'g': 8, 'h': 9, 'i': 10, 'j': 11}
RAIL = {-4: ('VBAT_SYS', '+'), -3: ('GND_LOAD', '-'), 14: ('GND_LOAD', '-'), 15: ('VBAT_SYS', '+')}
RAIL_COLS = [c for c in range(2, 61) if (c - 2) % 6 != 5]


def breadboard():
    W, H, P = 1800, 1334, 22
    bb = Board('bb', P, 128, 596)
    free = Board('free', P, 0, 0)

    # ---- modules and parts on the breadboard (column, row number; see BB_ROWS)
    bb.add('M3', 'd1mini', 4, 10, 270, label='M3  Wemos D1 Mini', lab=(7.5, -0.9, 'middle'))
    bb.add('U3', 'hl802', 18, 4, 90, label='U3 3.3 V', lab=(19.0, 5.85, 'start'))
    bb.add('C2', 'elec', 16, 2, 0, rad=1.25, pitch=2, label='C2 470u', lab=(19.4, 2.35, 'start'))
    bb.add('M2', 'promini', 26, 2, 0, label='M2  Pro Mini\n328P or 328PB', lab=(39.3, 4.2, 'start'))
    bb.add('Q2', 'to92', 22, 8, 180, label='Q2 2N3904', lab=(21, 7.15, 'middle'))
    bb.add('R8', 'res', 26, 10, 180, span=5, ohms=47000, label='R8 47k', lab=(23.5, 12.35, 'middle'))
    bb.add('R9', 'res', 21, 11, 90, span=3, ohms=100000, label='R9 100k', lab=(20.4, 13.4, 'end'))
    bb.add('R10', 'res', 15, 10, 0, span=5, ohms=10000, label='R10 10k', lab=(17.5, 12.35, 'middle'))
    bb.add('R5', 'res', 5, 15, 270, ohms=220000, label='R5 220k', lab=(4.4, 13.1, 'end'))
    bb.add('C4', 'cer', 29, 1, 180, label='C4 100n', lab=(26.6, 1.35, 'end'))
    bb.add('C3', 'elec', 30, -4, 90, rad=1.0, label='C3 100u', lab=(31.4, -5.05, 'start'))
    bb.add('R4', 'res', 32, 0, 270, span=3, ohms=47000, label='R4 47k', lab=(32.7, -1.1, 'start'))
    bb.add('SW1', 'tact2', 30, 11, 0, label='SW1 test', lab=(31.1, 13.0, 'start'))
    bb.add('LDR1', 'ldr', 35, 11, 0, label='LDR1', lab=(36.5, 12.8, 'middle'))
    bb.add('R3', 'res', 37, 9, 0, ohms=47, label='R3 47R', lab=(39.8, 10.45, 'middle'))
    bb.add('JP1', 'jumper', 15, 9, 0, nets=['ESP_3V3', 'ESP_3V3'], label='JP1', lab=(15.5, 7.75, 'middle'))

    # ---- jumper wires (breadboard wires carry the colour of their net)
    wires = [
        ((10, 0), (10, -3), 'GND_LOAD', {}),                          # D1 Mini G
        ((4, 11), (6, 11), 'WAKE', dict(bend=-0.55, tag='JP2 wake', tag_at=(7.9, 12.85))),
        ((11, 11), (15, 11), 'ESP_3V3', dict(bend=0.25)),
        ((8, 11), (20, 11), 'UART_RX_INVERTED', dict(bend=0.13, tag='D6 RX', tag_at=(13, 12.9))),
        ((16, 0), (16, -4), 'VBAT_SYS', {}),                          # U3 VIN
        ((18, 0), (18, -3), 'GND_LOAD', {}),                          # U3 GND
        ((22, 11), (22, 14), 'GND_LOAD', {}),                         # Q2 emitter
        ((29, 0), (29, -4), 'VBAT_SYS', {}),                          # M2 VCC
        ((27, 0), (27, -3), 'GND_LOAD', {}),                          # M2 GND
        ((32, 1), (38, 7), 'LDR_SENSE', dict(via=((35, -1.8), (40.2, 2.5)), tag='A1', tag_at=(38.6, 0.9))),
        ((60, -4), (60, 15), 'VBAT_SYS', dict(bend=0.05)),            # rail links
        ((59, -3), (59, 14), 'GND_LOAD', dict(bend=0.05)),
    ]
    for a, b, net, kw in wires:
        bb.wire(a, b, net, **kw)

    # ---- off-board power section (soldered leads, never on the breadboard)
    ext = {}
    s = Svg(W, H)
    header(s, W, 'Breadboard layout: the whole system',
           'Tier 2 jumpers fitted. The panel, charger, cells, fuses and service switch stay on soldered leads; '
           'only the protected VBAT_SYS and OUT- reach the breadboard.', 'BREADBOARD LAYOUT')
    ext.update(draw_cells(s, 150, 168))
    m1 = free.add('M1', 'tp4056', 740 / P, 316 / P, 180, label='M1  protected TP4056', lab=(28.9, 8.15, 'middle'))
    u0 = free.add('U0', 'buck', 1010 / P, 316 / P, 180, label='U0  5 V buck (Option B)', lab=(42.3, 8.15, 'middle'))
    ext.update({f'PV1.{k}': v for k, v in draw_panel(s, 1100, 182, box='left').items()})
    ext.update(draw_fuse(s, 410, 264, 'FB2'))
    ext.update(draw_fuse(s, 410, 318, 'FB1'))
    ext.update(draw_fuse(s, 520, 392, 'F2', vertical=True))
    ext.update(draw_switch(s, 612, 440, 'S1'))
    ext.update(draw_ledstring(s, 1130, 992, minus_up=True))

    # ---- nets and checks
    nets = Nets()
    for p in bb.parts + free.parts:
        brd = p.board
        for term, xy, _ in p.pins:
            nets.term(brd.node(xy), term)
    for t, xy in ext.items():
        nets.term(('ext', t), t)
    holes = {}
    for p in bb.parts:
        for term, xy, _ in p.pins:
            holes.setdefault(xy, []).append(p.ref)
    for w in bb.wires:
        for e in (w['a'], w['b']):
            holes.setdefault(e, []).append('wire')
    cables = []   # (net, end, end, drawing options)

    def pin(part, name):
        return next(xy for t, xy, _ in part.pins if t == f'{part.ref}.{name}')

    def cable(net, a, b, **kw):
        cables.append((net, a, b, kw))

    def hole(xy):
        holes.setdefault(xy, []).append('lead')
        return ('bb', xy)

    ext['SPLICE+'] = (478, 292)
    ext['SPLICE-'] = (478, 214)
    cable('PV_POS', ('ext', 'PV1.+'), ('free', pin(u0, 'IN+')))
    cable('PV_RETURN', ('ext', 'PV1.-'), ('free', pin(u0, 'IN-')))
    cable('CHARGE_5V', ('free', pin(u0, 'OUT+')), ('free', pin(m1, 'IN+')))
    cable('CHARGE_RETURN', ('free', pin(u0, 'OUT-')), ('free', pin(m1, 'IN-')))
    cable('CELL1_POS', ('ext', 'BT1.+'), ('ext', 'FB1.1'), pts=[(198, 392), (362, 392), (362, 318)])
    cable('CELL2_POS', ('ext', 'BT2.+'), ('ext', 'FB2.1'), pts=[(282, 374), (350, 374), (350, 264)])
    cable('PACK_POS', ('ext', 'FB1.2'), ('ext', 'SPLICE+'))
    cable('PACK_POS', ('ext', 'FB2.2'), ('ext', 'SPLICE+'))
    cable('PACK_POS', ('ext', 'SPLICE+'), ('free', pin(m1, 'B+')))
    cable('PACK_NEG', ('ext', 'BT1.-'), ('ext', 'SPLICE-'), pts=[(198, 160), (240, 160), (300, 206)])
    cable('PACK_NEG', ('ext', 'BT2.-'), ('ext', 'SPLICE-'), pts=[(282, 164), (360, 164), (400, 214)])
    cable('PACK_NEG', ('ext', 'SPLICE-'), ('free', pin(m1, 'B-')))
    cable('PROTECTED_POS', ('free', pin(m1, 'OUT+')), ('ext', 'F2.1'))
    cable('FUSED_POS', ('ext', 'F2.2'), ('ext', 'S1.1'))
    cable('VBAT_SYS', ('ext', 'S1.2'), hole((22, -4)))
    cable('GND_LOAD', ('free', pin(m1, 'OUT-')), hole((3, -3)), pts=[(520, 142), (100, 142), (100, 490), (194, 490)])
    cable('LED_POS', hole((41, 11)), ('ext', 'JLED.+'), via=((41.5, 17.4), (43.2, 18.2)))
    cable('GND_LOAD', hole((44, 14)), ('ext', 'JLED.-'), via=((44.2, 15.6), (44.6, 17.2)))

    # breadboard strips and wires
    for c in range(1, 64):
        for rows in ((0, 1, 2, 3, 4), (7, 8, 9, 10, 11)):
            for r in rows[1:]:
                nets.join(('bb', c, r), ('bb', c, rows[0]))
    for r in RAIL:
        for c in RAIL_COLS[1:]:
            nets.join(('bb', c, r), ('bb', RAIL_COLS[0], r))
    for w in bb.wires:
        nets.join(bb.node(w['a']), bb.node(w['b']))
    for p in bb.parts:
        if p.kind == 'jumper':
            nets.join(bb.node(p.pins[0][1]), bb.node(p.pins[1][1]))

    def node(e):
        if e[0] == 'bb':
            return bb.node(e[1])
        if e[0] == 'free':
            return free.node(e[1])
        return e

    for net, a, b, _ in cables:
        nets.join(node(a), node(b))
    nets.check('breadboard')

    errs = []
    for xy, who in holes.items():
        c, r = xy
        valid = 1 <= c <= 63 and (r in BB_ROWS.values() or (r in RAIL and c in RAIL_COLS))
        if not valid:
            errs.append(f'no hole at {xy} ({who})')
        if len(who) > 1:
            errs.append(f'two leads in {xy}: {who}')
        for p in bb.parts:
            if p.kind in MODULES and p.ref not in who and any(inside(bx, xy) for bx in p.boxes):
                errs.append(f'{who} at {xy} is under {p.ref}')
    errs += ['overlap ' + o for o in overlaps(bb.parts, allow=[('C3', 'R4')])]
    if errs:
        raise SystemExit('breadboard layout FAILED\n  ' + '\n  '.join(errs))

    # ---- draw
    used = set(holes)
    draw_bb(s, bb, used)
    for p in bb.parts:
        p.draw(s)
    for p in free.parts:
        p.draw(s)

    def page(e):
        if e[0] == 'bb':
            return bb.px(*e[1])
        if e[0] == 'free':
            return free.px(*e[1])
        return ext[e[1]]

    for net, a, b, kw in cables:
        p1, p2 = page(a), page(b)
        via = kw.get('via')
        if via and a[0] == 'bb':
            via = tuple(bb.px(*v) for v in via)
        d = wire_path(p1, p2, kw.get('bend', 0.12), via, kw.get('pts'))
        draw_wire(s, d, net, 6.2, [p for e, p in ((a, p1), (b, p2)) if e[0] == 'bb'])
    for key in ('SPLICE+', 'SPLICE-'):
        x, y = ext[key]
        s.rect(x - 9, y - 7, 18, 14, fill='#3b3f45', rx=4)
    for w in bb.wires:
        p1, p2 = bb.px(*w['a']), bb.px(*w['b'])
        via = w.get('via')
        if via:
            via = tuple(bb.px(*v) for v in via)
        draw_wire(s, wire_path(p1, p2, w.get('bend', 0.18), via), w['net'], 0.3 * P, [p1, p2])
    for p in bb.parts + free.parts:
        p.draw_label(s)
    for w in bb.wires:
        if w.get('tag'):
            tx, ty = bb.px(*w['tag_at'])
            tag(s, tx, ty, w['tag'], mix(colour(w['net']), '#000000', 0.1))

    # off-board labels
    lab = [(1215, 366, 'PV1  solar panel', 'Option A panels skip U0'), (240, 420, 'BT1 + BT2  1S2P', 'matched cells'),
           (410, 246, 'FB2 1 A', None), (410, 346, 'FB1 1 A', None), (548, 396, 'F2 1 A', None),
           (644, 444, 'S1 service', None)]
    for x, y, t, sub in lab:
        anchor = 'start' if t[:2] in ('F2', 'S1') else 'middle'
        s.text(x, y, t, 12, INK, True, anchor, halo=True)
        if sub:
            s.text(x, y + 14, sub, 11.5, MUTED, anchor=anchor, halo=True)
    lx, ly = ext['JLED.+']
    s.text(lx + 128, ly + 46, 'JLED  low-power LED string (≤ 20 mA)', 12, INK, True, 'middle', halo=True)
    tag(s, 612, 486, 'VBAT_SYS', RED)
    tag(s, 100, 330, 'OUT-', '#2a2e33')

    legend(s, 42, 1068, [('VBAT_SYS', 'VBAT_SYS / protected +'), ('GND_LOAD', 'GND_LOAD / OUT-'),
                         ('PV_POS', 'Panel'), ('CHARGE_5V', '5 V charge'), ('PACK_POS', 'Cell side'),
                         ('ESP_3V3', 'ESP 3V3'), ('WAKE', 'Removable link'), ('UART_TX', 'Logic / sensor')])
    notes(s, 42, 1092, 850, 'Build notes', [
        f'{len(bb.wires) - 2} jumper wires on the board (JP2 is the yellow D0-RST link), 2 rail links, one JP1 header.',
        'Tier 1: remove the JP1 shunt and power the D1 Mini from its USB. Remove JP2 to flash it over USB.',
        'Rails: outer red = VBAT_SYS, inner blue = GND_LOAD, linked top to bottom at columns 59 and 60.',
        'Q2 flat face toward the channel (E-B-C = columns 22-21-20). Check the pin order of your part.',
        'M1 B- stays behind the protection: never join it to OUT- or a breadboard rail.',
        'Power enters M2 top-row VCC from the rail; RAW stays empty. Regulator and power LED off first (Gate 0).',
        'Shade LDR1 from the LED string: with the lights on, ldr= may rise only a few percent (Gate 3).'])
    notes(s, 912, 1092, 846, 'Why it is laid out this way', [
        'Every module pin has one free hole beside it, so parts plug straight into the pin columns:',
        'R5 A0 to rail, R9 base to rail, R4 A1 to rail, SW1 D2 to rail, C4 across the M2 pins.',
        'U3 straddles the channel so its input and output pads never share a column.',
        'D1 Mini antenna overhangs the left end; its USB faces U3, which is low enough for the plug.',
        'Nothing sits by the M2 serial header, so a USB-UART can clip on to monitor TXO (TX to RX, GND).',
        'The whole drawing is checked against docs/netlist.json when it is generated.'],
        GREEN, '#f3faf7', '#a9d8c6')
    return s


def draw_bb(s, b, used):
    P = b.P
    x0, y0 = b.px(-0.4, -5.4)
    x1, y1 = b.px(64.4, 16.4)
    s.rect(x0 + 4, y0 + 7, x1 - x0, y1 - y0, fill='#dfe3e6', rx=12)
    s.rect(x0, y0, x1 - x0, y1 - y0, fill='#f3f3f2', stroke='#cfd3d6', stroke_width=1.5, rx=12)
    cx0, cy0 = b.px(0.2, 4.95)
    cx1, cy1 = b.px(63.8, 6.05)
    s.rect(cx0, cy0, cx1 - cx0, cy1 - cy0, fill='#e2e5e7', rx=5)
    for y, c in ((-4.7, RED), (-2.3, '#2f6fd1'), (13.3, '#2f6fd1'), (15.7, RED)):
        ax, ay = b.px(1.5, y)
        bx, _ = b.px(62.5, y)
        s.line(ax, ay, bx, ay, stroke=c, stroke_width=2)
    for r, (net, sign) in RAIL.items():
        for c in (0.3, 63.7):
            lx, ly = b.px(c, r)
            s.text(lx, ly + 5, sign, 15, RED if sign == '+' else '#2f6fd1', True, 'middle')
    for name, r in BB_ROWS.items():
        for c in (0.0, 64.0):
            lx, ly = b.px(c, r)
            s.text(lx, ly + 4, name, 11, '#9aa1a8', False, 'middle')
    for c in [1] + list(range(5, 64, 5)):
        for r in (-1.3, 12.6):
            lx, ly = b.px(c, r)
            s.text(lx, ly + 4, str(c), 10.5, '#9aa1a8', False, 'middle')
    # highlight the strips that hold a lead (as breadboard software does)
    lit = set()
    for c, r in used:
        if r in RAIL:
            lit.add((c, r, r))
        else:
            lit.add((c, 0, 4) if r <= 4 else (c, 7, 11))
    for c, ra, rb in lit:
        hx, hy = b.px(c - 0.42, ra - 0.42)
        s.rect(hx, hy, 0.84 * P, (rb - ra + 0.84) * P, fill='#c6ecc8', stroke='#96d59c', stroke_width=1, rx=4)
    for c in range(1, 64):
        for r in list(BB_ROWS.values()) + ([k for k in RAIL] if c in RAIL_COLS else []):
            hx, hy = b.px(c, r)
            s.rect(hx - 0.2 * P, hy - 0.2 * P, 0.4 * P, 0.4 * P, fill='#3d4146', rx=1.5)


# ================================================================= perfboard

PF_W, PF_H = 38, 26
ROUTE_ORDER = ['WAKE:d0', 'WAKE:rst', 'ADC_BATT', 'UART_TX', 'UART_BASE', 'UART_RX_INVERTED', 'ESP_3V3',
               'ESP_3V3:u3', 'TEST', 'PWM', 'LED_POS', 'LDR_POWER', 'LDR_SENSE', 'CHARGE_5V',
               'CHARGE_RETURN', 'PV_POS', 'PV_RETURN', 'PACK_POS', 'PACK_NEG', 'PROTECTED_POS',
               'GND_LOAD', 'VBAT_SYS']


def route(occ, pins_by_net, order, links=()):
    """Maze router for underside solder traces on the 0.1 in grid. occ maps
    each lead's hole to its net; links are top-side wires already joining two
    holes. Returns ({net: set of hole pairs}, {hole: net})."""
    used = dict(occ)
    partner = {}
    for a, b in links:
        partner.setdefault(a, []).append(b)
        partner.setdefault(b, []).append(a)
    edges = {}
    steps = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def grow(tree, h):
        stack = [h]
        while stack:
            h = stack.pop()
            if h not in tree:
                tree.add(h)
                stack.extend(partner.get(h, []))

    for net in order:
        todo = list(dict.fromkeys(pins_by_net[net]))
        tree = set()
        grow(tree, todo.pop(0))
        todo = [t for t in todo if t not in tree]
        while todo:
            heap = [(0, h, None, None) for h in tree]
            heapq.heapify(heap)
            prev, done, target = {}, set(), None
            while heap:
                d, h, came, dirn = heapq.heappop(heap)
                if h in done:
                    continue
                done.add(h)
                prev[h] = came
                if h in todo:
                    target = h
                    break
                for dx, dy in steps:
                    n = (h[0] + dx, h[1] + dy)
                    if n in done or not (0 <= n[0] < PF_W and 0 <= n[1] < PF_H):
                        continue
                    if used.get(n) not in (None, net):
                        continue
                    cost = 1 + (0.8 if dirn and dirn != (dx, dy) else 0)
                    cost += sum(0.2 for ex, ey in steps
                                if used.get((n[0] + ex, n[1] + ey)) not in (None, net))
                    heapq.heappush(heap, (d + cost, n, h, (dx, dy)))
            if target is None:
                print(ascii_map(used))
                raise SystemExit(f'perfboard: cannot route {net}; still open {todo}')
            h = target
            while prev[h] is not None:
                a = prev[h]
                edges.setdefault(net, set()).add(tuple(sorted((a, h))))
                used[a] = used[h] = net
                h = a
            grow(tree, target)
            for t in list(tree):
                grow(tree, t)
            todo = [t for t in todo if t not in tree]
    return edges, used


def ascii_map(used):
    keys = {}
    rows = []
    for y in range(PF_H):
        row = ''
        for x in range(PF_W):
            n = used.get((x, y))
            if n is None:
                row += '.'
            elif n.startswith('x:'):
                row += 'o'
            else:
                row += keys.setdefault(n, 'ABCDEFGHIJKLMNPQRSTUVWXYZabcdefghijk'[len(keys)])
        rows.append(f'{y:2d} {row}')
    return '\n'.join(rows) + '\n' + '  '.join(f'{k}={n}' for n, k in keys.items())


def perfboard():
    W, H, P = 1800, 1444, 28
    pb = Board('pb', P, 380, 196)
    add = pb.add
    add('M3', 'd1mini', 10, 1, 90, label='M3  Wemos D1 Mini', lab=(6.6, 12.35, 'middle'))
    add('M2', 'promini', 33, 1, 90, label='M2  Pro Mini\n328P or 328PB', lab=(30, 13.6, 'middle'))
    add('C4', 'cer', 34, 4, 270, label='C4', lab=(34.5, 1.35, 'middle'))
    add('R4', 'res', 35, 7, 270, ohms=47000, label='R4 47k', lab=(36.2, 5.6, 'start'))
    add('C3', 'elec', 37, 2, 180, rad=1.0, label='C3 100u', lab=(37.2, -0.9, 'middle'))
    add('R8', 'res', 26, 1, 180, ohms=47000, label='R8 47k', lab=(24, 0.2, 'middle'))
    add('SW1', 'tact4', 24, 5, 0, label='SW1 test', lab=(25, 9.35, 'middle'))
    add('Q2', 'to92', 21, 3, 180, label='Q2', lab=(22.4, 2.95, 'start'))
    add('R9', 'res', 20, 4, 90, span=3, ohms=100000, label='R9 100k', lab=(20.8, 8.3, 'middle'))
    add('R10', 'res', 18, 7, 270, span=3, ohms=10000, label='R10 10k', lab=(17.5, 5.9, 'end'))
    add('JP2', 'jumper', 14, 0, 90, nets=['WAKE:d0', 'WAKE:rst'], label='JP2', lab=(14, -0.95, 'middle'))
    add('R5', 'res', 18, 2, 180, ohms=220000, label='R5 220k', lab=(16, 1.35, 'middle'))
    add('JP1', 'jumper', 16, 8, 0, nets=['ESP_3V3:u3', 'ESP_3V3'], label='JP1', lab=(15.3, 8.3, 'end'))
    add('U3', 'hl802', 14, 10, 0, label='U3 3.3 V', lab=(15.5, 9.2, 'middle'))
    add('C2', 'elec', 14, 14, 0, rad=1.2, pitch=2, label='C2 470u', lab=(17.4, 14.35, 'start'))
    add('R3', 'res', 27, 13, 90, span=3, ohms=47, label='R3 47R', lab=(26.4, 15.6, 'end'))
    add('J4', 'term', 37, 15, 90, nets=['GND_LOAD', 'LED_POS'], label='J4 LED', lab=(37.2, 19.1, 'middle'))
    add('J5', 'term', 37, 10, 90, nets=['LDR_SENSE', 'LDR_POWER'], label='J5 LDR', lab=(37.2, 8.75, 'middle'))
    add('M1', 'tp4056', 13, 22, 180, label='M1  protected TP4056', lab=(8, 16.35, 'middle'))
    add('U0', 'buck', 23, 22, 180, label='U0  5 V buck (Option B)', lab=(19.5, 16.35, 'middle'))
    add('J1', 'term', 24, 25, 180, nets=['PV_RETURN', 'PV_POS'], label='J1 PV', lab=(26, 24.3, 'start'))
    add('J2', 'term', 0, 21, 270, nets=['PACK_POS', 'PACK_NEG'], label='J2 BATT', lab=(-0.4, 17.4, 'middle'))
    add('J3', 'term', 5, 25, 180, nets=['VBAT_SYS', 'PROTECTED_POS'], label='J3 F2/S1', lab=(7, 24.3, 'start'))
    topwires = [((34, 5), (34, 18), 'VBAT_SYS')]
    override = {'M3.D0': 'WAKE:d0', 'M3.RST': 'WAKE:rst', 'U3.VOUT': 'ESP_3V3:u3'}

    # ---- route the underside traces
    occ, pins_by_net = {}, {}
    for p in pb.parts:
        for term, xy, net in p.pins:
            net = override.get(term, net)
            key = net or f'x:{term}'
            if occ.get(xy, key) != key:
                raise SystemExit(f'perfboard: two nets in hole {xy}')
            occ[xy] = key
            if net:
                pins_by_net.setdefault(net, []).append(xy)
    for a, b, net in topwires:
        for e in (a, b):
            occ[e] = net
            pins_by_net[net].append(e)
    edges, used = route(occ, pins_by_net, ROUTE_ORDER, [(a, b) for a, b, _ in topwires])

    # ---- off-board items
    s = Svg(W, H)
    header(s, W, 'Perfboard layout: the whole system',
           'Tier 2 jumpers fitted. Modules sit in sockets or on header pins; coloured lines are the solder '
           'traces on the underside, seen through the board.', 'PERFBOARD LAYOUT')
    ext = {}
    ext.update(draw_cells(s, 30, 600))
    ext.update(draw_fuse(s, 270, 690, 'FB2'))
    ext.update(draw_fuse(s, 270, 742, 'FB1'))
    ext.update(draw_fuse(s, 400, 1010, 'F2'))
    ext.update(draw_switch(s, 540, 1010, 'S1'))
    ext.update({f'PV1.{k}': v for k, v in draw_panel(s, 1180, 960, box='left').items()})
    ext.update(draw_ldr_probe(s, 1660, 420))
    ext.update(draw_ledstring(s, 1552, 640, 220, minus_up=True))
    ext['SPLICE+'] = (318, 760)
    ext['SPLICE-'] = (318, 640)

    nets = Nets()
    for p in pb.parts:
        for term, xy, _ in p.pins:
            nets.term(pb.node(xy), term)
    for t in ext:
        nets.term(('ext', t), None if t.startswith('SPLICE') else t)
    for net, es in edges.items():
        for a, b in es:
            nets.join(pb.node(a), pb.node(b))
    for a, b, _ in topwires:
        nets.join(pb.node(a), pb.node(b))
    for p in pb.parts:
        if p.kind == 'jumper':
            nets.join(pb.node(p.pins[0][1]), pb.node(p.pins[1][1]))
    tpin, entry = {}, {}
    for p in pb.parts:
        if p.kind == 'term':
            for i, (_, xy, _) in enumerate(p.pins):
                tpin[p.ref, i] = xy
                ex, ey = rot(0, -1.3, p.r)
                entry[xy] = pb.px(xy[0] + ex, xy[1] + ey)
    cables = [
        ('PACK_POS', ('pb', tpin['J2', 0]), ('ext', 'SPLICE+'), dict(pts=[(318, 784)])),
        ('PACK_NEG', ('pb', tpin['J2', 1]), ('ext', 'SPLICE-'), dict(pts=[(318, 728)])),
        ('PACK_POS', ('ext', 'FB2.2'), ('ext', 'SPLICE+'), dict(pts=[(318, 690)])),
        ('PACK_POS', ('ext', 'FB1.2'), ('ext', 'SPLICE+'), {}),
        ('CELL2_POS', ('ext', 'BT2.+'), ('ext', 'FB2.1'), dict(pts=[(162, 810), (220, 810), (220, 690)])),
        ('CELL1_POS', ('ext', 'BT1.+'), ('ext', 'FB1.1'), dict(pts=[(78, 830), (232, 830), (232, 742)])),
        ('PACK_NEG', ('ext', 'BT1.-'), ('ext', 'SPLICE-'), dict(pts=[(78, 584), (318, 584)])),
        ('PACK_NEG', ('ext', 'BT2.-'), ('ext', 'SPLICE-'), dict(pts=[(162, 598), (304, 598), (304, 640)])),
        ('PROTECTED_POS', ('pb', tpin['J3', 1]), ('ext', 'F2.1'), dict(pts=[(464, 972), (340, 972), (340, 1010)])),
        ('FUSED_POS', ('ext', 'F2.2'), ('ext', 'S1.1'), dict(pts=[(480, 1010), (480, 994)])),
        ('VBAT_SYS', ('ext', 'S1.2'), ('pb', tpin['J3', 0]), dict(pts=[(540, 1052), (600, 1052), (600, 962), (520, 962)])),
        ('PV_POS', ('ext', 'PV1.+'), ('pb', tpin['J1', 1]), dict(pts=[(996, 1051)])),
        ('PV_RETURN', ('ext', 'PV1.-'), ('pb', tpin['J1', 0]), dict(pts=[(1052, 1029)])),
        ('LDR_SENSE', ('pb', tpin['J5', 0]), ('ext', 'LDR1.2'), dict(pts=[(1654, 476)])),
        ('LDR_POWER', ('pb', tpin['J5', 1]), ('ext', 'LDR1.1'), dict(pts=[(1666, 532)])),
        ('GND_LOAD', ('pb', tpin['J4', 0]), ('ext', 'JLED.-'), dict(pts=[(1500, 616), (1500, 632)])),
        ('LED_POS', ('pb', tpin['J4', 1]), ('ext', 'JLED.+'), dict(pts=[(1512, 672), (1512, 648)])),
    ]
    for net, a, b, _ in cables:
        nets.join(pb.node(a[1]) if a[0] == 'pb' else a, pb.node(b[1]) if b[0] == 'pb' else b)
    nets.check('perfboard')

    errs = []
    for p in pb.parts:
        for q in pb.parts:
            if q.kind in MODULES and q is not p:
                for _, xy, _ in p.pins:
                    if any(inside(bx, xy) for bx in q.boxes):
                        errs.append(f'{p.ref} lead {xy} under {q.ref}')
    for a, b, _ in topwires:
        for e in (a, b):
            for q in pb.parts:
                if q.kind in MODULES and inside(q.box, e):
                    errs.append(f'top wire end {e} under {q.ref}')
    errs += ['overlap ' + o for o in overlaps(pb.parts)]
    if errs:
        raise SystemExit('perfboard layout FAILED\n  ' + '\n  '.join(errs))

    # ---- draw
    draw_pb(s, pb)
    for p in pb.parts:
        p.draw(s)
    for net, es in edges.items():
        c = colour(net)
        for a, b in es:
            (x1, y1), (x2, y2) = pb.px(*a), pb.px(*b)
            s.line(x1, y1, x2, y2, stroke=c, stroke_width=0.36 * P, stroke_linecap='round', opacity=0.72)
    for a, b, net in topwires:
        p1, p2 = pb.px(*a), pb.px(*b)
        draw_wire(s, wire_path(p1, p2, 0.1), net, 0.3 * P, [p1, p2])

    def page(e):
        return entry[e[1]] if e[0] == 'pb' else ext[e[1]]

    for net, a, b, kw in cables:
        p1, p2 = page(a), page(b)
        draw_wire(s, wire_path(p1, p2, kw.get('bend', 0.12), None, kw.get('pts')), net, 6.2)
    for key in ('SPLICE+', 'SPLICE-'):
        x, y = ext[key]
        s.rect(x - 9, y - 7, 18, 14, fill='#3b3f45', rx=4)
    for p in pb.parts:
        p.draw_label(s)
    for x, y, t, sub in [(120, 858, 'BT1 + BT2  1S2P', 'matched cells'), (270, 674, 'FB2 1 A', None),
                         (270, 774, 'FB1 1 A', None), (400, 1042, 'F2 1 A', None), (540, 1078, 'S1 service', None),
                         (1295, 1142, 'PV1  solar panel', 'Option A panels: no U0'),
                         (1660, 396, 'LDR1', None), (1660, 580, 'JLED  LED string', '≤ 20 mA')]:
        plate(s, x, y, t)
        if sub:
            plate(s, x, y + 15, sub, bold=False)

    n_traces = sum(len(es) for es in edges.values())
    legend(s, 42, 1164, [('VBAT_SYS', 'VBAT_SYS'), ('GND_LOAD', 'GND_LOAD'), ('PV_POS', 'Panel'),
                         ('CHARGE_5V', '5 V charge'), ('PACK_POS', 'Cell side'), ('ESP_3V3', 'ESP 3V3'),
                         ('WAKE', 'Wake link'), ('UART_TX', 'Logic / sensor')], title='NETS')
    notes(s, 42, 1188, 850, 'Build notes', [
        f'One top-side wire (VBAT_SYS, red, beside M2). Everything else is solder bridge or tinned wire underneath, '
        f'about {n_traces * 2.54 / 10:.0f} cm.',
        'M2 and M3 plug into female headers. M1, U0 and U3 stand on header pins: their pads are not all on',
        '0.1 in pitch, so bend the pins to suit and follow the pad labels, not these positions.',
        'Tier 1: pull the JP1 shunt and power M3 from USB. Pull JP2 to flash M3 over USB.',
        'Cable entries: J1 panel, J2 cells, J3 to F2 and S1, J4 LED string, J5 LDR.',
        'Flash, check and rework M2 off the carrier (guides 04, 08). Power enters its VCC; RAW is never wired.',
        'Mount LDR1 where it sees the sky but not the LED string: ldr= may rise only a few percent (Gate 3).'])
    notes(s, 912, 1188, 846, 'Why it is laid out this way', [
        'M3 USB overhangs the left edge; its antenna end faces only small, low parts, away from the cells.',
        'M2 stands on end so TX, D2, D7 and D9 face the parts they drive; A1 and VCC face the right edge.',
        'Traces run under the modules between their pin rows, which is where most of the wiring hides.',
        'M1 B- only reaches J2: it never joins OUT- or any GND_LOAD trace.',
        'M2 serial header overhangs the top edge, free for a USB-UART monitor (TXO to RX, GND to GND).',
        'The whole drawing is checked against docs/netlist.json when it is generated.'],
        GREEN, '#f3faf7', '#a9d8c6')
    return s


def draw_pb(s, b):
    P = b.P
    x0, y0 = b.px(-0.75, -0.75)
    x1, y1 = b.px(PF_W - 0.25, PF_H - 0.25)
    s.rect(x0 + 5, y0 + 8, x1 - x0, y1 - y0, fill='#dfe4e8', rx=10)
    s.rect(x0, y0, x1 - x0, y1 - y0, fill='#2f8c47', stroke='#1f6a32', stroke_width=2, rx=10)
    for x in range(PF_W):
        for y in range(PF_H):
            cx, cy = b.px(x, y)
            s.circle(cx, cy, 0.34 * P, fill='#d6dade', stroke='#9fa6ab', stroke_width=0.8)
            s.circle(cx, cy, 0.13 * P, fill='#1c2a1f')
    for x in [0] + list(range(4, PF_W, 5)):
        cx, cy = b.px(x, -0.75)
        s.text(cx, cy - 5, str(x + 1), 10.5, '#9aa1a8', False, 'middle')
    for y in range(0, PF_H, 5):
        cx, cy = b.px(-0.75, y)
        s.text(cx - 6, cy + 4, chr(65 + y), 10.5, '#9aa1a8', False, 'end')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in (('breadboard-layout', breadboard), ('perfboard-layout', perfboard)):
        svg = OUT / f'{name}.svg'
        make().save(svg)
        print('  wrote', svg.relative_to(ROOT), export_png(svg) and '(+ png)')


if __name__ == '__main__':
    main()
