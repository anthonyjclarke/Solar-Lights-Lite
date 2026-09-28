#!/usr/bin/env python3
"""Generate the SolarLights Lite v0.5 current-build KiCad schematic:
direct pin-drive LED branch (no Q1/R6/R7/F1), 1S2P per-cell fusing, a
main-rail service switch, U0/U3 regulators, and the NPN-inverted D1/TX to
D6 development-UART receiver. Writes to its own project so the
Rev 0.3 audit-baseline schematic in ../../kicad/ is untouched.

Needs KiCad's stock symbol libraries (KICAD_LIBS, default /usr/share/kicad/symbols).
"""
import os, re, uuid, json

LIBDIR = os.environ.get("KICAD_LIBS", "/usr/share/kicad/symbols")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.makedirs(os.path.join(OUT, "tools"), exist_ok=True)
PRJ = "SolarLights_Lite_Current"
NS = uuid.UUID("9f2d77a1-55b6-4f2e-9a11-77c0de5501ac")
U = lambda: str(uuid.uuid4())
SU = lambda r: str(uuid.uuid5(NS, r))
ROOT = str(uuid.uuid5(NS, "root"))
E = '(effects (font (size 1.27 1.27)))'
EH = '(effects (font (size 1.27 1.27)) hide)'

# ----------------------------------------------------------------- parts
P = {}
def part(ref, lib, val, at, pins, fp="", note="", dnp=False, hide_val=False):
    P[ref] = dict(lib=lib, val=val, at=at, pins=pins, fp=fp, note=note, dnp=dnp, hide_val=hide_val)

RES = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
CAP = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
ECAP = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"

# --- solar input, regulator (TBD), charger, cells --------------------------
part("J1", "Connector_Generic:Conn_01x02", "PV in", (30, 45, 180), {"1": "PV+", "2": "GND"}, note="screw terminal")
part("U0", "SolarLights_Lite:Reg5V_TBD", "5 V reg - TBD", (85, 45, 0),
     {"IN+": "PV+", "IN-": "GND", "OUT+": "IN+", "OUT-": "GND"},
     note="module not yet selected - see BUILD_GUIDE.md")
part("M1", "SolarLights_Lite:TP4056_DW01A", "TP4056 + DW01A", (135, 55, 0),
     {"IN+": "IN+", "IN-": "GND", "B+": "BATT_BUS", "B-": "BATT-", "OUT+": "OUT+", "OUT-": "GND", "CHRG": "CHRG"},
     note="charger + protection; CHRG not wired")
part("FB1", "Device:Fuse", "1 A", (120, 84, 90), {"1": "BATT_BUS", "2": "BATT1+"})
part("FB2", "Device:Fuse", "1 A", (150, 84, 90), {"1": "BATT_BUS", "2": "BATT2+"})
part("BT1", "Device:Battery_Cell", "18650", (120, 95, 0), {"1": "BATT1+", "2": "BATT-"})
part("BT2", "Device:Battery_Cell", "18650", (150, 95, 0), {"1": "BATT2+", "2": "BATT-"})
part("F2", "Device:Fuse", "1 A", (177, 40, 90), {"1": "OUT+", "2": "VBAT_SW"})
part("S1", "Switch:SW_SPST", "service", (192, 40, 0), {"1": "VBAT_SW", "2": "VBAT"})
# --- controller (BTE13-010A Pro Mini, converted to internal 8 MHz) --------
part("M2", "SolarLights_Lite:Pro_Mini_BTE13", "BTE13-010A - int. 8 MHz", (230, 120, 0),
     {"VCC": "VBAT", "GND": "GND", "A1": "LDR_SENSE", "D2": "BTN",
      "D7": "LDR_PWR", "D1": "UART_TX", "D8": "NC_D8", "D9": "PWM", "A0": "NC_A0",
      "D10": "NC_D10", "D11": "NC_D11"},
     note="RAW unused; A0/D10/D11 reserved, left open")
