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
 line(42,850,1398,850,'#d5e0e6',1);text(42,877,'v0.5 AS BUILT  |  30-SEP-2026  |  ACTIVE BENCH DEVELOPMENT',13,GREEN,True);text(1175,877,f'SHEET {n} OF 7 / A3',13,MUTED)
def save(name):
 renderSVG.drawToFile(D,str(DOC/(name+'.svg')));return D
# ---- presentation layer: shadowed cards, ref pills, pin chips, icons, line hops.
# renderSVG ignores fill opacity, so soft colours are pre-mixed onto white (tint).
import math
from reportlab.graphics.shapes import Polygon, ArcPath
from reportlab.pdfbase.pdfmetrics import stringWidth
def tint(c,a):
 c=c.lstrip('#');return '#'+''.join(f'{round(255-(255-int(c[i:i+2],16))*a):02x}' for i in (0,2,4))
def tw(t,size,bold=False):return stringWidth(t,'Helvetica-Bold' if bold else 'Helvetica',size)
def poly(pts,fill=None,stroke=None,w=1.5):
 flat=[v for x,y in pts for v in (x,H-y)]
 D.add(Polygon(flat,fillColor=HexColor(fill) if fill else None,strokeColor=HexColor(stroke) if stroke else None,strokeWidth=w))
def disc(x,y,r,fill,stroke=None,w=1.5):
 D.add(Circle(x,H-y,r,fillColor=HexColor(fill) if fill else None,strokeColor=HexColor(stroke) if stroke else None,strokeWidth=w))
def arc(x,y,r,a0,a1,c,w=2.5):
 p=ArcPath(strokeColor=HexColor(c),strokeWidth=w,fillColor=None,strokeLineCap=1);p.addArc(x,H-y,r,a0,a1,moveTo=True);D.add(p)
def box(x,y,w,h,fill,stroke=None,r=0,sw=2):
 D.add(Rect(x,H-y-h,w,h,rx=r,ry=r,fillColor=HexColor(fill) if fill else None,strokeColor=HexColor(stroke) if stroke else None,strokeWidth=sw))
def pill(x,y,label,bg,fg='#ffffff',size=12,pad=8):
 w=tw(label,size,True)+2*pad;h=size+9
 box(x,y,w,h,bg,None,h/2);text(x+pad,y+h-6,label,size,fg,True);return w
def card(x,y,w,h,accent,fill='#ffffff',stroke='#d3dee6'):
 box(x+3,y+6,w,h,tint('#0b2238',0.08),None,14)
 box(x,y,w,h,fill,stroke,14,1.2)
 box(x+18,y,w-36,4,accent,None,2)
def head(x,y,ref,title,sub,accent,tcol=INK):
 pw=pill(x+18,y+20,ref,accent,size=12) if ref else -8
 text(x+26+pw,y+36,title,19,tcol,True)
 if sub:text(x+18,y+62,sub,13.5,MUTED)
def chip(x,y,label,c,size=11.5):
 w=tw(label,size,True)+12
 box(x,y-9,w,18,tint(c,0.13),c,4,1);text(x+6,y+4.5,label,size,c,True);return w
def rchip(x,y,label,c,size=11.5):
 """chip right-aligned to x (for pins on a card's right edge)"""
 return chip(x-tw(label,size,True)-12,y,label,c,size)
def row(x,y,pin_,c,t,size=13.5):text(x+chip(x,y,pin_,c)+10,y+5,t,size,INK)
def arrow(x,y,d,c,s=7):
 pts={'r':[(x+s,y),(x-s,y-s),(x-s,y+s)],'l':[(x-s,y),(x+s,y-s),(x+s,y+s)],'d':[(x,y+s),(x-s,y-s),(x+s,y-s)],'u':[(x,y-s),(x-s,y+s),(x+s,y+s)]}[d]
 poly(pts,c)
def vhop(x,y1,y2,hops,c,w=3):
 """Vertical wire from y1 down to y2 that hops (semicircle) over each rail y in hops."""
 ys=[y1]+[v for hy in sorted(hops) for v in (hy-7,hy+7)]+[y2]
 for a,b in zip(ys[::2],ys[1::2]):line(x,a,x,b,c,w)
 for hy in hops:arc(x,hy,7,-90,90,c,w)
def badge(cx,cy,c):disc(cx,cy,21,tint(c,0.12))
def i_sun(cx,cy,c):
 disc(cx,cy,6.5,c)
 for k in range(8):
  a=k*math.pi/4;line(cx+10*math.cos(a),cy+10*math.sin(a),cx+14.5*math.cos(a),cy+14.5*math.sin(a),c,2.2)
def i_bolt(cx,cy,c):poly([(cx+3,cy-13),(cx-8,cy+2),(cx-1,cy+2),(cx-4,cy+13),(cx+8,cy-3),(cx+1,cy-3)],c)
def i_shield(cx,cy,c):
 poly([(cx,cy-13),(cx+10,cy-9),(cx+9,cy+3),(cx,cy+12),(cx-9,cy+3),(cx-10,cy-9)],c);path([(cx-5,cy),(cx-1,cy+4),(cx+6,cy-5)],'#ffffff',2.4)
def i_batt(cx,cy,c):
 box(cx-12,cy-7,22,14,None,c,2,2);box(cx+10,cy-3,3,6,c,None);box(cx-9,cy-4,11,8,c,None)
def i_chip(cx,cy,c):
 box(cx-8,cy-8,16,16,c,None,2)
 for k in (-4,0,4):line(cx-13,cy+k,cx-8,cy+k,c,2);line(cx+8,cy+k,cx+13,cy+k,c,2);line(cx+k,cy-13,cx+k,cy-8,c,2);line(cx+k,cy+8,cx+k,cy+13,c,2)
def i_wifi(cx,cy,c):
 for r in (5,10,15):arc(cx,cy+7,r,45,135,c,2.6)
 disc(cx,cy+7,2.6,c)
def i_gauge(cx,cy,c):
 arc(cx,cy+5,13,0,180,c,2.6);line(cx,cy+5,cx+8,cy-4,c,2.4);disc(cx,cy+5,2.8,c)
def i_check(cx,cy,c):path([(cx-8,cy),(cx-2,cy+6),(cx+9,cy-7)],c,3)
def i_warn(cx,cy,c):
 poly([(cx,cy-13),(cx+13,cy+10),(cx-13,cy+10)],c);box(cx-1.5,cy-5,3,9,'#ffffff',None);disc(cx,cy+7,1.8,'#ffffff')
def i_info(cx,cy,c):
 disc(cx,cy,12,c);box(cx-1.6,cy-2,3.2,9,'#ffffff',None);disc(cx,cy-6,2,'#ffffff')
def i_bulb(cx,cy,c):
 disc(cx,cy-3,9,c);box(cx-5,cy+6,10,6,c,None,1.5);line(cx-4,cy+14,cx+4,cy+14,c,2)
