#!/usr/bin/env python3
"""External wiring model for Solar Lights Lite.

Writes docs/netlist.json and docs/wire-schedule.csv from one net list, then
checks the rules that keep the build safe. It models module terminals only:
it does not verify module internals, footprints or physical construction.
Run: python3 tools/make_netlist.py
"""
from pathlib import Path
import csv, json

DOC = Path(__file__).resolve().parents[1] / 'docs'
nets = {
    'PV_POS': ['PV1.+', 'U0.IN+'], 'PV_RETURN': ['PV1.-', 'U0.IN-'],
    'CHARGE_5V': ['U0.OUT+', 'M1.IN+'], 'CHARGE_RETURN': ['U0.OUT-', 'M1.IN-'],
    'CELL1_POS': ['BT1.+', 'FB1.1'], 'CELL2_POS': ['BT2.+', 'FB2.1'],
    'PACK_POS': ['FB1.2', 'FB2.2', 'M1.B+'], 'PACK_NEG': ['BT1.-', 'BT2.-', 'M1.B-'],
    'PROTECTED_POS': ['M1.OUT+', 'F2.1'], 'FUSED_POS': ['F2.2', 'S1.1'],
    'VBAT_SYS': ['S1.2', 'M2.VCC', 'C3.+', 'C4.1', 'U3.VIN', 'C2.+', 'R5.1'],
    'GND_LOAD': ['M1.OUT-', 'M2.GND', 'C3.-', 'C4.2', 'JLED.-', 'R4.2', 'SW1.2', 'U3.GND',
                 'C2.-', 'M3.G', 'Q2.E', 'R9.2'],
    'PWM': ['M2.D9', 'R3.1'], 'LED_POS': ['R3.2', 'JLED.+'],
    'LDR_POWER': ['M2.D7', 'LDR1.1'], 'LDR_SENSE': ['LDR1.2', 'R4.1', 'M2.A1'],
    'TEST': ['M2.D2', 'SW1.1'], 'UART_TX': ['M2.D1/TX', 'R8.1'],
    'UART_BASE': ['R8.2', 'R9.1', 'Q2.B'], 'UART_RX_INVERTED': ['Q2.C', 'R10.2', 'M3.D6'],
    'ESP_3V3': ['U3.VOUT', 'M3.3V3', 'R10.1'], 'ADC_BATT': ['R5.2', 'M3.A0'],
    'WAKE': ['M3.D0', 'M3.RST'],
}
notes = {
    'PV_POS': 'Option A panels: PV1 + connects straight to M1 IN+ (no U0)',
    'PV_RETURN': 'Option A panels: PV1 - connects straight to M1 IN-',
    'PACK_NEG': 'NO bridge to OUT- / GND_LOAD',
    'ESP_3V3': 'Tier 2 only; in Tier 1 the D1 Mini runs from USB and U3 VOUT is open',
    'WAKE': 'Tier 2 deep-sleep wake',
}

(DOC / 'netlist.json').write_text(json.dumps({
    'revision': '0.6',
    'scope': 'External module terminals only; internal connections must be verified. Not a PCB netlist.',
    'nets': nets}, indent=2) + '\n')
with (DOC / 'wire-schedule.csv').open('w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['Net', 'Connect these terminals together', 'Notes'])
    for n, p in nets.items():
        w.writerow([n, '; '.join(p), notes.get(n, '')])

# Safety rules for the external wiring model.
seen = {}
for n, pins in nets.items():
    for p in pins:
        assert p not in seen, (p, n, seen.get(p))  # every terminal on exactly one net
        seen[p] = n
assert seen['M1.B-'] != seen['M1.OUT-']        # battery negative stays behind the protection FETs
assert seen['M1.IN-'] != seen['M1.OUT-']       # no external IN-/OUT- link (the module may join them)
assert seen['M3.3V3'] != seen['M2.VCC']        # the ESP never runs from the raw battery rail
assert seen['JLED.-'] == seen['M1.OUT-']       # LED string returns to load ground, no switch
assert seen['R3.1'] == seen['M2.D9']           # R3 is fed from the pin, not the battery rail
assert not any(p.startswith(('Q1.', 'R6.', 'R7.', 'F1.')) for p in seen)  # no LED driver stage
assert seen['M3.D6'] == seen['Q2.C']           # telemetry arrives inverted on D6
assert 'M3.TX' not in seen                     # receive-only link
print(f'PASS: {len(nets)} external nets, {len(seen)} unique terminals; wiring rules hold.')
