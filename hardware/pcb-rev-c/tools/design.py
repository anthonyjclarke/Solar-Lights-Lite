"""Rev C carrier definition (started from Rev B). Coordinates are mm from the board's upper-left
corner (x right, y down). Charger module M1 is now on the board; cell wires land
on CELL pads (B+ / B- are their own nets, never joined to GND_LOAD). No fuses.
"""
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
NAME = 'SolarLights_Carrier_RevC'
NS = uuid.UUID('856b5145-fddc-4d7f-b94f-439c0dcbe99a')
uid = lambda s: str(uuid.uuid5(NS, 'C' + s))
BW, BH = 74, 51.5                       # board outline
M2_LX, M2_RX, M2_PIN1_Y = 3.38, 18.62, 6.0       # Pro Mini socket rows (15.24 mm apart)
M3_LX, M3_RX, M3_PIN1_Y = 24.37, 47.23, 1.7      # D1 Mini socket rows (22.86 mm apart)

RES = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
SOLDER = 'Carrier:SolderPads_1x02_P2.54mm'
M1FP = 'Carrier:TP4056_Module_6pad_Overlay'
SOCKET = 'Connector_PinSocket_2.54mm:PinSocket_1x{:02d}_P2.54mm_Vertical'

# ---- TP4056 module, measured (17.2 wide, 26.73 long, rows 22 apart, IN row 1.5 from the USB end).
# Bottom row from the module in hand (fit sheet + ruler photos, 27-Oct-2026): OUT- 3.45 B- 7.45 B+ 3.10 OUT+;
# the vendor drawing's 2.54 / 8.92 / 2.54 does not match it. USB-C end up,
# flush with the board's top edge. u = along the module from the USB end, v = from the +side edge.
M1_ORIGIN = (53.0, 1.0)               # board position of the module's outline corner after rotation
M1_SIZE = (17.2, 26.73)               # footprint on board: width x, length y
M1_HOLE, M1_PAD = 1.2, 2.2          # hole 1.2 measured, pad assumed
_M1_UV = {1: (1.5, 1.6),    # IN+
          2: (1.5, 15.6),   # IN-   (14 mm from IN+)
          3: (23.5, 1.6),   # OUT+  (22 mm from the IN row)
          4: (23.5, 15.6),  # OUT-
          5: (23.5, 4.70),  # B+    (3.10 from OUT+)
          6: (23.5, 12.15)} # B-    (7.45 from B+, 3.45 from OUT-)
def _m1(u, v):                         # 90 deg clockwise: module left (USB) end goes to top
    return (M1_ORIGIN[0] + M1_SIZE[0] - v, M1_ORIGIN[1] + u)
M1_PADS_BOARD = {n: _m1(*uv) for n, uv in _M1_UV.items()}
_o = M1_PADS_BOARD[1]
M1_PADS_REL = {n: (round(x - _o[0], 3), round(y - _o[1], 3)) for n, (x, y) in M1_PADS_BOARD.items()}

PARTS = {}
def add(ref, value, symbol, footprint, xy, nets, sch, angle=0, tier='all', note=''):
    PARTS[ref] = dict(value=value, symbol=symbol, footprint=footprint,
                      xy=xy, angle=angle, nets={str(k): v for k, v in nets.items()},
                      sch=sch, tier=tier, note=note, uuid=uid(ref))
def pads2(ref, value, xy, nets, sch, tier='all', note=''):
    add(ref, value, 'Connector_Generic:Conn_01x02', SOLDER, xy, dict(enumerate(nets, 1)), sch, 0, tier, note)

# Solder-point row along the bottom edge. Pad 1 (square) is on the left.
ROW_Y = 47.5
PAIR_X = dict(LED=17.2, LDR=22.3, U3IN=36.9, U3OUT=42.9, S1=49, CELL=57, PV=65)   # SW1 sits between LDR and U3IN

add('M1', 'TP4056 module', 'Connector_Generic:Conn_01x06', M1FP, M1_PADS_BOARD[1],
    {1: 'CHARGE_5V', 2: 'CHARGE_RETURN', 3: 'PROTECTED_POS', 4: 'GND_LOAD', 5: 'PACK_POS', 6: 'PACK_NEG'},
    (60, 32), note='Protected TP4056 charger (TP4056/TC4056+DW01A+8205A), USB-C end up. Lower PROG to 100-150 mA BEFORE fitting. Pads IN+ IN- OUT+ OUT- B+ B-.')