def i_usb(cx,cy,c):
 line(cx,cy+12,cx,cy-9,c,2.4);poly([(cx,cy-14),(cx-5,cy-7),(cx+5,cy-7)],c)
 path([(cx,cy+4),(cx-8,cy-2),(cx-8,cy-6)],c,2.2);disc(cx-8,cy-7,2.6,c);path([(cx,cy+1),(cx+8,cy-5),(cx+8,cy-8)],c,2.2);box(cx+5.5,cy-11,5,5,c,None)
def i_box(cx,cy,c):
 poly([(cx,cy-12),(cx+12,cy-6),(cx,cy),(cx-12,cy-6)],c);poly([(cx-12,cy-3),(cx-1.5,cy+2.5),(cx-1.5,cy+13),(cx-12,cy+7)],c);poly([(cx+12,cy-3),(cx+1.5,cy+2.5),(cx+1.5,cy+13),(cx+12,cy+7)],c)
def i_flag(cx,cy,c):
 line(cx-8,cy-12,cx-8,cy+13,c,2.4);poly([(cx-8,cy-12),(cx+10,cy-6),(cx-8,cy+1)],c)
def i_led(cx,cy,c):
 poly([(cx-7,cy-8),(cx-7,cy+8),(cx+6,cy)],c);line(cx+7,cy-8,cx+7,cy+8,c,2.4)
 for d in (0,6):line(cx+2+d,cy-10,cx+7+d,cy-15,c,1.6)
def grid():
 """faint engineering grid behind the content"""
 for gx in range(42,1399,36):line(gx,140,gx,842,'#f2f6f9',0.7)
 for gy in range(140,843,36):line(42,gy,1398,gy,'#f2f6f9',0.7)
def strip(y,label,msg,c=AMBER,size=13):
 box(42,y,1356,34,tint(c,0.09),tint(c,0.35),10,1);w=pill(52,y+6,label,c,size=11);text(52+w+14,y+22,msg,size,INK)
def legend(y,items):
 text(42,y+4,'NETS',11,MUTED,True);lx=88
 for lab,c,dash in items:
  line(lx,y,lx+26,y,c,3.5,dash);text(lx+34,y+4,lab,12,INK);lx+=34+tw(lab,12)+26
def warn(msg,y=804,c=AMBER,label='RULE'):
 box(42,y,1356,34,tint(c,0.1),tint(c,0.4),10,1);w=pill(52,y+6,label,c,size=11);text(52+w+14,y+22,msg,13.5,c,True)
def info(x,y,w,title,items,c,icon,fill='#ffffff',stroke='#d3dee6',size=13,lead=21,tcol=None):
 """note card with an icon badge; returns its height"""
 h=58+len(items)*lead;card(x,y,w,h,c,fill,stroke);badge(x+34,y+36,c);icon(x+34,y+36,c)
 text(x+66,y+34,title,16,tcol or (c if c==AMBER else INK),True);lines(x+66,y+58,items,size,MUTED,lead);return h
def cell(x,y,c=PURPLE,label=None):
 """battery cell symbol, + terminal up; wire ends at y-12 (+) and y+12 (-)"""
 line(x,y-12,x,y-6,c,2);line(x-22,y-6,x+22,y-6,c,3);line(x-11,y+6,x+11,y+6,c,5);line(x,y+6,x,y+12,c,2)
 text(x-32,y-8,'+',15,c,True)
 if label:text(x+34,y+6,label,16,INK,True)
def hfuse(x,y,c=RED,label=None):
 """horizontal fuse body from x to x+52, centred on y"""
 box(x,y-9,52,18,'#ffffff',c,0,2);line(x,y,x+52,y,c,1.5)
 if label:text(x,y-16,label,12,c,True)
def hswitch(x,y,c=RED,label=None):
 """SPST from x to x+46"""
 disc(x+4,y,4,'#ffffff',c,2);line(x+8,y-2,x+42,y-16,c,2.5);disc(x+46,y,4,'#ffffff',c,2)
 if label:text(x-8,y+24,label,12,c,True)
pages=[]
header(1,'Power, charging & battery','Terminal-level schematic. Amber blocks are open items or need bench qualification. All loads connect to protected outputs.')
grid()
legend(160,(('PV input',BLUE,None),('Regulated 5 V',RED,[6,4]),('VBAT_SYS  protected +',RED,None),('GND_LOAD / OUT-',GND,None),('Cell side  B+ / B-',PURPLE,None)))
T=196
# PV1 -> U0 -> M1 input chain
card(42,T,232,214,BLUE);head(42,T,'PV1','Existing','AS102-0712A 1.2 W',BLUE);badge(234,T+34,BLUE);i_sun(234,T+34,AMBER)
lines(60,T+96,['Vmp 7 V / Imp 170 mA','Voc 7.6 V at 25 C','Cold Voc: measure'],14,INK,22)
rchip(262,T+162,'+',BLUE);rchip(262,T+190,'-',BLUE)
card(330,T,274,214,AMBER,'#fffaf0','#e5c58f');head(330,T,'U0','5 V regulator','OPEN ITEM - not fitted',AMBER,AMBER);badge(564,T+34,AMBER);i_bolt(564,T+34,AMBER)
lines(348,T+96,['Bench: 5 V panel direct to M1','Choose once panel is final','Vin rating > cold Voc'],14,INK,22)
chip(344,T+162,'IN+',BLUE);chip(344,T+190,'IN-',BLUE);rchip(592,T+162,'OUT+',RED);rchip(592,T+190,'OUT-',BLUE)
card(660,T,310,300,INK);head(660,T,'M1','Protected 4056','Verify actual chip and pad labels',INK);badge(930,T+34,GREEN);i_shield(930,T+34,GREEN)
lines(678,T+96,['Start 100-150 mA charge','PROG resistor: verify law','Cell TEMP inhibit unresolved'],14,AMBER,22)
chip(674,T+162,'IN+',RED);chip(674,T+190,'IN-',BLUE)
rchip(958,T+104,'OUT+',RED);rchip(958,T+244,'OUT-',GND)
chip(722,T+282,'B+',PURPLE);chip(862,T+282,'B-',PURPLE)
for yy,c in ((T+162,BLUE),(T+190,BLUE)):line(274,yy,330,yy,c,3.5);disc(274,yy,4,c);disc(330,yy,4,c)
arrow(302,T+162,'r',BLUE)
line(604,T+162,660,T+162,RED,3.5,[6,4]);arrow(632,T+162,'r',RED);line(604,T+190,660,T+190,BLUE,3.5)
for x_,y_ in ((604,T+162),(660,T+162),(604,T+190),(660,T+190)):disc(x_,y_,4,INK)
# protected outputs: OUT+ -> F2 -> S1 -> VBAT_SYS, OUT- -> GND_LOAD
VY,GY=T+104,T+244
line(970,VY,1010,VY,RED,3.5);hfuse(1010,VY,RED,'F2  1 A');line(1062,VY,1110,VY,RED,3.5);hswitch(1110,VY,RED,'S1 service')
line(1160,VY,1386,VY,RED,5);arrow(1386,VY,'r',RED,8);pill(1300,VY-34,'VBAT_SYS',RED,size=12)
line(970,GY,1386,GY,GND,5);arrow(1386,GY,'r',GND,8);pill(1300,GY-34,'GND_LOAD',GND,size=12)
disc(970,VY,4.5,RED);disc(970,GY,4.5,GND)
box(1010,VY+30,376,66,tint(INK,0.04),'#e1e9ee',10,1)
pill(1024,VY+40,'To sheets 2 and 3',INK,size=11)
text(1024,VY+84,'VBAT_SYS: battery voltage   |   GND_LOAD: OUT- only',13,INK)
# 1S2P pack, each positive fused
card(250,540,650,248,PURPLE,tint(PURPLE,0.04),tint(PURPLE,0.3));head(250,540,'BT1 + BT2','1S2P / matched cells / individually fused','',PURPLE,PURPLE)
badge(860,574,PURPLE);i_batt(860,574,PURPLE)
BP,BN=T+300,T+300
TOPB,BOTB=610,730
path([(740,T+300),(740,TOPB),(330,TOPB)],PURPLE,3);path([(880,T+300),(880,BOTB),(330,BOTB)],PURPLE,3)
for x,label in [(390,'BT1'),(640,'BT2')]:
 disc(x,TOPB,4.5,PURPLE);disc(x,BOTB,4.5,PURPLE)
 line(x,TOPB,x,622,PURPLE,2.5);res(x,652,'FB'+label[-1],'1 A',True,PURPLE);line(x,687,x,694,PURPLE,2.5)
 cell(x,706,PURPLE,label+' / 18650');line(x,718,x,BOTB,PURPLE,2.5)
