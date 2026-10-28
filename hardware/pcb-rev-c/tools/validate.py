"""Independent connection checks against the existing module wiring schedule,
firmware pins and KiCad's exported netlist. Run with KiCad bundled Python after
ERC, DRC (including schematic parity) and netlist export.
"""
import json, re, math, hashlib, xml.etree.ElementTree as ET
from collections import defaultdict
import pcbnew as pcb
from design import ROOT, NAME
REPO=ROOT.parents[1]
def require(condition,description):
    if not condition:raise AssertionError(description)
    passed.append(description)
passed=[]
b=pcb.LoadBoard(str(ROOT/(NAME+'.kicad_pcb')))
actual=defaultdict(set)
for fp in b.GetFootprints():
    for pad in fp.Pads():
        n=pad.GetNetname()
        if n and not n.startswith('unconnected-'):actual[n.lstrip('/')].add((fp.GetReference(),pad.GetNumber()))
sch=defaultdict(set)
for n in ET.parse(ROOT/'review'/'schematic-netlist.xml').findall('.//nets/net'):
    if not n.get('name').startswith('unconnected-'):
        sch[n.get('name').lstrip('/')].update((x.get('ref'),x.get('pin')) for x in n.findall('node'))
require(dict(actual)==dict(sch),'Exact schematic-to-PCB endpoint equality (including full module sockets)')
expected={n:set(t) for n,t in json.loads((REPO/'docs'/'netlist.json').read_text())['nets'].items()}
# Rev B and C have no fuses: F2, FB1 and FB2 are removed from the documented wiring, which
# joins the nets either side of each. Everything else must still match the schedule.
for ref in ('F2','FB1','FB2'):
    a=next(n for n,t in expected.items() if ref+'.1' in t);c=next(n for n,t in expected.items() if ref+'.2' in t)
    if a!=c:expected[a]|=expected.pop(c)
    expected[a]={t for t in expected[a] if not t.startswith(ref+'.')}
bindings={'M2.VCC':('JM2R1','4'),'M2.GND':('JM2L1','4'),'M2.D9':('JM2L1','12'),
 'M2.D7':('JM2L1','10'),'M2.A1':('JM2R1','7'),'M2.D2':('JM2L1','5'),
 'M2.D1/TX':('JM2L1','1'),'M3.G':('JM3R1','7'),'M3.3V3':('JM3L1','8'),
 'M3.D6':('JM3L1','5'),'M3.A0':('JM3L1','2'),'M3.D0':('JM3L1','3'),'M3.RST':('JM3L1','1'),
 'M1.IN+':('M1','1'),'M1.IN-':('M1','2'),'M1.OUT+':('M1','3'),'M1.OUT-':('M1','4'),'M1.B+':('M1','5'),'M1.B-':('M1','6'),
 'U0.OUT+':('JPV1','1'),'U0.OUT-':('JPV1','2'),'BT1.+':('JCELL1','1'),'BT2.+':('JCELL1','1'),
 'BT1.-':('JCELL1','2'),'BT2.-':('JCELL1','2'),
 'U3.VIN':('JU3IN1','1'),'U3.GND':('JU3IN1','2'),'U3.VOUT':('JU3OUT1','1'),
 'S1.1':('JS1','1'),'S1.2':('JS1','2'),'JLED.+':('JLED1','1'),'JLED.-':('JLED1','2'),
 'LDR1.1':('JLDR1','1'),'LDR1.2':('JLDR1','2'),'SW1.1':('SW1','1'),
 'SW1.2':('SW1','2'),'Q2.E':('Q2','1'),'Q2.B':('Q2','2'),'Q2.C':('Q2','3')}
merged={n:set(v) for n,v in actual.items()}
for a,c in [('VBAT_SYS','SENSE_FEED'),('ESP_3V3','REG_3V3'),('ESP_D0','ESP_RESET')]:
    joined=merged[a]|merged[c]
    for n in list(merged):
        if merged[n] & joined:merged[n]=joined
for net,terminals in expected.items():
    mapped=[]
    for t in terminals:
        if t in bindings:mapped.append(bindings[t])
        elif re.match(r'^(C[234]|R[34589]|R10|RV1)\.',t):
            ref,pin=t.split('.');mapped.append((ref, {'+':'1','-':'2'}.get(pin,pin)))
    if len(mapped)<2:continue
    group=next((v for v in merged.values() if mapped[0] in v),set())
    require(set(mapped)<=group,'Wire schedule preserved (fuses removed, tier links closed): '+net)
used=set().union(*actual.values())
require(('JM2R1','1') not in used,'Controller RAW remains electrically isolated')
require(('JM3R1','8') not in used,'D1 Mini 5V remains electrically isolated')
require('FUSED_POS' not in actual and not any(r in ('F2','J1') for r,_ in used),'No fuse nets or parts on the carrier')
require(actual['PACK_NEG']=={('M1','6'),('JCELL1','2')},'Cell negative (B-) reaches only the charger B- pad and the CELL pad')
require(actual['PACK_POS']=={('M1','5'),('JCELL1','1')},'Cell positive reaches only the charger B+ pad and the CELL pad')
require(('M1','6') not in actual['GND_LOAD'] and ('JCELL1','2') not in actual['GND_LOAD'],'B- has no copper connection to GND_LOAD (OUT-)')
require(actual['CHARGE_RETURN']=={('M1','2'),('JPV1','2')},'Charger IN- is not linked to OUT- on the carrier')
require(actual['CHARGE_5V']=={('M1','1'),('JPV1','1')},'Solar input reaches only charger IN+ and the PV pad')
require(actual['PROTECTED_POS']=={('M1','3'),('JS1','1')},'Charger OUT+ reaches the rail only through S1')
require(actual['GND_LOAD']>={('M1','4')},'Charger OUT- is the load ground')
require(actual['LED_POS']=={('R3','2'),('JLED1','1')},'LED positive is fed only through R3')
require(actual['PWM']=={('R3','1'),('JM2L1','12')},'R3 is driven only by D9')
require(actual['LDR_SENSE']=={('R4','1'),('JLDR1','2'),('JM2R1','7')},'A1 sees only the LDR and R4')
require(actual['LDR_TRIM']=={('R4','2'),('RV1','1')} and {('RV1','2'),('RV1','3')}<=actual['GND_LOAD'],
        'RV1 is a rheostat (wiper to pin 3) between R4 and ground')
