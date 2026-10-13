"""Export: LDraw MPD (for BrickLink Studio), BrickLink wanted-list XML, and compact viewer JSON."""
import json, collections, numpy as np
from build import m, STEPS, MODULES, MID_MODS
from core import P, COLORS, BL_ID
from ldlib import bbox

SECTIONS = {1: 'Base and floor', 2: 'Interior', 3: 'Walls', 4: 'Narthex railing and aisle ceilings', 5: 'Ribs',
            6: 'Aisle roofs', 7: 'Gables', 8: 'Porch', 9: 'Roof modules'}
SUBS = ['base', 'interior', 'walls', 'loft', 'ribs', 'aisles', 'gables', 'porch', 'roof_rear', 'roof_organ', 'roof_organ_lid', 'roof_mid', 'roof_mid_lid', 'roof_front', 'roof_lanterns']
SUB_TITLE = {'base': 'Baseplates, chancel platform and floor', 'interior': 'Pews and chancel furniture',
             'walls': 'Walls, posts and doors', 'loft': 'Narthex railing, chancel beams and aisle ceilings',
             'ribs': 'Glulam ribs', 'aisles': 'Knee walls and aisle roofs', 'gables': 'Front and rear gables, reredos',
             'porch': 'Entrance porch', 'roof_rear': 'Rear roof module (fixed)',
             'roof_organ': 'Roof bay over the altar with organ grilles, fixed left side',
             'roof_organ_lid': 'Roof bay over the altar, lift-off right side',
             'roof_lanterns': 'Lanterns hanging from the fixed left ceiling',
             'roof_mid_lid': 'Middle roof bay, lift-off right side (build %d)' % len(MID_MODS),
             'roof_mid': 'Middle roof bay, fixed left side (build %d)' % len(MID_MODS), 'roof_front': 'Front roof module (fixed) with cross'}

order = sorted(STEPS, key=lambda s: STEPS[s]['order'])
sidx = {s: i for i, s in enumerate(order)}

def module_of(p):
    if not p['sub'].startswith('roof'): return -1
    for i, (a, b) in enumerate(MODULES):
        if a <= p['z0'] < b: return i
    return -1

# ------------------------------------------------------------------ LDraw MPD
def write_mpd(path):
    L = []
    L += ['0 FILE st_andrews_nave.ldr', "0 St. Andrew's Episcopal Church, Newport News - minifig-scale nave",
          '0 Name: st_andrews_nave.ldr', "0 Author: St. Andrew's LEGO project (generated)", '0 !LDRAW_ORG Unofficial_Model', '']
    for sub in SUBS:
        if sub in ('roof_mid', 'roof_mid_lid'):
            for i, (a, b) in enumerate(MID_MODS):
                dz = a - MID_MODS[0][0]
                L.append('1 16 0 0 %d 1 0 0 0 1 0 0 0 1 %s.ldr' % (-20 * dz, sub))
        else:
            L.append('1 16 0 0 0 1 0 0 0 1 0 0 0 1 %s.ldr' % sub)
        L.append('0 STEP')
    L.append('')
    for sub in SUBS:
        L += ['0 FILE %s.ldr' % sub, '0 ' + SUB_TITLE[sub], '0 Name: %s.ldr' % sub,
              "0 Author: St. Andrew's LEGO project (generated)", '0 !LDRAW_ORG Unofficial_Model']
        parts = [p for p in m.parts if p['sub'] == sub and not p.get('copy_of')]
        bystep = collections.defaultdict(list)
        for p in parts: bystep[sidx[p['step']]].append(p)
        for si in sorted(bystep):
            L.append('0 // ' + STEPS[order[si]]['title'])
            for p in bystep[si]: L.append(m.ldraw_line(p))
            L.append('0 STEP')
        L.append('')
    open(path, 'w').write('\n'.join(L))

# ------------------------------------------------------------------ BrickLink XML
def bom():
    c = collections.Counter((p['pid'], p['color']) for p in m.parts)
    return c
def write_bl(path):
    out = ['<INVENTORY>']
    for (pid, col), n in sorted(bom().items()):
        out.append('<ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>%s</ITEMID><COLOR>%d</COLOR><MINQTY>%d</MINQTY></ITEM>'
                   % (BL_ID.get(pid, pid), COLORS[col][2], n))
    out.append('</INVENTORY>')
    open(path, 'w').write('\n'.join(out))

