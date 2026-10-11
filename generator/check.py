"""Structural checks: every part must be clutched (stud-to-tube) into a chain that reaches a baseplate."""
import numpy as np, collections, sys
from build import m, STEPS
from core import P

def bottom_points(p):
    pi = P(p['pid'])
    if pi.kind == 'door': return []
    if pi.kind == 'inv':
        loc = [(sx, 0.0) for sx in np.arange(pi.lx0 + 10, pi.lx1, 20)]
    else:
        loc = [(sx, sz) for sx in np.arange(pi.lx0 + 10, pi.lx1, 20) for sz in np.arange(pi.lz0 + 10, pi.lz1, 20)]
    out = []
    for sx, sz in loc:
        q = p['R'] @ np.array([sx, 0, sz]) + p['pos']
        out.append((round(q[0] / 10), round(-q[2] / 10)))     # half-stud units
    return out

studs = {}
for i, p in enumerate(m.parts):
    for (x, h, z) in p['studs']:
        studs[(round(2 * x), round(2 * z), h)] = i
adj = collections.defaultdict(set); nconn = collections.Counter()
for j, p in enumerate(m.parts):
    for (bx, bz) in bottom_points(p):
        i = studs.get((bx, bz, p['h0']))
        if i is not None and i != j:
            adj[i].add(j); adj[j].add(i); nconn[j] += 1
# doors hang on their frames
for j, p in enumerate(m.parts):
    if p['pid'] == '60616a': adj[j].add(j - 1); adj[j - 1].add(j)
base = [i for i, p in enumerate(m.parts) if p['pid'] == '3811']
seen = set(base); q = collections.deque(base)
while q:
    i = q.popleft()
    for j in adj[i]:
        if j not in seen: seen.add(j); q.append(j)
floating = [i for i in range(len(m.parts)) if i not in seen]
print('parts', len(m.parts), 'connected', len(seen), 'floating', len(floating))
by = collections.Counter((m.parts[i]['pid'], STEPS[m.parts[i]['step']]['title']) for i in floating)
for k, v in by.most_common(40): print(' ', v, k)
weak = [j for j, p in enumerate(m.parts) if nconn[j] == 1 and P(p['pid']).kind not in ('door',) and p['pid'] != '3811']
print('parts held by a single stud from below:', len(weak))
by = collections.Counter((m.parts[i]['pid'], STEPS[m.parts[i]['step']]['title'].split(':')[0]) for i in weak)
for k, v in by.most_common(15): print(' ', v, k)