pill(268,752,'NEVER',RED,size=11);text(338,767,'Never series-connect these cells to a 1S charger. Do not bridge B- to OUT-.',13.5,INK,True)
info(944,540,454,'Ground check before wiring',['Some modules join IN- to OUT- internally.','Confirm yours; do not add an external link.','B- remains behind the protection FETs.','Service with panel and batteries removed.'],AMBER,i_warn,'#fffaf0','#e5c58f',13.5,24)
warn('No pair of series diodes is accepted as overvoltage protection. Unattended charging awaits cell-temperature protection.')

pages.append(save('01-power'))
header(2,'Light controller & LED driver','Reused 16 MHz Pro Mini converted to internal 8 MHz. Switched LDR; dusk to dawn at 100% command, with R3 setting the current.')
grid()
legend(160,(('VBAT_SYS  protected +',RED,None),('GND_LOAD / OUT-',GND,None),('Logic / sensor / LED drive',GREEN,None)))
# M2 with rail stubs
MT,MB=250,670
pill(392,190,'VBAT_SYS',RED,size=12);line(440,211,440,MT,RED,3);text(448,MT-8,'VCC',12,RED,True)
pill(560,190,'GND_LOAD',GND,size=12);line(605,211,605,MT,GND,3);text(613,MT-8,'GND',12,GND,True)
card(350,MT,340,MB-MT,INK);head(350,MT,'M2','BTE13-010A','ATmega328P, verified 8 MHz',INK);badge(650,MT+34,INK);i_chip(650,MT+34,INK)
lines(368,MT+96,['Remove regulator + power LED','VCC supplied directly; RAW unused','D10/D11: open, reserved','No raw-panel sense on A0; no Q1'],14,INK,23)
chip(362,460,'D7',GREEN);chip(362,560,'A1',GREEN);chip(362,630,'D2',GREEN)
rchip(678,460,'D9 / PWM',GREEN);rchip(678,630,'D8 / status',GREEN)
# switched LDR divider
LX=170
path([(350,460),(LX,460),(LX,495)],GREEN,3);disc(350,460,4,GREEN)
disc(LX,515,27,'#ffffff',GREEN,2);box(LX-7,495,14,40,'#ffffff',GREEN,0,2)
for ax,ay in ((LX-44,478),(LX-36,494)):line(ax,ay,ax+14,ay+12,GREEN,2);poly([(ax+17,ay+15),(ax+6,ay+13),(ax+14,ay+5)],GREEN)
text(LX+38,510,'LDR1',15,GREEN,True);text(LX+38,530,'ambient light',13,MUTED)
line(LX,535,LX,560,GREEN,3);disc(LX,560,5,GREEN);line(LX,560,350,560,GREEN,3);disc(350,560,4,GREEN)
line(LX,560,LX,565,GREEN,3);res(LX,600,'R4','47k',True);line(LX,635,LX,655,GND,2);ground(LX,655)
# test button
path([(350,630),(300,630),(300,700)],GREEN,3);disc(350,630,4,GREEN)
disc(300,700,4.5,INK);disc(352,700,4.5,INK);line(306,686,346,686,INK,2.5);line(326,674,326,686,INK,2.5);line(352,700,392,700,GND,2);ground(392,700)
pill(266,730,'SW1 / test',INK,size=12)
# D9 straight to R3 and the string - no switching device (20-Sep-2026)
RX=1000
path([(690,460),(760,460),(760,300),(RX,300),(RX,310)],GREEN,3);disc(690,460,4,GREEN);arrow(880,300,'r',GREEN)
res(RX,345,'R3','47R',True,GREEN);line(RX,380,RX,400,GREEN,3)
card(915,400,170,92,GREEN,'#f3faf1','#a8cc97');head(915,400,'','JLED / string','+ top / - bottom',GREEN)
line(RX,492,RX,700,GND,3);ground(RX,700)
# design card
card(1110,250,288,300,INK);text(1128,284,'No Q1, R6, R7 or F1',17,INK,True)
lines(1128,314,['Measured string: 2.56 V drop','I = (VBAT - 2.56) / (R3 + 30R)','21 / 15 / 11 mA at','4.20 / 3.70 / 3.40 V','Fit 56R to stay under 20 mA'],14,INK,24)
box(1128,448,252,1,'#e1e9ee',None);lines(1128,476,['Pin max 40 mA absolute','Fit R3 at the board end'],14,AMBER,24)
badge(1358,284,GREEN);i_led(1358,284,GREEN)
# status out to sheet 3
line(690,630,800,630,GREEN,3);disc(690,630,4,GREEN);arrow(800,630,'r',GREEN);pill(812,620,'to sheet 3',GREEN,size=11)
# decoupling at the controller
for cx_,lab,val in ((720,'C3','100u / 10 V'),(890,'C4','100n')):
 pill(cx_-38,666,'VBAT_SYS',RED,size=10);line(cx_,685,cx_,700,RED,2);cap(cx_,735,lab,val);ground(cx_,770)
