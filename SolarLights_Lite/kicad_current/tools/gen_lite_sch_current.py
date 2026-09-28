#!/usr/bin/env python3
"""Generate the SolarLights Lite v0.5 current-build KiCad schematic:
direct pin-drive LED branch (no Q1/R6/R7/F1), 1S2P per-cell fusing, a
main-rail service switch, U0/U3 regulators, and the NPN-inverted D1/TX to
D6 development-UART receiver. Writes to its own project so the
Rev 0.3 audit-baseline schematic in ../../kicad/ is untouched.

Layout: six framed functional blocks on a 2.54 mm (100 mil) grid. Inter-block
nets travel by net label (VBAT, 3V3_TEL, PWM, UART_TX, BTN, LDR_*) instead of
sheet-long wires. All coordinates below are in grid units (G = 2.54 mm).

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
FLIP = False
G = 2.54
g = lambda v: round(v * G, 3)

# ----------------------------------------------------------------- parts
P = {}
def part(ref, lib, val, at, pins, fp="", note="", dnp=False, hide_val=False, mirror=False, note_at=None):
    """`at` is (x, y, angle) in grid units; `note_at` is (x, y, justify) in grid units, or "hide"."""
    P[ref] = dict(lib=lib, val=val, at=(g(at[0]), g(at[1]), at[2]), pins=pins, fp=fp,
                  note=note, dnp=dnp, hide_val=hide_val, mirror=mirror, note_at=note_at)

RES = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
CAP = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm"
ECAP = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"

# --- 1 solar input, regulator (TBD), charger, cells ------------------------
part("J1", "Connector_Generic:Conn_01x02", "PV in", (14, 20, 0), {"1": "PV+", "2": "GND"},
     note="screw terminal", mirror=True)
part("U0", "SolarLights_Lite:Reg5V_TBD", "5 V reg - TBD", (30, 21, 0),
     {"IN+": "PV+", "IN-": "GND", "OUT+": "IN+", "OUT-": "GND"},
     note="module not yet selected - see BUILD_GUIDE.md")
part("M1", "SolarLights_Lite:TP4056_DW01A", "TP4056 + DW01A", (52, 22, 0),
     {"IN+": "IN+", "IN-": "GND", "B+": "BATT_BUS", "B-": "BATT-", "OUT+": "OUT+", "OUT-": "GND", "CHRG": "CHRG"},
     note="charger + protection; CHRG not wired", note_at="hide")
part("FB1", "Device:Fuse", "1 A", (44, 32.5, 0), {"1": "BATT_BUS", "2": "BATT1+"})
part("FB2", "Device:Fuse", "1 A", (54, 32.5, 0), {"1": "BATT_BUS", "2": "BATT2+"})
part("BT1", "Device:Battery_Cell", "18650", (44, 38, 0), {"1": "BATT1+", "2": "BATT-"})
part("BT2", "Device:Battery_Cell", "18650", (54, 38, 0), {"1": "BATT2+", "2": "BATT-"})
# --- 2 battery rail: main fuse then service switch --------------------------
part("F2", "Device:Fuse", "1 A", (75.5, 20, 90), {"1": "OUT+", "2": "VBAT_SW"})
part("S1", "Switch:SW_SPST", "service", (83, 20, 0), {"1": "VBAT_SW", "2": "VBAT"})
part("C3", "Device:C_Polarized", "100u", (93, 25.5, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP)
# --- 3 LED driver: direct pin drive, no Q1/R6/R7/F1 -------------------------
part("R3", "Device:R", "47R", (120.5, 20, 90), {"1": "PWM", "2": "LED+"}, fp=RES,
     note="measured string, ~15 mA @3.7 V; try 56R for <20 mA @4.2 V")
part("J2", "Connector_Generic:Conn_01x02", "LED string", (146, 20, 0), {"1": "LED+", "2": "LED-"},
     note="screw terminal")
# --- 4 controller (BTE13-010A Pro Mini, converted to internal 8 MHz) --------
part("M2", "SolarLights_Lite:Pro_Mini_BTE13", "BTE13-010A - int. 8 MHz", (38, 66, 0),
     {"VCC": "VBAT", "GND": "GND", "A1": "LDR_SENSE", "D2": "BTN",
      "D7": "LDR_PWR", "D1": "UART_TX", "D8": "NC_D8", "D9": "PWM", "A0": "NC_A0",
      "D10": "NC_D10", "D11": "NC_D11"},
     note="RAW unused; A0/D10/D11 reserved, left open")
part("LDR1", "SolarLights_Lite:LDR", "LDR", (16, 83.5, 0), {"1": "LDR_PWR", "2": "LDR_SENSE"})
part("R4", "Device:R", "100k", (16, 89.5, 0), {"1": "LDR_SENSE", "2": "GND"}, fp=RES)
part("SW1", "Switch:SW_Push", "test", (40, 84, 0), {"1": "BTN", "2": "GND"})
# --- 5 development telemetry: NPN-inverted D1/TX to D6 UART receiver --------
part("R8", "Device:R", "47k", (78.5, 67, 90), {"1": "UART_TX", "2": "Q2_BASE"}, fp=RES)
part("R9", "Device:R", "100k", (82, 71.5, 0), {"1": "Q2_BASE", "2": "GND"}, fp=RES, note="B-E pulldown")
part("Q2", "Device:Q_NPN_BCE", "2N3904", (89, 67, 0), {"1": "Q2_BASE", "2": "D1_D6", "3": "GND"},
     note="dev UART inverter")
part("R10", "Device:R", "10k", (94, 60.5, 180), {"1": "D1_D6", "2": "3V3_TEL"}, fp=RES, note="pull-up")
part("R5", "Device:R", "220k", (104.5, 68, 90), {"1": "VBAT", "2": "D1_A0"}, fp=RES,
     note="battery sense, unaffected by U3")
part("M3", "SolarLights_Lite:D1_Mini", "Wemos D1 Mini", (128, 66, 0),
     {"5V": "3V3_TEL", "G": "GND", "A0": "D1_A0", "D5": "NC_D5", "D6": "D1_D6", "D0": "D0RST", "RST": "D0RST"},
     note="ESPHome v0.5 dev UART; always-on; onboard regulator removed")
# --- 6 D1 Mini's own 3.3 V supply (TBD) -------------------------------------
part("C2", "Device:C_Polarized", "470u", (84, 89.5, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP, note="at U3 input")
part("U3", "SolarLights_Lite:Reg3V3_TBD", "3V3 tel. - HL802A cand.", (98, 88, 0),
     {"IN+": "VBAT", "IN-": "GND", "OUT+": "3V3_TEL", "OUT-": "GND"},
     note="TPS63802/HL802A breakout, jumper=3.3V; candidate, not bench-qualified",
     note_at=(111, 89, "left"))

# Box symbols: pins listed top to bottom; widths are half-widths on the 2.54 grid.
CUSTOM = {
 "TP4056_DW01A": dict(ref="M", w=20.32,
   left=[("IN+", "IN+"), ("IN-", "IN−")],
   right=[("OUT+", "OUT+"), ("OUT-", "OUT−"), ("CHRG", "CHRG")],
   bottom=[("B+", "B+"), ("B-", "B−")]),
 "Pro_Mini_BTE13": dict(ref="M", w=20.32,
   left=[("VCC", "VCC"), ("A1", "A1"), ("A0", "A0"), ("GND", "GND")],
   right=[("D9", "D9 PWM"), ("D1", "D1 TX"), ("D2", "D2 btn"), ("D7", "D7 LDR"), ("D8", "D8 open"), ("D10", "D10"), ("D11", "D11")]),
 "D1_Mini": dict(ref="M", w=17.78,
   left=[("5V", "5V"), ("D6", "D6"), ("A0", "A0")],
   right=[("D0", "D0"), ("RST", "RST"), ("D5", "D5"), ("G", "G")]),
 "LDR": dict(ref="LDR", ldr=True),
 "Reg5V_TBD": dict(ref="U", w=10.16, left=[("IN+", "IN+"), ("IN-", "IN−")], right=[("OUT+", "OUT+"), ("OUT-", "OUT−")]),
 "Reg3V3_TBD": dict(ref="U", w=10.16, left=[("IN+", "IN+"), ("IN-", "IN−")], right=[("OUT+", "OUT+"), ("OUT-", "OUT−")]),
}
def box_h(d):
    n = max(len(d["left"]), len(d["right"]))
    return ((n + 1) // 2 + 1) * G

def ldr_symbol(name, prefix):
    """Vertical photoresistor: resistor body with two incoming light arrows."""
    arrow = lambda x0, y0: (
        f'      (polyline (pts (xy {x0} {y0}) (xy {x0 + 1.524} {y0 - 1.524})) (stroke (width 0.254) (type default)) (fill (type none)))\n'
        f'      (polyline (pts (xy {x0 + 1.524} {y0 - 1.524}) (xy {x0 + 0.762} {y0 - 1.397}) (xy {x0 + 1.397} {y0 - 0.762}) (xy {x0 + 1.524} {y0 - 1.524})) (stroke (width 0.254) (type default)) (fill (type outline)))')
    return "\n".join([
        f'  (symbol "{prefix}{name}" (pin_numbers hide) (pin_names hide) (in_bom yes) (on_board yes)',
        f'    (property "Reference" "LDR" (at 2.54 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))',
        f'    (property "Value" "{name}" (at 2.54 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))',
        f'    (property "Footprint" "" (at 0 0 0) {EH})',
        f'    (property "Datasheet" "" (at 0 0 0) {EH})',
        f'    (symbol "{name}_0_1"',
        f'      (rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))',
        arrow(-4.064, 2.286), arrow(-4.064, 0.254),
        '    )',
        f'    (symbol "{name}_1_1"',
        f'      (pin passive line (at 0 3.81 270) (length 1.27) (name "~" {E}) (number "1" {E}))',
        f'      (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" {E}) (number "2" {E}))',
        '    )\n  )'])

def custom_symbol(name, d, prefix=""):
    if d.get("ldr"):
        return ldr_symbol(name, prefix)
    h, w = box_h(d), d["w"]
    o = [f'  (symbol "{prefix}{name}" (in_bom yes) (on_board yes)',
         f'    (property "Reference" "{d["ref"]}" (at 0 {h + 3.81} 0) {E})',
         f'    (property "Value" "{name}" (at 0 {h + 1.27} 0) {E})',
         f'    (property "Footprint" "" (at 0 0 0) {EH})',
         f'    (property "Datasheet" "" (at 0 0 0) {EH})',
         f'    (symbol "{name}_0_1" (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'    (symbol "{name}_1_1"']
    for i, (num, nm) in enumerate(d["left"]):
        o.append(f'      (pin passive line (at {-w-G:.2f} {h - G*(i+1):.2f} 0) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
    for i, (num, nm) in enumerate(d["right"]):
        o.append(f'      (pin passive line (at {w+G:.2f} {h - G*(i+1):.2f} 180) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
    for i, (num, nm) in enumerate(d.get("bottom", [])):
        x = -w / 2 + i * w
        o.append(f'      (pin passive line (at {x:.2f} {-h-G:.2f} 90) (length 2.54) (name "{nm or "~"}" {E}) (number "{num}" {E}))')
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
for ref, p in list(P.items()) + [("_gnd", dict(lib="power:GND"))]:
    lid = p["lib"]
    if lid in SYMS: continue
    if lid.startswith("SolarLights_Lite:"):
        nm = lid.split(":")[1]
        body = custom_symbol(nm, CUSTOM[nm], prefix="SolarLights_Lite:")
        SYMS[lid] = (body, pins_of(body))
    else:
        blk = stock(lid)
        SYMS[lid] = ("  " + blk.replace(f'(symbol "{lid.split(":")[1]}"', f'(symbol "{lid}"', 1), pins_of(blk))

# rotation of a library pin into sheet coordinates (verified against KiCad);
# `(mirror y)` flips the symbol left-right before rotation
def xf(sx, sy, ang, px, py, mirror=False):
    if mirror: px = -px
    if ang == 0:   return (sx + px, sy - py)
    if ang == 90:  return (sx - py, sy - px)
    if ang == 180: return (sx - px, sy + py)
    return (sx + py, sy + px)          # 270

PIN = {}
for ref, p in P.items():
    sx, sy, ang = p["at"]
    for num, (px, py, _) in SYMS[p["lib"]][1].items():
        PIN[(ref, num)] = xf(sx, sy, ang, px, py, p["mirror"])
def pin(ref, num):
    x, y = PIN[(ref, str(num))]
    return (round(x / G, 3), round(y / G, 3))      # back to grid units

# ---------------------------------------------------------------- drawing
items, gnds, ncs, SEGS, TAPS = [], [], [], [], set()
R2D = lambda v: round(v, 2)
def pt(q):
    return (R2D(g(q[0])), R2D(g(q[1])))
def wire(*pts):
    """Record an orthogonal run (grid units). Segments are split later so every
    tap lands on a wire END - KiCad only connects wires that share an endpoint."""
    for a, b in zip(pts, pts[1:]):
        a, b = pt(a), pt(b)
        assert a[0] == b[0] or a[1] == b[1], ("diagonal wire", a, b)
        if a != b:
            SEGS.append((a, b))
def gnd(x, y):
    gnds.append(pt((x, y))); TAPS.add(pt((x, y)))
def noconnect(q):
    ncs.append(pt(q))
def label(net, x, y, ang=0):
    """ang 0: text runs right of (x, y); 180: runs left; 90: runs up."""
    j = "right bottom" if ang == 180 else "left bottom"
    X, Y = pt((x, y)); TAPS.add((X, Y))
    items.append(f'  (label "{net}" (at {X:.2f} {Y:.2f} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))')
def text(s, x, y, size=1.27, bold=False, italic=False):
    st = (" bold" if bold else "") + (" italic" if italic else "")
    th = f" (thickness {0.3 if bold else 0.1524})"
    items.append(f'  (text "{s}" (at {g(x):.2f} {g(y):.2f} 0) (effects (font (size {size} {size}){th}{st}) (justify left bottom)) (uuid "{U()}"))')
def block(n, title, x0, y0, x1, y1):
    """Dashed frame around a functional block, numbered title in its top-left corner."""
    items.append(f'  (rectangle (start {g(x0):.2f} {g(y0):.2f}) (end {g(x1):.2f} {g(y1):.2f}) '
                 f'(stroke (width 0.254) (type dash) (color 72 72 72 1)) (fill (type none)) (uuid "{U()}"))')
    text(f"{n}  {title}", x0 + 1, y0 + 2.5, size=2.0, bold=True)

# ---- frames: two rows, top = power path, bottom = control + telemetry
block(1, "Solar input, charger & cells",       6, 7, 64, 46)
block(2, "Battery rail - fuse + service switch", 66, 7, 104, 46)
block(3, "LED output - direct pin drive",       106, 7, 158, 46)
block(4, "Controller - Pro Mini BTE13-010A",    6, 50, 64, 96)
block(5, "Telemetry - Wemos D1 Mini (development)", 66, 50, 158, 80)
block(6, "Telemetry 3.3 V supply",              66, 82, 158, 96)

# ---- 1  PV -> U0 -> TP4056 -> cells -----------------------------------------
wire(pin("J1", 1), pin("U0", "IN+"))
wire(pin("J1", 2), pin("U0", "IN-"))
wire((19, 21), (19, 24)); gnd(19, 24)
wire(pin("U0", "OUT+"), pin("M1", "IN+"))
wire(pin("U0", "OUT-"), pin("M1", "IN-"))
wire((41, 21), (41, 24)); gnd(41, 24)
oxm, oym = pin("M1", "OUT-")
wire((oxm, oym), (oxm + 2, oym), (oxm + 2, oym + 3)); gnd(oxm + 2, oym + 3)
noconnect(pin("M1", "CHRG"))
# cells: each behind its own fuse off the shared BATT_BUS node
bp, bn = pin("M1", "B+"), pin("M1", "B-")
BUS_Y, RET_Y = 29, 41
wire(bp, (bp[0], BUS_Y))
wire((44, BUS_Y), (54, BUS_Y))
wire((44, BUS_Y), pin("FB1", 1)); wire((54, BUS_Y), pin("FB2", 1))
wire(pin("FB1", 2), pin("BT1", 1)); wire(pin("FB2", 2), pin("BT2", 1))
wire(pin("BT1", 2), (44, RET_Y), (59, RET_Y), (59, bn[1] + 1), (bn[0], bn[1] + 1), bn)
wire(pin("BT2", 2), (54, RET_Y))
label("BATT_BUS", 49, BUS_Y); label("BATT-", 45, RET_Y)
text("1S2P - each cell fused off the charger B+ node. TP4056 CHRG not wired.", 8, 44.5, italic=True)

# ---- 2  battery rail: main fuse then service switch -> VBAT -----------------
wire(pin("M1", "OUT+"), pin("F2", 1))
wire(pin("F2", 2), pin("S1", 1))
wire(pin("S1", 2), (100, 20)); label("VBAT", 100, 20)
wire((93, 20), pin("C3", 1))
wire(pin("C3", 2), (93, 29)); gnd(93, 29)
text("VBAT feeds the Pro Mini, U3 and R5 by net label", 68, 44.5, italic=True)

# ---- 3  LED driver: R3 direct from D9 to the string -------------------------
wire((116, 20), pin("R3", 1)); label("PWM", 116, 20, 180)
wire(pin("R3", 2), pin("J2", 1))
jx, jy = pin("J2", 2)
wire((jx, jy), (jx - 3, jy), (jx - 3, jy + 3)); gnd(jx - 3, jy + 3)
text("no Q1 / R6 / R7 / F1 - D9 drives the string through R3", 108, 44.5, italic=True)

# ---- 4  Pro Mini ------------------------------------------------------------
lx = pin("M2", "VCC")[0]
wire(pin("M2", "VCC"), (lx - 4, pin("M2", "VCC")[1])); label("VBAT", lx - 4, pin("M2", "VCC")[1], 180)
wire(pin("M2", "A1"), (lx - 4, pin("M2", "A1")[1])); label("LDR_SENSE", lx - 4, pin("M2", "A1")[1], 180)
noconnect(pin("M2", "A0"))
gx_, gy_ = pin("M2", "GND")
wire((gx_, gy_), (gx_ - 2, gy_), (gx_ - 2, gy_ + 3)); gnd(gx_ - 2, gy_ + 3)
rx = pin("M2", "D9")[0]
for p_, net in (("D9", "PWM"), ("D1", "UART_TX"), ("D2", "BTN"), ("D7", "LDR_PWR")):
    wire(pin("M2", p_), (rx + 4, pin("M2", p_)[1])); label(net, rx + 4, pin("M2", p_)[1])
for p_ in ("D8", "D10", "D11"):
    noconnect(pin("M2", p_))
# switched LDR divider (fitted by default, SENSOR_LDR=1)
l1, l2 = pin("LDR1", 1), pin("LDR1", 2)
wire((l1[0] - 3, l1[1] - 2), (l1[0], l1[1] - 2), l1); label("LDR_PWR", l1[0] - 3, l1[1] - 2, 180)
wire(l2, pin("R4", 1))
wire((l2[0], l2[1] + 1), (l2[0] + 3, l2[1] + 1)); label("LDR_SENSE", l2[0] + 3, l2[1] + 1)
r4b = pin("R4", 2)
wire(r4b, (r4b[0], r4b[1] + 2)); gnd(r4b[0], r4b[1] + 2)
text("Light sensor (switched by D7)", 8, 77)
# test button
s1, s2 = pin("SW1", 1), pin("SW1", 2)
wire((s1[0] - 3, s1[1]), s1); label("BTN", s1[0] - 3, s1[1], 180)
wire(s2, (s2[0] + 2, s2[1]), (s2[0] + 2, s2[1] + 3)); gnd(s2[0] + 2, s2[1] + 3)
text("Test button", 33, 77)

# ---- 5  telemetry: D1/TX -> R8 -> Q2 (inverter) -> D1 Mini D6 ---------------
r8a = pin("R8", 1)
wire((r8a[0] - 4, r8a[1]), r8a); label("UART_TX", r8a[0] - 4, r8a[1], 180)
bxq, byq = pin("Q2", 1)
wire(pin("R8", 2), (bxq, byq))
r9t = pin("R9", 1)
wire((r9t[0], byq), r9t)
r9b = pin("R9", 2)
wire(r9b, (r9b[0], r9b[1] + 2)); gnd(r9b[0], r9b[1] + 2)
ex, ey = pin("Q2", 3)
wire((ex, ey), (ex, r9b[1] + 2)); gnd(ex, r9b[1] + 2)
cx, cy = pin("Q2", 2)
d6 = pin("M3", "D6")
wire((cx, cy), (cx, d6[1]), d6)                # collector -> D6
r10a = pin("R10", 1)
wire(r10a, (r10a[0], d6[1]))                   # R10 pull-up taps the collector
r10b = pin("R10", 2)
wire(r10b, (r10b[0], r10b[1] - 2)); label("3V3_TEL", r10b[0], r10b[1] - 2, 90)
label("D1_D6", cx + 6, d6[1])
v5 = pin("M3", "5V")
wire((v5[0] - 5, v5[1]), v5); label("3V3_TEL", v5[0] - 5, v5[1], 180)
a0 = pin("M3", "A0")
r5a, r5b = pin("R5", 1), pin("R5", 2)
wire(r5b, (a0[0] - 2, r5b[1]), (a0[0] - 2, a0[1]), a0)
wire((r5a[0] - 3, r5a[1]), r5a); label("VBAT", r5a[0] - 3, r5a[1], 180)
noconnect(pin("M3", "D5"))
d0, rst = pin("M3", "D0"), pin("M3", "RST")
wire(d0, (d0[0] + 3, d0[1]), (d0[0] + 3, rst[1]), rst)
gm = pin("M3", "G")
wire(gm, (gm[0] + 4, gm[1]), (gm[0] + 4, gm[1] + 3)); gnd(gm[0] + 4, gm[1] + 3)
text("Arduino D1/TX -> inverted 9600-baud UART -> D6. D0-RST for deep-sleep wake.", 68, 78.5, italic=True)

# ---- 6  U3: low-Iq 3.3 V for the D1 Mini, straight off VBAT -----------------
ui, un = pin("U3", "IN+"), pin("U3", "IN-")
uo, uon = pin("U3", "OUT+"), pin("U3", "OUT-")
GB_Y = 93
wire((78, ui[1]), ui); label("VBAT", 78, ui[1], 180)
wire((84, ui[1]), pin("C2", 1))
wire(pin("C2", 2), (84, GB_Y))
wire(un, (un[0] - 2, un[1]), (un[0] - 2, GB_Y))
wire(uon, (uon[0] + 2, uon[1]), (uon[0] + 2, GB_Y))
wire((84, GB_Y), (uon[0] + 2, GB_Y)); gnd(98, GB_Y)
wire(uo, (uo[0] + 6, uo[1])); label("3V3_TEL", uo[0] + 6, uo[1])

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
    ends = {q for seg in SEGS for q in seg} | TAPS
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
def field(x, y, eff, just=None, ang=0):
    if just and FLIP:          # KiCad mirrors field justification on 180-degree symbols
        just = {"left": "right", "right": "left"}[just]
    e = eff if just is None else eff[:-1] + f" (justify {just}))"
    return f'(at {x:.2f} {y:.2f} {ang}) {e}'

def sym_block(ref, lib, val, at, fp, note, dnp, pins, hide_val=False, mirror=False, note_at=None):
    global FLIP
    sx, sy, ang = at
    sx, sy = R2D(sx), R2D(sy)
    FLIP = ang == 180
    fa = 90 if ang in (90, 270) else 0     # fields rotate with the symbol; 90 reads horizontal
    NE = '(effects (font (size 1.016 1.016) italic))'
    custom = lib.startswith("SolarLights_Lite:")
    horiz = len(pins) == 2 and all(a in (0, 180) for (_, _, a) in pins.values())
    nj = None
    if custom and "w" in CUSTOM[lib.split(":")[1]]:
        d = CUSTOM[lib.split(":")[1]]
        h = box_h(d)
        low = sy + h + (2 * G if d.get("bottom") else 0)
        r = (sx, sy - h - 3.81, None); v = (sx, sy - h - 1.27, None)
        n_ = (sx, low + 1.9, None)
    elif lib == "Device:Q_NPN_BCE":
        r = (sx + 5.08, sy - 1.27, "left"); v = (sx + 5.08, sy + 1.27, "left")
        n_ = (sx + 5.08, sy + 3.6, "left")
    elif lib.startswith("Connector_"):
        r = (sx, sy - 2.54, None); v = (sx, sy + 6.35, None); n_ = (sx, sy + 8.4, None)
    elif ang in (90, 270) or horiz:
        r = (sx, sy - 3.81, None); v = (sx, sy + 3.81, None)
        n_ = (sx, sy + 6.0, None)
        if horiz and lib.startswith("Switch:"):
            r = (sx, sy - 3.81, None); v = (sx, sy + 2.54, None); n_ = (sx, sy + 4.6, None)
    else:                                    # upright two-pin part: fields to the right
        r = (sx + 2.54, sy - 1.27, "left"); v = (sx + 2.54, sy + 1.27, "left")
        n_ = (sx + 2.54, sy + 3.3, "left")
    ref_eff = EH if ref.startswith("#PWR") else E
    props = [f'    (property "Reference" "{ref}" {field(r[0], r[1], ref_eff, r[2], fa)})',
             f'    (property "Value" "{val}" {field(v[0], v[1], EH if hide_val else E, v[2], fa)})',
             f'    (property "Footprint" "{fp}" (at {sx:.2f} {sy:.2f} 0) {EH})',
             f'    (property "Datasheet" "~" (at {sx:.2f} {sy:.2f} 0) {EH})']
    if isinstance(note_at, tuple):
        n_ = (g(note_at[0]), g(note_at[1]), note_at[2])
    if note_at == "hide":
        NE = NE.replace("italic)", "italic) hide")
    if note:
        props.append(f'    (property "Note" "{note}" {field(n_[0], n_[1], NE, n_[2], fa)})')
    pu = "\n".join(f'    (pin "{n}" (uuid "{U()}"))' for n in pins)
    mir = " (mirror y)" if mirror else ""
    return f'''  (symbol (lib_id "{lib}") (at {sx:.2f} {sy:.2f} {ang}){mir} (unit 1)
    (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"})
    (uuid "{SU(ref)}")
{chr(10).join(props)}
{pu}
    (instances (project "{PRJ}" (path "/{ROOT}" (reference "{ref}") (unit 1))))
  )'''

body = []
for ref, p in P.items():
    body.append(sym_block(ref, p["lib"], p["val"], p["at"], p["fp"], p["note"], p["dnp"],
                          SYMS[p["lib"]][1], p["hide_val"], p["mirror"], p["note_at"]))
for i, (x, y) in enumerate(gnds):
    body.append(sym_block(f"#PWR{i+101:03d}", "power:GND", "GND", (x, y, 0), "", "", False, SYMS["power:GND"][1], hide_val=True))

lib_symbols = "\n".join(SYMS[k][0] for k in SYMS)
sch = f'''(kicad_sch (version 20230121) (generator eeschema)
  (uuid "{ROOT}")
  (paper "A3")
  (title_block
    (title "Solar Front Lights - Lite (current build)")
    (date "28-Sep-2026")
    (rev "0.5")
    (company "AJC & Co")
    (comment 1 "D8 and D5 are open in the development profile.")
    (comment 2 "v0.5: Arduino D1/TX -> R8/Q2/R10 -> D1 Mini D6 (inverted 9600-baud UART).")
    (comment 3 "direct-drive LED and D1 Mini development telemetry")
    (comment 4 "Flow: panel -> U0 -> TP4056 -> battery rail -> Pro Mini,")
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
json.dump({r: {k: v for k, v in p.items() if k not in ("at", "mirror", "note_at")} for r, p in P.items()},
          open(os.path.join(OUT, "tools", "lite_parts_current.json"), "w"), indent=1)
print("parts", len(P), "gnd symbols", len(gnds), "no-connect", len(ncs))
