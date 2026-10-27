"""Render the Rev C carrier: pin headers on every solder point, then the
final assembly with M1-M3 fitted and the modules' own male pins in the sockets.
Works on temporary copies, so the project and fabrication files are untouched.
Run with KiCad's bundled Python from the pcb-rev-c folder: python3 tools/make_doc_renders.py

M2 uses the SnapEDA Arduino Pro Mini STEP when 3dmodels/snapeda/ holds it (not in git: the
SnapEDA licence restricts redistributing the raw model); otherwise the stand-in. M1 and M3 are
stand-ins from tools/make_module_models.py.
"""
import os, subprocess, sys, tempfile
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).resolve().parent))
from design import ROOT, NAME

CLI = Path(os.environ.get('KICAD_APP', '/Applications/KiCad/KiCad.app')) / 'Contents/MacOS/kicad-cli'
OUT = ROOT / 'review' / 'renders'          # docs/images/pcb shows Rev B, as ordered; copy these there if Rev C replaces it
MODELS = ROOT / '3dmodels'
SNAPEDA = MODELS / 'snapeda' / 'Arduino_Pro_Mini.step'
HDR = '${KICAD10_3DMODEL_DIR}/Connector_PinHeader_2.54mm.3dshapes/'
MODULE_Z = 11.04            # module underside: 8.5 mm socket + 2.54 mm header spacer
ANGLED = ['--side', 'top', '--perspective', '--rotate', '-35,0,20', '--zoom', '0.9']
VIEWS = {'carrier-angled.png': (False, ANGLED),
         'carrier-top.png': (False, ['--side', 'top']),
         'carrier-bottom.png': (False, ['--side', 'bottom']),
         'carrier-assembled-angled.png': (True, ANGLED),
         'carrier-assembled-top.png': (True, ['--side', 'top']),
         'carrier-assembled-side.png': (True, ['--side', 'right', '--zoom', '1.6'])}


def model(path, offset=(0, 0, 0), rotation=(0, 0, 0)):
    m = pcbnew.FP_3DMODEL(); m.m_Filename = str(path)
    m.m_Offset = pcbnew.VECTOR3D(*offset); m.m_Rotation = pcbnew.VECTOR3D(*rotation)
    return m


def build(modules):
    board = pcbnew.LoadBoard(str(ROOT / f'{NAME}.kicad_pcb'))
    for fp in board.GetFootprints():
        ref, name = fp.GetReference(), fp.GetFPID().GetLibItemName()
        if name == 'SolderPads_1x02_P2.54mm':   # pads run along x; the library header runs along y
            fp.Models().clear(); fp.Models().push_back(model(HDR + 'PinHeader_1x02_P2.54mm_Vertical.step', rotation=(0, 0, -90)))
        elif name == 'Pads_2x03_P2.54mm':
            fp.Models().clear(); fp.Models().push_back(model(HDR + 'PinHeader_2x03_P2.54mm_Vertical.step'))
        if not modules:
            continue
        if ref.startswith(('JM2', 'JM3')):       # module's male pins, long end down into the socket
            n = 12 if ref.startswith('JM2') else 8
            fp.Models().push_back(model(HDR + f'PinHeader_1x{n:02d}_P2.54mm_Vertical.step', (0, 0, MODULE_Z), (0, 180, 0)))
        if ref == 'JM2L1':
            if SNAPEDA.exists():                 # SolidWorks Y-up export, origin at the board centre
                fp.Models().push_back(model(SNAPEDA, (7.62, -12.77, MODULE_Z), (-90, 0, 0)))
            else:
                fp.Models().push_back(model(MODELS / 'Pro_Mini_standin.wrl', (0, 0, MODULE_Z)))
        elif ref == 'JM3L1':
            fp.Models().push_back(model(MODELS / 'D1_Mini_standin.wrl', (0, 0, MODULE_Z)))
        elif ref == 'M1':                        # ~2 mm proud on wire links
            fp.Models().push_back(model(MODELS / 'TP4056_USBC_standin.wrl', (0, 0, 2.0)))
    return board


OUT.mkdir(parents=True, exist_ok=True)
print('M2 model:', SNAPEDA.name if SNAPEDA.exists() else 'stand-in')
with tempfile.TemporaryDirectory() as tmp:
    for modules in (False, True):
        pcb = Path(tmp) / f'render{int(modules)}.kicad_pcb'
        build(modules).Save(str(pcb))
        for out, (assembled, args) in VIEWS.items():
            if assembled != modules:
                continue
            subprocess.run([str(CLI), 'pcb', 'render', *args, '--quality', 'high', '--background', 'opaque',
                            '-w', '1400', '-h', '950', '-o', str(OUT / out), str(pcb)], check=True, capture_output=True)
            print('rendered', OUT / out)
