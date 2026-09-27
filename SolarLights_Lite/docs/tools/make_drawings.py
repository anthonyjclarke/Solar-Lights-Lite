#!/usr/bin/env python3
"""v0.5 development drawings. Vector SVG/PDF plus raster previews from one source.
Run with a Python environment containing reportlab and pypdfium2.
"""
from pathlib import Path
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle, PolyLine
from reportlab.graphics import renderSVG, renderPDF
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
import pypdfium2 as pdf
import csv, json
DOC=Path(__file__).resolve().parents[1]
PROJECT=DOC.parents[1]
OUT=PROJECT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
W,H=1440,900
INK='#173047'; MUTED='#516578'; RED='#c1363d'; GND='#334454'; BLUE='#176eb0'; GREEN='#008572'; AMBER='#ad6200'; PURPLE='#7a4bb1'
D=None

def line(x1,y1,x2,y2,c=INK,w=2,dash=None):
 o=Line(x1,H-y1,x2,H-y2,strokeColor=HexColor(c),strokeWidth=w)
 if dash:o.strokeDashArray=dash
 D.add(o)
def path(points,c=INK,w=2,dash=None):
 for a,b in zip(points,points[1:]):line(*a,*b,c,w,dash)
def text(x,y,t,size=17,c=INK,bold=False):D.add(String(x,H-y,t,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=HexColor(c)))
def lines(x,y,items,size=16,c=INK,leading=25):
 for i,t in enumerate(items):text(x,y+i*leading,t,size,c)
def rect(x,y,w,h,fill='#ffffff',stroke='#cbd7df',r=12):D.add(Rect(x,H-y-h,w,h,rx=r,ry=r,fillColor=HexColor(fill),strokeColor=HexColor(stroke),strokeWidth=1.5))
def dot(x,y,c=INK):D.add(Circle(x,H-y,4,fillColor=HexColor(c),strokeColor=None))
def cross(x,y,c=RED,size=8,w=3):
 line(x-size,y-size,x+size,y+size,c,w);line(x-size,y+size,x+size,y-size,c,w)
def pin(x,y,label,side='right',c=INK):
 dot(x,y,c);text(x+12 if side=='right' else x-12,y-9,label,16,c)
def tag(x,y,label,c=INK):
 text(x,y-9,label,16,c,True);line(x,y,x+45,y,c)
def ground(x,y,label='GND_LOAD'):
 line(x,y,x,y+10,GND);line(x-14,y+10,x+14,y+10,GND);line(x-9,y+16,x+9,y+16,GND);line(x-4,y+22,x+4,y+22,GND);text(x+20,y+19,label,14,GND)
def res(x,y,label,value,vertical=False,c=INK):
 if vertical:
  line(x,y-35,x,y-20,c);rect(x-8,y-20,16,40,'#ffffff',c,0);line(x,y+20,x,y+35,c);text(x+17,y-4,label,16,c,True);text(x+17,y+17,value,15,c)
 else:
  line(x-50,y,x-30,y,c);rect(x-30,y-8,60,16,'#ffffff',c,0);line(x+30,y,x+50,y,c);text(x-28,y-20,label+' '+value,15,c,True)
def cap(x,y,label,value):
 line(x,y-35,x,y-7,RED);line(x-17,y-7,x+17,y-7,RED);line(x-17,y+7,x+17,y+7,GND);line(x,y+7,x,y+35,GND);text(x+24,y-8,label+' '+value,15,INK,True);text(x-29,y-14,'+',18,RED)
def module(x,y,w,h,title,sub,amber=False):
 rect(x,y,w,h,'#fff8e9' if amber else '#edf5f8', '#d6a34f' if amber else '#9ab6c4');text(x+20,y+34,title,21,AMBER if amber else INK,True);text(x+20,y+62,sub,14,MUTED)
def note(x,y,w,title,items,amber=False):
 ht=55+len(items)*24;rect(x,y,w,ht,'#fff8e9' if amber else '#f0f5f8');text(x+18,y+30,title,18,AMBER if amber else INK,True);lines(x+18,y+56,items,15,MUTED,24)
