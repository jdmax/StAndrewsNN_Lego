import os, numpy as np, functools
ROOT='/tmp/claude-0/-home-claude/530bcb80-0f4d-5fa3-b13e-ffc2d088d554/scratchpad/ldraw/lib/complete/ldraw'
DIRS=['parts','p','parts/s','p/48']
def find(name):
    n=name.replace('\\','/').lower()
    for d in ['parts','p','']:
        p=os.path.join(ROOT,d,n)
        if os.path.exists(p): return p
    for d in DIRS:
        p=os.path.join(ROOT,d,os.path.basename(n))
        if os.path.exists(p): return p
    return None
@functools.lru_cache(None)
def lines(name):
    p=find(name)
    if not p: return None
    return open(p,encoding='latin-1').read().splitlines()
def title(name):
    L=lines(name); return L[0][2:].strip() if L else None
@functools.lru_cache(None)
def geom(name):
    """returns (tris Nx3x3, studs list of (pos,dir)) in part coords"""
    L=lines(name); tris=[]; studs=[]
    if L is None: return np.zeros((0,3,3)), []
    for ln in L:
        t=ln.split()
        if not t: continue
        if t[0]=='1':
            x,y,z=map(float,t[2:5]); m=np.array(list(map(float,t[5:14]))).reshape(3,3); sub=' '.join(t[14:]).lower()
            base=os.path.basename(sub.replace('\\','/'))
            if base.startswith('stud') and base in ('stud.dat','stud2.dat','stud2a.dat','studa.dat','stud10.dat','stud15.dat','stud3.dat','stud4.dat','stud4a.dat','stud6.dat','stud6a.dat','stud4o.dat'):
                # record stud/anti-stud position; still include geometry for bbox
                studs.append((base, np.array([x,y,z]), m[:,1]))
            T,S=geom(sub)
            if len(T): tris.append(T@m.T+np.array([x,y,z]))
            for b,p,d in S: studs.append((b,m@p+np.array([x,y,z]), m@d))
        elif t[0]=='3':
            v=np.array(list(map(float,t[2:11]))).reshape(3,3); tris.append(v[None])
        elif t[0]=='4':
            v=np.array(list(map(float,t[2:14]))).reshape(4,3); tris.append(v[[0,1,2]][None]); tris.append(v[[0,2,3]][None])
    T=np.concatenate(tris) if tris else np.zeros((0,3,3))
    return T, studs
def bbox(name):
    T,_=geom(name); P=T.reshape(-1,3); return P.min(0),P.max(0)
