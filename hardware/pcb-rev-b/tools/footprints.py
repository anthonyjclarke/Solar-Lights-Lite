"""Custom through-hole footprints for Rev B, written as .kicad_mod text.
Pure Python (no pcbnew). Coordinates are mm, footprint origin = pin 1.
"""

def _pad(num, x, y, size, drill, shape):
    return (f'\t(pad "{num}" thru_hole {shape}\n\t\t(at {x:.4f} {y:.4f})\n\t\t(size {size} {size})\n'
            f'\t\t(drill {drill})\n\t\t(layers "*.Cu" "*.Mask")\n\t\t(remove_unused_layers no)\n\t)\n')

def _rect(x0, y0, x1, y1, layer, width):
    return (f'\t(fp_rect\n\t\t(start {x0} {y0})\n\t\t(end {x1} {y1})\n\t\t(stroke\n\t\t\t(width {width})\n'
            f'\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "{layer}")\n\t)\n')

def _footprint(name, descr, pads, court, ref_at):
    head = (f'(footprint "{name}"\n\t(version 20260206)\n\t(generator "solar-lights-rev-b")\n'
            f'\t(layer "F.Cu")\n\t(descr "{descr}")\n')
    props = ''.join(
        f'\t(property "{k}" "{v}"\n\t\t(at {ref_at[0]} {ref_at[1]} 0)\n\t\t(layer "{layer}")\n'
        f'\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
        for k, v, layer in (('Reference', 'REF**', 'F.SilkS'), ('Value', name, 'F.Fab')))
    return head + props + '\t(attr through_hole)\n' + _rect(*court, 'F.CrtYd', 0.05) + ''.join(pads) + ')\n'

def solder_pads_1x02():
    """Two 1.8 mm pads at 2.54 mm, side by side along x; pad 1 square.
    A wire or a 2-pin header can be soldered here."""
    pads = [_pad(1, 0, 0, 1.8, 1.0, 'rect'), _pad(2, 2.54, 0, 1.8, 1.0, 'circle')]
    return _footprint('SolderPads_1x02_P2.54mm',
                      '1x2 plated solder points, 2.54 mm pitch, horizontal; wire or header', pads,
                      (-1.2, -1.2, 3.74, 1.2), (1.27, -2.2))

def tp4056_module(pads_mm, hole, pad):
    """Six overlay holes under a 6-pad TP4056 charger module (nominal, to be measured).
    pads_mm: {number: (x, y)} relative to pad 1."""
    pads = [_pad(n, x, y, pad, hole, 'rect' if n == 1 else 'circle') for n, (x, y) in sorted(pads_mm.items())]
    xs = [p[0] for p in pads_mm.values()]; ys = [p[1] for p in pads_mm.values()]
    return _footprint('TP4056_Module_6pad_Overlay',
                      'Six plated holes matching the pad holes of a TP4056 protected charger module (NOMINAL - measure)',
                      pads, (min(xs) - 1.4, min(ys) - 1.4, max(xs) + 1.4, max(ys) + 1.4), (0, -3.5))

def pads_2x03():
    """AVR ISP 2x03 pads (pin numbering as a standard 2x03 header, pin 1 square), no silkscreen."""
    pads = [_pad(1, 0, 0, 1.8, 1.0, 'rect')] + [
        _pad(n, 2.54 * ((n - 1) % 2), 2.54 * ((n - 1) // 2), 1.8, 1.0, 'circle') for n in range(2, 7)]
    return _footprint('Pads_2x03_P2.54mm', '2x3 plated holes for a 2.54 mm AVR ISP header (fit a pin header)', pads,
                      (-1.2, -1.2, 3.74, 6.28), (1.27, -2.2))

def mounting_hole():
    pad = ('\t(pad "" np_thru_hole circle\n\t\t(at 0 0)\n\t\t(size 3.2 3.2)\n\t\t(drill 3.2)\n'
           '\t\t(layers "*.Cu" "*.Mask")\n\t)\n')
    return _footprint('MountingHole_3.2mm_Small', 'M3 mounting hole, small courtyard', [pad], (-1.9, -1.9, 1.9, 1.9), (0, -2.8))

FOOTPRINTS = {'SolderPads_1x02_P2.54mm': solder_pads_1x02, 'Pads_2x03_P2.54mm': pads_2x03,
              'MountingHole_3.2mm_Small': mounting_hole}
