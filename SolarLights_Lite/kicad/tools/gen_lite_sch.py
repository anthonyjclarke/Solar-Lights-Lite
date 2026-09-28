#!/usr/bin/env python3
"""Generate the SolarLights Lite KiCad schematic – fully wired, laid out so the
circuit reads left to right: panel -> charger -> battery rail -> loads.

Only the optional LDR pair uses net labels (LDR_PWR / LDR_SENSE); everything
else is drawn with real wires, junctions and GND symbols.
Needs KiCad's stock symbol libraries (KICAD_LIBS, default /usr/share/kicad/symbols).
"""
import os, re, uuid, json

LIBDIR = os.environ.get("KICAD_LIBS", "/usr/share/kicad/symbols")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRJ = "SolarLights_Lite"
NS = uuid.UUID("9f2d77a1-55b6-4f2e-9a11-77c0de5501ab")
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

# --- solar input, charger, cells -------------------------------------------
part("J1", "Connector_Generic:Conn_01x02", "PV in", (30, 45, 180), {"1": "PV+", "2": "GND"}, note="screw terminal")
part("D1", "Device:D_Schottky", "1N4001", (70, 45, 180), {"1": "PVD", "2": "PV+"})
part("D2", "Device:D_Schottky", "1N4001", (90, 45, 180), {"1": "IN+", "2": "PVD"}, note="2 in series: Voc < 8 V")
part("R1", "Device:R", "1M", (48, 62, 0), {"1": "PV+", "2": "PANEL_SENSE"}, fp=RES)
part("R2", "Device:R", "330k", (48, 82, 0), {"1": "PANEL_SENSE", "2": "GND"}, fp=RES)
part("C1", "Device:C", "100n", (63, 74, 0), {"1": "PANEL_SENSE", "2": "GND"}, fp=CAP)
part("M1", "SolarLights_Lite:TP4056_DW01A", "TP4056 + DW01A", (135, 55, 0),
     {"IN+": "IN+", "IN-": "GND", "B+": "BATT+", "B-": "BATT-", "OUT+": "OUT+", "OUT-": "GND", "CHRG": "CHRG"},
     note="charger + protection")
part("BT1", "Device:Battery_Cell", "18650", (120, 90, 0), {"1": "BATT+", "2": "BATT-"})
part("BT2", "Device:Battery_Cell", "18650", (150, 90, 0), {"1": "BATT+", "2": "BATT-"})
part("F2", "Device:Fuse", "3 A", (177, 40, 90), {"1": "OUT+", "2": "VBAT"})
# --- controller --------------------------------------------------------------
part("M2", "SolarLights_Lite:Pro_Mini_3V3", "Pro Mini 3.3 V 8 MHz", (230, 120, 0),
     {"VCC": "VBAT", "GND": "GND", "A0": "PANEL_SENSE", "A1": "LDR_SENSE", "D2": "BTN",
      "D7": "LDR_PWR", "D8": "LIGHTS", "D9": "PWM", "D10": "MODE1", "D11": "MODE2"},
     note="LED + regulator removed")
