import html
S=[]; e=S.append; esc=html.escape
def box(x,y,w,h,t,sub="",sub2="",dashed=False):
    e(f'<rect class="{"ext" if dashed else "mod"}" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>')
    e(f'<text class="t" x="{x+12}" y="{y+22}">{esc(t)}</text>')
    if sub: e(f'<text class="s" x="{x+12}" y="{y+39}">{esc(sub)}</text>')
    if sub2: e(f'<text class="s" x="{x+12}" y="{y+54}">{esc(sub2)}</text>')
def chip(x,y,w,h,a,b="",dashed=False,warn=False):
    cls = "chipw" if warn else ("chipd" if dashed else "chip")
    e(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/><text class="r" x="{x+8}" y="{y+16}">{esc(a)}</text>')
    if b: e(f'<text class="s" x="{x+8}" y="{y+31}">{esc(b)}</text>')
def note(x,y,t,cls="s"): e(f'<text class="{cls}" x="{x}" y="{y}">{esc(t)}</text>')
def pin(x,y,label,side):
    e(f'<circle class="port" cx="{x}" cy="{y}" r="3.2"/>')
    if side=="l": e(f'<text class="p" x="{x+8}" y="{y+4}">{esc(label)}</text>')
    elif side=="r": e(f'<text class="p" x="{x-8}" y="{y+4}" text-anchor="end">{esc(label)}</text>')
    elif side=="b": e(f'<text class="p" x="{x}" y="{y-8}" text-anchor="middle">{esc(label)}</text>')
    elif side=="t": e(f'<text class="p" x="{x}" y="{y+16}" text-anchor="middle">{esc(label)}</text>')
def wire(c,pts,label=None,lx=0,ly=0,anchor="middle",dash=False):
    d=" ".join(f"{a},{b}" for a,b in pts)
    da = ' stroke-dasharray="6 5"' if dash else ''
    e(f'<g class="w {c}"><polyline points="{d}"{da}/>')
    if label: e(f'<text class="wl" x="{lx}" y="{ly}" text-anchor="{anchor}">{esc(label)}</text>')
    e('</g>')
def dot(c,x,y): e(f'<circle class="dot {c}" cx="{x}" cy="{y}" r="3.6"/>')
def gnd(x,y):
    e(f'<g class="gs"><line x1="{x}" y1="{y}" x2="{x}" y2="{y+9}"/><line x1="{x-7}" y1="{y+9}" x2="{x+7}" y2="{y+9}"/><line x1="{x-4}" y1="{y+13}" x2="{x+4}" y2="{y+13}"/><line x1="{x-1.5}" y1="{y+17}" x2="{x+1.5}" y2="{y+17}"/></g>')

W,H=1220,860
e(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="SolarLights Lite hookup diagram with the 5 V camera panel: panel through a single 1N5819 Schottky into the TP4056 module, cells on B plus and B minus, OUT plus and OUT minus rails feeding the Arduino Pro Mini, the MOSFET LED driver and the Wemos D1 Mini." xmlns="http://www.w3.org/2000/svg">')
e('<text class="h" x="20" y="30">SolarLights Lite – hookup with the 5 V (“10 W”) camera panel</text>')

# panel
box(20,56,178,118,"Solar panel 5 V","IP65 camera type · real ≈ 3.5 W","Voc 6.2 V · Isc 0.75 A",dashed=True)
note(32,150,"red = +, black = −")
pin(198,96,"+","l"); pin(198,136,"−","l")
# blocking diode (single Schottky)
chip(236,78,150,38,"D1  1N5819","Schottky ≈ 0.4 V")
note(236,176,"one diode only – omit it if the panel")
note(236,190,"already has its own blocking diode")
wire("wpv",[(198,96),(236,96)],"PV+",216,89)
wire("wpv",[(386,96),(416,96)])
wire("wg",[(198,136),(416,136)],"PV−",300,129)
dot("wpv",216,96)
# panel sense divider
chip(236,418,182,48,"R1 1M / R2 330k","+ C1 100 nF · panel sense")
note(236,484,"DARK 1.2 V · LIGHT 2.5 V (rescaled)")
wire("wpv",[(216,96),(216,442),(236,442)])
# TP4056
box(416,50,200,170,"TP4056 + DW01A module","linear charger + 1S protection","CHRG = IC pin 7 = red LED cathode")
pin(416,96,"IN+","l"); pin(416,136,"IN−","l")
pin(616,96,"OUT+","r"); pin(616,136,"OUT−","r"); pin(616,196,"CHRG (LED)","r")
pin(470,220,"B+","b"); pin(556,220,"B−","b")
chip(236,212,182,40,"IN+ ≥ 4.6 V while charging","2 × 1N4001 would drop it to 3.3 V",warn=True)
# cells
box(416,312,200,78,"2 × 18650 in parallel","matched cells · 1S2P")
wire("wbat",[(470,220),(470,312)],"B+",478,268,"start")
wire("wg",[(556,220),(556,312)],"B−",564,268,"start")
# rails
wire("wbat",[(616,96),(664,96),(664,760)],"OUT+ battery rail",670,776,"start")
wire("wg",[(616,136),(696,136),(696,740)],"OUT− GND rail",722,756,"start")
# Pro Mini
box(740,56,220,290,"Arduino Pro Mini 3.3 V","8 MHz · regulator + LED removed")
for y,l in [(100,"VCC"),(130,"GND"),(170,"A0"),(250,"A1 (LDR opt.)")]: pin(740,y,l,"l")
for y,l in [(110,"D9 PWM"),(160,"D8 LIGHTS_ON"),(200,"D2 button"),(240,"D10 / D11"),(290,"D7 LDR power")]: pin(960,y,l,"r")
wire("wbat",[(664,100),(740,100)]); dot("wbat",664,100)
wire("wg",[(696,130),(740,130)]); dot("wg",696,130)
wire("wsig",[(418,442),(714,442),(714,170),(740,170)],"PANEL_SENSE",560,436)
# MOSFET + LED
chip(1000,82,190,56,"Q1 logic-level N-FET","IRLZ44N / IRLB8721 / AO3400")
note(1008,176,"100 Ω gate · 100k gate→GND")
chip(1000,186,190,34,"IRFZ34N will not work here","needs ~10 V gate – see note 5",warn=True)
wire("wsig",[(960,110),(1000,110)])
pin(1095,138,"S","t"); gnd(1095,138)
chip(1000,400,190,40,"F1 fuse 0.5 A · R3 Rlim","value from string test")
wire("wbat",[(664,420),(1000,420)],None); dot("wbat",664,420)
box(1000,480,190,70,"LED string","≈ 200 mA at 100 %",dashed=True)
wire("wbat",[(1060,440),(1060,480)],"LED+",1052,466,"end")
wire("wled",[(1190,98),(1206,98),(1206,515),(1190,515)],"LED− to drain",1198,470,"end")
# button, jumpers, LDR
chip(1000,236,110,36,"SW1 push","to GND")
wire("wsig",[(960,200),(986,200),(986,254),(1000,254)])
chip(1000,282,150,36,"JP1 D10 · JP2 D11","to GND = mode")
wire("wsig",[(960,240),(974,240),(974,300),(1000,300)])
chip(1000,328,190,48,"LDR + R4 100k","optional light sensor",dashed=True)
wire("wsig",[(960,290),(968,290),(968,352),(1000,352)],dash=True)
wire("wsig",[(1000,366),(992,366),(992,386),(724,386),(724,250),(740,250)],dash=True)
# D1 Mini
box(740,470,220,210,"Wemos D1 Mini","ESPHome · hourly deep sleep")
for y,l in [(520,"5V"),(550,"G"),(590,"A0"),(640,"D6 CHRG")]: pin(740,y,l,"l")
pin(960,540,"D5","r"); note(752,668,"D0 ↔ RST link · 470 µF at 5V")
wire("wbat",[(664,520),(740,520)]); dot("wbat",664,520)
wire("wg",[(696,550),(740,550)]); dot("wg",696,550)
wire("wbat",[(664,590),(740,590)],"R5 220k",700,583); dot("wbat",664,590)
wire("wtel",[(960,160),(980,160),(980,540),(960,540)],"100k / 220k",972,470,"end")
wire("wtel",[(616,196),(628,196),(628,640),(740,640)],"BAT43 Schottky",636,625,"start")

# notes block
e('<rect class="np" x="20" y="530" width="600" height="300" rx="6"/>')
e('<text class="t" x="36" y="556">What changes for this panel</text>')
notes = [
 ("1", "One Schottky, not two silicon diodes. 2 × 1N4001 drop ~1.7 V at 0.7 A;"),
 ("",  "5 V − 1.7 V = 3.3 V at IN+ and the pack never reaches 4.2 V."),
 ("2", "No over-voltage guard needed: Voc 6.2 V (6.7 V cold) is well under the"),
 ("",  "TP4056's 8 V limit, so the diode is only there to block night reverse flow."),
 ("3", "Panel thresholds rescaled: PANEL_DARK_V 1.2, PANEL_LIGHT_V 2.5."),
 ("",  "Divider R1/R2 unchanged – 1.66 V max at A0."),
 ("4", "Charge current self-limits at ~0.7 A (0.35 A per cell). TP4056 heat"),
 ("",  "≈ 0.6 W – mount the module where air moves."),
 ("5", "Q1 must be logic-level. IRFZ34N is a 10 V-gate part: worst-case Vgs(th)"),
 ("",  "is 4 V, above the 3.3 V drive, and threshold rises as it gets colder."),
 ("6", "Harvest ≈ 1,350 mAh/day in June vs 560 mAh/day used at Stage 2."),
]
y=580
for n,t in notes:
    if n: e(f'<text class="nn" x="36" y="{y}">{esc(n)}</text>')
    e(f'<text class="nt" x="56" y="{y}">{esc(t)}</text>')
    y += 21 if n=="" else 19
# legend
e('<rect class="np" x="640" y="700" width="560" height="130" rx="6"/>')
e('<text class="t" x="656" y="726">Wire colours</text>')
leg=[("wpv","PV – panel positive, before the diode"),("wbat","OUT+ battery rail (protected)"),
     ("wg","Ground / OUT−"),("wsig","Pro Mini signals"),("wtel","D1 Mini telemetry"),("wled","LED return to drain")]
lx=656; ly=752
for i,(c,t) in enumerate(leg):
    cx = lx + (i%2)*276; cy = ly + (i//2)*24
    e(f'<g class="w {c}"><polyline points="{cx},{cy-4} {cx+26},{cy-4}"/></g>')
    e(f'<text class="s" x="{cx+34}" y="{cy}">{esc(t)}</text>')
e('</svg>')

css = """  .mod{fill:#E9E4DA;stroke:#D3CCBF;stroke-width:1.2}
  .ext{fill:#FCFBF8;stroke:#1E1B16;stroke-width:1.3;stroke-dasharray:5 4}
  .chip{fill:#FCFBF8;stroke:#D3CCBF}
  .chipd{fill:#FCFBF8;stroke:#645E53;stroke-dasharray:4 3}
  .chipw{fill:#FBF0E6;stroke:#B26F12;stroke-width:1.3}
  .np{fill:#F4F1EA;stroke:#D3CCBF}
  text{font-family:"Helvetica Neue",Arial,sans-serif;fill:#1E1B16}
  .h{font:600 19px "Helvetica Neue",Arial,sans-serif}
  .t{font:600 15px "Helvetica Neue",Arial,sans-serif}
  .s{font:400 11px "Helvetica Neue",Arial,sans-serif;fill:#645E53}
  .nn{font:600 11.5px "SF Mono",Menlo,monospace;fill:#B26F12}
  .nt{font:400 12px "Helvetica Neue",Arial,sans-serif;fill:#3A362F}
  .r{font:500 11.5px "SF Mono",Menlo,monospace}
  .p{font:500 11px "SF Mono",Menlo,monospace;fill:#645E53}
  .port{fill:#FCFBF8;stroke:#1E1B16;stroke-width:1.2}
  .w polyline{fill:none;stroke:currentColor;stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}
  .wl{font:500 11px "SF Mono",Menlo,monospace;fill:currentColor;paint-order:stroke;stroke:#FCFBF8;stroke-width:4px;stroke-linejoin:round}
  .dot{fill:currentColor}
  .wpv{color:#B26F12} .wbat{color:#BF3A2B} .wg{color:#5E5A52} .wsig{color:#2B5FB3} .wtel{color:#0B8276} .wled{color:#7A4FB5}
  .gs line{stroke:#5E5A52;stroke-width:1.6}"""
body = "\n".join(S)
svg = body.replace('xmlns="http://www.w3.org/2000/svg">',
                   'xmlns="http://www.w3.org/2000/svg">\n<style>\n'+css+'\n</style>\n'
                   f'<rect x="0" y="0" width="{W}" height="{H}" fill="#FCFBF8"/>',1)
open('/tmp/claude-0/lite5/wiring5.svg','w').write(svg)
open('/tmp/claude-0/lite5/preview.html','w').write('<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#FCFBF8}</style></head><body>'+svg+'</body></html>')
print("svg bytes", len(svg))
