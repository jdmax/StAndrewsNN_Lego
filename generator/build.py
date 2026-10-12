"""St. Andrew's Episcopal, Newport News - minifig-scale nave, generated on a stud grid.

Grid: x across (-30..30), z along (-58 rear .. 47 front), h in plates. Baseplates 64 x 128.
Massing model -> studs at ~0.336 m/stud, 1 plate ~0.134 m.
"""
import hashlib
from core import *

# ------------------------------------------------------------------ layout constants
ZF, ZFI = 47, 46                             # front wall: outer / inner skin rows
ZR, ZRI = -58, -57                           # rear wall: outer / inner skin rows
ZRD = -56                                    # reredos lining
RIBS = [-52, -40, -28, -16, -4, 8, 20, 32, 44]   # rib columns (1 stud thick), 12 studs apart
WIN = [r + 5 for r in RIBS[:-1]]             # one window pair centred in each bay
POSTS_Z = RIBS
MODULES = [(ZR - 1, RIBS[0])] + [(a, b) for a, b in zip(RIBS, RIBS[1:])] + [(RIBS[-1], ZF + 2)]
MID_MODS = MODULES[2:-1]                     # identical lift-off modules
CHAPEL = range(41, 45)                       # chapel door in the right wall near the front corner
K = 41                                       # roof break (plates)
def layer_h(k): return K + 3 * (k - 1)        # bottom of steep-roof layer k
PEW_SEATS = [-20 + 3 * i for i in range(17)]

def mosaic(*key):
    hsh = int(hashlib.md5(repr(key).encode()).hexdigest(), 16) % 20
    return TDB if hsh < 10 else TLB if hsh < 14 else TRED if hsh < 17 else TYEL
PANE = [None, TDB, TLB, TDB, TYEL, TDB, TRED]

def trans_or_brick(col):
    if col == TCLR: return {1: '3005', 2: '3065', 4: '3066', 6: '3067a'}
    if COLORS[col][3]: return {1: '3005', 2: '3065'}
    return BRICK1
def trans_or_plate(col):
    return {1: '3024', 2: '3023'} if COLORS[col][3] else PLATE1

BRICKS2D = {(8, 2): '3007', (6, 2): '2456', (4, 2): '3001', (3, 2): '3002', (2, 2): '3003', (2, 1): '3004', (1, 1): '3005',
            (8, 1): '3008', (6, 1): '3009', (4, 1): '3010', (3, 1): '3622'}
PLATES2D = {(8, 6): '3036', (6, 6): '3958', (8, 4): '3035', (6, 4): '3032', (4, 4): '3031', (10, 2): '3832', (12, 2): '2445',
            (8, 2): '3034', (6, 2): '3795', (4, 2): '3020', (3, 2): '3021', (2, 2): '3022',
            (8, 1): '3460', (6, 1): '3666', (4, 1): '3710', (3, 1): '3623', (2, 1): '3023', (1, 1): '3024'}
TILES2D = {(4, 2): '87079', (2, 2): '3068b', (8, 1): '4162', (6, 1): '6636', (4, 1): '2431', (3, 1): '63864',
           (2, 1): '3069b', (1, 1): '3070b'}

m = Model()
STEPS = {}   # id -> dict(order, title, sub, mult)
def step(order, title, sub='main', mult=1):
    sid = '%s|%s' % (order, title)
    STEPS[sid] = dict(order=order, title=title, sub=sub, mult=mult)
    m.step = sid; m.sub = sub
    return sid

def window_at(z):
    for wi, z0 in enumerate(WIN):
        if z0 <= z < z0 + 3: return wi, z - z0
    return None

# ------------------------------------------------------------------ wall cell colours
def front_feature(x, h):
    if not (-4 <= x < 4) or h < 32: return None
    if x in (-4, 3): return WHITE
    if x in (-3, 2): return mosaic('strip', x, h)
    if 77 <= h < 80: return WHITE
    if -1 <= x < 1 and 35 <= h < 89: return WHITE
    return TAN