part("C3", "Device:C_Polarized", "100u", (196, 128, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP)
part("R6", "Device:R", "100R", (266, 106, 90), {"1": "PWM", "2": "Q1G"}, fp=RES)
part("R7", "Device:R", "100k", (292, 112, 0), {"1": "Q1G", "2": "GND"}, fp=RES)
part("R8", "Device:R", "100k", (266, 124, 90), {"1": "LIGHTS", "2": "D1_D5"}, fp=RES)
part("R9", "Device:R", "220k", (278, 150, 0), {"1": "D1_D5", "2": "GND"}, fp=RES)
part("SW1", "Switch:SW_Push", "test", (270, 190, 0), {"1": "BTN", "2": "GND"})
part("JP1", "Connector_Generic:Conn_01x02", "MODE1 all-night", (248, 150, 0), {"1": "MODE1", "2": "GND"})
part("JP2", "Connector_Generic:Conn_01x02", "MODE2 cap 30 %", (248, 165, 0), {"1": "MODE2", "2": "GND"})
part("LDR1", "SolarLights_Lite:LDR", "LDR (opt.)", (140, 185, 0), {"1": "LDR_PWR", "2": "LDR_SENSE"}, dnp=True)
part("R4", "Device:R", "100k", (172, 196, 0), {"1": "LDR_SENSE", "2": "GND"}, fp=RES, dnp=True)
# --- LED driver ---------------------------------------------------------------
part("F1", "Device:Fuse", "0.5 A", (355, 52, 0), {"1": "VBAT", "2": "LED_IN"})
part("R3", "Device:R", "Rlim", (355, 68, 0), {"1": "LED_IN", "2": "LED+"}, fp=RES, note="from string test")
part("J2", "Connector_Generic:Conn_01x02", "LED string", (375, 78, 0), {"1": "LED+", "2": "LED-"}, note="screw terminal")
part("Q1", "Device:Q_NMOS_GDS", "IRLZ44N", (320, 90, 0), {"1": "Q1G", "2": "LED-", "3": "GND"},
     fp="Package_TO_SOT_THT:TO-220-3_Vertical", note="or IRLB8721 / AO3400")
# --- telemetry ----------------------------------------------------------------
part("M3", "SolarLights_Lite:D1_Mini", "Wemos D1 Mini", (330, 175, 0),
     {"5V": "VBAT", "G": "GND", "A0": "D1_A0", "D5": "D1_D5", "D6": "D1_D6", "D0": "D0RST", "RST": "D0RST"},
     note="ESPHome, hourly deep sleep")
part("C2", "Device:C_Polarized", "470u", (315, 200, 0), {"1": "VBAT", "2": "GND"}, fp=ECAP)
part("R5", "Device:R", "220k", (290, 150, 0), {"1": "VBAT", "2": "D1_A0"}, fp=RES)
part("D3", "Device:D_Schottky", "BAT43", (270, 177.54, 0), {"1": "CHRG", "2": "D1_D6"})

CUSTOM = {
 "TP4056_DW01A": dict(ref="M", w=17.78,
   left=[("IN+", "IN+"), ("IN-", "IN−")],
   right=[("OUT+", "OUT+"), ("OUT-", "OUT−"), ("CHRG", "CHRG")],
   bottom=[("B+", "B+"), ("B-", "B−")]),
 "Pro_Mini_3V3": dict(ref="M", w=19.05,
   left=[("VCC", "VCC"), ("GND", "GND"), ("A0", "A0"), ("A1", "A1")],
   right=[("D9", "D9 PWM"), ("D8", "D8 lights"), ("D2", "D2 btn"), ("D10", "D10"), ("D11", "D11"), ("D7", "D7 LDR")]),
 "D1_Mini": dict(ref="M", w=17.78,
   left=[("5V", "5V"), ("G", "G"), ("A0", "A0"), ("D6", "D6")],
   right=[("D5", "D5"), ("D0", "D0"), ("RST", "RST")]),
 "LDR": dict(ref="LDR", w=5.08, left=[("1", "")], right=[("2", "")]),
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
items, gnds, SEGS = [], [], []
R2D = lambda v: round(v, 2)
def wire(pts):
    """Record an orthogonal run. Segments are split later so every tap lands on
    a wire END – KiCad only connects wires that share an endpoint."""
    for a, b in zip(pts, pts[1:]):
        a, b = (R2D(a[0]), R2D(a[1])), (R2D(b[0]), R2D(b[1]))
        if a != b:
            SEGS.append((a, b))
def junction(x, y):
    pass          # junctions are worked out automatically from the split points
def gnd(x, y):
    gnds.append((x, y))
def label(net, x, y, ang=0):
    j = "right bottom" if ang == 180 else "left bottom"
    items.append(f'  (label "{net}" (at {x:.2f} {y:.2f} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}"))')
def text(s, x, y, size=2.54, bold=True):
    b = " bold" if bold else ""
    items.append(f'  (text "{s}" (at {x} {y} 0) (effects (font (size {size} {size}) (thickness 0.508){b}) (justify left bottom)) (uuid "{U()}"))')

# ---- block titles
text("1  Panel in · blocking diodes · TP4056 charger · cells", 25, 24)
text("2  Protected battery rail", 185, 24)
text("3  LED driver", 300, 24)
text("4  Arduino Pro Mini – dusk/dawn, schedule, PWM", 180, 100)
text("5  Wemos D1 Mini – reports to Home Assistant", 296, 152)

# ---- PV chain -------------------------------------------------------------
wire([pin("J1", 1), pin("D1", 2)])
wire([pin("D1", 1), pin("D2", 2)])
wire([pin("D2", 1), (105, 45), (105, pin("M1", "IN+")[1]), pin("M1", "IN+")])
wire([pin("J1", 2), (25, pin("J1", 2)[1]), (25, 62)]); gnd(25, 62)
# panel-sense divider taps PV+ before the diodes
wire([(48, 45), pin("R1", 1)])
wire([pin("R1", 2), pin("R2", 1)])
wire([pin("R2", 2), (48, 92)]); gnd(48, 92)
wire([(48, pin("C1", 1)[1]), pin("C1", 1)])
wire([pin("C1", 2), (63, 88)]); gnd(63, 88)
# sense line to the Pro Mini (lane under the charger)
wire([(48, 73), (36, 73), (36, 160), (206, 160), (206, pin("M2", "A0")[1]), pin("M2", "A0")])
# charger grounds
wire([pin("M1", "IN-"), (108, pin("M1", "IN-")[1]), (108, 66)]); gnd(108, 66)
wire([pin("M1", "OUT-"), (160, pin("M1", "OUT-")[1]), (160, 62)]); gnd(160, 62)
# cells (1S2P)
bp, bn = pin("M1", "B+"), pin("M1", "B-")
wire([bp, (bp[0], 78), (120, 78), pin("BT1", 1)])
wire([(120, 78), (150, 78), pin("BT2", 1)])
wire([bn, (bn[0], 70), (168, 70), (168, 100), (120, 100), pin("BT1", 2)])
wire([(150, 100), pin("BT2", 2)])
# ---- battery rail ---------------------------------------------------------
wire([pin("M1", "OUT+"), (170, pin("M1", "OUT+")[1]), (170, 40), pin("F2", 1)])
RAIL_Y = 40
wire([pin("F2", 2), (390, RAIL_Y)])
def rail_drop(x, to_pin):
    wire([(x, RAIL_Y), (x, to_pin[1]), to_pin])
rail_drop(196, pin("C3", 1))
rail_drop(200, pin("M2", "VCC"))
rail_drop(290, pin("R5", 1))
rail_drop(300, pin("M3", "5V"))
rail_drop(315, pin("C2", 1))
rail_drop(355, pin("F1", 1))
wire([pin("C3", 2), (196, 140)]); gnd(196, 140)
wire([pin("C2", 2), (315, 210)]); gnd(315, 210)
# ---- Pro Mini -------------------------------------------------------------
wire([pin("M2", "GND"), (204, pin("M2", "GND")[1]), (204, 132)]); gnd(204, 132)
# D9 -> gate of Q1, with the gate pull-down
wire([pin("M2", "D9"), (258, pin("M2", "D9")[1]), (258, 106), pin("R6", 1)])
wire([pin("R6", 2), (285, 106), (285, 90), pin("Q1", 1)])
wire([(285, 100), (292, 100), pin("R7", 1)])
wire([pin("R7", 2), (292, 122)]); gnd(292, 122)
# D8 -> divider -> D1 Mini D5
wire([pin("M2", "D8"), (262, pin("M2", "D8")[1]), (262, 124), pin("R8", 1)])
wire([pin("R8", 2), (278, 124), (278, 140), (365, 140), (365, pin("M3", "D5")[1]), pin("M3", "D5")])
wire([(278, 140), pin("R9", 1)])
wire([pin("R9", 2), (278, 162)]); gnd(278, 162)
# test button
wire([pin("M2", "D2"), (254, pin("M2", "D2")[1]), (254, 190), pin("SW1", 1)])
wire([pin("SW1", 2), (282, 190), (282, 198)]); gnd(282, 198)
# mode jumpers
wire([pin("M2", "D10"), (241, pin("M2", "D10")[1]), (241, 150), pin("JP1", 1)])
wire([pin("JP1", 2), (238, pin("JP1", 2)[1]), (238, 157)]); gnd(238, 157)
wire([pin("M2", "D11"), (244, pin("M2", "D11")[1]), (244, 165), pin("JP2", 1)])
wire([pin("JP2", 2), (234, pin("JP2", 2)[1]), (234, 172)]); gnd(234, 172)
# optional LDR – the only labelled net pair on the sheet
wire([pin("M2", "D7"), (259, pin("M2", "D7")[1])]); label("LDR_PWR", 259, pin("M2", "D7")[1])
wire([pin("M2", "A1"), (190, pin("M2", "A1")[1])]); label("LDR_SENSE", 190, pin("M2", "A1")[1], 180)
wire([pin("LDR1", 1), (124, pin("LDR1", 1)[1])]); label("LDR_PWR", 124, pin("LDR1", 1)[1], 180)
wire([pin("LDR1", 2), (172, pin("LDR1", 2)[1]), pin("R4", 1)])
label("LDR_SENSE", 172, pin("LDR1", 2)[1])
wire([pin("R4", 2), (172, 203)]); gnd(172, 203)
# ---- LED driver -----------------------------------------------------------
wire([pin("F1", 2), pin("R3", 1)])
wire([pin("R3", 2), (355, 78), pin("J2", 1)])
wire([pin("Q1", 2), (322.54, 80.54), pin("J2", 2)])
wire([pin("Q1", 3), (322.54, 106)]); gnd(322.54, 106)
# ---- D1 Mini --------------------------------------------------------------
wire([pin("M3", "G"), (305, pin("M3", "G")[1]), (305, 186)]); gnd(305, 186)
wire([pin("R5", 2), (290, 175), pin("M3", "A0")])
wire([pin("D3", 2), pin("M3", "D6")])
wire([pin("M1", "CHRG"), (176, pin("M1", "CHRG")[1]), (176, 215), (250, 215), (250, 177.54), pin("D3", 1)])
wire([pin("M3", "D0"), (358, pin("M3", "D0")[1]), (358, pin("M3", "RST")[1]), pin("M3", "RST")])

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
    (title "Solar Front Lights – Lite")
    (date "18-Sep-2026")
    (rev "0.3")
    (company "AJC & Co")
    (comment 1 "Flow: panel -> diodes -> TP4056 -> battery rail -> Pro Mini, LED driver, D1 Mini")
    (comment 2 "Stage 1: existing 1.2 W panel · Stage 2: 6 V 5 W panel")
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
open(os.path.join(OUT, "SolarLights_Lite.kicad_sym"), "w").write(
    "(kicad_symbol_lib (version 20220914) (generator gen_lite_sch)\n" +
    "\n".join(custom_symbol(n, d) for n, d in CUSTOM.items()) + "\n)\n")
open(os.path.join(OUT, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (lib (name "SolarLights_Lite")(type "KiCad")(uri "${KIPRJMOD}/SolarLights_Lite.kicad_sym")(options "")(descr "Lite module symbols"))\n)\n')
if not os.path.exists(os.path.join(OUT, PRJ + ".kicad_pro")):
    json.dump({"meta": {"filename": PRJ + ".kicad_pro", "version": 1}}, open(os.path.join(OUT, PRJ + ".kicad_pro"), "w"), indent=2)
json.dump({r: {k: v for k, v in p.items() if k != "at"} for r, p in P.items()}, open(os.path.join(OUT, "tools", "lite_parts.json"), "w"), indent=1)
print("parts", len(P), "gnd symbols", len(gnds))
