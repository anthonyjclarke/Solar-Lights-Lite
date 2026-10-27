#!/bin/zsh
# After run_checks.sh passes: export fabrication files, render, build review/fit PDFs and the design zip.
# REPORTLAB_PY must be a Python with reportlab, pypdfium2 and pillow installed.
set -e
KICAD=${KICAD_APP:-/Applications/KiCad/KiCad.app}
PY=$KICAD/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=$KICAD/Contents/MacOS/kicad-cli
RL=${REPORTLAB_PY:?set REPORTLAB_PY to a python with reportlab and pypdfium2}
N=SolarLights_Carrier_RevC
$PY tools/export.py | tail -1
$PY tools/check_fabrication.py | tail -1
$PY tools/make_module_models.py >/dev/null
$PY tools/make_doc_renders.py | tail -1                 # review/renders: headers, then modules fitted
$CLI pcb render --side top --quality basic --background opaque --width 1800 --height 1300 -o review/pcb-top.png $N.kicad_pcb
$CLI sch export pdf -o review/schematic.pdf $N.kicad_sch
$RL tools/make_review.py; $RL tools/make_fit_sheet.py; $RL tools/make_module_check.py
rm -rf tools/__pycache__ $N'_design_REVIEW.zip'
zip -qr $N'_design_REVIEW.zip' README.md $N.kicad_pro $N.kicad_sch $N.kicad_pcb fp-lib-table Carrier.pretty tools review -x '*.DS_Store'