def header(n,title,sub):
 global D
 D=Drawing(W,H);rect(0,0,W,H,'#ffffff','#ffffff',0);text(42,38,'SOLARLIGHTS / REBUILD 2026',15,GREEN,True);text(42,80,title,32,INK,True);text(42,110,sub,16,MUTED)
 line(42,132,1398,132,'#d5e0e6',1)
 line(42,850,1398,850,'#d5e0e6',1);text(42,877,'v0.5 DEVELOPMENT PROPOSAL  |  27-SEP-2026  |  NOT RELEASED FOR OUTDOOR ASSEMBLY',13,AMBER,True);text(1175,877,f'SHEET {n} OF 6 / A3',13,MUTED)
def save(name):
 renderSVG.drawToFile(D,str(DOC/(name+'.svg')));return D
pages=[]
header(1,'Power, charging & battery','Terminal-level schematic. Amber blocks need part selection and bench qualification. All loads connect to protected outputs.')
module(45,195,205,210,'PV1 / existing','AS102-0712A 1.2 W')
lines(64,285,['Vmp 7 V / Imp 170 mA','Voc 7.6 V at 25 C','Cold Voc: measure'],15,MUTED)
pin(250,350,'+',c=BLUE);pin(250,385,'-',c=BLUE)
module(325,195,265,220,'U0 / 5 V regulator','PART TBD - required',True)
lines(345,275,['Vin rating > cold Voc','5 V at load AND no-load','Test cloud/startup cycling'],15,MUTED,20)
pin(325,350,'IN+',c=BLUE);pin(325,385,'IN-',c=BLUE);pin(590,350,'OUT+',c=RED);pin(590,385,'OUT-',c=BLUE)
line(250,350,325,350,BLUE);line(250,385,325,385,BLUE)
module(690,195,280,310,'M1 / protected 4056','Verify actual chip and pad labels')
lines(710,275,['Start 100-150 mA charge','PROG resistor: verify law','Cell TEMP inhibit unresolved'],15,AMBER,20)
pin(690,350,'IN+',c=RED);pin(690,385,'IN-',c=BLUE);line(590,350,690,350,RED);line(590,385,690,385,BLUE)
pin(970,350,'OUT+',c=RED);pin(970,470,'OUT-',c=GND)
pin(755,505,'B+',c=PURPLE);pin(895,505,'B-',c=PURPLE)
res(1070,350,'F2','1 A');line(970,350,1020,350,RED);line(1120,350,1160,350,RED)
line(1160,350,1190,330,RED);dot(1160,350,RED);dot(1205,350,RED);text(1160,310,'S1 service',15,INK,True);line(1205,350,1360,350,RED);text(1230,332,'VBAT_SYS',17,RED,True)
line(970,470,1360,470,GND);text(1220,452,'GND_LOAD',17,GND,True)
lines(1110,540,['To sheets 2 and 3','VBAT_SYS: battery voltage','GND_LOAD: OUT- only'],17,INK)
# Battery branches, each positive fused.
path([(755,505),(755,580),(300,580)],PURPLE)
path([(895,505),(895,740),(300,740)],PURPLE)
for x,label in [(350,'BT1'),(610,'BT2')]:
 line(x,580,x,605,PURPLE);res(x,640,'FB'+label[-1],'1 A',True,PURPLE);line(x,675,x,689,PURPLE)
 line(x-22,689,x+22,689,PURPLE,3);line(x-11,701,x+11,701,PURPLE,3);line(x,701,x,740,PURPLE)
 text(x-24,682,'+',16,PURPLE);text(x+45,700,label+' / 18650',18,INK,True);dot(x,580,PURPLE);dot(x,740,PURPLE)
