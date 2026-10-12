"""Core: part catalogue, placement on a stud grid, LDraw output, packers.

World frame (same as the massing model): x across the nave (studs, + = right seen from the
entrance looking at the altar is -x... we simply keep the massing model's axes), z along the
nave (+z = front/entrance), h = height in plates above the baseplate top.
LDraw: X = 20*x, Y = -8*h, Z = -20*z   (proper rotation: flips Y and Z).
"""
import numpy as np, math
from ldlib import geom, title, bbox

# ---------------------------------------------------------------- colours
COLORS = {  # ldraw code: (name, viewer hex, bricklink id, transparent)
    0: ('Black', '#1b2a34', 11, False),
    2: ('Green', '#237841', 6, False),
    15: ('White', '#f4f4f4', 1, False),
    19: ('Tan', '#e4cd9e', 2, False),
    70: ('Reddish Brown', '#582a12', 88, False),
    71: ('Light Bluish Gray', '#a0a5a9', 86, False),
    72: ('Dark Bluish Gray', '#6c6e68', 85, False),
    84: ('Medium Nougat', '#aa7d55', 150, False),
    379: ('Sand Blue', '#6074a1', 55, False),
    33: ('Trans-Dark Blue', '#0a3bb5', 14, True),
    36: ('Trans-Red', '#c91a09', 17, True),
    43: ('Trans-Light Blue', '#aee9ef', 15, True),
    46: ('Trans-Yellow', '#f5cd2f', 19, True),
    47: ('Trans-Clear', '#e8f2f4', 12, True),
    297: ('Pearl Gold', '#aa7f2e', 115, False),
    34: ('Trans-Green', '#5fa86c', 20, True),
}
WHITE, TAN, RB, LBG, DBG, MN, SB, BLACK, GREEN, GOLD = 15, 19, 70, 71, 72, 84, 379, 0, 2, 297
TDB, TRED, TLB, TYEL, TCLR, TGRN = 33, 36, 43, 46, 47, 34

# ---------------------------------------------------------------- parts
# kind: box | tile | slope | slope18 | inv | dbl | fence | grille | jumper | doorframe | door
KINDS = {}
def _k(kind, *ids):
    for i in ids: KINDS[i] = kind
_k('box', '3005', '3004', '3622', '3010', '3009', '3008', '6111', '6112', '3003', '3002', '3001', '2456', '3007', '3006',
   '3065', '3066', '3067a', '3062b',
   '3024', '3023', '3623', '3710', '3666', '3460', '4477', '60479', '3022', '3021', '3020', '3795', '3034', '3832', '2445',
   '4282', '3031', '3032', '3035', '3030', '3029', '3958', '3036', '3033', '3028', '3027', '3811')
_k('tile', '3070b', '3069b', '63864', '2431', '6636', '4162', '3068b', '87079')
_k('slope', '3040b', '3039', '3037')
_k('slope18', '30363', '60477')
_k('inv', '3665a', '3660a')
_k('dbl', '3044b', '3043', '3041')
_k('fence', '30055'); _k('grille', '2877'); _k('jumper', '15573')
_k('doorframe', '60596'); _k('door', '60616a')
_k('round', '6141', '85861'); _k('bar', '30374', '87994')

BL_ID = {'6141': '4073', '3040b': '3040', '3665a': '3665', '3660a': '3660', '3044b': '3044', '3067a': '3067'}

class PartInfo:
    def __init__(s, pid):
        s.id = pid; s.kind = KINDS[pid]; s.name = title(pid + '.dat')
        lo, hi = bbox(pid + '.dat')
        snap = lambda v: round(v / 10) * 10
        if s.kind == 'door':
            s.lx0, s.lx1, s.lz0, s.lz1, s.hp = 0, 0, 0, 0, 0   # lives inside its frame
        else:
            s.lx0, s.lx1, s.lz0, s.lz1 = snap(lo[0]), snap(hi[0]), snap(lo[2]), snap(hi[2])
            s.hp = int(round(hi[1] / 8))
        _, studs = geom(pid + '.dat')
        top = ('stud.dat', 'stud2.dat', 'stud2a.dat', 'stud6.dat', 'stud6a.dat', 'stud10.dat', 'stud15.dat')
        s.studs = sorted({(float(p[0]), float(p[2])) for b, p, d in studs if b in top and p[1] <= 4.5})
        if s.kind in ('tile', 'dbl', 'door', 'bar'): s.studs = []