warn('All ground symbols on this sheet mean OUT-. R3 sets the peak current; duty changes the average only. Verify current at 4.20 V and 100% duty.')

pages.append(save('02-controller'))
header(3,'Low-power telemetry reference (D1 Mini)','Retained for the later production profile. This is not the always-on D1 Mini UART test system on sheet 6.')
grid()
legend(160,(('VBAT_SYS  protected +',RED,None),('ESP 3V3',RED,[2,3]),('GND_LOAD / OUT-',GND,None),('Logic / sensor',GREEN,None)))
# U3 supply
UT=246
pill(62,196,'VBAT_SYS',RED,size=12);line(100,217,100,UT,RED,3)
pill(250,196,'GND_LOAD',GND,size=12);line(300,217,300,UT,GND,3)
card(42,UT,320,196,AMBER,'#fffaf0','#e5c58f');head(42,UT,'U3','3.3 V supply','TPS63802 breakout, 3.3 V',AMBER,AMBER);badge(322,UT+34,AMBER);i_bolt(322,UT+34,AMBER)
lines(60,UT+96,['VIN: VBAT_SYS (battery only)','OUT: D1 3V3 pin only','Qualify radio bursts + standby'],14,INK,22)
rchip(350,420,'3V3',RED)
# M3 D1 Mini
MX,MT,MB=760,246,540
card(MX,MT,400,MB-MT,INK);head(MX,MT,'M3','D1 Mini','Powered from U3 only',INK);badge(MX+360,MT+34,BLUE);i_wifi(MX+360,MT+34,BLUE)
lines(MX+18,MT+96,['5V pin + USB: not connected','Onboard regulator: fitted, unused'],14,INK,22)
chip(MX+12,380,'A0',GREEN);chip(MX+12,420,'3V3',RED);chip(MX+12,500,'D5',GREEN)
rchip(MX+388,380,'D0',GREEN);rchip(MX+388,440,'RST',GREEN);chip(MX+184,MB-22,'G',GND)
path([(MX+400,380),(MX+440,380),(MX+440,440),(MX+400,440)],GREEN,3);disc(MX+400,380,4,GREEN);disc(MX+400,440,4,GREEN)
text(MX+448,415,'deep-sleep wake',12,MUTED)
line(MX+196,MB,MX+196,MB+26,GND,3);ground(MX+196,MB+26)
# 3V3 supply rail and battery sense
line(362,420,MX,420,RED,3.5);disc(362,420,4,RED);disc(MX,420,4,RED);arrow(560,420,'r',RED)
pill(440,196,'VBAT_SYS',RED,size=12);line(490,217,490,245,RED,3);res(490,280,'R5','220k',True);path([(490,315),(490,380),(MX,380)],GREEN,3);disc(MX,380,4,GREEN)
text(560,372,'battery sense',12,GREEN,True)
# input capacitor
pill(56,476,'VBAT_SYS',RED,size=11);line(136,486,200,486,RED,2.5);line(200,486,200,492);cap(200,527,'C2','470u / 10 V');ground(200,562)
# status interface: M2 D8 -> R8 -> Q2 -> D5, collector pulled up to ESP 3V3 only
QY=660
pill(42,QY-10,'M2 D8',GREEN,size=12);line(106,QY,220,QY,GREEN,3);arrow(160,QY,'r',GREEN);res(270,QY,'R8','47k',False,GREEN);line(320,QY,445,QY,GREEN,3);disc(360,QY,5,GREEN)
line(360,QY,360,QY+5,GREEN,3);res(360,QY+40,'R9','100k',True);line(360,QY+75,360,QY+80,GND,2);ground(360,QY+80)
disc(480,QY,38,'#ffffff',INK,2);line(458,QY-22,458,QY+22,INK,3);line(445,QY,458,QY,GREEN,3)
path([(458,QY-12),(500,QY-40),(500,QY-60)],INK,2);path([(458,QY+12),(500,QY+40),(500,QY+85)],GND,2);poly([(500,QY+40),(486,QY+37),(494,QY+27)],GND);ground(500,QY+85)
text(470,QY-44,'C',11,INK,True);text(426,QY-8,'B',11,GREEN,True);text(470,QY+54,'E',11,GND,True)
pill(540,QY+30,'Q2 / 2N3904',INK,size=12);text(542,QY+72,'check E/B/C',13,MUTED)
line(500,QY-60,620,QY-60,GREEN,3);disc(620,QY-60,5,GREEN);path([(620,QY-60),(700,QY-60),(700,500),(MX,500)],GREEN,3);disc(MX,500,4,GREEN);arrow(730,500,'r',GREEN)
line(620,QY-60,620,QY-95,RED,2.5);res(620,QY-130,'R10','10k',True,RED);line(620,QY-165,620,QY-178,RED,2.5,[2,3]);pill(582,QY-200,'ESP 3V3',RED,size=11)
info(830,610,568,'Interface behaviour',['D8 HIGH -> Q2 ON -> D5 LOW -> HA Lights On = true.','Collector pulls up only to the ESP supply; YAML is inverted.','A0 calculation assumes onboard 220k / 100k resistors.','Calibrate actual battery voltage; percentage is approximate.'],BLUE,i_info,size=13.5,lead=23)
warn('Disconnect external power AND signal leads before USB/programmer servicing. Never supply the ESP 3V3 pin from the cell directly.',label='SAFETY',c=RED)

pages.append(save('03-telemetry'))
header(4,'What to assemble inside the enclosure','Top-down placement concept, not a drilling template. Use terminal labels and the wire schedule for electrical connections.')
grid()
# enclosure with cable glands on the top wall
box(45,206,920,600,tint('#0b2238',0.08),None,26)
box(42,200,920,600,'#f4f7f9','#8599a9',26,2)
for x,l,c in [(170,'PANEL',BLUE),(510,'LIGHTS',GREEN),(800,'LDR',GREEN)]:
 line(x+47,152,x+47,184,c,4);box(x,182,95,34,'#e3eaf0','#8599a9',8,1.5);text(x+47-tw(l,12,True)/2,204,l,12,INK,True)
badge(80,248,INK);i_box(80,248,INK);text(110,254,'WEATHERPROOF BOX / SHADED POSITION',16,INK,True)
# perfboard carrier
box(78,280,640,396,'#fffaf0','#c8b787',12,1.5);pill(94,292,'PERFBOARD / MODULE CARRIER',tint(AMBER,0.8),size=11)
for x in range(98,706,22):
 for y in range(330,668,22):disc(x,y,1.4,'#e3d6b6')
