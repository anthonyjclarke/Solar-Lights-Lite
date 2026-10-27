"""Write simple stand-in 3D models (VRML) for the three plug-in modules, for renders only.
Each model is made of boxes at the module's measured outline, pin rows and main parts;
they are not manufacturer models. Origin = the module's pin 1 / IN+ hole as placed on the
carrier footprint, z = 0 at the module's underside. KiCad VRML units are 0.1 inch.
Run with any Python 3: python3 tools/make_module_models.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / '3dmodels'
U = 1 / 2.54                                     # mm -> KiCad VRML units
PCB_BLUE, PCB_BLACK = (0.10, 0.20, 0.75), (0.08, 0.08, 0.09)
METAL, CHIP, GOLD, WHITE = (0.78, 0.79, 0.80), (0.12, 0.12, 0.13), (0.85, 0.68, 0.25), (0.92, 0.92, 0.90)


def box(x0, y0, z0, x1, y1, z1, rgb):
    """Axis-aligned box in carrier mm (y down on the board, so VRML y = -y)."""
    v = [(x, -y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    pts = ', '.join(f'{x * U:.4f} {y * U:.4f} {z * U:.4f}' for x, y, z in v)
    faces = '0 1 3 2 -1 4 6 7 5 -1 0 4 5 1 -1 2 3 7 6 -1 0 2 6 4 -1 1 5 7 3 -1'
    r, g, b = rgb
    return (f'Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {b} '
            f'specularColor 0.2 0.2 0.2 shininess 0.3 }} }}\n'
            f'  geometry IndexedFaceSet {{ solid FALSE coord Coordinate {{ point [ {pts} ] }} '
            f'coordIndex [ {faces} ] }} }}\n')


def holes(xs, y0, n, z0, z1):
    """Gold ring marks where header pins pass through a module board."""
    return ''.join(box(x - .6, y0 + 2.54 * i - .6, z0, x + .6, y0 + 2.54 * i + .6, z1, GOLD)
                   for x in xs for i in range(n))


def write(name, shapes):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text('#VRML V2.0 utf8\n# Stand-in render model, not a manufacturer model. CC0 1.0.\n' + shapes)
    print('wrote', OUT / name)


T = 1.0                                          # module board thickness, mm

# M3 Wemos D1 Mini: 25.6 x 34.2; rows 22.86 apart; pin 1 (RST) 9.0 mm from the antenna end.
# Antenna end at y -9.0, USB end at y +25.2 (pin 1 frame, socket footprint origin).
d1 = box(-1.37, -9.0, 0, 24.23, 25.2, T, PCB_BLUE)
d1 += box(3.43, -9.0, T, 19.43, 15.0, T + .8, PCB_BLACK)        # ESP-12 carrier PCB with antenna
d1 += box(4.43, -1.0, T + .8, 18.43, 14.0, T + 3.0, METAL)      # ESP-12 shield
d1 += box(7.68, 20.0, T, 15.18, 25.8, T + 2.6, METAL)           # micro-USB, proud of the USB end
d1 += box(-0.2, 16.5, T, 3.0, 19.7, T + 1.6, WHITE)             # reset button
d1 += holes((0, 22.86), 0, 8, T, T + .05)
write('D1_Mini_standin.wrl', d1)

# M1 TP4056 USB-C module: 17.2 x 26.73, USB-C end up, on the IN+ hole frame used by the carrier.
tp = box(-15.6, -1.5, 0, 1.6, 25.23, T, PCB_BLUE)
tp += box(-11.5, -2.1, T, -2.5, 5.4, T + 3.2, METAL)            # USB-C receptacle, flush with the end
tp += box(-9.5, 8.0, T, -4.5, 12.0, T + 1.5, CHIP)              # TP4056 (SOP-8)
tp += box(-12.5, 15.0, T, -9.5, 18.0, T + 1.1, CHIP)            # DW01A
tp += box(-6.5, 15.0, T, -3.5, 18.0, T + 1.1, CHIP)             # 8205A
tp += box(-1.0, 8.0, T, .6, 9.0, T + .6, (0.85, 0.15, 0.15))    # charge LED
tp += box(-1.0, 10.0, T, .6, 11.0, T + .6, (0.15, 0.35, 0.90))  # done LED
for x, y in [(0, 0), (-14, 0), (0, 22), (-14, 22), (-10.55, 22), (-3.1, 22)]:
    tp += box(x - .7, y - .7, T, x + .7, y + .7, T + .05, GOLD)
    tp += box(x - .3, y - .3, -3.8, x + .3, y + .3, T + .5, METAL)   # wire link through both boards
write('TP4056_USBC_standin.wrl', tp)

# M2 Pro Mini, used only when the SnapEDA STEP is absent: 18 x 33.3; rows 15.24 apart;
# pin 1 (TX) 4.0 mm from the serial end.
pm = box(-1.38, -4.0, 0, 16.62, 29.3, T, PCB_BLUE)
pm += box(4.1, 9.0, T, 11.1, 16.0, T + 1.0, CHIP)               # ATmega328P (TQFP-32)
pm += box(5.6, 23.5, T, 9.6, 27.5, T + 1.5, WHITE)              # reset button
pm += holes((0, 15.24), 0, 12, T, T + .05)
pm += holes((1.27 + 2.54 * i for i in range(6)), -2.7, 1, T, T + .05)   # serial header
write('Pro_Mini_standin.wrl', pm)
