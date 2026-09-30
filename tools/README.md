# Tools

Generators for the drawings and wiring data in `docs/`. Edit the generator, then
regenerate; do not hand-edit the outputs.

| Script                 | Writes                                        |
| :--------------------- | :-------------------------------------------- |
| `make_drawings.py`     | Sheet SVGs and PNGs, A3 drawings PDF          |
| `make_board_map.py`    | `docs/drawings/BTE13-010A-pin-map.*`          |
| `make_usbasp_sheet.py` | `docs/drawings/usbasp-wiring.*`               |
| `make_bench_sheet.py`  | `docs/drawings/controller-bench-sheet.*`      |
| `make_netlist.py`      | `docs/netlist.json`, `docs/wire-schedule.csv` |
| `make_guide.py`        | `docs/ASSEMBLY.html` from guides 01–12        |

`make_netlist.py` needs only the Python standard library and also checks the
wiring rules (for example that B- is never joined to OUT-). `make_guide.py`
needs `markdown`; the drawing scripts need `reportlab` and `pypdfium2`. Run
`make_guide.py` last, after any drawing, CSV or guide change:

```bash
python3 -m venv .venv
.venv/bin/pip install reportlab pypdfium2 markdown
.venv/bin/python tools/make_drawings.py
.venv/bin/python tools/make_guide.py
```

The KiCad schematic has its own generator in `hardware/kicad/tools/`; see
[`hardware/kicad/README.md`](../hardware/kicad/README.md).