card(105,338,222,104,AMBER,'#fffaf0','#e5c58f');head(105,338,'U0','Input 5 V','Open item - not fitted',AMBER,AMBER)
card(105,486,222,120,INK);head(105,486,'M1','Charger','IN / B / OUT labelled',INK)
card(452,338,240,112,INK);head(452,338,'M2','Pro Mini','8 MHz; sockets; ISP access',INK)
card(452,500,240,112,GREEN,'#f3faf1','#a8cc97');head(452,500,'','LED driver','R3 only - D9 direct',GREEN)
# protected rails on the carrier
line(372,318,372,630,RED,7);line(398,318,398,630,GND,7);chip(362,306,'+',RED);chip(389,306,'-',GND)
line(327,520,372,520,RED,3);line(327,568,398,568,GND,3)
line(372,366,452,366,RED,3);line(398,412,452,412,GND,3);line(372,528,452,528,RED,3);line(398,580,452,580,GND,3)
for x_,y_,c in ((372,520,RED),(398,568,GND),(372,366,RED),(398,412,GND),(372,528,RED),(398,580,GND)):disc(x_,y_,4.5,c)
pill(328,642,'Protected rails',INK,size=11)
# telemetry modules and antenna keep-out
card(752,300,186,112,AMBER,'#fffaf0','#e5c58f');head(752,300,'U3','3V3','TPS63802',AMBER,AMBER)
card(752,448,186,168,INK);head(752,448,'M3','D1','Sockets / service',INK)
box(768,568,154,30,tint(BLUE,0.18),BLUE,4,1.5);i_wifi(790,580,BLUE);text(810,589,'ANTENNA',13,BLUE,True)
D.add(Rect(742,H-676,206,100,rx=10,ry=10,fillColor=None,strokeColor=HexColor(BLUE),strokeWidth=1.5,strokeDashArray=[5,4]))
text(760,666,'Keep antenna clear',14,BLUE,True)
# cells: parallel holder, each + lead fused
for x,l in [(90,'BT1'),(430,'BT2')]:
 box(x+3,708,262,62,tint('#0b2238',0.08),None,31)
 box(x,702,262,62,'#d7e8da','#80a888',31,1.5);box(x+22,702,70,62,'#bcd9c2',None,0);box(x+262,720,16,26,'#c7d2cc','#80a888',3,1.5)
 text(x+104,739,l+' / 18650',17,INK,True);text(x+34,740,'-',20,GND,True);text(x+238,741,'+',20,RED,True)
text(92,790,'Insulated parallel holder; fuse each + lead; separate cells from heat.',13.5,MUTED)
# build notes
def steps(y,title,items,c,icon,marker,fill='#ffffff',stroke='#d3dee6'):
 h=62+len(items)*26;card(990,y,408,h,c,fill,stroke);badge(1024,y+36,c);icon(1024,y+36,c)
 text(1056,y+42,title,16,c if c==AMBER else INK,True)
 for i,t in enumerate(items):
  yy=y+74+i*26;marker(i,yy);text(1040,yy+5,t,13.5,INK)
 return h
def num(i,yy):disc(1020,yy,10,GREEN);text(1016 if i<9 else 1012,yy+4.5,str(i+1),11,'#ffffff',True)
def swatch(c):return lambda i,yy:(box(1008,yy-7,22,14,c,None,3))
steps(196,'Build in this order',['Qualify panel regulator + charger.','Convert and test the Pro Mini.','Add R3 (47R) and light string - no MOSFET.','Add LDR; check dusk/dawn + LVC.','Assemble the protected, fused pack.','Add optional telemetry and measure.'],GREEN,i_flag,num)
cols=[RED,GND,BLUE,PURPLE,GREEN]
steps(432,'Label every connector',['RED: protected positive / VBAT_SYS','BLACK: load return / OUT-','BLUE: panel input pair','PURPLE: battery-only connections','GREEN: logic / sensor signals'],INK,i_info,lambda i,yy:box(1008,yy-7,22,14,cols[i],None,3))
steps(642,'Before closing the lid',['Strain relief, polarity, cell insulation.','No exposed underside copper.','Charger/cell temperature tests passed.','Log charge, load and actual brightness.'],AMBER,i_check,lambda i,yy:box(1011,yy-7,14,14,'#ffffff',AMBER,3,1.5),'#fffaf0','#e5c58f')

pages.append(save('04-assembly'))
header(5,'Staged power-up & serial diagnostics','Battery powers the controller. The USB-UART listens only: connect RX and GND; leave its power and control pins open.')
grid()
legend(160,(('OUT+ -> VBAT_SYS',RED,None),('OUT- / GND',GND,None),('Cell side  B+ / B-',PURPLE,None),('M2 TX -> adapter RX',GREEN,None)))
T,B=196,416
VY,GY=280,380
# M1 protected charger and one-cell test source
card(42,T,290,B-T,INK);head(42,T,'M1','Protected 4056','Read pad labels, not positions',INK);badge(292,T+34,GREEN);i_shield(292,T+34,GREEN)
lines(60,T+96,['Cell connects to B+ / B-','Load uses OUT+ / OUT-','Never bridge B- to OUT-'],13.5,INK,23)
rchip(320,VY,'OUT+',RED);rchip(320,GY,'OUT-',GND);chip(96,B-20,'B+',PURPLE);chip(246,B-20,'B-',PURPLE)
box(63,468,250,62,tint('#0b2238',0.08),None,31);box(60,462,250,62,'#d7e8da','#80a888',31,1.5);box(310,480,14,26,'#c7d2cc','#80a888',3,1.5)
text(82,490,'BT1 / one suitable 1S cell',15,INK,True);text(84,514,'-',17,PURPLE,True);text(286,514,'+',17,PURPLE,True)
path([(110,B),(110,440),(290,440),(290,462)],PURPLE,3);vhop(260,B,448,[440],PURPLE);path([(260,448),(88,448),(88,462)],PURPLE,3)
# OUT+ -> F2 -> S1 -> M2 VCC ; OUT- -> M2 GND
line(332,VY,352,VY,RED,3.5);hfuse(352,VY,RED,'F2  1 A');line(404,VY,430,VY,RED,3.5);hswitch(430,VY,RED);text(408,VY+26,'S1 service switch',12,RED,True);line(476,VY,530,VY,RED,3.5)
line(332,GY,530,GY,GND,3.5);disc(500,GY,5,GND)
for x_,y_,c in ((332,VY,RED),(530,VY,RED),(332,GY,GND),(530,GY,GND)):disc(x_,y_,4,c)
card(530,T,300,B-T,INK);head(530,T,'M2','BTE13-010A','internal 8 MHz / debug build',INK);badge(790,T+34,INK);i_chip(790,T+34,INK)
chip(542,VY,'VCC',RED);chip(542,GY,'GND',GND);chip(542,330,'RAW: OPEN',AMBER);cross(520,330,AMBER,6,2)
rchip(818,300,'TX',GREEN);rchip(818,340,'RX: OPEN',MUTED)
info(530,430,330,'Serial checkpoints',['DAY off: state=0 pct=0 / about 8 s ticks','D2 test: state=0 pct=100','LVC: state=4 pct=0; button cannot relight'],GREEN,i_check,size=12.5,lead=20)
# USB-UART board, pin order copied from the supplied photo: USB left, header right
BX=910
card(BX,T,488,330,GREEN,'#f0faf7','#9fd0c4');text(BX+20,T+36,'USB-UART / EZSBC-style board',18,GREEN,True);text(BX+20,T+60,'Pin order copied from the supplied photo',13,MUTED)
box(878,300,74,120,'#dce5e9','#768a96',6,1.5);box(870,326,26,68,'#eef2f4','#768a96',3,1.5);text(884,440,'USB',12,MUTED,True)
box(1000,290,150,160,'#263746',None,8);disc(1075,340,21,'#3b5063');i_usb(1075,340,'#ffffff');text(1038,410,'USB-UART',14,'#ffffff',True)
HX=1262
box(HX,256,20,240,'#263746',None,3)
pins=[('DTR',276,False),('RX',316,True),('TX',356,False),('VO',396,False),('CTS',436,False),('GND',476,True)]
for label,y,used in pins:
 c=GREEN if used else MUTED
 line(HX-22,y,HX,y,c,3);disc(HX-22,y,4,c);text(HX+30,y+5,label,15,c,True)
 if not used:cross(HX-22,y,RED,6,2.5);pill(HX+30+tw(label,15,True)+8,y-10,'OPEN',RED,size=10,pad=6)