_PI = {}
def P(pid):
    if pid not in _PI: _PI[pid] = PartInfo(pid)
    return _PI[pid]

def rotY(r):
    c, s = [(1, 0), (0, 1), (-1, 0), (0, -1)][r % 4]
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)
FACE_R = {'+z': 0, '-x': 1, '-z': 2, '+x': 3}       # slope descent direction -> rotation
AXIS_R = {'x': 0, 'z': 1}                           # long axis of a plain part -> rotation

# ---------------------------------------------------------------- model
class Model:
    def __init__(s):
        s.parts = []          # dicts
        s.occ = {}            # (x,z,h) -> part index
        s.seams = {}          # (axis, fixed, htop) -> set of boundaries
        s.step = 'unset'; s.sub = 'main'
        s.collisions = []

    def place(s, pid, color, x0, z0, h0, r=0, check=True, mark=True, note=None):
        """Place part with its world footprint min corner at (x0, z0), bottom at h0 (plates)."""
        pi = P(pid); R = rotY(r)
        cs = np.array([[pi.lx0, 0, pi.lz0], [pi.lx1, 0, pi.lz0], [pi.lx0, 0, pi.lz1], [pi.lx1, 0, pi.lz1]]) @ R.T
        X0, X1, Z0, Z1 = cs[:, 0].min(), cs[:, 0].max(), cs[:, 2].min(), cs[:, 2].max()
        ox, oz = x0 - X0 / 20, z0 + Z1 / 20
        wx, wz = (X1 - X0) / 20, (Z1 - Z0) / 20
        pos = np.array([20 * ox, -8 * (h0 + pi.hp), -20 * oz])
        idx = len(s.parts)
        cells = []
        if mark and pi.hp:
            for x in range(math.floor(x0 + 1e-6), math.ceil(x0 + wx - 1e-6)):
                for z in range(math.floor(z0 + 1e-6), math.ceil(z0 + wz - 1e-6)):
                    for h in range(h0, h0 + pi.hp):
                        c = (x, z, h)
                        if c in s.occ and check:
                            s.collisions.append((pid, c, s.parts[s.occ[c]]['pid'], s.step))
                        s.occ[c] = idx; cells.append(c)
        # world studs (for viewer)
        studs = []
        for sx, sz in pi.studs:
            p = R @ np.array([sx, 0, sz]) + pos
            studs.append((p[0] / 20, h0 + pi.hp, -p[2] / 20))
        s.parts.append(dict(pid=pid, color=color, pos=pos, R=R, r=r, step=s.step, sub=s.sub,
                            x0=x0, z0=z0, h0=h0, wx=wx, wz=wz, hp=pi.hp, studs=studs, note=note))
        return idx

    def free(s, x, z, h): return (x, z, h) not in s.occ

    def ldraw_line(s, p):
        R = p['R']; x, y, z = p['pos']
        f = lambda v: ('%.3f' % v).rstrip('0').rstrip('.') if abs(v - round(v)) > 1e-6 else str(int(round(v)))
        m = ' '.join(f(v) for v in R.flatten())
        return f"1 {p['color']} {f(x)} {f(y)} {f(z)} {m} {p['pid']}.dat"

# ---------------------------------------------------------------- 1-D run packer
BRICK1 = {1: '3005', 2: '3004', 3: '3622', 4: '3010', 6: '3009', 8: '3008'}
TRANS1 = {1: '3005', 2: '3065', 3: '3622', 4: '3066', 6: '3067a'}
PLATE1 = {1: '3024', 2: '3023', 3: '3623', 4: '3710', 6: '3666', 8: '3460'}
TILE1 = {1: '3070b', 2: '3069b', 3: '63864', 4: '2431', 6: '6636', 8: '4162'}
BRICK2 = {1: '3004', 2: '3003', 3: '3002', 4: '3001', 6: '2456', 8: '3007'}   # 2 wide across the run
PLATE2 = {1: '3023', 2: '3022', 3: '3021', 4: '3020', 6: '3795', 8: '3034', 10: '3832', 12: '2445'}
SLOPE45 = {1: '3040b', 2: '3039', 4: '3037'}
INV45 = {1: '3665a', 2: '3660a'}
SLOPE18 = {1: '60477', 2: '30363'}
RIDGE = {1: '3044b', 2: '3043', 4: '3041'}

