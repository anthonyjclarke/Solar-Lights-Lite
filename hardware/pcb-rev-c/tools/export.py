"""Export portable bare-board fabrication files only after validated CAD checks.
Run with KiCad Python. Rendering is a separate kicad-cli pcb render command.
"""
import os, json, hashlib, subprocess, zipfile
import pcbnew as p
from design import ROOT, NAME
cli=os.environ.get('KICAD_CLI','/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
val=json.loads((ROOT/'review'/'validation.json').read_text())
for suffix,h in val['sha256'].items():
    assert hashlib.sha256((ROOT/(NAME+suffix)).read_bytes()).hexdigest()==h,'Revalidate changed CAD before export'
board=ROOT/(NAME+'.kicad_pcb');fab=ROOT/'fabrication';review=ROOT/'review'
def run(*args):subprocess.run([cli,*map(str,args)],check=True)
run('pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts',
    '--subtract-soldermask','-o',str(fab)+'/',board)
run('pcb','export','drill','--format','excellon','--excellon-units','mm','--excellon-separate-th',
    '--generate-report','--report-path',review/'drill-report.txt','-o',str(fab)+'/',board)
for filename,layers in [('top-copper.svg','F.Cu,F.SilkS,Edge.Cuts'),
                        ('bottom-copper.svg','B.Cu,B.SilkS,Edge.Cuts'),
                        ('assembly.svg','F.Fab,F.SilkS,Dwgs.User,Edge.Cuts')]:
    run('pcb','export','svg','--layers',layers,'--mode-single','--page-size-mode','2','-o',review/filename,board)
run('pcb','export','pdf','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,F.Fab,Dwgs.User',
    '--common-layers','Edge.Cuts','--mode-multipage','--scale','1','-o',review/'pcb-layers.pdf',board)
b=p.LoadBoard(str(board));pads=[];texts=[]
for fp in b.GetFootprints():
    for pad in fp.Pads():
        pads.append({'ref':fp.GetReference(),'pin':pad.GetNumber(),
          'x':p.ToMM(pad.GetPosition().x)-50,'y':p.ToMM(pad.GetPosition().y)-50,
          'width':p.ToMM(pad.GetSize().x),'height':p.ToMM(pad.GetSize().y),
          'angle':pad.GetOrientationDegrees(),'drill':p.ToMM(pad.GetDrillSize().x),
          'rect':pad.GetShape()==p.PAD_SHAPE_RECT,'net':pad.GetNetname()})
for d in b.GetDrawings():
    if isinstance(d,p.PCB_TEXT) and d.GetLayer()==p.F_SilkS:
        texts.append({'text':d.GetText(),'x':p.ToMM(d.GetPosition().x)-50,'y':p.ToMM(d.GetPosition().y)-50})
(review/'fit-geometry.json').write_text(json.dumps({'pads':pads,'labels':texts},indent=2)+'\n')
files=sorted(x for x in fab.iterdir() if x.suffix.lower() in ('.gtl','.gbl','.gts','.gbs','.gto','.gbo','.gm1','.gbr','.gbrjob','.drl'))
required=['F_Cu.gtl','B_Cu.gbl','F_Mask.gts','B_Mask.gbs','F_Silkscreen.gto','B_Silkscreen.gbo','Edge_Cuts.gm1','PTH.drl','NPTH.drl']
for suffix in required:assert any(f.name.endswith(suffix) for f in files),suffix
archive=ROOT/(NAME+'_fabrication_REVIEW.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in files:z.write(file,file.name)
(review/'fabrication-sha256.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2)+'\n')
print('Packaged',len(files),'fabrication files:',archive)
