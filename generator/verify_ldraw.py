"""Check every LDraw placement against the design grid using the real part geometry."""
import numpy as np
from build import m
from core import P
from export import FACE
from ldlib import geom
bad=0
for p in m.parts:
    pi=P(p['pid'])
    if pi.kind in ('door',): continue
    T,_=geom(p['pid']+'.dat'); V=T.reshape(-1,3); V=V[V[:,1]>=0]   # body only (no studs)
    W=V@p['R'].T+p['pos']; X=W[:,0]/20; Z=-W[:,2]/20; H=-W[:,1]/8
    ok = (abs(X.min()-p['x0'])<0.06 and abs(X.max()-(p['x0']+p['wx']))<0.06 and abs(Z.min()-p['z0'])<0.06
          and abs(Z.max()-(p['z0']+p['wz']))<0.06 and abs(H.min()-p['h0'])<0.06 and abs(H.max()-(p['h0']+pi.hp))<0.06)
    if pi.kind in ('slope','slope18','inv'):
        o=p['R']@np.zeros(3)+p['pos']; cx,cz=o[0]/20,-o[2]/20
        f=FACE[p['r']%4]
        if f==0: want=(p['x0']+0.5,None)
        elif f==1: want=(p['x0']+p['wx']-0.5,None)
        elif f==2: want=(None,p['z0']+0.5)
        else: want=(None,p['z0']+p['wz']-0.5)
        if want[0] is not None and abs(cx-want[0])>0.01: ok=False
        if want[1] is not None and abs(cz-want[1])>0.01: ok=False
    if not ok:
        bad+=1
        if bad<8: print('MISMATCH',p['pid'],p['x0'],p['z0'],p['h0'],p['wx'],p['wz'],'ldraw x',X.min(),X.max(),'z',Z.min(),Z.max(),'h',H.min(),H.max())
print('checked',len(m.parts),'mismatches',bad)