def gable_color(side, skin, x, h, k=None):
    """|x| < 22 above the brick wall. side front/rear, skin outer/inner."""
    if side == 'front':
        # rake glass runs the full length of both roof edges, right up to the apex
        # rake glass follows the roof line from the apex, then carries on down the same slope
        # below the roof break until it meets the aisle glass
        kk = k if (k is not None and k >= 1) else ((h - K) // 3 + 1 if h >= 24 else None)
        if kk is not None:
            lim = 20 - kk
            if x in (lim - 1, lim - 2, lim - 3, -lim, -lim + 1, -lim + 2): return mosaic('rake', x, h)
        f = front_feature(x, h)
        if h >= 30 and h < 32 and -4 <= x < 4: return WHITE if skin == 'outer' else MN
        if f is not None:
            if skin == 'outer' or f in (TDB, TLB, TRED, TYEL): return f
            if x in (-4, 3): return MN            # no white frames inside, glass meets the wood
            return WHITE if f == WHITE else LBG   # grey panel with the white cross, as seen from the nave
        return SB if skin == 'outer' else MN
    else:
        rose = rose_cell(x, h)
        if skin == 'outer':
            return rose if rose else WHITE
        if rose or cross_hole(x, h): return None
        return WHITE

def rose_cell(x, h):
    if -2 <= x < 2 and 65 <= h < 71:
        return TYEL if (-1 <= x < 1) else TDB
    if -1 <= x < 1 and (62 <= h < 65 or 71 <= h < 74): return TRED
    return None
def cross_hole(x, h):
    if -1 <= x < 1 and (44 <= h < 59 or 77 <= h < 80): return True
    if x in (-5, -4, 3, 4) and 65 <= h < 71: return True
    return False

def clerestory(z, c):
    if z >= ZFI or z <= ZRI: return TCLR               # corners
    o = z % 4
    if o == 0: return WHITE                            # mullion
    if o == 2: return [TRED, TGRN, TDB, TYEL][(z // 4) % 4]   # diamond medallion
    return TLB if c == 9 else TCLR

def wall_color(skin, side, x, z, c):
    h = 3 * c
    if side in ('left', 'right'):
        chapel = side == 'right' and c <= 5            # chapel door near the front corner
        if c >= 8: return clerestory(z, c)
        if skin == 'outer':
            if chapel and z in CHAPEL: return None        # door frame
            w = window_at(z)
            if w and ZRI < z < ZFI:
                wi, o = w
                if c in (0, 7) or o == 1: return WHITE
                return PANE[c] if wi % 2 == 0 else [None, TDB, TDB, TLB, TDB, TRED, TDB][c]
            return TAN
        else:
            if chapel and z in CHAPEL: return None
            w = window_at(z)
            if w and 1 <= c <= 6 and ZRI < z < ZFI: return None
            return WHITE
    ax = abs(x + 0.5)
    if side == 'front':
        if skin == 'outer':
            if c < 8:
                if -4 <= x < 4 and c <= 5: return None              # door frames
                if x in (-5, 4) and c <= 5: return mosaic('side', x, c)
                return TAN
            if ax < 22: return gable_color('front', 'outer', x, h)
            if ax < 28: return mosaic('aisle', x, h, 'o')
            return TCLR
        else:
            if c < 8:
                if -5 <= x < 5 and c <= 5: return None
                if c == 7 and -28 <= x < 28: return None             # loft plate + 2 plates
                return WHITE
            if ax < 22: return gable_color('front', 'inner', x, h)
            if ax < 28: return mosaic('aisle', x, h, 'o')
            return TCLR
    else:  # rear
        if c < 8: return TAN if skin == 'outer' else WHITE
        if ax < 28: return WHITE
        return TCLR

def ring_course(c, which):
    h0 = 3 * c; even = c % 2 == 0
    for skin, (xr, xl, zf, zb) in (('outer', (29, -30, ZF, ZR)), ('inner', (28, -29, ZFI, ZRI))):
        side_z = range(zb, zf + 1) if even else range(zb + 1, zf)
        fr_x = range(xl + 1, xr) if even else range(xl, xr + 1)
        for side, x in (('right', xr), ('left', xl)):
            if side == which:
                lay_run(m, 'z', x, side_z.start, [wall_color(skin, side, x, z, c) for z in side_z], h0, trans_or_brick)
        for side, z in (('front', zf), ('rear', zb)):
            if side == which:
                lay_run(m, 'x', z, fr_x.start, [wall_color(skin, side, x, z, c) for x in fr_x], h0, trans_or_brick)

def door(x0, z, h0=0, color_frame=WHITE, color_door=RB, rf=2):
    i = m.place('60596', color_frame, x0, z, h0, r=rf)
    p = m.parts[i]['pos']; Rf = rotY(rf)
    m.place('60616a', color_door, 0, 0, 0, r=0, check=False, mark=False)
    m.parts[-1]['pos'] = p + Rf @ np.array([32, 0, 5]); m.parts[-1]['R'] = Rf @ rotY(2)

# ================================================================== 1 base & floor
step((1, 0), 'Baseplates', 'base')
for x0 in (-32, 0):
    for z0 in (-60, -28, 4, 36):
        m.place('3811', LBG, x0, z0, 0)

step((1, 1), 'Chancel platform: brick layer', 'base')
plat = {(x, z) for x in range(-20, 20) for z in range(ZRD, -26) if z not in RIBS or abs(x + 0.5) < 20}
amb = {(x, z) for s in (1, -1) for x in (range(22, 28) if s > 0 else range(-28, -22)) for z in range(ZRD, -30)}
pack_area(m, plat | amb, 0, BRICKS2D, prefer='x', colorfn=lambda x, z: LBG)
step((1, 2), 'Chancel platform: plate layer', 'base')
pack_area(m, plat | amb, 3, PLATES2D, prefer='z', colorfn=lambda x, z: LBG)
step((1, 3), 'Chancel and ambulatory steps', 'base')
steps_c = {(x, z) for x in range(-6, 6) for z in range(-26, -24)}
steps_a = {(x, -29) for x in list(range(22, 28)) + list(range(-28, -22))}
pack_area(m, steps_c | steps_a, 0, PLATES2D, prefer='x', colorfn=lambda x, z: LBG)
pack_area(m, steps_c | steps_a, 1, PLATES2D, prefer='z', colorfn=lambda x, z: LBG)
pack_area(m, steps_c | steps_a, 2, TILES2D, prefer='x', colorfn=lambda x, z: LBG)

# ================================================================== 2 interior furniture
step((2, 0), 'Pews: front half', 'interior')
def pew(s, xa, xb):
    lay_run(m, 'x', s, xa, [RB] * (xb - xa), 0, BRICK1)                   # seat
    lay_run(m, 'x', s + 1, xa, [RB] * (xb - xa), 0, BRICK1)               # back, two courses
    lay_run(m, 'x', s + 1, xa, [RB] * (xb - xa), 3, BRICK1)
    lay_run(m, 'x', s + 1, xa, [RB] * (xb - xa), 6, TILE1, hp=1)
for i, s in enumerate(PEW_SEATS):
    if i == 9: step((2, 1), 'Pews: back half', 'interior')
    pew(s, 3, 19); pew(s, -19, -3)

step((2, 2), 'Pulpit', 'interior')
pul = {(x, z) for x in range(-18, -14) for z in range(-26, -22)}
for c in range(3):
    pack_area(m, pul, 3 * c, {(4, 2): '3001', (2, 4): '3001', (2, 2): '3003'} if False else BRICKS2D,
              prefer='x' if c % 2 == 0 else 'z', colorfn=lambda x, z: RB)
for c in range(2):
    h = 9 + 3 * c
    lay_run(m, 'x', -23, -18, [RB] * 4, h, {2: '2877'})                                  # fluted front
    lay_run(m, 'z', -18, -26, [RB] * 3, h, BRICK1)
    lay_run(m, 'z', -15, -26, [RB] * 3, h, BRICK1)
lay_run(m, 'x', -23, -18, [RB] * 4, 15, TILE1, hp=1)
lay_run(m, 'z', -18, -26, [RB] * 3, 15, TILE1, hp=1)
lay_run(m, 'z', -15, -26, [RB] * 3, 15, TILE1, hp=1)

step((2, 3), 'Altar dais, altar and altar rail', 'interior')
dais = {(x, z) for x in range(-10, 10) for z in range(-55, -48)}
pack_area(m, dais, 4, PLATES2D, prefer='x', colorfn=lambda x, z: LBG)
pack_area(m, dais, 5, PLATES2D, prefer='z', colorfn=lambda x, z: LBG)
alt = {(x, z) for x in range(-3, 3) for z in range(-54, -51)}
pack_area(m, alt, 6, BRICKS2D, prefer='x', colorfn=lambda x, z: RB)
pack_area(m, alt, 9, BRICKS2D, prefer='z', colorfn=lambda x, z: RB)
pack_area(m, alt, 12, TILES2D, prefer='x', colorfn=lambda x, z: WHITE)
pack_area(m, dais - alt, 6, TILES2D, prefer='x', colorfn=lambda x, z: WHITE)
for x0 in (-9, -5, 1, 5):
    m.place('30055', RB, x0, -46, 4, r=0)

step((2, 4), 'Choir pews: three rows each side', 'interior')
ZS = -38                                         # choir pews run z -38..-31, facing the centre aisle
for sd in (1, -1):
    X = (lambda x: x) if sd > 0 else (lambda x: -x - 1)
    for h in (4, 7):                             # fluted front along the centre aisle
        lay_run(m, 'z', X(7), ZS, [RB] * 8, h, {2: '2877'})
    lay_run(m, 'z', X(7), ZS, [RB] * 8, 10, TILE1, hp=1)
    for seat in (9, 12, 15):
        lay_run(m, 'z', X(seat), ZS, [RB] * 8, 4, BRICK1)
        for h in (4, 7):
            lay_run(m, 'z', X(seat + 1), ZS, [RB] * 8, h, BRICK1)
        lay_run(m, 'z', X(seat + 1), ZS, [RB] * 8, 10, TILE1, hp=1)
for h in (4, 7):                                 # fluted parapets across the front of the choir
    lay_run(m, 'x', -27, 7, [RB] * 6, h, {2: '2877'})
    m.place('3005', RB, 13, -27, h)
    lay_run(m, 'x', -27, -19, [RB] * 12, h, {2: '2877'})
lay_run(m, 'x', -27, 7, [RB] * 7, 10, TILE1, hp=1)
lay_run(m, 'x', -27, -19, [RB] * 12, 10, TILE1, hp=1)

step((2, 6), 'Organ console', 'interior')
org = {(x, z) for x in range(-19, -14) for z in range(-44, -40)}
for c in range(2):
    pack_area(m, org, 4 + 3 * c, BRICKS2D, prefer='x' if c % 2 == 0 else 'z', colorfn=lambda x, z: RB)
lay_run(m, 'x', -41, -19, [WHITE] * 5, 10, TILE1, hp=1)              # lower manual, nearest the bench
lay_run(m, 'x', -42, -19, [BLACK] * 5, 10, TILE1, hp=1)              # upper manual
for zr in (-43, -44):                                                 # music desk / case behind the keys
    lay_run(m, 'x', zr, -19, [RB] * 5, 10, BRICK1)
for x0 in (-18, -16):                                                  # bench
    m.place('3005', RB, x0, -39, 4)
m.place('3710', RB, -18, -39, 7, r=0)

step((2, 5), 'Lectern', 'interior')
lec = {(x, z) for x in range(14, 18) for z in range(-29, -26)}
for c in range(3):
    pack_area(m, lec, 4 + 3 * c, BRICKS2D, prefer='x' if c % 2 == 0 else 'z', colorfn=lambda x, z: RB)
m.place('3039', RB, 15, -28, 13, r=FACE_R['-z'])

# ================================================================== 3 walls, course by course
for c in range(10):
    h0 = 3 * c
    step((3, c * 5 + 0), 'Course %d: front wall' % (c + 1), 'walls')
    if c == 0:
        door(-4, ZF); door(0, ZF)
    ring_course(c, 'front')
    step((3, c * 5 + 1), 'Course %d: rear wall' % (c + 1), 'walls')
    ring_course(c, 'rear')
    step((3, c * 5 + 2), 'Course %d: left wall' % (c + 1), 'walls')
    ring_course(c, 'left')
    step((3, c * 5 + 3), 'Course %d: right wall' % (c + 1), 'walls')
    if c == 0: door(29, CHAPEL[0], rf=1, color_door=WHITE)      # chapel door, opening outward
    ring_course(c, 'right')
    step((3, c * 5 + 4), 'Course %d: posts and inner walls' % (c + 1), 'walls')
    for z in POSTS_Z:                                   # posts run up to the aisle ceiling (no beam in the nave)
        if c < 9 or z >= -28:
            for x0 in (20, -22):
                m.place('3004', RB, x0, z, h0, r=0)
    if c < 9:
        for x0 in (20, -22):                                   # chancel side walls (white, 2 wide)
            lay_run(m, 'z', ('chw', x0), ZRD, [None if z in RIBS else WHITE for z in range(ZRD, -28)], h0, BRICK2, width_axis_min=x0)
    # cross walls at the end of each aisle, doors into the ambulatory
    for sd in (1, -1):
        xs = list(range(22, 28)) if sd > 0 else list(range(-28, -22))
        def cw(x):
            lx = x if sd > 0 else -x - 1
            if c <= 5: return None if 23 <= lx < 27 else WHITE
            if c == 6 and 24 <= lx < 26: return GREEN
            return WHITE
        if c == 0: door(23 if sd > 0 else -27, -28)
        lay_run(m, 'x', -28, xs[0], [cw(x) for x in xs], h0, BRICK1)
    # narthex wall
    if c < 7:
        def nw(x):
            if c <= 5 and -3 <= x < 3: return None
            if c <= 5 and x in (-4, 3): return RB
            if c <= 5 and -27 <= x < -23: return None
            if c == 6 and -4 <= x < 4: return RB
            return WHITE
        if c == 0: door(-27, 33)
        lay_run(m, 'x', 33, -28, [nw(x) for x in range(-28, 28)], h0, BRICK1)

# ================================================================== 4 loft, beams, slab
step((4, 0), 'Choir loft floor', 'loft')
loft = {(x, z) for x in range(-28, 28) for z in range(33, ZFI + 1) if m.free(x, z, 21)}
LOFT1 = {(12, 2): '2445', (10, 2): '3832', (8, 2): '3034', (6, 2): '3795', (4, 2): '3020', (2, 2): '3022', (2, 1): '3023', (1, 1): '3024'}
pack_area(m, loft, 21, LOFT1, prefer='z', colorfn=lambda x, z: MN)
pack_area(m, loft, 22, PLATES2D, prefer='x', colorfn=lambda x, z: MN)
lay_run(m, 'x', ZFI, -28, [WHITE] * 56, 23, PLATE1, hp=1)
step((4, 1), 'Choir loft railing', 'loft')
for x0 in list(range(-20, 20, 4)) + [23, -27]:
    m.place('30055', RB, x0, 33, 23, r=0)
step((4, 2), 'Arcade beams', 'loft')
for x0 in (20, -22):
    lay_run(m, 'z', ('beam', x0), ZRD, [None if z in RIBS else WHITE for z in range(ZRD, -28)], 27, BRICK2, width_axis_min=x0)   # chancel walls only
step((4, 3), 'Aisle ceilings (lower plate layer)', 'loft')
def slab_cells():
    out = set()
    for sd in (1, -1):
        for xx in range(20, 32):
            x = xx if sd > 0 else -xx - 1
            # under the rib line only at the ribs (post caps) and over the chancel walls
            zr = range(ZR, ZF + 1) if xx >= 22 else [z for z in range(ZRD, ZFI) if z in RIBS or z < -28]
            for z in zr: out.add((x, z))
    return out
def slab_col(x, z):
    if z == ZF and abs(x + 0.5) < 30: return mosaic('slab', x, z)
    if abs(x + 0.5) < 22: return RB                                  # post caps   # glass carries on up to the aisle roof
    return WHITE if z == ZR and abs(x + 0.5) < 30 else MN
sc = slab_cells()
pack_area(m, sc, 30, PLATES2D, prefer='x', colorfn=slab_col)
step((4, 4), 'Aisle ceilings (upper plate layer)', 'loft')
pack_area(m, sc, 31, PLATES2D, prefer='z', colorfn=slab_col)

# ================================================================== 5 ribs
step((5, 0), 'Glulam ribs', 'ribs')
def rib(z):
    """Right half: slope stair standing just clear of the lift-off roof.
    Left half: solid from the inverted-slope underside up to the roof surface, so the fixed
    roof slopes clutch straight onto it."""
    for k in range(-2, 19):                       # right half (and lower part of the left)
        m.place('3040b', RB, 18 - k, z, layer_h(k), r=FACE_R['+x'])
        if k <= 16: m.place('3665a', RB, 16 - k, z, layer_h(k), r=FACE_R['-x'])
        if k <= 0:
            m.place('3040b', RB, -(20 - k), z, layer_h(k), r=FACE_R['-x'])
            m.place('3665a', RB, -(18 - k), z, layer_h(k), r=FACE_R['+x'])
    for k in range(1, 21):                        # left half, solid to the roof
        a, b = -(22 - k), min(-(18 - k), 0)
        if k == 19: b = -1                        # leave room for the rib's ridge cap
        cols = [RB] * (b - a)
        for i, L, col in dp_partition(cols, set(BRICK1.keys())):
            m.place(BRICK1[L], RB, a + i, z, layer_h(k), r=0)
        if k <= 16: m.place('3665a', RB, -(18 - k), z, layer_h(k), r=FACE_R['+x'])
    m.place('3004', RB, -1, z, layer_h(17), r=0)
    m.place('3044b', RB, -1, z, layer_h(19), r=1)
for z in RIBS: rib(z)

# ================================================================== 6 knee walls + aisle roofs
for ci, h in enumerate((32, 35, 38)):
    step((6, ci), 'Knee walls and aisle roof, layer %d' % (ci + 1), 'aisles')
    for sd in (1, -1):
        xa, xb = (20, 21) if sd > 0 else (-21, -22)
        xmin = 20 if sd > 0 else -22
        for x in (xa, xb):                               # rib outer corner only; open between ribs
            outer = x in (21, -22)
            single = [(RB if z in RIBS else MN) if (m.free(x, z, h) and (z in RIBS or (outer and h == 38))) else None
                      for z in range(ZRD, ZFI)]
            lay_run(m, 'z', x, ZRD, single, h, BRICK1)
        # aisle roof stair: one course of 18-degree slopes plus fill behind it
        lo, hi = [(28, 32), (25, 29), (22, 26)][ci]
        x0 = lo if sd > 0 else -hi
        lay_run(m, 'z', ('a18', sd), ZR, [DBG] * (ZF + 2 - ZR), h, SLOPE18, width_axis_min=x0, face='+x' if sd > 0 else '-x', forbid={ZF + 1})
        fill = range(22, lo) if sd > 0 else range(-lo, -22)
        for x in fill:
            def fc(z):
                if z in (ZFI, ZF): return mosaic('afill', x, z, h)
                if z in (ZR, ZRI): return WHITE
                return MN if abs(x + 0.5) < 23 else LBG     # wood face seen behind the ribs
            lay_run(m, 'z', x, ZR, [fc(z) for z in range(ZR, ZF + 1)], h, trans_or_brick)

# ================================================================== 7 gables (front, rear + reredos)
def gable_band(side, h, hp, xs, k=None, table=None):
    zo, zi = (ZF, ZFI) if side == 'front' else (ZR, ZRI)
    for skin, z in (('outer', zo), ('inner', zi)):
        cols = [gable_color(side, skin, x, h, k) for x in xs]
        cols = [c if (c is None or m.free(x, z, h)) else None for x, c in zip(xs, cols)]
        lay_run(m, 'x', z, xs[0], cols, h, table or (trans_or_plate if hp == 1 else trans_or_brick), hp=hp)

def reredos(h, hp, xs):
    def col(x):
        if h < 11: return LBG
        if -5 <= x < 5: return None
        return WHITE
    cols = [col(x) if m.free(x, ZRD, h) else None for x in xs]
    lay_run(m, 'x', ZRD, xs[0], cols, h, PLATE1 if hp == 1 else BRICK1, hp=hp)

step((7, 0), 'Reredos wainscot', 'gables')
reredos(4, 1, list(range(-20, 20)))
reredos(5, 3, list(range(-20, 20)))
reredos(8, 3, list(range(-20, 20)))
step((7, 1), 'Gables: eave band', 'gables')
for side in ('front', 'rear'):
    gable_band(side, 30, 1, list(range(-22, 22)))
    gable_band(side, 31, 1, list(range(-22, 22)))
hs = list(range(11, 41, 3))      # reredos courses below the roof break
gh = [32, 35, 38] + [layer_h(k) for k in range(1, 20)]
groups = [gh[0:3]] + [gh[i:i + 3] for i in range(3, len(gh), 3)]
for gi, grp in enumerate(groups):
    step((7, 2 + gi), 'Gables: courses %d-%d plates up' % (grp[0], grp[-1] + 3), 'gables')
    for rh in [h for h in hs if grp[0] - 21 <= h < grp[-1] + 3] if gi == 0 else []:
        reredos(rh, 3, list(range(-20, 20)))
    for h in grp:
        if h < K:
            xs = list(range(-22, 22)); k = None
        else:
            k = (h - K) // 3 + 1; lim = 20 - k
            xs = list(range(-lim, lim))
        for side in ('front', 'rear'):
            gable_band(side, h, 3, xs, k)
        if h >= K:
            reredos(h, 3, [x for x in xs if -20 <= x < 20])

# ================================================================== 8 porch
step((8, 0), 'Porch piers', 'porch')
for c in range(7):
    for x0 in (-7, 5):
        m.place('3003', TAN, x0, ZF + 1, 3 * c)
step((8, 1), 'Porch canopy', 'porch')
canopy = {(x, z) for x in range(-7, 7) for z in range(ZF + 1, ZF + 8)}
pack_area(m, canopy, 21, PLATES2D, prefer='x', colorfn=lambda x, z: WHITE)
pack_area(m, canopy, 22, PLATES2D, prefer='z', colorfn=lambda x, z: WHITE)
lay_run(m, 'z', ('pc', -1), ZF + 1, [DBG] * 7, 23, SLOPE18, width_axis_min=-7, face='-x')
lay_run(m, 'z', ('pc', 1), ZF + 1, [DBG] * 7, 23, SLOPE18, width_axis_min=3, face='+x')
for x in range(-3, 3):
    lay_run(m, 'z', x, ZF + 1, [WHITE] * 7, 23, BRICK1)
lay_run(m, 'z', ('pc2', -1), ZF + 1, [DBG] * 7, 26, SLOPE18, width_axis_min=-4, face='-x')
lay_run(m, 'z', ('pc2', 1), ZF + 1, [DBG] * 7, 26, SLOPE18, width_axis_min=0, face='+x')
pack_area(m, {(x, z) for x in (-1, 0) for z in range(ZF + 1, ZF + 8)}, 29, TILES2D, prefer='z', colorfn=lambda x, z: DBG)

# ================================================================== 9 roof modules
LANTERN_LAYERS = (9,)                     # ceiling layer the lanterns hang from, about midway up the slope
def module(z0, z1, name, order, organ=False, cross=False, mult=1, title=None, split=False):
    """split: left half stays as part of the fixed roof; the right half (+ centre, top course
    and ridge) is a lid that lifts straight off. Nothing fixed sits on top of the lid."""
    n = z1 - z0
    def ic(z, k):
        return BLACK if organ and 3 <= k <= 11 and z0 + 3 <= z < z1 - 3 else MN
    def reg(k, sd):
        x0 = 22 - k if sd > 0 else -(24 - k)
        lay_run(m, 'z', ('roof', name, sd), z0, [DBG] * n, layer_h(k), SLOPE45,
                width_axis_min=x0, face='+x' if sd > 0 else '-x')
    def inv(k, sd):
        x0 = 20 - k if sd > 0 else -(22 - k)
        hook = split and not organ and sd < 0 and k in LANTERN_LAYERS
        cols = [None if (sd < 0 and z in RIBS) or (hook and z == z0 + 6) else ic(z, k) for z in range(z0, z1)]
        if hook:     # a plain brick here gives the ceiling a flat spot with an anti-stud to hang a lantern from
            m.place('3004', MN, k - 22, z0 + 6, layer_h(k), r=0)
        lay_run(m, 'z', ('roof', name, sd), z0, cols, layer_h(k), INV45,
                width_axis_min=x0, face='-x' if sd > 0 else '+x')
    def top(k):
        if k == 21: lay_run(m, 'z', ('ctr', name), z0, [MN] * n, layer_h(k), BRICK2, width_axis_min=-1)
        if k == 23:
            zz = z1 - 1 if cross else z1
            lay_run_ridge(z0, [DBG] * (zz - z0), layer_h(k), name)
    groups = [(1, 3), (4, 6), (7, 9), (10, 12), (13, 15), (16, 18), (19, 21), (22, 23)]
    if not split:
        for gi, (ka, kb) in enumerate(groups):
            step((9, order, gi), '%s: layers %d-%d' % (title or name, ka, kb), name, mult)
            for k in range(ka, kb + 1):
                for sd in (1, -1):
                    if k <= 22: reg(k, sd)
                    if k <= 20: inv(k, sd)
                top(k)
    else:
        for gi, (ka, kb) in enumerate(groups[:-1]):
            step((9, order, gi), '%s, fixed left side: layers %d-%d' % (title or name, ka, kb), name, mult)
            for k in range(ka, kb + 1):
                reg(k, -1)
                if k <= 20: inv(k, -1)
        for gi, (ka, kb) in enumerate(groups):
            step((9, order, 10 + gi), '%s, lift-off right side: layers %d-%d' % (title or name, ka, kb), name + '_lid', mult)
            for k in range(ka, kb + 1):
                if k <= 22: reg(k, 1)
                if k <= 20: inv(k, 1)
                if k == 22: reg(k, -1)
                top(k)
    if cross:
        step((9, order, 9), 'Cross on the front gable', name, 1)
        hc = layer_h(23)
        m.place('15573', WHITE, -1, z1 - 1, hc, r=0)
        m.place('3005', WHITE, -0.5, z1 - 1, hc + 1, check=False)
        m.place('3005', WHITE, -0.5, z1 - 1, hc + 4, check=False)
        m.place('3623', WHITE, -1.5, z1 - 1, hc + 7, r=0, check=False)
        m.place('3005', WHITE, -0.5, z1 - 1, hc + 8, check=False)
        m.place('3070b', WHITE, -0.5, z1 - 1, hc + 11, check=False)

def lay_run_ridge(z0, cols, h, name):
    # double slopes, ridge along z (r=1)
    pieces = dp_partition(cols, set(RIDGE.keys()), frozenset(m.seams.get(('z', ('ctr', name), h), set())))
    for i, L, col in pieces:
        m.place(RIDGE[L], col, -1, z0 + i, h, r=1)

module(*MODULES[0], 'roof_rear', 0, title='Rear roof module (behind the reredos rib)')
module(*MODULES[1], 'roof_organ', 1, organ=True, split=True, title='Roof bay over the altar, with organ grilles')
mid0 = len(m.parts)
module(*MID_MODS[0], 'roof_mid', 2, mult=len(MID_MODS), split=True, title='Middle roof bay (build %d)' % len(MID_MODS))
mid1 = len(m.parts)
for bi, (z0, z1) in enumerate(MID_MODS[1:]):     # copy the middle module to the other bays
    dz = z0 - MID_MODS[0][0]
    for p in m.parts[mid0:mid1]:
        m.step = p['step']; m.sub = p['sub']
        i = m.place(p['pid'], p['color'], p['x0'], p['z0'] + dz, p['h0'], p['r'])
        m.parts[i]['copy_of'] = bi + 1
module(*MODULES[-1], 'roof_front', 3, cross=True, title='Front roof module with the cross')

# ================================================================== lanterns
step((9, 5, 0), 'Hang the lanterns from the fixed ceiling', 'roof_lanterns')
LANTERN_BAYS = [r + 6 for r in RIBS[2:-1]]          # the five nave bays and the narthex bay; none over the chancel
def lantern(x, z, ceil, double):
    """Round-plate anchor clutched into the ceiling's inverted slope, black bar(s), lantern of
    two white round bricks between pearl-gold caps."""
    h = ceil - 1
    a = m.place('6141', GOLD, x, z, h)
    chain = [a]
    for i in range(2 if double else 1):
        h -= 10; chain.append(m.place('30374', BLACK, x + 0.5, z + 0.5, h))
        if double and i == 0:
            h -= 1; chain.append(m.place('85861', BLACK, x, z, h))      # slim joiner between the two rods
    h -= 1; top = m.place('85861', GOLD, x, z, h)
    for _ in range(2):
        h -= 3; m.place('3062b', WHITE, x, z, h)
    h -= 1; m.place('6141', GOLD, x, z, h)
    for i in range(len(chain) - 1): m.parts[chain[i + 1]]['link'] = chain[i]
    m.parts[top]['link'] = chain[-1]
for z in LANTERN_BAYS:
    for j in LANTERN_LAYERS:
        lantern(j - 21, z, layer_h(j), True)     # one per bay, on a long two-part rod

# ================================================================== floor tiles (shown early)
step((1, 4), 'Floor tiles', 'base')
tiles = set()
for x in range(-28, 28):
    for z in range(ZRD, ZFI):
        if m.free(x, z, 0): tiles.add((x, z))
porch_t = {(x, z) for x in range(-7, 7) for z in range(ZF + 1, ZF + 8) if m.free(x, z, 0)}
def tcol(x, z):
    if -3 <= x < 3 and -24 <= z < 33: return DBG
    return LBG
pack_area(m, tiles | porch_t, 0, TILES2D, prefer='z', colorfn=tcol)
step((1, 5), 'Platform tiles', 'base')
pt = {(x, z) for (x, z) in (plat | amb) if m.free(x, z, 4)}
pack_area(m, pt, 4, TILES2D, prefer='x', colorfn=lambda x, z: LBG)

if __name__ == '__main__':
    print('parts', len(m.parts), 'collisions', len(m.collisions))
    for c in m.collisions[:20]: print(c)