def dp_partition(colors, sizes, joints_below=frozenset(), forbid=frozenset()):
    """Partition cells 0..n-1 into same-colour pieces of allowed lengths.
    sizes: dict color-> set of allowed lengths (or one set for all). Penalise joints that line
    up with joints in the course below (stagger) and lots of small pieces."""
    n = len(colors); INF = 1e9
    dp = [INF] * (n + 1); prev = [None] * (n + 1); dp[0] = 0
    for i in range(n):
        if dp[i] >= INF: continue
        allowed = sizes(colors[i]) if callable(sizes) else sizes
        for L in sorted(allowed, reverse=True):
            j = i + L
            if j > n or any(colors[k] != colors[i] for k in range(i, j)): continue
            cost = 1.0 + (0.6 if L == 1 else 0)
            if 0 < j < n and j in joints_below: cost += 3.0
            if 0 < j < n and j in forbid: cost += 50.0
            if dp[i] + cost < dp[j]: dp[j] = dp[i] + cost; prev[j] = i
    if dp[n] >= INF: raise ValueError('cannot partition run %r' % (colors,))
    out = []; j = n
    while j:
        i = prev[j]; out.append((i, j - i, colors[i])); j = i
    return out[::-1]

def split_runs(cells):
    """cells: list of (coord, color|None) in order -> contiguous non-None runs"""
    runs, cur = [], []
    for c, col in cells:
        if col is None:
            if cur: runs.append(cur); cur = []
        else: cur.append((c, col))
    if cur: runs.append(cur)
    return runs

def lay_run(m, axis, fixed, a0, colors, h0, table, hp=3, width_axis_min=None, kind='brick', face=None, forbid=()):
    """Lay a straight run of 1-wide (or table-defined) pieces along `axis` starting at a0.
    colors: list (None = gap). table: dict length->pid (or callable(color)->dict).
    width_axis_min: the min coordinate across the run (default fixed)."""
    cells = [(a0 + i, c) for i, c in enumerate(colors)]
    key_below = (axis, fixed, h0)
    jb_abs = m.seams.get(key_below, set())
    for run in split_runs(cells):
        start = run[0][0]; cols = [c for _, c in run]
        tab = (lambda col: table(col)) if callable(table) else (lambda col: table)
        jb = {j - start for j in jb_abs}
        fb = {j - start for j in forbid}
        pieces = dp_partition(cols, lambda col: set(tab(col).keys()), frozenset(jb), frozenset(fb))
        for i, L, col in pieces:
            pid = tab(col)[L]
            a = start + i
            wmin = fixed if width_axis_min is None else width_axis_min
            if face is not None:
                r = FACE_R[face]
            else:
                pi = P(pid); ex, ez = (pi.lx1 - pi.lx0) / 20, (pi.lz1 - pi.lz0) / 20
                if axis == 'x': r = 0 if ex == L else 1
                else: r = 0 if ez == L else 1
            if axis == 'x': m.place(pid, col, a, wmin, h0, r)
            else: m.place(pid, col, wmin, a, h0, r)
            m.seams.setdefault((axis, fixed, h0 + hp), set()).update({a, a + L})

# ---------------------------------------------------------------- 2-D area packer
def pack_area(m, cells, h0, sizes, prefer='x', hp=1, colorfn=None):
    """Greedy rectangle packing. cells: set of (x,z). sizes: dict (w,d)->pid with w along x, d along z
    in the part's r=0 orientation (local X -> world x). prefer: which axis to scan first."""
    cells = set(cells); done = set()
    rects = []
    for (w, d), pid in sizes.items():
        rects.append((w, d, pid, 0))
        if w != d: rects.append((d, w, pid, 1))
    rects.sort(key=lambda t: (-(t[0] * t[1]), (t[0] < t[1]) if prefer == 'x' else (t[0] > t[1])))
    order = sorted(cells, key=(lambda c: (c[1], c[0])) if prefer == 'x' else (lambda c: (c[0], c[1])))
    col = colorfn or (lambda x, z: None)
    for (x, z) in order:
        if (x, z) in done: continue
        c0 = col(x, z)
        for w, d, pid, r in rects:
            if COLORS[c0][3] and w * d > 2: continue        # transparent parts: 1x1 and 1x2 only
            fp = [(x + i, z + j) for i in range(w) for j in range(d)]
            if all(c in cells and c not in done and col(*c) == c0 for c in fp):
                m.place(pid, c0, x, z, h0, r); done.update(fp); break
        else:
            raise ValueError('pack_area stuck at %r' % ((x, z),))