# ------------------------------------------------------------------ viewer data
FACE = {3: 0, 1: 1, 0: 2, 2: 3}     # r -> face index (+x,-x,+z,-z)
PRIM = {'box': 0, 's45': 1, 's18': 2, 'inv': 3, 'dbl': 4}
def prims(p):
    pi = P(p['pid']); k = pi.kind
    x0, z0, h0, wx, wz, hp = p['x0'], p['z0'], p['h0'], p['wx'], p['wz'], p['hp']
    f = FACE[p['r'] % 4]
    if k in ('box', 'tile', 'grille', 'jumper'): return [(0, x0, h0, z0, wx, hp, wz, 0)]
    if k == 'round': return [(0, x0 + 0.08, h0, z0 + 0.08, wx - 0.16, hp, wz - 0.16, 0)]
    if k == 'bar': return [(0, x0 - 0.1, h0, z0 - 0.1, 0.2, hp, 0.2, 0)]
    if k == 'slope': return [(1, x0, h0, z0, wx, hp, wz, f)]
    if k == 'slope18': return [(2, x0, h0, z0, wx, hp, wz, f)]
    if k == 'inv': return [(3, x0, h0, z0, wx, hp, wz, f)]
    if k == 'dbl': return [(4, x0, h0, z0, wx, hp, wz, f)]
    if k == 'fence':
        out = [(0, x0, h0, z0, wx, 1, wz, 0)]
        along_x = wx > wz
        L = wx if along_x else wz
        for i in range(5):
            t = 0.35 + i * (L - 0.7) / 4
            if along_x: out.append((0, x0 + t - 0.12, h0 + 1, z0 + 0.38, 0.24, 4.4, 0.24, 0))
            else: out.append((0, x0 + 0.38, h0 + 1, z0 + t - 0.12, 0.24, 4.4, 0.24, 0))
        out.append((0, x0, h0 + 5.2, z0 + 0.3, wx, 0.8, 0.4, 0) if along_x else (0, x0 + 0.3, h0 + 5.2, z0, 0.4, 0.8, wz, 0))
        return out
    if k == 'doorframe':
        along_x = wx > wz
        if along_x:
            return [(0, x0, h0, z0, 0.35, hp, wz, 0), (0, x0 + wx - 0.35, h0, z0, 0.35, hp, wz, 0),
                    (0, x0, h0 + hp - 0.8, z0, wx, 0.8, wz, 0)]
        return [(0, x0, h0, z0, wx, hp, 0.35, 0), (0, x0, h0, z0 + wz - 0.35, wx, hp, 0.35, 0),
                (0, x0, h0 + hp - 0.8, z0, wx, 0.8, wz, 0)]
    if k == 'door':
        lo, hi = bbox(p['pid'] + '.dat')
        pts = np.array([[a, b, c] for a in (lo[0], hi[0]) for b in (max(lo[1], 0), hi[1]) for c in (lo[2], hi[2])]) @ p['R'].T + p['pos']
        X, Y, Z = pts[:, 0] / 20, -pts[:, 1] / 8, -pts[:, 2] / 20
        return [(0, X.min(), Y.min(), Z.min(), X.max() - X.min(), Y.max() - Y.min(), Z.max() - Z.min(), 0)]
    raise ValueError(k)

def viewer_data():
    pids = sorted({p['pid'] for p in m.parts}); pidx = {p: i for i, p in enumerate(pids)}
    cols = sorted({p['color'] for p in m.parts}); cidx = {c: i for i, c in enumerate(cols)}
    parts, pr, st = [], [], []
    r1 = lambda v: round(float(v), 2)
    for i, p in enumerate(m.parts):
        parts.append([pidx[p['pid']], cidx[p['color']], sidx[p['step']], module_of(p), 1 if p['sub'].endswith('_lid') else 0])
        for q in prims(p): pr.append([i, q[0]] + [r1(v) for v in q[1:7]] + [q[7]])
    # studs with the step at which they get covered (then hidden)
    bottoms = {}
    for j, p in enumerate(m.parts):
        pi = P(p['pid'])
        if pi.kind in ('door', 'inv', 'bar'): continue
        for x in range(int(np.floor(p['x0'] + 1e-6)), int(np.ceil(p['x0'] + p['wx'] - 1e-6))):
            for z in range(int(np.floor(p['z0'] + 1e-6)), int(np.ceil(p['z0'] + p['wz'] - 1e-6))):
                k = (x, z, p['h0']); s = sidx[p['step']]
                if pi.kind != 'door' and (k not in bottoms or s < bottoms[k][0]):
                    if not COLORS[p['color']][3]: bottoms[k] = (s, j)
    for i, p in enumerate(m.parts):
        if p['pid'] == '3811': continue      # baseplate studs drawn as a texture-free grid instead
        for (x, h, z) in p['studs']:
            cover = bottoms.get((int(np.floor(x)), int(np.floor(z)), h))
            cs = cover[0] if cover and cover[1] != i else 99999
            if cs <= sidx[p['step']]: continue
            st.append([i, round(x * 2), h, round(z * 2), cs])
    steps = []
    for s in order:
        S = STEPS[s]; steps.append([S['title'], S['order'][0], S['mult'], S['sub']])
    cat = [[pid, P(pid).name.replace('  ', ' '), BL_ID.get(pid, pid), P(pid).kind] for pid in pids]
    colors = [[c, COLORS[c][0], COLORS[c][1], 1 if COLORS[c][3] else 0, COLORS[c][2]] for c in cols]
    return dict(parts=parts, prims=pr, studs=st, steps=steps, cat=cat, colors=colors,
                sections=SECTIONS, modules=[list(x) for x in MODULES])

if __name__ == '__main__':
    import os
    os.makedirs('out', exist_ok=True)
    write_mpd('out/st_andrews_nave.mpd'); write_bl('out/st_andrews_bricklink.xml')
    d = viewer_data()
    s = json.dumps(d, separators=(',', ':'))
    open('out/data.json', 'w').write(s)
    print('steps', len(d['steps']), 'parts', len(d['parts']), 'prims', len(d['prims']), 'studs', len(d['studs']), 'json KB', len(s) // 1024)
    print('unique part/colour lots', len(bom()))