text(300,556,'1S2P / matched cells / individually fused',17,PURPLE,True)
text(300,780,'Never series-connect these cells to a 1S charger. Do not bridge B- to OUT-.',17,INK,True)
note(1000,600,385,'Ground check before wiring',['Some modules join IN- to OUT- internally.','Confirm yours; do not add an external link.','B- remains behind the protection FETs.','Service with panel and batteries removed.'],True)
text(45,833,'No pair of series diodes is accepted as overvoltage protection. Unattended charging awaits cell-temperature protection.',16,AMBER,True)
pages.append(save('01-power'))
header(2,'Light controller & LED driver','Reused 16 MHz Pro Mini converted to internal 8 MHz. Switched LDR; dusk to dawn at 100% command, with R3 setting the current.')
module(350,210,325,430,'M2 / BTE13-010A','ATmega328P, verified 8 MHz')
lines(370,290,['Remove regulator + power LED','VCC supplied directly; RAW unused','D10/D11: open, reserved','No raw-panel sense on A0; no Q1'],16,MUTED)
# Power inputs at top using labels
line(435,175,435,210,RED);text(370,169,'VBAT_SYS',16,RED,True)
line(600,175,600,210,GND);text(553,169,'GND_LOAD',16,GND,True)
text(445,200,'VCC',14,RED);text(610,200,'GND',14,GND)
# LDR left local circuit
pin(350,400,'D7',c=GREEN);path([(350,400),(160,400),(160,425)],GREEN)
res(160,460,'LDR1','ambient light',True,GREEN);D.add(Circle(160,H-460,29,fillColor=None,strokeColor=HexColor(GREEN),strokeWidth=1.5));line(100,415,124,440,GREEN);line(104,439,124,440,GREEN);line(123,420,124,440,GREEN)
line(160,495,160,525,GREEN);dot(160,525,GREEN);line(160,525,350,525,GREEN);pin(350,525,'A1',c=GREEN)
line(160,525,160,545,GREEN);res(160,580,'R4','100k',True);line(160,615,160,655,GND);ground(160,655)
# Button
pin(350,600,'D2',c=GREEN);line(265,600,350,600,GREEN);line(265,600,265,705,GREEN);dot(265,705);dot(315,705);line(272,692,309,692);line(290,681,290,692);line(315,705,355,705,GND);ground(355,705);text(208,744,'SW1 / test',16,INK,True)
# driver output - measured string driven straight from D9, no switching device (20-Sep-2026)
pin(675,400,'D9 / PWM',c=GREEN);path([(675,400),(735,400),(735,250),(1090,250)],GREEN)
res(1090,290,'R3','47R',True,GREEN);line(1090,325,1090,380,GREEN)
rect(1000,380,180,83,'#f0f8ed','#7fab66');text(1018,412,'JLED / string',18,INK,True);text(1018,439,'+ top / - bottom',14,MUTED)
line(1090,463,1090,705,GND);ground(1090,705)
text(1210,258,'No Q1, R6, R7 or F1',17,INK,True)
lines(1210,286,['Measured string: 2.56 V drop','I = (VBAT - 2.56) / (R3 + 30R)','21 / 15 / 11 mA at','4.20 / 3.70 / 3.40 V','Fit 56R to stay under 20 mA'],15,MUTED)
text(1210,414,'Pin max 40 mA absolute',15,AMBER);text(1210,436,'Fit R3 at the board end',15,AMBER)
# status to next sheet
pin(675,600,'D8 / status',c=GREEN);line(675,600,815,600,GREEN);text(700,632,'to sheet 3',14,GREEN)
# decoupling separated labels no hidden routing
cap(500,727,'C3','100u / 10 V');line(500,675,500,692,RED);text(435,670,'VBAT_SYS',14,RED,True);ground(500,762)
cap(700,727,'C4','100n');line(700,675,700,692,RED);text(640,670,'VBAT_SYS',14,RED,True);ground(700,762)
text(45,833,'All ground symbols on this sheet mean OUT-. R3 sets the peak current; duty changes the average only. Verify current at 4.20 V and 100% duty.',16,AMBER,True)
pages.append(save('02-controller'))
header(3,'Low-power telemetry reference (D1 Mini)','Retained for the later production profile. This is not the always-on D1 Mini UART test system on sheet 6.')
module(65,210,310,230,'U3 / 3.3 V supply','Buck-boost module TBD',True)
lines(85,303,['Input: protected battery rail','Qualify radio bursts + standby','Use specified output capacitors'],16,MUTED)
line(95,180,95,210,RED);text(60,173,'VBAT_SYS',16,RED,True);line(330,180,330,210,GND);text(258,173,'GND_LOAD',16,GND,True)
pin(375,390,'3V3',c=RED);line(375,390,755,390,RED)
module(755,180,390,370,'M3 / D1 Mini','Isolate onboard regulator first')
pin(755,390,'3V3',c=RED);lines(778,282,['5V / USB: disconnected','D6: not fitted'],17,MUTED)
pin(1145,390,'D0',c=GREEN);pin(1145,445,'RST',c=GREEN);path([(1145,390),(1220,390),(1220,445),(1145,445)],GREEN)
pin(950,550,'G',c=GND);line(950,550,950,595,GND);ground(950,595)
# battery adc top stub separate
text(430,166,'VBAT_SYS',16,RED,True);line(490,180,490,245,RED);res(490,280,'R5','220k',True);path([(490,315),(490,345),(755,345)],GREEN);pin(755,345,'A0',c=GREEN)
# Input cap
cap(190,505,'C2','470u / 10 V');tag(110,470,'VBAT_SYS',RED);line(155,470,190,470,RED);ground(190,540)
# NPN status below, named D8 connector
text(70,655,'M2 D8',17,GREEN,True);line(70,680,220,680,GREEN);res(270,680,'R8','47k',False,GREEN);line(320,680,445,680,GREEN);dot(360,680,GREEN)
res(360,715,'R9','100k',True);ground(360,755);line(360,750,360,755,GND)
D.add(Circle(480,H-680,39,fillColor=None,strokeColor=HexColor(INK),strokeWidth=2));line(458,658,458,702,INK,3);line(445,680,458,680,GREEN);path([(458,667),(500,639),(500,615)],INK);path([(458,693),(500,721),(500,770)],GND);path([(485,704),(493,717),(479,715)],GND);ground(500,770)
text(552,724,'Q2 / 2N3904',17,INK,True);text(552,747,'check E/B/C',14,MUTED)
# collector pullup and signal
line(500,615,620,615,GREEN);dot(620,615,GREEN);path([(620,615),(680,615),(680,475),(755,475)],GREEN);pin(755,475,'D5',c=GREEN)
line(620,615,620,565,RED);res(620,530,'R10','10k',True,RED);line(620,495,620,455,RED);text(582,444,'ESP 3V3',16,RED,True)
note(830,665,540,'Interface behaviour',['D8 HIGH -> Q2 ON -> D5 LOW -> HA Lights On = true.','Collector pulls up only to the ESP supply; YAML is inverted.','A0 calculation assumes onboard 220k / 100k resistors.','Calibrate actual battery voltage; percentage is approximate.'])
text(45,833,'Disconnect external power AND signal leads before USB/programmer servicing. Never supply the ESP 3V3 pin from the cell directly.',16,AMBER,True)
pages.append(save('03-telemetry'))
header(4,'What to assemble inside the enclosure','Top-down placement concept, not a drilling template. Use terminal labels and the wire schedule for electrical connections.')
# Enclosure and board
rect(45,180,915,630,'#f2f5f7','#8599a9',26);text(70,213,'WEATHERPROOF BOX / SHADED POSITION',17,INK,True)
rect(90,245,615,410,'#fffaf0','#c8b787',10);text(110,274,'PERFBOARD / MODULE CARRIER',16,MUTED,True)
# schematic perf dots light
for x in range(108,690,22):
 for y in range(295,640,22):D.add(Circle(x,H-y,1.4,fillColor=HexColor('#dfd3b6'),strokeColor=None))
