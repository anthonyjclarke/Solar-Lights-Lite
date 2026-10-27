# Solar Lights Lite – PCB carrier Rev C

Started **28-Oct-2026** from Rev B. Status: **draft; not reviewed for fabrication.**

Rev C begins as an exact copy of the Rev B layout. Only the revision marks differ: the board is
`SolarLights_Carrier_RevC`, the silkscreen reads `SOLAR LIGHTS LITE / C`, and the schematic title block
says `C / DRAFT`. Until changes are recorded below, the [Rev B README](../pcb-rev-b/README.md) describes
this design in full: connections, tiers, modules, ISP, TP4056 geometry and open measurements.

Open `SolarLights_Carrier_RevC.kicad_pro` in **KiCad 10 or later**.

---

## What changed from Rev B

| Change | Rev C |
|:-------|:------|
| –      | –     |

---

## Working on Rev C

The board, schematic, footprints and BOM are generated from `tools/design.py` (placement, nets,
labels) and `tools/footprints.py`. Make layout changes there, not in KiCad, then rerun the checks;
`generate.py` overwrites the KiCad files. `tools/validate.py` holds the design rules (B– isolation,
board area, tier population): update it when a change is deliberate.

```
tools/run_checks.sh          # generate, polish, ERC, netlist, DRC with parity, validate
```

When the checks pass, `REPORTLAB_PY=<python with reportlab, pypdfium2> tools/build_outputs.sh` exports
the fabrication files, review PDFs, fit sheet and design zip. The renders go to `review/renders/`, not
`docs/images/pcb/`: guide 13 shows Rev B, the board as ordered. Copy them across when Rev C replaces it.

Rev B stays unchanged as the record of the ordered board.