pads2('JPV1', 'PV IN + / -', (PAIR_X['PV'], ROW_Y), ['CHARGE_5V', 'CHARGE_RETURN'], (110, 32),
      note='U0 5.00 V output (external) or Option A panel (Voc <= 6.5 V). Never a raw >6.5 V panel.')
pads2('JCELL1', 'CELL B+ / B-', (PAIR_X['CELL'], ROW_Y), ['PACK_POS', 'PACK_NEG'], (160, 32),
      note='1S2P pack joined in parallel at the holder, matched cells. B- is NOT ground; no fuses.')
pads2('JS1', 'S1 OUT+ / SYS', (PAIR_X['S1'], ROW_Y), ['PROTECTED_POS', 'VBAT_SYS'], (210, 32),
      note='Service switch S1 (or 2-pin header + shunt). Open it before connecting a programmer that supplies target power.')

add('JM2L', 'M2 LEFT / serial end top', 'Connector_Generic:Conn_01x12', SOCKET.format(12), (M2_LX, M2_PIN1_Y),
    dict(enumerate(['UART_TX', None, 'AVR_RESET', 'GND_LOAD', 'TEST', None, None, None, None, 'LDR_POWER', None, 'PWM'], 1)),
    (42, 94), note='Top to bottom: TX RX RST GND D2 D3 D4 D5 D6 D7 D8 D9.')
add('JM2R', 'M2 RIGHT / serial end top', 'Connector_Generic:Conn_01x12', SOCKET.format(12), (M2_RX, M2_PIN1_Y),
    dict(enumerate([None, 'GND_LOAD', 'AVR_RESET', 'VBAT_SYS', None, None, 'LDR_SENSE', None, 'ISP_SCK', 'ISP_MISO', 'ISP_MOSI', None], 1)),
    (93, 94), note='Top to bottom: RAW GND RST VCC A3 A2 A1 A0 D13 D12 D11 D10. Rows 15.24 mm apart; verify clone.')
# ISP lies on its side below M2: pin 1 lower left, odd pins along the lower row, the box header's key slot faces down.
add('JISP', '2x3 male header 2.54 mm', 'Connector_Generic:Conn_02x03_Odd_Even',
    'Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical', (6.0, 42.2),
    {1: 'ISP_MISO', 2: 'VBAT_SYS', 3: 'ISP_SCK', 4: 'ISP_MOSI', 5: 'AVR_RESET', 6: 'GND_LOAD'}, (124, 94), 90,
    note='Standard AVR ISP, in-circuit with M2 fitted. Outline is a DC3-6P box header, clear of M2; a plain 2x3 header fits the same holes. Open S1 if the programmer supplies VCC.')
add('C3', '100u / 10V', 'Device:C_Polarized', 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
    (20.0, 39.0), {1: 'VBAT_SYS', 2: 'GND_LOAD'}, (30, 140))
add('C4', '100n', 'Device:C', 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm',
    (8.6, 20.2), {1: 'VBAT_SYS', 2: 'GND_LOAD'}, (66, 140), 90, note='Fits under M2.')
add('R3', '56R / 0.25W', 'Device:R', RES, (8.6, 22.8), {1: 'PWM', 2: 'LED_POS'}, (30, 187), 270,
    note='Direct GPIO drive; 56R keeps peak current near 19 mA at 4.20 V. No cable-short protection. Fits under M2.')
pads2('JLED1', 'LED + / -', (PAIR_X['LED'], ROW_Y), ['LED_POS', 'GND_LOAD'], (70, 187),
      note='Low-power LED string only; no connection to VBAT_SYS.')
pads2('JLDR1', 'LDR D7 / A1', (PAIR_X['LDR'], ROW_Y), ['LDR_POWER', 'LDR_SENSE'], (109, 187),
      note='Remote LDR between these two pads, no ground lead.')
add('R4', '22k', 'Device:R', RES, (12.2, 26.0), {1: 'LDR_SENSE', 2: 'LDR_TRIM'}, (143, 187), 90,
    note='Fixed part of the LDR lower leg; with RV1 the leg is 22k-72k (47k at mid-travel). Fits under M2.')