module(115,315,210,100,'U0 / input 5 V','Selected after bench test',True)
module(115,470,210,120,'M1 / charger','IN / B / OUT labelled')
module(425,320,230,115,'M2 / Pro Mini','8 MHz; sockets; ISP access')
module(425,495,230,115,'LED driver','R3 only - D9 direct')
# rail explicit route physical illustrative
line(368,300,368,615,RED,6);line(390,300,390,615,GND,6);text(345,289,'+    -',18,INK,True)
line(325,500,368,500,RED,3);line(325,550,390,550,GND,3);text(334,650,'Protected rails',16,INK,True)
line(368,350,425,350,RED,3);line(390,395,425,395,GND,3);line(368,520,425,520,RED,3);line(390,570,425,570,GND,3)
# telemetry antenna right
module(745,275,175,130,'U3 / 3V3','Optional',True);module(745,470,175,150,'M3 / D1','Sockets / service')
rect(760,578,145,28,'#c9dfeb','#9ab6c4',2);text(774,598,'ANTENNA',14,BLUE,True);text(745,650,'Keep antenna clear',16,BLUE,True)
# cells with physical positive fuses
for x,l in [(110,'BT1'),(420,'BT2')]:
 rect(x,695,260, 72,'#d7e8da','#80a888',30);rect(x+247,715,18,30,'#d7e8da','#80a888',3);text(x+20,739,l+' / 18650   -      +',18,INK,True)