part("C3", "Device:C_Polarized", "100u", (196, 128, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP)
part("SW1", "Switch:SW_Push", "test", (270, 190, 0), {"1": "BTN", "2": "GND"})
part("LDR1", "SolarLights_Lite:LDR", "LDR", (140, 185, 0), {"1": "LDR_PWR", "2": "LDR_SENSE"})
part("R4", "Device:R", "100k", (172, 196, 0), {"1": "LDR_SENSE", "2": "GND"}, fp=RES)
# --- development telemetry: NPN-inverted D1/TX to D6 UART receiver ---------
part("R8", "Device:R", "47k", (275, 130, 90), {"1": "UART_TX", "2": "Q2_BASE"}, fp=RES)
part("R9", "Device:R", "100k", (275, 148, 0), {"1": "Q2_BASE", "2": "GND"}, fp=RES, note="base-emitter pulldown")
part("Q2", "Device:Q_NPN_BCE", "2N3904", (295, 130, 0), {"1": "Q2_BASE", "2": "D1_D6", "3": "GND"},
     note="development UART inverter")
part("R10", "Device:R", "10k", (330, 118, 0), {"1": "D1_D6", "2": "3V3_TEL"}, fp=RES, note="pull-up to 3V3_TEL")
# --- LED driver: direct pin drive, no Q1/R6/R7/F1 --------------------------
part("R3", "Device:R", "47R", (355, 68, 0), {"1": "PWM", "2": "LED+"}, fp=RES,
     note="measured string, ~15 mA @3.7 V; try 56R for <20 mA @4.2 V")
part("J2", "Connector_Generic:Conn_01x02", "LED string", (375, 78, 0), {"1": "LED+", "2": "LED-"}, note="screw terminal")
# --- D1 Mini + its own 3.3 V supply (TBD) ----------------------------------
part("U3", "SolarLights_Lite:Reg3V3_TBD", "3V3 tel. - HL802A cand.", (300, 205, 0),
     {"IN+": "VBAT", "IN-": "GND", "OUT+": "3V3_TEL", "OUT-": "GND"},
     note="TPS63802/HL802A breakout, jumper=3.3V; candidate, not bench-qualified")
part("C2", "Device:C_Polarized", "470u", (283, 205, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP, note="at U3 input")
part("M3", "SolarLights_Lite:D1_Mini", "Wemos D1 Mini", (330, 175, 0),
     {"5V": "3V3_TEL", "G": "GND", "A0": "D1_A0", "D5": "NC_D5", "D6": "D1_D6", "D0": "D0RST", "RST": "D0RST"},
     note="ESPHome v0.5 dev UART; always-on; onboard regulator removed")
part("R5", "Device:R", "220k", (290, 150, 0), {"1": "VBAT", "2": "D1_A0"}, fp=RES, note="battery sense, unaffected by U3")

CUSTOM = {
 "TP4056_DW01A": dict(ref="M", w=17.78,
   left=[("IN+", "IN+"), ("IN-", "IN−")],
   right=[("OUT+", "OUT+"), ("OUT-", "OUT−"), ("CHRG", "CHRG")],
   bottom=[("B+", "B+"), ("B-", "B−")]),
 "Pro_Mini_BTE13": dict(ref="M", w=19.05,
   left=[("VCC", "VCC"), ("GND", "GND"), ("A0", "A0"), ("A1", "A1")],
   right=[("D9", "D9 PWM"), ("D1", "D1 TX"), ("D8", "D8 open"), ("D2", "D2 btn"), ("D10", "D10"), ("D11", "D11"), ("D7", "D7 LDR")]),
 "D1_Mini": dict(ref="M", w=17.78,
   left=[("5V", "5V"), ("G", "G"), ("A0", "A0"), ("D6", "D6")],
   right=[("D5", "D5"), ("D0", "D0"), ("RST", "RST")]),
 "LDR": dict(ref="LDR", w=5.08, left=[("1", "")], right=[("2", "")]),
 "Reg5V_TBD": dict(ref="U", w=10.16, left=[("IN+", "IN+"), ("IN-", "IN−")], right=[("OUT+", "OUT+"), ("OUT-", "OUT−")]),
 "Reg3V3_TBD": dict(ref="U", w=10.16, left=[("IN+", "IN+"), ("IN-", "IN−")], right=[("OUT+", "OUT+"), ("OUT-", "OUT−")]),
}

def custom_symbol(name, d, prefix=""):
    n = max(len(d["left"]), len(d["right"]))
    h = (int(((n + 1) * 2.54) / 2 / 2.54) + 1) * 2.54
    w = d["w"]
    o = [f'  (symbol "{prefix}{name}" (in_bom yes) (on_board yes)',
         f'    (property "Reference" "{d["ref"]}" (at {-w} {h+2.54} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))',
         f'    (property "Value" "{name}" (at {-w} {-h-2.54} 0) (effects (font (size 1.27 1.27)) (justify left top)))',
         f'    (property "Footprint" "" (at 0 0 0) {EH})',
         f'    (property "Datasheet" "" (at 0 0 0) {EH})',
         f'    (symbol "{name}_0_1" (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'    (symbol "{name}_1_1"']
    for i, (num, nm) in enumerate(d["left"]):
        o.append(f'      (pin passive line (at {-w-2.54:.2f} {h - 2.54*(i+1):.2f} 0) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
    for i, (num, nm) in enumerate(d["right"]):
        o.append(f'      (pin passive line (at {w+2.54:.2f} {h - 2.54*(i+1):.2f} 180) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
    for i, (num, nm) in enumerate(d.get("bottom", [])):
        x = -w / 2 + i * w
        o.append(f'      (pin passive line (at {x:.2f} {-h-2.54:.2f} 90) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
    o.append('    )\n  )')
    return "\n".join(o)

# ---------------------------------------------------------------- symbols
def sexpr(t, i):
    d = 0
    for j in range(i, len(t)):
        if t[j] == '(': d += 1
        elif t[j] == ')':
            d -= 1
            if d == 0: return t[i:j+1]
_c = {}
def stock(lib_id):
    lib, name = lib_id.split(":")
    if lib not in _c: _c[lib] = open(os.path.join(LIBDIR, lib + ".kicad_sym")).read()
    t = _c[lib]
    blk = sexpr(t, t.find(f'\n  (symbol "{name}"') + 3)
    assert "(extends" not in blk.split("\n")[0], lib_id
    return blk
PIN_RE = re.compile(r'\(pin \w+ \w+ \(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]*)"', re.S)
pins_of = lambda b: {m.group(4): (float(m.group(1)), float(m.group(2)), int(m.group(3))) for m in PIN_RE.finditer(b)}

SYMS = {}
for ref, p in list(P.items()) + [("_gnd", dict(lib="power:GND")), ("_nc", dict(lib="power:GND"))]:
    lid = p["lib"]
    if lid in SYMS: continue
    if lid.startswith("SolarLights_Lite:"):
        nm = lid.split(":")[1]
        body = custom_symbol(nm, CUSTOM[nm], prefix="SolarLights_Lite:")
        SYMS[lid] = (body, pins_of(body))
    else:
        blk = stock(lid)
        SYMS[lid] = ("  " + blk.replace(f'(symbol "{lid.split(":")[1]}"', f'(symbol "{lid}"', 1), pins_of(blk))

# rotation of a library pin into sheet coordinates (verified against KiCad)
def xf(sx, sy, ang, px, py):
    if ang == 0:   return (sx + px, sy - py)
    if ang == 90:  return (sx - py, sy - px)
    if ang == 180: return (sx - px, sy + py)
    return (sx + py, sy + px)          # 270

PIN = {}
for ref, p in P.items():
    sx, sy, ang = p["at"]
    for num, (px, py, _) in SYMS[p["lib"]][1].items():
        PIN[(ref, num)] = xf(sx, sy, ang, px, py)
pin = lambda ref, num: PIN[(ref, str(num))]

# ---------------------------------------------------------------- drawing
items, gnds, ncs, SEGS = [], [], [], []
R2D = lambda v: round(v, 2)
def wire(pts):
    """Record an orthogonal run. Segments are split later so every tap lands on
    a wire END - KiCad only connects wires that share an endpoint."""
    for a, b in zip(pts, pts[1:]):
        a, b = (R2D(a[0]), R2D(a[1])), (R2D(b[0]), R2D(b[1]))
        if a != b:
            SEGS.append((a, b))
def junction(x, y):
    pass          # junctions are worked out automatically from the split points
def gnd(x, y):
    gnds.append((x, y))
def noconnect(x, y):
    ncs.append((x, y))
def label(net, x, y, ang=0):
    j = "right bottom" if ang == 180 else "left bottom"
    items.append(f'  (label "{net}" (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))')
def text(s, x, y, size=2.54, bold=True):
    b = " bold" if bold else ""
    items.append(f'  (text "{s}" (at {x} {y} 0) (effects (font (size {size} {size}) (thickness 0.508){b}) (justify left bottom)) (uuid "{U()}"))')

# ---- block titles
text("1  Panel in - U0 (TBD 5 V reg) - TP4056 charger - cells", 20, 24)
text("2  Battery rail: fused 1S2P + service switch", 185, 24)
text("3  LED driver: direct drive, no MOSFET", 340, 24)
text("4  Arduino (BTE13-010A) - dusk/dawn, schedule, PWM", 180, 100)
text("5  Wemos D1 Mini - reports to Home Assistant", 296, 163)

# ---- PV chain -> U0 -> charger --------------------------------------------
wire([pin("J1", 1), pin("U0", "IN+")])
wire([pin("J1", 2), (25, pin("J1", 2)[1]), (25, 62)]); gnd(25, 62)
wire([(25, 62), (25, 51), pin("U0", "IN-")])
wire([pin("U0", "OUT+"), (105, 45), (105, pin("M1", "IN+")[1]), pin("M1", "IN+")])
wire([pin("U0", "OUT-"), (85, 60), (108, 60), (108, 66)]); gnd(108, 66)
wire([pin("M1", "IN-"), (108, pin("M1", "IN-")[1]), (108, 66)])
wire([pin("M1", "OUT-"), (160, pin("M1", "OUT-")[1]), (160, 62)]); gnd(160, 62)
noconnect(pin("M1", "CHRG")[0], pin("M1", "CHRG")[1])
# cells: each behind its own fuse off the shared BATT_BUS node
bp, bn = pin("M1", "B+"), pin("M1", "B-")
wire([bp, (bp[0], 78), (120, 78), pin("FB1", 1)])
wire([(120, 78), (150, 78), pin("FB2", 1)])
wire([pin("FB1", 2), pin("BT1", 1)])
wire([pin("FB2", 2), pin("BT2", 1)])
wire([bn, (bn[0], 70), (168, 70), (168, 105), (120, 105), pin("BT1", 2)])
wire([(150, 105), pin("BT2", 2)])
# ---- battery rail: main fuse then service switch --------------------------
wire([pin("M1", "OUT+"), (170, pin("M1", "OUT+")[1]), (170, 40), pin("F2", 1)])
wire([pin("F2", 2), pin("S1", 1)])
RAIL_Y = 40
wire([pin("S1", 2), (196, RAIL_Y)])
wire([(196, RAIL_Y), (390, RAIL_Y)])
def rail_drop(x, to_pin):
    wire([(x, RAIL_Y), (x, to_pin[1]), to_pin])
rail_drop(196, pin("C3", 1))
rail_drop(215, pin("M2", "VCC"))
rail_drop(283, pin("C2", 1))
rail_drop(290, pin("R5", 1))
wire([pin("C3", 2), (196, 140)]); gnd(196, 140)
# ---- Pro Mini (BTE13-010A) -------------------------------------------------
wire([pin("M2", "GND"), (204, pin("M2", "GND")[1]), (204, 132)]); gnd(204, 132)
noconnect(*pin("M2", "A0"))
noconnect(*pin("M2", "D8"))
noconnect(*pin("M2", "D10"))
noconnect(*pin("M2", "D11"))
# D9 straight to R3 - no gate driver
wire([pin("M2", "D9"), (258, pin("M2", "D9")[1]), (258, 68), pin("R3", 1)])
# D1/TX -> base resistor -> Q2 (development UART inverter); R9 pulls the base down
wire([pin("M2", "D1"), (pin("R8", 1)[0], pin("M2", "D1")[1]), pin("R8", 1)])
wire([pin("R8", 2), pin("Q2", 1)])
bx = (pin("R8", 2)[0] + pin("Q2", 1)[0]) / 2
wire([(bx, pin("R8", 2)[1]), (bx, pin("R9", 1)[1]), pin("R9", 1)])
wire([pin("R9", 2), (pin("R9", 2)[0], pin("R9", 2)[1] + 6)]); gnd(pin("R9", 2)[0], pin("R9", 2)[1] + 6)
# test button
wire([pin("M2", "D2"), (254, pin("M2", "D2")[1]), (254, 190), pin("SW1", 1)])
wire([pin("SW1", 2), (282, 190), (282, 198)]); gnd(282, 198)
# switched LDR - now fitted by default (SENSOR_LDR=1)
wire([pin("M2", "D7"), (259, pin("M2", "D7")[1])]); label("LDR_PWR", 259, pin("M2", "D7")[1])
wire([pin("M2", "A1"), (190, pin("M2", "A1")[1])]); label("LDR_SENSE", 190, pin("M2", "A1")[1], 180)
wire([pin("LDR1", 1), (124, pin("LDR1", 1)[1])]); label("LDR_PWR", 124, pin("LDR1", 1)[1], 180)
wire([pin("LDR1", 2), (172, pin("LDR1", 2)[1]), pin("R4", 1)])
label("LDR_SENSE", 172, pin("LDR1", 2)[1])
wire([pin("R4", 2), (172, 203)]); gnd(172, 203)
# ---- LED driver: R3 direct from D9 to the string --------------------------
wire([pin("R3", 2), (355, 78), pin("J2", 1)])
wire([pin("J2", 2), (322, 78), (322, 90)]); gnd(322, 90)
# ---- Q2 (development UART inverter): emitter to GND, collector feeds D1_D6 -
ex, ey = pin("Q2", 3)
wire([(ex, ey), (ex, 142)]); gnd(ex, 142)
cx, cy = pin("Q2", 2)
r10x, r10y = pin("R10", 1)
wire([(cx, cy), (cx, r10y), pin("R10", 1)])
# collector net continues right to the D1 Mini D6 UART receiver
wire([(cx + 20, r10y), (365, r10y), (365, pin("M3", "D6")[1]), pin("M3", "D6")])
# ---- D1 Mini + its own telemetry supply U3 ---------------------------------
wire([pin("M3", "G"), (305, pin("M3", "G")[1]), (305, 186)]); gnd(305, 186)
wire([pin("R5", 2), (290, 175), pin("M3", "A0")])
noconnect(*pin("M3", "D5"))
wire([pin("M3", "D0"), (358, pin("M3", "D0")[1]), (358, pin("M3", "RST")[1]), pin("M3", "RST")])
# 3V3_TEL node: R10 bottom, U3 output and M3 5V all meet at (r10x, 205)
wire([pin("R10", 2), (r10x, 205)])
wire([pin("U3", "OUT+"), (r10x, 205)])
wire([pin("M3", "5V"), (r10x, pin("M3", "5V")[1]), (r10x, 205)])
label("3V3_TEL", r10x + 1, 205)
# U3 input from the protected battery rail; both grounds join the main bus
rail_drop(270, pin("U3", "IN+"))
wire([pin("U3", "IN-"), (300, 218)]); gnd(300, 218)
wire([pin("U3", "OUT-"), (300, 218)])
wire([pin("C2", 2), (283, 218), (300, 218)])

# ------------------------------------------------- split runs at every tap
def on_seg(q, a, b):
    if a[0] == b[0] == q[0]:
        return min(a[1], b[1]) < q[1] < max(a[1], b[1])
    if a[1] == b[1] == q[1]:
        return min(a[0], b[0]) < q[0] < max(a[0], b[0])
    return False

changed = True
while changed:
    changed = False
    ends = {q for seg in SEGS for q in seg}
    for i, (a, b) in enumerate(SEGS):
        hit = sorted((q for q in ends if on_seg(q, a, b)),
                     key=lambda q: (q[0] - a[0]) ** 2 + (q[1] - a[1]) ** 2)
        if hit:
            chain = [a] + hit + [b]
            SEGS[i:i+1] = [(chain[k], chain[k + 1]) for k in range(len(chain) - 1)]
            changed = True
            break

from collections import Counter
cnt = Counter(q for seg in SEGS for q in seg)
for (a, b) in SEGS:
    items.append(f'  (wire (pts (xy {a[0]:.2f} {a[1]:.2f}) (xy {b[0]:.2f} {b[1]:.2f})) (stroke (width 0) (type default)) (uuid "{U()}"))')
for q, n in cnt.items():
    if n >= 3:
        items.append(f'  (junction (at {q[0]:.2f} {q[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{U()}"))')
for (x, y) in ncs:
    items.append(f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{U()}"))')

# ---------------------------------------------------------------- emit
def sym_block(ref, lib, val, at, fp, note, dnp, pins, hide_val=False):
    sx, sy, ang = at
    custom = lib.startswith("SolarLights_Lite:")
    horiz = len(pins) == 2 and all(a in (0, 180) for (_, _, a) in pins.values())
    if custom:
        rx, ry, vx, vy = sx, sy - 16.51, sx, sy + 13.97
    elif ang in (90, 270) or horiz:
        rx, ry, vx, vy = sx, sy - 3.81, sx, sy + 3.81
    else:
        rx, ry, vx, vy = sx + 3.81, sy - 1.27, sx + 3.81, sy + 1.27
    ref_eff = EH if ref.startswith("#PWR") else E
    props = [f'    (property "Reference" "{ref}" (at {rx:.2f} {ry:.2f} 0) {ref_eff})',
             f'    (property "Value" "{val}" (at {vx:.2f} {vy:.2f} 0) {EH if hide_val else E})',
             f'    (property "Footprint" "{fp}" (at {sx:.2f} {sy:.2f} 0) {EH})',
             f'    (property "Datasheet" "~" (at {sx:.2f} {sy:.2f} 0) {EH})']
    if note:
        props.append(f'    (property "Note" "{note}" (at {sx:.2f} {sy + (16.51 if custom else 7.62):.2f} 0) (effects (font (size 1.016 1.016)) (justify left)))')
    pu = "\n".join(f'    (pin "{n}" (uuid "{U()}"))' for n in pins)
    return f'''  (symbol (lib_id "{lib}") (at {sx:.2f} {sy:.2f} {ang}) (unit 1)
    (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"})
    (uuid "{SU(ref)}")
{chr(10).join(props)}
{pu}
    (instances (project "{PRJ}" (path "/{ROOT}" (reference "{ref}") (unit 1))))
  )'''

body = []
for ref, p in P.items():
    body.append(sym_block(ref, p["lib"], p["val"], p["at"], p["fp"], p["note"], p["dnp"], SYMS[p["lib"]][1], p["hide_val"]))
for i, (x, y) in enumerate(gnds):
    body.append(sym_block(f"#PWR{i+101:03d}", "power:GND", "GND", (x, y, 0), "", "", False, SYMS["power:GND"][1], hide_val=True))

lib_symbols = "\n".join(SYMS[k][0] for k in SYMS)
sch = f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid "{ROOT}")
  (paper "A3")
  (title_block
    (title "Solar Front Lights - Lite (current build)")
    (date "27-Sep-2026")
    (rev "0.5")
    (company "AJC & Co")
    (comment 1 "Flow: panel -> U0 -> TP4056 -> battery rail -> Pro Mini, direct-drive LED and D1 Mini development telemetry")
    (comment 2 "v0.5: Arduino D1/TX -> R8/Q2/R10 -> D1 Mini D6 (inverted 9600-baud UART). D8 and D5 are open in the development profile.")
  )
  (lib_symbols
{lib_symbols}
  )
{chr(10).join(items)}
{chr(10).join(body)}
  (sheet_instances (path "/" (page "1")))
)
'''
open(os.path.join(OUT, PRJ + ".kicad_sch"), "w").write(sch)
open(os.path.join(OUT, "SolarLights_Lite_Current.kicad_sym"), "w").write(
    "(kicad_symbol_lib (version 20220914) (generator gen_lite_sch_current)\n" +
    "\n".join(custom_symbol(n, d) for n, d in CUSTOM.items()) + "\n)\n")
open(os.path.join(OUT, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (lib (name "SolarLights_Lite")(type "KiCad")(uri "${KIPRJMOD}/SolarLights_Lite_Current.kicad_sym")(options "")(descr "Lite module symbols"))\n)\n')
json.dump({"meta": {"filename": PRJ + ".kicad_pro", "version": 1}}, open(os.path.join(OUT, PRJ + ".kicad_pro"), "w"), indent=2)
json.dump({r: {k: v for k, v in p.items() if k != "at"} for r, p in P.items()}, open(os.path.join(OUT, "tools", "lite_parts_current.json"), "w"), indent=1)
print("parts", len(P), "gnd symbols", len(gnds), "no-connect", len(ncs))