require(actual['TEST']=={('SW1','1'),('JM2L1','5')} and ('SW1','2') in actual['GND_LOAD'],'On-board SW1 pulls D2 to ground')
require(actual['REG_3V3']=={('JP1','1'),('JU3OUT1','1')},'Removing JP1 isolates U3 positive output from ESP supply')
require(actual['SENSE_FEED']=={('JP3','2'),('R5','1')},'Removing JP3 isolates battery-sense feed')
isp={'1':'ISP_MISO','2':'VBAT_SYS','3':'ISP_SCK','4':'ISP_MOSI','5':'AVR_RESET','6':'GND_LOAD'}
require(all(('JISP1',p) in actual[n] for p,n in isp.items()),'Standard six-pin AVR ISP ordering')
require(actual['ISP_SCK']=={('JISP1','3'),('JM2R1','9')} and actual['ISP_MISO']=={('JISP1','1'),('JM2R1','10')} and actual['ISP_MOSI']=={('JISP1','4'),('JM2R1','11')},
        'ISP SCK/MISO/MOSI go only to M2 D13/D12/D11')
require(len([f for f in b.GetFootprints() if f.GetReference().startswith('H')])==3,'Three mounting holes')
from design import M2_BODY
isp_top=min(pcb.ToMM(g.GetBoundingBox().GetY())-50 for g in b.FindFootprintByReference('JISP1').GraphicalItems() if g.GetLayer()==pcb.F_SilkS)
require(isp_top>M2_BODY[3],f'ISP box-header outline starts {isp_top-M2_BODY[3]:.1f} mm below the M2 outline')
bb=b.GetBoardEdgesBoundingBox();area=pcb.ToMM(bb.GetWidth())*pcb.ToMM(bb.GetHeight())
require(area<4000,f'Board area {area:.0f} mm2 is under half of Rev A (8000 mm2)')
cfg=(REPO/'firmware/controller/include/config.h').read_text()
for setting,value in [('PIN_LED_PWM',9),('PIN_LDR_PWR',7),('ADC_LDR',1),('PIN_BUTTON',2),('PIN_TX',1)]:
    require(bool(re.search(r'\b'+setting+r'\s*=\s*'+str(value)+r'\s*;',cfg)),'Firmware pin matches carrier: '+setting)
for name in ['drc','erc']:
    report=json.loads((ROOT/'review'/(name+'.json')).read_text())
    violations=report.get('violations',[])+report.get('unconnected_items',[])+report.get('schematic_parity',[])
    violations += [v for s in report.get('sheets',[]) for v in s['violations']]
    require(not violations,'KiCad '+name.upper()+': zero errors, warnings, unconnected items or exclusions')
require(all(pcb.ToMM(t.GetWidth())>=.3-1e-6 for t in b.GetTracks() if not isinstance(t,pcb.PCB_VIA)), 'Every copper track is at least 0.30 mm wide')
require(all(pcb.ToMM(t.GetDrillValue())>=.4-1e-6 for t in b.GetTracks() if isinstance(t,pcb.PCB_VIA)),'Via drill at least 0.40 mm')
# Model checks are disclosed as estimates, never as physical qualification.
R3_OHM=56
models={'LED_typical_mA':{str(v):round(1000*(v-2.56)/(R3_OHM+30),2) for v in (3.4,3.7,4.2)},
 'LED_4V2_sensitivity_mA':{'min':round(1000*(4.2-2.7)/(R3_OHM*1.05+40),2),
                         'max':round(1000*(4.2-2.3)/(R3_OHM*.95+20),2)},
 'A0_chip_at_4V2_V':4.2*100/540,'A0_header_at_4V2_V':4.2*320/540,
 'UART_base_uA_at_3V0_Vbe_0V8':1e6*((3-.8)/47000-.8/100000),
 'UART_collector_uA_at_3V3_Vce_0V2':1e6*(3.3-.2)/10000,
 # Copper resistivity 1.724e-5 ohm mm (20 C), with all lengths in mm.
 'trace_100mm_0V8mm_1oz_400mA_drop_mV':1000*.4*.00001724*100/(.8*.035)}
require(24<models['trace_100mm_0V8mm_1oz_400mA_drop_mV']<25,'Copper resistance unit check: 100 mm trace drops about 25 mV at 400 mA')
require(models['A0_chip_at_4V2_V']<1,'D1 Mini ADC model below 1 V IF onboard 220k/100k divider is present')
require(models['UART_collector_uA_at_3V3_Vce_0V2']/models['UART_base_uA_at_3V0_Vbe_0V8']<10,
        'UART inverter calculated forced beta below 10 at 3.0 V (still requires 9600-baud bench test)')
out={'status':'CAD_CHECKS_PASS_PHYSICAL_QUALIFICATION_PENDING','checks':passed,'models_not_measurements':models,
     'sha256':{suffix:hashlib.sha256((ROOT/(NAME+suffix)).read_bytes()).hexdigest() for suffix in ('.kicad_pcb','.kicad_sch')}}
(ROOT/'review'/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS:',len(passed),'checks. Physical fit/current/charger/radio tests remain pending.')
