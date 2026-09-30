#!/usr/bin/env python3
"""BTE13-010A reference-board orientation and connection map; not to scale.
Writes docs/drawings/BTE13-010A-pin-map.svg/.pdf/.png. Needs reportlab and pypdfium2.
"""
from pathlib import Path
from reportlab.graphics.shapes import Drawing,Rect,String,Circle,Line
from reportlab.graphics import renderPDF,renderSVG
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4,landscape
import pypdfium2
P=Path(__file__).resolve().parents[1]/'docs'/'drawings';W,H=1400,870;d=Drawing(W,H)
def rect(x,y,w,h,fill,edge='#b7cbd5'):d.add(Rect(x,H-y-h,w,h,rx=10,fillColor=HexColor(fill),strokeColor=HexColor(edge)))
def txt(x,y,t,size=19,color='#173047',bold=False):d.add(String(x,H-y,t,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=HexColor(color)))
def line(x,y,x2,y2,c='#173047'):d.add(Line(x,H-y,x2,H-y2,strokeColor=HexColor(c),strokeWidth=2))
rect(0,0,W,H,'#ffffff','#ffffff');txt(45,45,'SOLAR LIGHTS LITE / REFERENCE BOARD',16,'#008572',True);txt(45,93,'BTE13-010A: connection and programming map',31,bold=True)
txt(45,126,'Component side: serial header LEFT, crystal and reset button RIGHT (photos in docs/reference/).',19)
txt(45,160,'Read the actual silkscreen before soldering. Diagram is not a footprint or regulator-removal template.',16,'#a76000')
rect(150,290,1075,240,'#eaf2f7');rect(100,350,50,120,'#334454');txt(45,580,'Serial header',18,bold=True);txt(45,606,'Not the ISP connector',16)
rect(400,360,220,105,'#334454');txt(425,402,'ATmega328P',23,'#ffffff',True);txt(425,435,'Read ISP signature',16,'#ffffff')
rect(745,350,190,70,'#d1dce2');txt(768,394,'16.000 MHz',22,bold=True);txt(715,450,'Crystal can stay fitted when',17);txt(715,474,'internal 8 MHz is selected.',17)
rect(1000,360,110,70,'#d1dce2');txt(1018,403,'RESET',19,bold=True)
top=['RAW','GND','RST','VCC','A3','A2','A1','A0','13','12','11','10']
bottom=['TX','RX','RST','GND','2','3','4','5','6','7','8','9']
for row,y,ty in [(top,300,263),(bottom,520,568)]:
 for i,label in enumerate(row):
  x=210+i*83
  c=('#c1363d' if label=='VCC' else '#334454' if label=='GND' else '#ad6200' if label in ('RAW','RST','11','12','13') else '#008572' if label in ('A1','2','7','9','TX') else '#8797a4')
  d.add(Circle(x,H-y,10,fillColor=HexColor('#ffffff'),strokeColor=HexColor(c),strokeWidth=3));txt(x-17,ty,label,19,c,True)
  line(x,y+(-12 if y==300 else 12),x,ty+(9 if y==300 else -24),c)
rect(45,650,630,155,'#f0f6f8');txt(65,681,'OPERATING CONNECTIONS',18,'#008572',True)
for i,s in enumerate(['VCC = protected battery; GND = OUT-; RAW = unused','A1 = LDR sense; 7 = LDR power; 9 = LED PWM','TX = telemetry to Q2 2N3904; 2 = test button to GND','Regulator / power LED removed only after trace identification.']):txt(65,713+i*24,s,16)
rect(700,650,650,155,'#fff7e8');txt(720,681,'ISP CONNECTIONS / BOARD DISCONNECTED FROM BUILD',17,'#a76000',True)
for i,s in enumerate(['MOSI -> 11     MISO -> 12     SCK -> 13     RESET -> RST','Also connect target VCC and GND; use compatible voltage.','Set fuses once: L 0xE2, H 0xD9, E 0xFD (8 MHz internal).','A USB-to-serial adapter alone cannot perform this conversion.']):txt(720,713+i*24,s,16)
txt(45,840,'REV 0.6 / BTE13-010A reference board. Other Pro Mini clones differ: follow your own silkscreen. A4-A7 end pads not shown.',14,'#516578')
renderSVG.drawToFile(d,str(P/'BTE13-010A-pin-map.svg'))
out=P/'BTE13-010A-pin-map.pdf';c=Canvas(str(out),pagesize=landscape(A4));pw,ph=landscape(A4);s=min(pw/W,ph/H);c.translate((pw-W*s)/2,(ph-H*s)/2);c.scale(s,s);renderPDF.draw(d,c,0,0);c.save()
p=pypdfium2.PdfDocument(str(out));p[0].render(scale=1.8).to_pil().save(P/'BTE13-010A-pin-map.png')
print(out)
