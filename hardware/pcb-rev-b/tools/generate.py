#!/usr/bin/env python3
"""Generate the editable carrier schematic, local footprint library and routed
PCB. Run with KiCad's bundled Python (pcbnew + wx). Router uses conservative
clearance envelopes; the final KiCad DRC is the authority, never the router.
"""
import os, re, json, math, heapq, shutil, csv
from collections import defaultdict
import pcbnew as pcb
from design import *
import footprints as fpgen

KICAD = Path(os.environ.get('KICAD_SHARE','/Applications/KiCad/KiCad.app/Contents/SharedSupport'))
LIB = ROOT/'Carrier.pretty'
LIB.mkdir(exist_ok=True)
def expr(txt, start):
    depth=0; quoted=False; escaped=False
    for i in range(start,len(txt)):
        c=txt[i]
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(': depth+=1
        elif c==')':
            depth-=1
            if not depth: return txt[start:i+1]
    raise ValueError('Incomplete S-expression')
def stock(lid):
    lib,name=lid.split(':'); txt=(KICAD/'symbols'/(lib+'.kicad_sym')).read_text()
    m=re.search(r'\(symbol\s+"'+re.escape(name)+'"\s',txt)
    assert m, lid
    body=expr(txt,m.start())
    assert '(extends ' not in body, lid
    return body.replace(f'(symbol "{name}"',f'(symbol "{lid}"',1)
def effects(size=1.27): return f'(effects (font (size {size} {size})))'
E=effects(); hidden=E[:-1]+' hide)'
syms={p['symbol']:stock(p['symbol']) for p in PARTS.values()}
PIN_RE=re.compile(r'\(pin\s+\w+\s+\w+.*?\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\).*?\(number\s+"([^"]+)"',re.S)
def pins(body): return {m[3]:(float(m[0]),float(m[1]),float(m[2])) for m in PIN_RE.findall(body)}
rootuid=uid('schematic')
sheet=['(kicad_sch (version 20250114) (generator "eeschema")',
       f'(uuid "{rootuid}") (paper "A3")',
       '(title_block (title "Solar Lights Lite - carrier with charger") (date "27-Oct-2026") (rev "B / REVIEW") (company "No fuses; U0, U3 external"))',
       '(lib_symbols '+'\n'.join(syms.values())+')']
def schtext(t,x,y,size=1.5):
    sheet.append(f'(text {json.dumps(t)} (at {x} {y} 0) {effects(size)} (uuid "{uid(t)}"))')
for title,x,y in [('CHARGER M1 / SOLAR + CELL PADS / S1',75,18),('CONTROLLER + ISP / RAW NC',78,68),
                  ('LIGHTS + REMOTE SENSOR / BUTTON',83,169),('OPTIONAL D1 MINI SOCKETS',250,68),
                  ('UART INVERTER / BATTERY SENSE',246,126),('EXTERNAL U3 / REMOVABLE LINKS',250,211)]:
    schtext(title,x,y,2)
for ref,p in PARTS.items():
    lib_name,fp_name=p['footprint'].split(':')
    if lib_name=='Carrier':
        text=fpgen.tp4056_module(M1_PADS_REL,M1_HOLE,M1_PAD) if fp_name.startswith('TP4056') else fpgen.FOOTPRINTS[fp_name]()
        (LIB/(fp_name+'.kicad_mod')).write_text(text)
    else:
        txt=(KICAD/'footprints'/(lib_name+'.pretty')/(fp_name+'.kicad_mod')).read_text()
        if lib_name=='Connector_PinSocket_2.54mm':   # the module outline on the board replaces the socket outline
            txt=re.sub(r'\t\(fp_(?:line|rect|circle|arc|poly)\n(?:(?!\n\t\)\n).)*?\(layer "F\.SilkS"\)\n\t\)\n','',txt,flags=re.S)
        (LIB/(fp_name+'.kicad_mod')).write_text(txt)
    p['local_fp']='Carrier:'+fp_name
    x,y=(round(v/1.27)*1.27 for v in p['sch']); body=syms[p['symbol']]; ps=pins(body)
    assert set(ps)==set(p['nets']), (ref,ps,p['nets'])
    top=y-max(v[1] for v in ps.values())
    properties='\n'.join(f'(property "{key}" {json.dumps(val)} (at {xx} {yy} 0) {ef})'
          for key,val,xx,yy,ef in [('Reference',ref,x,top-6,E),('Value',p['value'],x,top-3,effects(.95)),
                 ('Footprint',p['local_fp'],x,y,hidden),('Datasheet','',x,y,hidden)])
    sheet.append(f'(symbol (lib_id "{p["symbol"]}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) '
        f'(uuid "{p["uuid"]}") {properties} '+
        ' '.join(f'(pin "{n}" (uuid "{uid(ref+"-pin-"+n)}"))' for n in ps)+
        f'(instances (project "{NAME}" (path "/{rootuid}" (reference "{ref}") (unit 1)))))')
    for n,(px,py,a) in ps.items():
        xx=round(x+px,4); yy=round(y-py,4); net=p['nets'][n]
        if net is None:
            sheet.append(f'(no_connect (at {xx} {yy}) (uuid "{uid(ref+n+"nc")}"))')
            continue
        dx=-10.16 if a==0 else 10.16
        end=round(xx+dx,4)
        sheet.append(f'(wire (pts (xy {xx} {yy}) (xy {end} {yy})) (stroke (width 0) (type default)) (uuid "{uid(ref+n+"wire")}"))')
        angle=180 if dx<0 else 0; justify='right bottom' if dx<0 else 'left bottom'
        sheet.append(f'(label "{net}" (at {end} {yy} {angle}) (effects (font (size 1 1)) (justify {justify})) (uuid "{uid(ref+n+"label")}"))')
schtext('U0 solar buck, U3 buck-boost, cells and S1 are external. B- is its own net: never joined to GND_LOAD. No fuses. All returns = M1 OUT-.',201,253,1.3)
schtext('Tier 0: omit telemetry. Tier 1: JP1 OPEN, USB. Tier 2: JP1 + JP2 closed, NO USB. JP3 closed only with powered M3.',201,260,1.3)
schtext('R3 peak current requires bench qualification. 47R matches existing circuit; no LED-cable short protection.',201,267,1.3)
(ROOT/(NAME+'.kicad_sch')).write_text('\n'.join(sheet)+')\n')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Carrier") (type "KiCad") (uri "${KIPRJMOD}/Carrier.pretty") (options "") (descr "Vendored Rev B carrier footprints")))\n')

board=pcb.BOARD()
V=lambda x,y: pcb.VECTOR2I(pcb.FromMM(x+50),pcb.FromMM(y+50))
MM=pcb.FromMM
netnames=sorted({n for p in PARTS.values() for n in p['nets'].values() if n})
nets={}
for name in netnames:
    n=pcb.NETINFO_ITEM(board,'/'+name); board.Add(n); nets[name]=n
settings=board.GetDesignSettings()
settings.m_TrackMinWidth=MM(.3); settings.m_MinClearance=MM(.25)
settings.m_CopperEdgeClearance=MM(.5); settings.m_MinThroughDrill=MM(.3)
settings.m_ViasMinSize=MM(.8); settings.m_ViasMinAnnularWidth=MM(.2)
settings.m_HoleToHoleMin=MM(.25); settings.m_HoleClearance=MM(.25)
settings.m_SilkClearance=MM(.15); settings.m_MinSilkTextHeight=MM(1)
settings.m_MinSilkTextThickness=MM(.15)
settings.SetBoardThickness(MM(1.6))
fps={}; pads_by_net=defaultdict(list)
for ref,p in PARTS.items():
    fp=pcb.FootprintLoad(str(LIB),p['local_fp'].split(':')[1]); assert fp
    board.Add(fp); fp.SetReference(ref); fp.SetValue(p['value']); fp.SetFPIDAsString(p['local_fp'])
    fp.SetPath(pcb.KIID_PATH('/'+rootuid+'/'+p['uuid']))
    fp.SetPosition(V(*p['xy'])); fp.SetOrientationDegrees(p['angle'])
    if ref.startswith(('JM2','JM3','JP','JL','JB','JU','JS','JC','JI')) or ref=='M1':
        fp.Reference().SetVisible(False)    # named by silkscreen text instead
    fp.Value().SetVisible(False)
    fp.Reference().SetTextSize(pcb.VECTOR2I(MM(1),MM(1))); fp.Reference().SetTextThickness(MM(.15))
    # Reference left at the standard footprint's safe location, independent of module labels.
    for pad in fp.Pads():
        n=p['nets'][pad.GetNumber()]
        if n: pad.SetNet(nets[n]); pads_by_net[n].append(pad)
        else:
            ncname=f'unconnected-({ref}-Pin_{pad.GetNumber()}-Pad{pad.GetNumber()})'
            nc=pcb.NETINFO_ITEM(board,ncname);board.Add(nc);pad.SetNet(nc)
    fps[ref]=fp
def line(a,b,layer,width=.15):
    s=pcb.PCB_SHAPE(); s.SetShape(pcb.SHAPE_T_SEGMENT); s.SetStart(V(*a));s.SetEnd(V(*b));s.SetLayer(layer);s.SetWidth(MM(width));board.Add(s)
def rect(x0,y0,x1,y1,layer):
    for a,b in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:line(a,b,layer)
rect(0,0,BW,BH,pcb.Edge_Cuts)
for i,(x,y) in enumerate(HOLES,1):
    (LIB/'MountingHole_3.2mm_Small.kicad_mod').write_text(fpgen.mounting_hole())
    fp=pcb.FootprintLoad(str(LIB),'MountingHole_3.2mm_Small')
    board.Add(fp); fp.SetReference('H'+str(i));fp.SetPosition(V(x,y));fp.Value().SetVisible(False);fp.Reference().SetVisible(False)
    fp.SetAttributes(fp.GetAttributes()|pcb.FP_EXCLUDE_FROM_BOM|pcb.FP_BOARD_ONLY)
def text(t,x,y,size=1,layer=pcb.F_SilkS,just='center'):
    s=pcb.PCB_TEXT(board);s.SetText(t);s.SetPosition(V(x,y));s.SetTextSize(pcb.VECTOR2I(MM(size),MM(size)));s.SetTextThickness(MM(.15));s.SetLayer(layer)
    s.SetHorizJustify({'left':pcb.GR_TEXT_H_ALIGN_LEFT,'right':pcb.GR_TEXT_H_ALIGN_RIGHT,'center':pcb.GR_TEXT_H_ALIGN_CENTER}[just]);board.Add(s)
S=pcb.F_SilkS
# --- Module outlines and orientation marks (true-size bodies; rotation cues) ---
def outline(body,open_top=False,heavy_top=False):
    x0,y0,x1,y1=body
    line((x0,y0),(x0,y1),S);line((x1,y0),(x1,y1),S);line((x0,y1),(x1,y1),S)
    if not open_top:line((x0,y0),(x1,y0),S,.3 if heavy_top else .15)
outline(M2_BODY,heavy_top=True)                       # Pro Mini, serial end at the heavy edge
text('SERIAL END',11,3.4)
line((11,4.6),(11,8.4),S);line((11,4.6),(10.1,5.6),S);line((11,4.6),(11.9,5.6),S)
for i,(l,r) in enumerate(zip(M2_L,M2_R)):
    y=M2_PIN1_Y+2.54*i
    text(l,M2_LX+1.6,y,1,just='left');text(r,M2_RX-1.6,y,1,just='right')
outline(M3_BODY,open_top=True)                        # D1 Mini, antenna overhangs the top edge
text('ANTENNA END',35.8,1.7);text('D1 MINI',35.8,3.5);text('USB',35.8,25.7)
line((32.3,M3_BODY[3]),(32.3,M3_BODY[3]+1.3),S);line((39.3,M3_BODY[3]),(39.3,M3_BODY[3]+1.3),S);line((32.3,M3_BODY[3]+1.3),(39.3,M3_BODY[3]+1.3),S)
for i,(l,r) in enumerate(zip(M3_L,M3_R)):
    y=M3_PIN1_Y+2.54*i
    text(l,M3_LX+1.6,y,1,just='left');text(r,M3_RX-1.6,y,1,just='right')
outline(M1_BODY,heavy_top=True)                       # TP4056 module, USB-C at the heavy edge
text('USB-C',61.5,3.0);text('TP4056',61.5,13.5)
for n,(nm,above) in {1:('IN+',False),2:('IN-',False),3:('OUT+',True),4:('OUT-',True),5:('B+',True),6:('B-',True)}.items():
    x,y=M1_PADS_BOARD[n];left=x<M1_BODY[0]+M1_SIZE[0]/2
    text(nm,(M1_BODY[0]+.7) if left else (M1_BODY[2]-.7),(y-3.3 if n in (3,4) else y-2.0) if above else y+2.3,just='left' if left else 'right')
# --- Solder-point names and polarity ---
for key,name,m1,m2 in PAIR_LABELS:
    x=PAIR_X[key]
    text(name,x+1.27,ROW_Y-3.7);text(m1,x,ROW_Y-2.0);text(m2,x+2.54,ROW_Y+2.2)
for ref,nm,dy in [('JP3','JP3 ADC',-2.0),('JP2','JP2 WAKE',-2.0),('JP1','JP1 BAT',-2.0)]:
    x,y=PARTS[ref]['xy'];text(nm,x+1.27,y+dy)
text('OPEN FOR USB',PARTS['JP1']['xy'][0]+1.27,PARTS['JP1']['xy'][1]+2.2)
ix,iy=PARTS['JISP1']['xy']
for idx,nm,side in ISP_LABELS:
    col=idx%2;row=idx//2
    if side=='L':text(nm,ix-1.4,iy+2.54*row,1,just='right')
    else:text(nm,ix+2.54+1.4,iy+2.54*row,1,just='left')
text('ISP',16.4,36.3)
for t,x,y,size,just in LABELS:text(t,x,y,size,just=just)

# Grid router. THT pads are accessible on both layers. It routes to a growing
# tree for each net, reserving all pad, trace and via copper with clearance.
# Rounded grid stubs are included explicitly and validated by KiCad DRC.
STEP=.25; NX=int(BW/STEP)+1; NY=int(BH/STEP)+1
obstacles=[[],[]]; traces=[]; vias=[]
def coord(p): return (pcb.ToMM(p.x)-50,pcb.ToMM(p.y)-50)
for fp in board.GetFootprints():
    for pad in fp.Pads():
        x,y=coord(pad.GetPosition()); sx=pcb.ToMM(pad.GetSize().x)/2;sy=pcb.ToMM(pad.GetSize().y)/2
        if fp.GetReference().startswith('H'): sx=sy=3.0   # no copper under an M3 head or standoff
        # Conservative box including round pads, and full mounting-hole diameter.
        obstacles[0].append((x,y,sx,sy,pad.GetNetname().lstrip('/')));obstacles[1].append((x,y,sx,sy,pad.GetNetname().lstrip('/')))
def blocked(net,width):
    result=[]; margin=.25+width/2+.04
    for layer in range(2):
        arr=bytearray(NX*NY)
        for x,y,sx,sy,n in obstacles[layer]:
            if n==net and n: continue
            lo=max(0,math.ceil((x-sx-margin)/STEP));hi=min(NX-1,math.floor((x+sx+margin)/STEP))
            bottom=max(0,math.ceil((y-sy-margin)/STEP));top=min(NY-1,math.floor((y+sy+margin)/STEP))
            for j in range(bottom,top+1): arr[j*NX+lo:j*NX+hi+1]=b'\1'*(hi-lo+1)
        for a,b,w,n in traces:
            if n==net or a[2]!=layer: continue
            ax,ay=a[0]*STEP,a[1]*STEP;bx,by=b[0]*STEP,b[1]*STEP
            r=w/2+margin
            for yy in range(max(0,math.ceil((min(ay,by)-r)/STEP)),min(NY-1,math.floor((max(ay,by)+r)/STEP))+1):
                for xx in range(max(0,math.ceil((min(ax,bx)-r)/STEP)),min(NX-1,math.floor((max(ax,bx)+r)/STEP))+1):
                    dx=bx-ax;dy=by-ay;t=max(0,min(1,((xx*STEP-ax)*dx+(yy*STEP-ay)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
                    if math.hypot(xx*STEP-ax-t*dx,yy*STEP-ay-t*dy)<r:arr[yy*NX+xx]=1
        for vx,vy,n in vias:
            if n==net:continue
            r=.4+margin
            for yy in range(max(0,math.ceil((vy-r)/STEP)),min(NY-1,math.floor((vy+r)/STEP))+1):
                for xx in range(max(0,math.ceil((vx-r)/STEP)),min(NX-1,math.floor((vx+r)/STEP))+1):
                    if math.hypot(xx*STEP-vx,yy*STEP-vy)<r:arr[yy*NX+xx]=1
        # Edges and radio keepout, conservative expansion.
        for yy in range(NY):
            for xx in range(NX):
                x=xx*STEP;y=yy*STEP
                if x<.5+width/2 or x>BW-.5-width/2 or y<.5+width/2 or y>BH-.5-width/2: arr[yy*NX+xx]=1
        result.append(arr)
    return result
def route(start,targets,net,width):
    masks=blocked(net,width); goals=set(targets)
    gx,gy=targets[0][:2]
    def h(s):return min(abs(s[0]-t[0])+abs(s[1]-t[1]) for t in targets)*1.05
    heap=[];cost={}; prev={}
    for l in (0,1):
        s=(*start,l);cost[s]=0;heapq.heappush(heap,(h(s),0,s))
    found=None
    while heap:
        _,g,s=heapq.heappop(heap)
        if g!=cost[s]:continue
        if s in goals:found=s;break
        x,y,l=s
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            xx=x+dx;yy=y+dy
            if not (0<=xx<NX and 0<=yy<NY) or masks[l][yy*NX+xx]:continue
            n=(xx,yy,l);ng=g+1
            if ng<cost.get(n,float('inf')):cost[n]=ng;prev[n]=s;heapq.heappush(heap,(ng+h(n),ng,n))
        # Via copper needs clearance beyond the trace's envelope.
        if 3<=x<NX-3 and 3<=y<NY-3:
            free=all(not masks[ll][(y+dy)*NX+x+dx] for ll in (0,1) for dx in range(-2,3) for dy in range(-2,3))
            if free:
                n=(x,y,1-l);ng=g+18
                if ng<cost.get(n,float('inf')):cost[n]=ng;prev[n]=s;heapq.heappush(heap,(ng+h(n),ng,n))
    if found is None:
        pcb.SaveBoard('/private/tmp/solar-route-debug.kicad_pcb',board)
        print('Endpoint masks',[(l,masks[l][start[1]*NX+start[0]],masks[l][gy*NX+gx]) for l in (0,1)])
        raise RuntimeError('No route: '+net+str(start))
    path=[found]
    while path[-1] in prev:path.append(prev[path[-1]])
    return path[::-1]
def track(a,b,width,net):
    if a==b:return
    t=pcb.PCB_TRACK(board);t.SetStart(V(*a));t.SetEnd(V(*b));t.SetWidth(MM(width));t.SetLayer(pcb.F_Cu if currentlayer==0 else pcb.B_Cu);t.SetNet(nets[net]);board.Add(t)
power=('VBAT_SYS','GND_LOAD','PROTECTED_POS','CHARGE_5V','CHARGE_RETURN','PACK_POS','PACK_NEG','REG_3V3','ESP_3V3')
order=sorted(netnames,key=lambda n:(n not in power,not n.startswith('ISP_'),-len(pads_by_net[n]),n))
for net in order:
    ps=pads_by_net[net];width=.8 if net in power else .3
    todo=list(ps); first=todo.pop(0); connected=[first]
    while todo:
        p,q=min(((p,q) for p in todo for q in connected),key=lambda pq:math.dist(coord(pq[0].GetPosition()),coord(pq[1].GetPosition())))
        sx,sy=coord(p.GetPosition()); tx,ty=coord(q.GetPosition())
        start=(round(sx/STEP),round(sy/STEP));end=(round(tx/STEP),round(ty/STEP))
        path=route(start,[(*end,0),(*end,1)],net,width)
        compact=[path[0]]
        for i in range(1,len(path)-1):
            a,b,c=path[i-1:i+2]
            if (b[0]-a[0],b[1]-a[1],b[2]-a[2])!=(c[0]-b[0],c[1]-b[1],c[2]-b[2]):compact.append(b)
        compact.append(path[-1]);currentlayer=path[0][2]
        track((sx,sy),(start[0]*STEP,start[1]*STEP),width,net)
        for a,b in zip(compact,compact[1:]):
            if a[2]!=b[2]:
                v=pcb.PCB_VIA(board);v.SetPosition(V(a[0]*STEP,a[1]*STEP));v.SetWidth(MM(.8));v.SetDrill(MM(.4));v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNet(nets[net]);board.Add(v);vias.append((a[0]*STEP,a[1]*STEP,net));currentlayer=b[2]
            else:
                currentlayer=a[2];track((a[0]*STEP,a[1]*STEP),(b[0]*STEP,b[1]*STEP),width,net);traces.append((a,b,width,net))
        currentlayer=path[-1][2];track((end[0]*STEP,end[1]*STEP),(tx,ty),width,net)
        todo.remove(p);connected.append(p)
    print('Routed',net,len(ps),'pads',flush=True)
pcb.SaveBoard(str(ROOT/(NAME+'.kicad_pcb')),board)
project={'meta':{'filename':NAME+'.kicad_pro','version':1},
 'board':{'design_settings':{'rules':{'min_clearance':.25,'min_track_width':.3,'min_through_hole_diameter':.3,
 'min_via_diameter':.8,'min_via_annular_width':.2,'min_copper_edge_clearance':.5,'min_hole_clearance':.25,
 'min_hole_to_hole':.25,'min_silk_clearance':.15,'min_text_height':1,'min_text_thickness':.15}}},
 'net_settings':{'classes':[{'name':'Default','clearance':.25,'track_width':.3,'via_diameter':.8,'via_drill':.4,
 'bus_width':12,'line_style':0,'microvia_diameter':.3,'microvia_drill':.1,'wire_width':6}], 'meta':{'version':4}}}
(ROOT/(NAME+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n')
with (ROOT/'review'/'assembly-bom.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Fit in tiers','Assembly note'])
    for ref,p in PARTS.items():w.writerow([ref,p['value'],p['local_fp'],p['tier'],p['note']])
(ROOT/'review'/'design-manifest.json').write_text(json.dumps({'parts':PARTS,'holes_mm':HOLES,'board_mm':[BW,BH],'vias':len(vias)},indent=2)+'\n')
print('Generated',NAME,'with',len(vias),'vias')