# data + common ground only; the lanes run under the board and up a clear channel
path([(830,300),(870,300),(870,548),(1190,548),(1190,316),(HX-22,316)],GREEN,3.5);disc(830,300,4,GREEN);arrow(1190,420,'u',GREEN)
text(880,566,'M2 TX -> adapter RX',12.5,GREEN,True)
path([(500,GY),(500,576),(1215,576),(1215,476),(HX-22,476)],GND,3.5)
text(520,594,'M2 GND / OUT- -> adapter GND',12.5,GND,True)
# lower row
h=info(42,610,386,'Before closing S1',['1  Meter OUT+ to OUT-: polarity correct.','2  Expect approximately the cell voltage.','3  UART power lead already removed.','4  Close S1; compare serial vdd with meter.'],INK,i_flag,size=13,lead=22)
card(450,610,430,176,GREEN);text(470,646,'Proceed one gate at a time',16,INK,True)
gx=[488+i*58 for i in range(7)]
for i,(x,label) in enumerate(zip(gx,['M2','BAT','LDR','LVC','5 V','PV','RUN']),1):
 if i<7:line(x+20,712,gx[i]-20,712,GREEN,2.5)
 disc(x,712,20,GREEN if i==1 else '#eaf7f4',GREEN,2);text(x-4.5 if i<10 else x-9,718,str(i),15,'#ffffff' if i==1 else GREEN,True)
 text(x-tw(label,12,True)/2,752,label,12,MUTED,True)
info(904,610,494,'USB-UART rules',['USB cable powers the adapter itself.','Do not connect VO to M2 VCC.','Leave DTR, TX and CTS open for monitoring.','Keep adapter USB-powered while M2 TX is attached.'],AMBER,i_usb,'#fffaf0','#e5c58f',13,22)
warn('SERIAL IS NOT A CHARGE METER: verify panel input, regulated 5 V, battery voltage and charge current with instruments.')

pages.append(save('05-staging'))
header(6,'Development telemetry (Wemos D1 Mini)','TEST SYSTEM ONLY: always-on Wi-Fi and UART capture. Reuses the existing status transistor parts; no INA226 or new telemetry module. Production D1 profile remains on sheet 3.')
grid()
strip(144,'READ THIS FIRST','Always-on Home Assistant test configuration: Q2/R8/R9/R10 become a safe, inverted UART receiver. The D1 Mini deep-sleep production reference is sheet 3.')
legend(202,(('UART  9600 baud, inverted',GREEN,None),('ESP 3V3',RED,[2,3]),('OUT- / GND_LOAD',GND,None),('Battery sense',BLUE,None)))
# The only active signal path: Arduino TX -> Q2 -> D1 D6.
T,B=232,470
card(42,T,300,B-T,INK);head(42,T,'1','M2 Arduino','Flash pro8_debug',INK);badge(302,T+34,INK);i_chip(302,T+34,INK)
row(60,322,'VCC',RED,'VBAT_SYS');row(60,352,'GND',GND,'OUT- / GND_LOAD');row(60,382,'D1/TX',GREEN,'9600-baud diagnostics');row(60,412,'D8',MUTED,'OPEN in this test profile')
rchip(330,442,'GND',GND)
# 2: reused receiver, drawn as a real inverter stage
card(400,T,520,B-T,GREEN,'#f0faf7','#9fd0c4');head(400,T,'2','Reused UART receiver','Q2 inverts and level-shifts the Arduino TX',GREEN)
line(342,382,430,382,GREEN,3.5);disc(342,382,4,GREEN);arrow(386,382,'r',GREEN);text(352,372,'D1 / TX',11,GREEN,True)
res(480,382,'R8','47k',False,GREEN);line(530,382,588,382,GREEN,3);disc(556,382,5,GREEN)
disc(612,382,34,'#ffffff',INK,2);line(592,362,592,402,INK,3)
path([(592,372),(630,348),(630,330)],INK,2);path([(592,392),(630,416),(630,500)],GND,2);poly([(630,416),(617,413),(624,404)],GND)
text(636,344,'C',11,INK,True);text(574,376,'B',11,GREEN,True);text(636,428,'E',11,GND,True)
# R9 is the base-emitter pull-down: top on the R8/Q2-base node, bottom on Q2 emitter / OUT-
line(556,382,556,392,GREEN,2.5);res(556,427,'R9','100k',True,GREEN);line(556,462,556,470,GND,2.5);path([(556,470),(556,478),(630,478)],GND,2.5);disc(630,478,4.5,GND)
pill(668,410,'Q2 / 2N3904',INK,size=12)
line(630,330,920,330,GREEN,3.5);disc(820,330,5,GREEN);arrow(880,330,'r',GREEN)
line(820,330,820,325,GREEN,2.5);res(820,290,'R10','10k',True,RED);line(820,255,820,250,RED,2.5,[2,3]);pill(788,236,'ESP 3V3',RED,size=11)
text(860,322,'D6 RX',11,GREEN,True)
# 3: D1 Mini
card(978,T,420,B-T,AMBER,'#fffaf0','#e5c58f');head(978,T,'3','M3 Wemos D1 Mini','Always-on test telemetry',AMBER,AMBER);badge(1358,T+34,AMBER);i_wifi(1358,T+34,AMBER)
row(996,322,'3V3',RED,'D1 micro-USB; U3 OUT unplugged');row(996,352,'D6',GREEN,'inverted UART RX');row(996,382,'A0',BLUE,'existing battery divider');row(996,412,'D5',MUTED,'OPEN; `output=` is light state')
chip(1000,452,'G',GND)
path([(920,330),(938,330),(938,352),(978,352)],GREEN,3.5);disc(978,352,4,GREEN)
# common return: both grounds share OUT-, but nothing returns from the D1 to the Arduino
path([(342,442),(370,442),(370,500),(1010,500),(1010,B)],GND,3.5);disc(342,442,4,GND);disc(630,500,5,GND);disc(1010,B,4,GND)
text(400,522,'OUT- / GND_LOAD common return only — D1 Mini TX remains OPEN',13,GND,True)
# battery reading, kept separate for an easy calibration check
card(42,560,410,208,BLUE);text(60,594,'Existing battery reading',17,INK,True);badge(412,594,BLUE);i_gauge(412,594,BLUE)
pill(60,612,'VBAT_SYS',RED,size=11);line(100,633,100,645,RED,2.5);res(100,680,'R5','220k',True,BLUE);line(100,715,100,782,BLUE,3)
lines(170,640,['D1 A0 has its onboard divider too.','Calibrate its 5.21 multiplier against','a meter. Compare it with parsed','Arduino VDD.'],13,MUTED,21)
path([(100,782),(958,782)],BLUE,3);vhop(958,382,782,[500],BLUE);line(958,382,978,382,BLUE,3);disc(978,382,4,BLUE);arrow(958,640,'u',BLUE)
info(480,560,450,'What Home Assistant receives',['Arduino: VDD, LDR, sense/mode/night, output duty,','LVC/test progress, cause, transition and raw line.','D1: battery voltage/percentage, Wi-Fi, reset, heap and uptime.'],GREEN,i_wifi,size=12.5,lead=22)
info(980,560,418,'No-purchase boundary',['Not measured: panel voltage, charge/load current, energy,','physical LED current or temperatures.','`output=` replaces D8-to-D5: leave both pins open.'],AMBER,i_warn,'#fffaf0','#e5c58f',12.5,22)
warn('Test rules: run pro8_debug • no USB-UART on M2 • D1 on micro-USB, U3 OUT off • use solar-lights-lite.yaml later for production',label='TEST RULES')

