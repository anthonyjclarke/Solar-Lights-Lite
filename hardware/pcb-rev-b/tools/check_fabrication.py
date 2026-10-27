"""Check the exported outline, drill tools, hole locations, layer identity and
ZIP content independently of pcbnew. This is not a supplier DFM check.
"""
import re,json,zipfile,hashlib
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from design import ROOT,NAME,BW,BH,HOLES
fab=ROOT/'fabrication'
GEOM=json.loads((ROOT/'review'/'fit-geometry.json').read_text());MAN=json.loads((ROOT/'review'/'design-manifest.json').read_text())
outline=(fab/(NAME+'-Edge_Cuts.gm1')).read_text()
commands=re.findall(r'X(-?\d+)Y(-?\d+)D0([12])\*',outline)
segments=[];last=None
for x,y,code in commands:
    point=(int(x)/1e6,int(y)/1e6)
    if code=='1':segments.append((last,point))
    last=point
assert len(segments)==4
degree=Counter(p for seg in segments for p in seg)
assert set(degree.values())=={2},'Outline is not a single closed rectangle'
assert set(degree)=={(50,-50),(50+BW,-50),(50+BW,-50-BH),(50,-50-BH)},'Outline dimensions/origin changed'
npth=(fab/(NAME+'-NPTH.drl')).read_text()
holes=set((float(x),float(y)) for x,y in re.findall(r'^X(-?[\d.]+)Y(-?[\d.]+)$',npth,re.M))
assert holes=={(50+x,-50-y) for x,y in HOLES},'Mounting hole locations'
assert re.findall(r'^T\d+C([\d.]+)$',npth,re.M)==['3.200']
pth=(fab/(NAME+'-PTH.drl')).read_text()
plated=[p for p in GEOM['pads'] if p['drill']>0 and not p['ref'].startswith('H')]
assert len(re.findall(r'^X',pth,re.M))==len(plated)+MAN['vias'],'Plated hole count'
assert set(re.findall(r'^T\d+C([\d.]+)$',pth,re.M))=={f'{d:.3f}' for d in {p['drill'] for p in plated}|{0.4}},'Plated drill sizes'
expected={'F_Cu.gtl':'Copper,L1,Top','B_Cu.gbl':'Copper,L2,Bot',
 'F_Mask.gts':'Soldermask,Top','B_Mask.gbs':'Soldermask,Bot',
 'F_Silkscreen.gto':'Legend,Top','B_Silkscreen.gbo':'Legend,Bot'}
for suffix,identity in expected.items():
    assert identity in (fab/(NAME+'-'+suffix)).read_text(),suffix
with zipfile.ZipFile(ROOT/(NAME+'_fabrication_REVIEW.zip')) as z:
    assert z.testzip() is None
    assert len(z.namelist())==10
    for f in z.namelist():assert z.read(f)==(fab/f).read_bytes(),f
report={'status':'EXPORTED_FILES_PASS_SUPPLIER_DFM_NOT_RUN','outline_mm':[BW,BH],
 'closed_outline_segments':4,'PTH_holes':len(plated)+MAN['vias'],'NPTH_holes':len(HOLES),'NPTH_diameter_mm':3.2,
 'zip_files':10,'checks':['Closed correctly sized outline','Gerber layer identities',
 'Three correct mounting-hole locations','Plated drill counts and tool sizes','ZIP CRC and exact file equality']}
(ROOT/'review'/'fabrication-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: export outline, drill counts/alignment, six layer identities and fabrication ZIP')