add('RV1', '50k 3296W', 'Device:R_Potentiometer', 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',
    (51.5, 38.5), {1: 'LDR_TRIM', 2: 'GND_LOAD', 3: 'GND_LOAD'}, (160, 205),
    note='Bourns 3296W-1-503 multi-turn trimmer, wired as a rheostat in series with R4. Sets the light level that counts as dusk; start at mid-travel (47k).')
add('SW1', '6x6 tactile', 'Switch:SW_Push', 'Button_Switch_THT:SW_PUSH_6mm_H9.5mm', (27.6, 44.0),
    {1: 'TEST', 2: 'GND_LOAD'}, (143, 227), note='On-board 6x6 mm THT tactile switch, tall stem (about 9.5 mm), normally open.')

add('JM3L', 'M3 LEFT / antenna end top', 'Connector_Generic:Conn_01x08', SOCKET.format(8), (M3_LX, M3_PIN1_Y),
    dict(enumerate(['ESP_RESET', 'ADC_BATT', 'ESP_D0', None, 'UART_RX_INVERTED', None, None, 'ESP_3V3'], 1)),
    (218, 94), tier='1/2', note='Top to bottom: RST A0 D0 D5 D6 D7 D8 3V3. Antenna end overhangs the board edge.')
add('JM3R', 'M3 RIGHT / antenna end top', 'Connector_Generic:Conn_01x08', SOCKET.format(8), (M3_RX, M3_PIN1_Y),
    dict(enumerate([None, None, None, None, None, None, 'GND_LOAD', None], 1)),
    (276, 94), tier='1/2', note='Top to bottom: TX RX D1 D2 D3 D4 G 5V. Rows 22.86 mm apart; 5V unconnected.')
add('R5', '220k', 'Device:R', RES, (38.06, 5.8), {1: 'SENSE_FEED', 2: 'ADC_BATT'}, (184, 185), 180, tier='1/2', note='Fits under M3.')
add('R10', '10k', 'Device:R', RES, (38.06, 9.8), {1: 'ESP_3V3', 2: 'UART_RX_INVERTED'}, (294, 144), 180, tier='1/2', note='Fits under M3.')
add('Q2', '2N3904 / EBC', 'Transistor_BJT:Q_NPN_EBC', 'Package_TO_SOT_THT:TO-92_Inline_Wide', (31.5, 14.4),
    {1: 'GND_LOAD', 2: 'UART_BASE', 3: 'UART_RX_INVERTED'}, (257, 144), tier='1/2',
    note='Specified onsemi TO-92 E=1 B=2 C=3. BC547 is not a drop-in replacement. Fits under M3.')
add('R8', '47k', 'Device:R', RES, (30.44, 18.6), {1: 'UART_TX', 2: 'UART_BASE'}, (184, 144), tier='1/2', note='Fits under M3.')
add('R9', '100k', 'Device:R', RES, (38.06, 22.4), {1: 'UART_BASE', 2: 'GND_LOAD'}, (220, 144), 180, tier='1/2', note='Fits under M3.')
pads2('JU3IN1', 'U3 VIN + / -', (PAIR_X['U3IN'], ROW_Y), ['VBAT_SYS', 'GND_LOAD'], (184, 227), '2',
      'External TPS63802 input. Short twisted pair; C2 local; verify regulator input capacitors on module.')
pads2('JU3OUT1', 'U3 VOUT + / -', (PAIR_X['U3OUT'], ROW_Y), ['REG_3V3', 'GND_LOAD'], (226, 227), '2',
      'External TPS63802 output measured 3.3 V before joining JP1. Never USB 5V here.')
add('C2', '470u / 10V', 'Device:C_Polarized', 'Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',
    (58.0, 36.0), {1: 'VBAT_SYS', 2: 'GND_LOAD'}, (266, 227), tier='2')
pads2('JP3', 'ADC link', (30.0, 33.0), ['VBAT_SYS', 'SENSE_FEED'], (220, 185), '1/2',
      'Fit a 2-pin header + shunt. Open when M3 is absent or unpowered; closed for battery measurement.')
pads2('JP2', 'D0 wake link', (38.0, 33.0), ['ESP_D0', 'ESP_RESET'], (267, 185), '2',
      'Header + shunt. Open for USB flashing; closed for production deep-sleep wake.')