pages.append(save('06-telemetry-dev'))
# Whole-system view for the assembly guide. Detailed terminal drawings remain on sheets 1, 2 and 6.
header(7,'Current architecture schematic','As-built v0.5 wiring. The development receiver captures the Arduino UART in Home Assistant; it is not a current or energy meter.')
grid()
strip(144,'HOW TO USE','System-level view. Follow sheets 1, 2 and 6 for terminal-level wiring. The editable KiCad source in kicad_current/ uses this same D1/TX-to-D6 development route.')
legend(202,(('PV input',BLUE,None),('VBAT_SYS  protected +',RED,None),('GND_LOAD / OUT-',GND,None),('Cell side  B+ / B-',PURPLE,None),('UART  9600 baud, inverted',GREEN,None),('Battery sense',BLUE,[6,4]),('ESP 3V3',RED,[2,3])))

# ---- row A: energy chain
TOP,AH=224,108
card(42,TOP,230,AH,BLUE);head(42,TOP,'PV1','Solar panel','Existing 1.2 W',BLUE);text(60,TOP+90,'PV+ / PV-',13,BLUE,True);badge(242,TOP+34,BLUE);i_sun(242,TOP+34,AMBER)
card(316,TOP,240,AH,AMBER,'#fffaf0','#e5c58f');head(316,TOP,'U0','5 V input','Open item - not fitted',AMBER,AMBER);text(334,TOP+90,'Bench: 5 V panel direct',13,AMBER,True);badge(526,TOP+34,AMBER);i_bolt(526,TOP+34,AMBER)
card(600,TOP,300,AH,INK);head(600,TOP,'M1','Protected charger','TP4056 family + protection',INK);text(618,TOP+90,'IN+ / IN-      B+ / B-',13,INK,True);badge(870,TOP+34,GREEN);i_shield(870,TOP+34,GREEN)
card(970,TOP,270,AH,PURPLE);head(970,TOP,'BT1 + BT2','1S2P cells','Each positive lead fused',PURPLE);text(988,TOP+90,'BATT+ / BATT-',13,PURPLE,True);badge(1210,TOP+34,PURPLE);i_batt(1210,TOP+34,PURPLE)
MY=TOP+AH/2
line(272,MY,316,MY,BLUE,3.5);arrow(296,MY,'r',BLUE)
line(556,MY,600,MY,RED,3.5);arrow(580,MY,'r',RED)
line(900,MY-8,970,MY-8,PURPLE,3.5);line(900,MY+8,970,MY+8,PURPLE,3.5);text(912,MY-16,'B+',11,PURPLE,True);text(912,MY+26,'B-',11,PURPLE,True)
text(1262,TOP+30,'cell-side wiring:',12,PURPLE,True);text(1262,TOP+48,'B+ / B- only',12,PURPLE,True)
text(1262,TOP+76,'loads connect to',12,MUTED);text(1262,TOP+94,'protected OUT+ only',12,MUTED)

# ---- protected distribution bus: OUT+ -> F2 -> S1 -> VBAT_SYS
VB,GB=428,462;BOT=TOP+AH
D.add(Rect(42,H-484,1356,78,rx=12,ry=12,fillColor=HexColor('#f5f8fa'),strokeColor=HexColor('#e1e9ee'),strokeWidth=1))
pill(52,VB-10,'VBAT_SYS',RED,size=11);pill(52,GB-10,'GND_LOAD',GND,size=11)
line(150,VB,1370,VB,RED,5);line(150,GB,1370,GB,GND,5)
FX=760;line(FX,BOT,FX,372,RED,3.5);text(FX+8,BOT+22,'OUT+',12,RED,True)
line(FX,372,1178,372,RED,3.5);arrow(1000,372,'r',RED)
D.add(Rect(1178,H-381,52,18,fillColor=HexColor('#ffffff'),strokeColor=HexColor(RED),strokeWidth=2));line(1178,372,1230,372,RED,1.5)
text(1184,360,'F2  1 A',12,RED,True)
line(1230,372,1272,372,RED,3.5);disc(1276,372,4,'#ffffff',RED,2);line(1280,370,1318,356,RED,2.5);disc(1322,372,4,'#ffffff',RED,2)
text(1262,395,'S1 service',12,RED,True)
line(1326,372,1370,372,RED,3.5);line(1370,372,1370,VB,RED,3.5);arrow(1370,400,'d',RED)
vhop(660,BOT,GB,[VB],GND,3.5);disc(660,GB,5,GND);text(668,BOT+22,'OUT-',12,GND,True)
text(1020,VB-12,'OUT+ -> F2 -> S1 -> VBAT_SYS',12,RED,True);text(1020,GB+17,'OUT- / GND_LOAD common return',12,GND,True)

