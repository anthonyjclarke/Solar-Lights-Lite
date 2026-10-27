#!/bin/zsh
# Regenerate, polish, run KiCad ERC/DRC, export the netlist and validate. Run from the project folder.
set -e
KICAD=${KICAD_APP:-/Applications/KiCad/KiCad.app}
PY=$KICAD/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=$KICAD/Contents/MacOS/kicad-cli
N=SolarLights_Carrier_RevB
$PY tools/generate.py | tail -1
$PY tools/polish.py | tail -1
$CLI sch erc --format json --exit-code-violations -o review/erc.json $N.kicad_sch
$CLI sch export netlist --format kicadxml -o review/schematic-netlist.xml $N.kicad_sch
$CLI pcb drc --format json --schematic-parity --all-track-errors --severity-all --exit-code-violations -o review/drc.json $N.kicad_pcb
$PY tools/validate.py