pads2('JP1', 'BAT power link', (46.0, 33.0), ['REG_3V3', 'ESP_3V3'], (305, 227), '2',
      'Header + shunt. Tier 1 OPEN, Tier 2 CLOSED. No automatic USB/battery interlock.')

# M3 heads/standoffs need ~5.6 mm: H2 clears JPV1, H3 sits below M1 clear of JP1 and C2.
HOLES = [(3.5, 48.0), (71.3, 48.0), (52.8, 31.5)]

# ---- Silkscreen description (drawn by generate.py on F.Silkscreen) ----
M2_BODY = (2.0, 2.0, 20.0, 35.3)        # Pro Mini outline: x0 y0 x1 y1
M3_BODY = (23.0, 0.9, 48.6, 26.9)       # D1 Mini outline; top is open (antenna overhangs the edge)
M1_BODY = (M1_ORIGIN[0], M1_ORIGIN[1], M1_ORIGIN[0] + M1_SIZE[0], M1_ORIGIN[1] + M1_SIZE[1])
M2_L = ['TX', 'RX', 'RST', 'GND', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']
M2_R = ['RAW', 'GND', 'RST', 'VCC', 'A3', 'A2', 'A1', 'A0', 'D13', 'D12', 'D11', 'D10']
M3_L = ['RST', 'A0', 'D0', 'D5', 'D6', 'D7', 'D8', '3V3']
M3_R = ['TX', 'RX', 'D1', 'D2', 'D3', 'D4', 'G', '5V']
# label text, x, y, size, justification, character width (None = size), angle (degrees)
LABELS = [('SOLAR LIGHTS LITE / C', 25.5, 36.6, 1.0, 'left', None, 0), ('ANTHONY CLARKE', 25.8, 38.4, 1.0, 'left', None, 0),
          ('github.com/anthonyjclarke/Solar-Lights-Lite', 72.2, 22.5, 1.0, 'center', 0.8, 90),  # right edge, beside M1
          ('LDR TRIM', 49.0, 42.0, 1.0, 'center', None, 0), ('TEST', 30.85, 42.2, 1.0, 'center', None, 0)]
# Solder-point names/polarity: (ref key, name, mark above pad 1, mark below pad 2)
PAIR_LABELS = [('LED', 'LED', '+', '-'), ('LDR', 'LDR', 'D7', 'A1'),
               ('U3IN', 'U3 IN', '+', '-'), ('U3OUT', 'U3 OUT', '+', '-'), ('S1', 'S1', 'OUT+', 'SYS'),
               ('CELL', 'CELL', 'B+', 'B-'), ('PV', 'PV<=6.5V', '+', '-')]
# ISP pin legend below the header (the box would cover labels beside the pins): text, x, y
ISP_LEGEND = [('ISP', 10.8, 46.4), ('1 MISO', 6.7, 47.8), ('2 VCC', 11.0, 47.8), ('3 SCK', 6.7, 49.2),
              ('4 MOSI', 11.0, 49.2), ('5 RST', 6.7, 50.6), ('6 GND', 11.0, 50.6)]
# Optional parts listed in the BOM but not placed: reference, value, footprint, tiers, note
BOM_OPTIONS = [('JISP1 (option)', 'DC3-6P 2x3 box header, 2.54 mm, straight',
                'Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical', 'optional',
                'Shrouded, keyed alternative to the plain 2x3 header: same holes, matches the silkscreen outline. Key slot faces the board bottom edge.')]

# KiCad annotation requires a numeric suffix even for descriptive connector refs.
for old in list(PARTS):
    if not old[-1].isdigit():
        p = PARTS.pop(old); p['uuid'] = uid(old + '1'); PARTS[old + '1'] = p

# Reference designators placed by hand beside their parts (x, y, justification);
# polish.py places the rest automatically.
REF_POS = {'R5': (39.2, 5.8, 'left'), 'R10': (39.2, 9.8, 'left'), 'Q2': (39.2, 14.4, 'left'),
           'R8': (39.2, 18.6, 'left'), 'R9': (39.2, 22.4, 'left'),
           'C4': (10.9, 14.6, 'center'), 'R4': (12.2, 16.5, 'center'), 'R3': (8.6, 32.3, 'center')}
