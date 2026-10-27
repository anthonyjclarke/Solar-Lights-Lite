"""Place readable reference text in free silkscreen space; do not suppress DRC.
Run after generate.py. Copper and component positions remain unchanged.
"""
import pcbnew as p
from design import ROOT, NAME, BW, BH, REF_POS
b=p.LoadBoard(str(ROOT/(NAME+'.kicad_pcb')))
M=p.FromMM
def pos(x,y):return p.VECTOR2I(M(x+50),M(y+50))
def box(obj,margin=0):
    bb=obj.GetBoundingBox()
    return (p.ToMM(bb.GetX())-margin,p.ToMM(bb.GetY())-margin,
            p.ToMM(bb.GetRight())+margin,p.ToMM(bb.GetBottom())+margin)
def intersects(a,c):return a[0]<c[2] and c[0]<a[2] and a[1]<c[3] and c[1]<a[3]
occupied=[]
bodies={}
for d in b.GetDrawings():
    if isinstance(d,p.PCB_SHAPE) and d.GetLayer()==p.F_SilkS:occupied.append(box(d,.2))
for fp in b.GetFootprints():
    for pad in fp.Pads():occupied.append(box(pad,.22))
    courts=[box(g,.15) for g in fp.GraphicalItems() if g.GetLayer()==p.F_CrtYd]
    if courts:bodies[fp.GetReference()]=(min(c[0] for c in courts),min(c[1] for c in courts),max(c[2] for c in courts),max(c[3] for c in courts))
    for g in fp.GraphicalItems():
        if g.GetLayer()==p.F_SilkS:occupied.append(box(g,.18))
def free(t,owner=None):
    a=box(t,.05)
    return a[0]>50.6 and a[1]>50.6 and a[2]<50+BW-.6 and a[3]<50+BH-.6 and not any(intersects(a,c) for c in occupied) and not (owner and any(intersects(a,c) for ref,c in bodies.items() if ref!=owner))
def place(t,x,y,reference=False,owner=None):
    t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    attempts=[(x,y)]
    for radius in ([1,2,3,4,5,6,7,8,9,10,12] if reference else [.5,1,1.5,2,3,4,5,6,7,8,10,12]):
        attempts.extend((x+dx,y+dy) for dx,dy in [(0,-radius),(0,radius),(-radius,0),(radius,0),(-radius,-radius),(radius,-radius),(-radius,radius),(radius,radius)])
    if reference:
        attempts.extend((x+dx,y+dy) for dx,dy in sorted(
            ((i/2,j/2) for i in range(-32,33) for j in range(-32,33)),
            key=lambda q:q[0]*q[0]+q[1]*q[1]))
    for xx,yy in attempts:
        t.SetPosition(pos(xx,yy))
        if free(t,owner):occupied.append(box(t,.18));return
    raise RuntimeError('No free silk position for '+t.GetText())
texts=sorted([d for d in b.GetDrawings() if isinstance(d,p.PCB_TEXT) and d.GetLayer()==p.F_SilkS],key=lambda t:-len(t.GetText()))
for t in texts:
    occupied.append(box(t,.2))
for fp in sorted(b.GetFootprints(),key=lambda f:-len(f.GetReference())):
    t=fp.Reference()
    if not t.IsVisible():continue
    if fp.GetReference() in REF_POS:
        x,y,j=REF_POS[fp.GetReference()]
        t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T));t.SetPosition(pos(x,y));t.SetTextSize(p.VECTOR2I(M(1),M(1)));t.SetTextThickness(M(.15))
        t.SetHorizJustify({'left':p.GR_TEXT_H_ALIGN_LEFT,'center':p.GR_TEXT_H_ALIGN_CENTER}[j])
        occupied.append(box(t,.18));continue
    t.SetTextSize(p.VECTOR2I(M(1),M(1)));t.SetTextThickness(M(.15))
    x=p.ToMM(t.GetPosition().x)-50;y=p.ToMM(t.GetPosition().y)-50
    place(t,x,y,True,fp.GetReference())
p.SaveBoard(str(ROOT/(NAME+'.kicad_pcb')),b)
print('Placed',len(texts),'board labels and all component references')