text(110,792,'Insulated parallel holder; fuse each + lead; separate cells from heat.',15,MUTED)
# glands
for x,l in [(190,'PANEL'),(530,'LIGHTS'),(820,'LDR')]:
 rect(x,163,95,36,'#e3eaf0','#8599a9',6);text(x+12,185,l,13,INK,True)
# annotations independent build sequence
note(995,180,398,'Build in this order',['1  Qualify panel regulator + charger.','2  Convert and test the Pro Mini.','3  Add R3 (47R) and light string - no MOSFET.','4  Add LDR; check dusk/dawn + LVC.','5  Assemble the protected, fused pack.','6  Add optional telemetry and measure.'])
note(995,420,398,'Label every connector',['RED: protected positive / VBAT_SYS','BLACK: load return / OUT-','BLUE: panel input pair','PURPLE: battery-only connections','GREEN: logic / sensor signals'])
note(995,637,398,'Before closing the lid',['Strain relief, polarity, cell insulation.','No exposed underside copper.','Charger/cell temperature tests passed.','Log charge, load and actual brightness.'],True)
pages.append(save('04-assembly'))
header(5,'Staged power-up & serial diagnostics','Battery powers the controller. The USB-UART listens only: connect RX and GND; leave its power and control pins open.')
# Protected battery and controller power path.
module(45,190,285,300,'M1 / protected 4056','Read pad labels, not positions')
lines(65,272,['Cell connects to B+ / B-','Load uses OUT+ / OUT-','Never bridge B- to OUT-'],15,MUTED,23)
pin(330,285,'OUT+',c=RED);pin(330,420,'OUT-',c=GND)
pin(110,490,'B+',c=PURPLE);pin(260,490,'B-',c=PURPLE)
res(400,285,'F2','1 A');line(330,285,350,285,RED);line(450,285,485,285,RED)
line(485,285,515,265,RED);dot(485,285,RED);dot(530,285,RED);text(472,238,'S1',15,INK,True);text(450,258,'service switch',13,MUTED)
module(530,190,285,300,'M2 / BTE13-010A','internal 8 MHz / debug build')
line(530,285,530,285,RED);line(530,285,565,285,RED);pin(565,285,'VCC',c=RED)
pin(565,420,'GND',c=GND);line(330,420,565,420,GND)
dot(815,335,GREEN);text(760,341,'TX',16,GREEN,True)
dot(815,375,MUTED);text(700,381,'RX: OPEN',16,MUTED,True)
text(585,455,'RAW: OPEN',15,AMBER,True);cross(565,453,AMBER,7,2)
# One-cell test source and explicit battery-only domain.
rect(65,555,245,80,'#d7e8da','#80a888',35);text(87,590,'BT1 / one suitable 1S cell',17,INK,True);text(89,617,'-                         +',17,PURPLE,True)
path([(110,490),(110,530),(275,530),(275,555)],PURPLE)
path([(260,490),(260,515),(95,515),(95,555)],PURPLE)
text(45,668,'Before closing S1',18,INK,True)
lines(45,696,['1  Meter OUT+ to OUT-: polarity correct.','2  Expect approximately the cell voltage.','3  UART power lead already removed.','4  Close S1; compare serial vdd with meter.'],15,MUTED,23)
# UART board based on the supplied EZSBC photo: USB at left, six-pin header at right.
rect(905,180,465,430,'#e6f4ef','#008572',12);text(930,214,'USB-UART / EZSBC-style board',20,GREEN,True);text(930,240,'Pin order copied from the supplied photo',14,MUTED)
rect(870,310,95,155,'#dce5e9','#768a96',5);rect(852,340,38,95,'#eef2f4','#768a96',3);text(876,490,'USB',15,MUTED,True)
rect(1010,285,120,190,'#263746','#263746',5);text(1033,385,'USB-UART',15,'#ffffff',True)
rect(1340,260,30,300,'#263746','#263746',2)
uart_pins=[('DTR',275,False),('RX',325,True),('TX',375,False),('VO',425,False),('CTS',475,False),('GND',525,True)]
for label,y,used in uart_pins:
 c=GREEN if used else MUTED
 line(1318,y,1355,y,c,3);dot(1318,y,c);text(1242 if label!='GND' else 1224,y+6,label,18,c,True)
 if not used:
  cross(1382,y,RED,8,3);text(1396,y+6,'OPEN',12,RED,True)