# ---- row C: loads
CY,CB=506,738
def taps(xv,xg):
 vhop(xv,VB,CY,[GB],RED,3);disc(xv,VB,5,RED);line(xg,GB,xg,CY,GND,3);disc(xg,GB,5,GND)
# M2 Pro Mini
card(42,CY,400,CB-CY,INK);head(42,CY,'M2','BTE13-010A Pro Mini','Internal 8 MHz, ISP programmed',INK);badge(402,CY+34,INK);i_chip(402,CY+34,INK);taps(190,230)
row(60,600,'VCC',RED,'<- VBAT_SYS');row(212,600,'GND',GND,'<- OUT-')
row(60,630,'D7',BLUE,'-> LDR -> A1 -> R4 -> OUT-')
row(60,660,'D9',AMBER,'-> R3 47R -> LED string -> OUT-')
row(60,690,'D1/TX',GREEN,'-> R8 -> Q2 base (9600 baud)')
row(60,720,'D8',MUTED,'open in the development profile')
# U3 3.3 V supply
card(520,CY,300,100,RED);head(520,CY,'U3','3.3 V supply','TPS63802 at 3.3 V for M3',RED);badge(780,CY+34,RED);i_bolt(780,CY+34,RED);taps(560,600)
text(538,CY+88,'VIN <- VBAT_SYS   OUT -> M3 (prod)',12.5,MUTED)
# M3 D1 Mini
MX=1000
card(MX,CY,398,CB-CY,AMBER,'#fffaf0','#e5c58f');head(MX,CY,'M3','Wemos D1 Mini','Always-on development telemetry',AMBER,AMBER);badge(1358,CY+34,AMBER);i_wifi(1358,CY+34,AMBER)
line(1300,GB,1300,CY,GND,3);disc(1300,GB,5,GND)
row(MX+18,592,'A0',BLUE,'<- R5 220k <- VBAT_SYS')
row(MX+18,622,'3V3',RED,'<- U3 (prod) / D1 USB (bench)')
row(MX+18,652,'GND',GND,'<- OUT-')
row(MX+18,690,'D6',GREEN,'<- Q2 collector (inverted RX)')
row(MX+18,720,'D5',MUTED,'open;  TX open')
D.add(Rect(1236,H-736,150,28,rx=14,ry=14,fillColor=HexColor(AMBER),strokeColor=None));i_wifi(1256,720,'#ffffff');text(1272,726,'Home Assistant',12,'#ffffff',True)
# lane: battery sense VBAT_SYS -> R5 -> A0 (dashed blue after the tap)
SX=880;vhop(SX,VB,592,[GB],RED,3);disc(SX,VB,5,RED)
line(SX,592,902,592,BLUE,3,[6,4]);D.add(Rect(902,H-600,56,16,fillColor=HexColor('#ffffff'),strokeColor=HexColor(BLUE),strokeWidth=2));line(958,592,MX,592,BLUE,3,[6,4]);arrow(986,592,'r',BLUE)
text(904,580,'R5 220k',12,BLUE,True)
# lane: U3 VOUT -> ESP 3V3 -> M3 (R10 pull-up hangs off it)
line(820,622,MX,622,RED,3,[2,3]);arrow(986,622,'r',RED);text(828,614,'ESP 3V3',11,RED,True);disc(940,622,4.5,RED)
# lane: D1/TX -> R8 -> Q2 -> D6
line(442,690,452,690,GREEN,3);D.add(Rect(452,H-698,52,16,fillColor=HexColor('#ffffff'),strokeColor=HexColor(GREEN),strokeWidth=2));line(504,690,520,690,GREEN,3)
text(452,676,'R8 47k',12,GREEN,True)
card(520,632,300,CB-632,GREEN,'#f0faf7','#9fd0c4')
disc(578,690,23,None,INK,2);line(566,674,566,706,INK,2.4);line(520,690,566,690,GREEN,3)
line(566,681,596,662,INK,2);line(566,699,596,718,GND,2);poly([(596,718),(584,716),(590,707)],GND)
text(548,684,'B',10,GREEN,True);text(600,660,'C',10,GREEN,True);text(600,729,'E',10,GND,True)
path([(596,662),(596,648),(806,648),(806,690),(820,690)],GREEN,2.4)
text(618,664,'Q2  2N3904 NPN inverter',13.5,INK,True)
text(618,684,'B: R8 47k from D1/TX',12,MUTED)
text(618,702,'C: D6 RX; R10 10k -> ESP 3V3',12,GREEN)
text(618,720,'E: OUT-; R9 100k B-E',12,GND)
line(820,690,MX,690,GREEN,3.5);arrow(986,690,'r',GREEN);text(836,682,'D6 RX',11,GREEN,True)
# R10 10k pull-up between ESP 3V3 and the D6 node
line(940,622,940,640,RED,2);D.add(Rect(932,H-676,16,36,fillColor=HexColor('#ffffff'),strokeColor=HexColor(GREEN),strokeWidth=2));line(940,676,940,690,GREEN,2);disc(940,690,4.5,GREEN)
text(952,664,'R10',11,GREEN,True)

# ---- bottom notes
def foot(x,w,title,items,c,fill,stroke,icon):
 card(x,752,w,86,c,fill,stroke);badge(x+34,795,c);icon(x+34,795,c);text(x+66,778,title,16,c if c==AMBER else INK,True);lines(x+66,800,items,13,MUTED,20)
foot(42,660,'Current visible in Home Assistant',['Arduino: state, VDD, LDR, output, low-voltage progress and raw diagnostics.','D1: battery, Wi-Fi, reset reason, heap and uptime.'],GREEN,'#ffffff','#d3dee6',i_check)
foot(724,674,'Still measured with instruments',['Panel/charge voltage and charge/load current or energy.','Physical LED current and temperature.'],AMBER,'#fff8e9','#ecd3a6',i_gauge)

pages.append(save('07-current-architecture'))
# Multipage A3 PDF; PDF render is authoritative preview.
fn=OUT/'SolarLights_Rev05_Drawings.pdf';cv=Canvas(str(fn),pagesize=landscape(A3));pw,ph=landscape(A3)
for d in pages:
 cv.saveState();scale=min(pw/W,ph/H);cv.translate((pw-W*scale)/2,(ph-H*scale)/2);cv.scale(scale,scale);renderPDF.draw(d,cv,0,0);cv.restoreState();cv.showPage()
cv.save()
p=pdf.PdfDocument(str(fn))
for i,page in enumerate(p):page.render(scale=1.3).to_pil().save(DOC/f'sheet-{i+1}.png')
print(fn)
