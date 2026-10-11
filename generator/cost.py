"""Rough BrickLink-style cost bands per piece (USD). Not live prices."""
from export import bom
from core import P, COLORS, BL_ID
SCARCE = {84, 379}     # medium nougat, sand blue: thinner supply, price premium
def band(pid, col):
    k = P(pid).kind; n = P(pid).name
    if pid == '3811': return (5.0, 9.0)
    if pid in ('60596', '60616a'): return (0.6, 1.5)
    if pid == '3067a': return (0.2, 0.4)
    if pid == '3037': return (0.15, 0.30)
    if pid == '30363' or pid == '60477': return (0.15, 0.35)
    if pid in ('3041', '3043'): return (0.2, 0.4)
    if pid == '3660a': return (0.10, 0.30)
    if k in ('slope', 'inv', 'dbl'): return (0.05, 0.12)
    if pid in ('3036', '3958', '3035', '3032', '3031', '3033', '3028'): return (0.35, 0.80)
    if pid in ('2445', '3832', '3034', '3795'): return (0.15, 0.35)
    if k == 'box' and 'Plate' in n: return (0.03, 0.09)
    if pid in ('3008', '3009', '3007', '2456', '6111', '6112'): return (0.10, 0.25)
    if k == 'box': return (0.04, 0.12)
    if pid in ('4162', '6636', '87079'): return (0.12, 0.28)
    if k == 'tile': return (0.04, 0.12)
    if k in ('fence', 'grille', 'jumper'): return (0.08, 0.25)
    return (0.05, 0.2)
lo = hi = 0; cats = {}
for (pid, col), n in bom().items():
    a, b = band(pid, col)
    if col in SCARCE: a, b = a * 1.3, b * 2.0
    lo += n * a; hi += n * b
    key = ('Steep roof (slopes + ceiling)' if pid in ('3037', '3660a', '3665a', '3040b', '3039', '3041', '3043', '3044b') and P(pid).kind != 'box'
           else 'Baseplates' if pid == '3811' else 'Everything else')
    c = cats.setdefault(key, [0, 0, 0]); c[0] += n; c[1] += n * a; c[2] += n * b
print('total pieces', sum(bom().values()), 'low %.0f high %.0f' % (lo, hi))
for k, (n, a, b) in cats.items(): print(f'{k:32s} {n:5d}  ${a:6.0f} - ${b:6.0f}')