# Data and common-ground wiring only. Routes stay visually separate.
path([(815,335),(875,335),(875,325),(1318,325)],GREEN,4)
text(835,305,'M2 TX -> adapter RX',15,GREEN,True)
path([(565,420),(835,420),(835,620),(1185,620),(1185,525),(1318,525)],GND,4)
text(850,612,'M2 GND / OUT- -> adapter GND',15,GND,True)
note(900,635,470,'USB-UART rules',['USB cable powers the adapter itself.','Do not connect VO to M2 VCC.','Leave DTR, TX and CTS open for monitoring.','Keep adapter USB-powered while M2 TX is attached.'],True)
# Visual pass-gate strip.
text(390,672,'Proceed one gate at a time',18,INK,True)
gate_x=[390,455,520,585,650,715,780]
gate_names=['M2','BAT','LDR','LVC','5 V','PV','RUN']
for i,(x,label) in enumerate(zip(gate_x,gate_names),1):
 D.add(Circle(x,H-724,24,fillColor=HexColor('#eaf7f4'),strokeColor=HexColor(GREEN),strokeWidth=2));text(x-5,730,str(i),16,GREEN,True);text(x-17,765,label,13,MUTED,True)
 if i<len(gate_x):line(x+24,724,gate_x[i]-24,724,GREEN,2)
