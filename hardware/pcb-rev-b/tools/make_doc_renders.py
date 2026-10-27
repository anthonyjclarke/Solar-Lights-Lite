"""Render the Rev B carrier for docs/13 with 2.54 mm pin headers on every solder point.
Works on a temporary copy, so the project and fabrication files are untouched.
Run with KiCad's bundled Python from the pcb-rev-b folder: python3 tools/make_doc_renders.py
Modules M1-M3 have no 3D models and are not shown.
"""
import os, subprocess, sys, tempfile
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).resolve().parent))
from design import ROOT, NAME

CLI = Path(os.environ.get('KICAD_APP', '/Applications/KiCad/KiCad.app')) / 'Contents/MacOS/kicad-cli'
OUT = ROOT.parents[1] / 'docs' / 'images' / 'pcb'
HDR = '${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/'
VIEWS = {'carrier-angled.png': ['--side', 'top', '--perspective', '--rotate', '-35,0,20', '--zoom', '0.9'],
         'carrier-top.png': ['--side', 'top'],
         'carrier-bottom.png': ['--side', 'bottom']}

board = pcbnew.LoadBoard(str(ROOT / f'{NAME}.kicad_pcb'))
for fp in board.GetFootprints():
    name = fp.GetFPID().GetLibItemName()
    model = pcbnew.FP_3DMODEL()
    if name == 'SolderPads_1x02_P2.54mm':      # pads run along x; the library header runs along y
        model.m_Filename = HDR + 'PinHeader_1x02_P2.54mm_Vertical.step'
        model.m_Rotation = pcbnew.VECTOR3D(0, 0, -90)
    elif name == 'Pads_2x03_P2.54mm':
        model.m_Filename = HDR + 'PinHeader_2x03_P2.54mm_Vertical.step'
    else:
        continue
    fp.Models().clear(); fp.Models().push_back(model)

OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    pcb = Path(tmp) / 'headers.kicad_pcb'
    board.Save(str(pcb))
    for out, args in VIEWS.items():
        subprocess.run([str(CLI), 'pcb', 'render', *args, '--quality', 'high', '--background', 'opaque',
                        '-w', '1400', '-h', '950', '-o', str(OUT / out), str(pcb)], check=True, capture_output=True)
        print('rendered', OUT / out)