note(390,520,425,'Serial checkpoints',['DAY off: state=0 pct=0 / about 8 s ticks','D2 test: state=0 pct=100','LVC: state=4 pct=0; button cannot relight'])
text(45,833,'SERIAL IS NOT A CHARGE METER: verify panel input, regulated 5 V, battery voltage and charge current with instruments.',16,AMBER,True)
pages.append(save('05-staging'))
header(6,'Development telemetry (Wemos D1 Mini)','TEST SYSTEM ONLY: always-on Wi-Fi and UART capture. Reuses the existing status transistor parts; no INA226 or new telemetry module. Production D1 profile remains on sheet 3.')
note(42,140,1356,'Read this first',['Always-on Home Assistant test configuration: Q2/R8/R9/R10 become a safe, inverted UART receiver. The D1 Mini deep-sleep production reference is sheet 3.'],True)
# Three blocks make the only active signal path unambiguous: Arduino TX -> Q2 -> D1 D6.
module(65,240,305,230,'1 / M2 Arduino','Flash pro8_debug')
lines(88,325,['VCC: VBAT_SYS','GND: OUT- / GND_LOAD','D1/TX: 9600-baud diagnostics','D8: OPEN in this test profile'],16,MUTED,25)
pin(370,420,'D1 / TX',c=GREEN);pin(370,450,'GND',c=GND)
module(475,240,435,230,'2 / Reused UART receiver','Q2 inverts and level-shifts the Arduino TX')
text(500,320,'M2 D1/TX',15,GREEN,True);path([(370,420),(420,420),(420,350),(500,350)],GREEN,3);line(500,350,545,350,GREEN,3);res(595,350,'R8','47k',False,GREEN);line(645,350,675,350,GREEN,3)
D.add(Circle(720,H-350,38,fillColor=None,strokeColor=HexColor(INK),strokeWidth=2));line(698,328,698,372,INK,3);line(675,350,698,350,GREEN)
path([(698,337),(755,305),(755,335)],INK);path([(698,363),(755,402),(755,442)],GND);ground(755,442,'OUT-')
res(665,400,'R9','100k',True,GREEN);line(665,435,665,442,GND)
line(755,335,820,335,GREEN,3);dot(820,335,GREEN);path([(820,335),(850,335),(850,435),(970,435)],GREEN,3)
res(820,300,'R10','10k',True,RED);text(780,255,'ESP 3V3',15,RED,True)
text(790,410,'Q2 / 2N3904',16,INK,True)
module(970,240,370,230,'3 / M3 Wemos D1 Mini','Always-on test telemetry',True)
lines(994,330,['3V3: qualified U3 buck-boost','D6: inverted UART RX','A0: existing battery divider','D5: OPEN; `output=` is light state'],16,MUTED,22)
pin(970,435,'D6 RX',c=GREEN);pin(970,465,'G',c=GND);pin(970,450,'A0',c=BLUE)
# The two ground pins share OUT-, but no signal returns from the D1 to the Arduino.
path([(370,450),(420,450),(420,490),(920,490),(920,465),(970,465)],GND,3)
text(470,514,'OUT- / GND_LOAD common return only — D1 Mini TX remains OPEN',15,GND,True)
# Battery sensing is separated from the UART drawing for an easy calibration check.
rect(65,565,365,155,'#edf5f8','#9ab6c4',12);text(88,598,'Existing battery reading',19,INK,True)
text(88,628,'VBAT_SYS',15,RED,True);line(190,620,190,642,RED);res(190,675,'R5','220k',True,BLUE);line(190,710,190,725,BLUE)
path([(190,725),(190,745),(935,745),(935,450),(970,450)],BLUE,3)
lines(245,632,['D1 A0 has its onboard divider too.','Calibrate its 5.21 multiplier against a meter.','Compare it with parsed','Arduino VDD.'],14,MUTED,19)
note(465,565,420,'What Home Assistant receives',['Arduino: VDD, LDR, sense/mode/night, output duty,','LVC/test progress, cause, transition and raw line.','D1: battery voltage/percentage, Wi-Fi, reset, heap and uptime.'])
note(910,565,430,'No-purchase boundary',['Not measured: panel voltage, charge/load current, energy,','physical LED current or temperatures.','`output=` replaces D8-to-D5: leave both pins open.'],True)
text(465,770,'Test rules: run pro8_debug • no USB-UART adapter on M2 • keep D1 awake • use solar-lights-lite.yaml later for production',16,AMBER,True)
pages.append(save('06-telemetry-dev'))
# Multipage A3 PDF; PDF render is authoritative preview.
fn=OUT/'SolarLights_Rev05_Drawings.pdf';cv=Canvas(str(fn),pagesize=landscape(A3));pw,ph=landscape(A3)
for d in pages:
 cv.saveState();scale=min(pw/W,ph/H);cv.translate((pw-W*scale)/2,(ph-H*scale)/2);cv.scale(scale,scale);renderPDF.draw(d,cv,0,0);cv.restoreState();cv.showPage()
cv.save()
p=pdf.PdfDocument(str(fn))
for i,page in enumerate(p):page.render(scale=1.3).to_pil().save(DOC/f'sheet-{i+1}.png')
print(fn)
