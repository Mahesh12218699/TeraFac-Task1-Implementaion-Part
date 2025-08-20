import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- Parameters ---
BRICK = (0.2, 0.1, 0.1)   # (Length, Width, Height)
T = 0.2
TARGET_BRICKS = 10000
BRICK_VOL = np.prod(BRICK)
TARGET_VOL = TARGET_BRICKS * BRICK_VOL

# --- Fill shell function ---
def fill_shell(L, W, H, t=T):
    u = 0.1
    nL, nW, nH = int(round(L/u)), int(round(W/u)), int(round(H/u))
    tu = int(round(t/u))
    occ = np.zeros((nL, nW, nH), dtype=bool)
    bricks = []

    def can_place(x0,x1,y0,y1,z0,z1):
        return (0 <= x0 < x1 <= nL) and (0 <= y0 < y1 <= nW) and (0 <= z0 < z1 <= nH) and (not occ[x0:x1, y0:y1, z0:z1].any())
    
    def place(x0,x1,y0,y1,z0,z1, orient):
        occ[x0:x1, y0:y1, z0:z1] = True
        bricks.append((x0*u, y0*u, z0*u, orient))
    
    # +X face
    for y in range(0, nW-1, 2):
        for z in range(0, nH, 1):
            if can_place(nL-tu,nL,y,y+2,z,z+1): place(nL-tu,nL,y,y+2,z,z+1,'X')
    # -X face
    for y in range(0, nW-1, 2):
        for z in range(0, nH, 1):
            if can_place(0,tu,y,y+2,z,z+1): place(0,tu,y,y+2,z,z+1,'X')
    # +Y face
    for x in range(0, nL-1, 2):
        for z in range(0, nH, 1):
            if can_place(x,x+2,nW-tu,nW,z,z+1): place(x,x+2,nW-tu,nW,z,z+1,'Y')
    # -Y face
    for x in range(0, nL-1, 2):
        for z in range(0, nH, 1):
            if can_place(x,x+2,0,tu,z,z+1): place(x,x+2,0,tu,z,z+1,'Y')
    # +Z face
    for x in range(0, nL-1, 2):
        for y in range(0, nW-1, 2):
            if can_place(x,x+2,y,y+2,nH-tu,nH): place(x,x+2,y,y+2,nH-tu,nH,'Z')
    # -Z face
    for x in range(0, nL-1, 2):
        for y in range(0, nW-1, 2):
            if can_place(x,x+2,y,y+2,0,tu): place(x,x+2,y,y+2,0,tu,'Z')

    wall_vol = occ.sum() * (0.1**3)
    bricks_used = len(bricks)
    return bricks, bricks_used, wall_vol, occ

# --- Search best fitting shell ---
def search_best():
    best = None
    for nL in range(36, 53):
        if nL % 2: continue
        for nW in range(36, 53):
            if nW % 2: continue
            for nH in range(30, 55):
                L, W, H = nL*0.1, nW*0.1, nH*0.1
                if L <= 2*T or W <= 2*T or H <= 2*T: continue
                bricks, used, wall_vol, _ = fill_shell(L,W,H,T)
                if used > TARGET_BRICKS: continue
                inner_vol = (L-2*T)*(W-2*T)*(H-2*T)
                deficit = TARGET_BRICKS - used
                score = (-deficit, inner_vol)
                cand = dict(L=L,W=W,H=H,used=used,deficit=deficit,inner_vol=inner_vol,wall_vol=wall_vol)
                if (best is None) or (score > (-best['deficit'], best['inner_vol'])):
                    best = cand
    return best

best = search_best()
print("=== Best discrete shell ===")
print(f"Outer dimensions (m): L={best['L']:.2f}, W={best['W']:.2f}, H={best['H']:.2f}")
print(f"Inner clear (m): {best['L']-2*T:.2f} × {best['W']-2*T:.2f} × {best['H']-2*T:.2f}")
print(f"Bricks used: {best['used']}  (leftover: {best['deficit']})   Target: {TARGET_BRICKS}")
print(f"Wall volume: {best['wall_vol']:.3f} m³ (target {TARGET_VOL:.3f} m³)")
print(f"Inner volume: {best['inner_vol']:.3f} m³")

# --- Export placements ---
placements, used, wall_vol, occ = fill_shell(best['L'], best['W'], best['H'], T)
df = pd.DataFrame(placements, columns=['x_m','y_m','z_m','orientation'])
csv_path = "/content/brick_placements.csv"
df.to_csv(csv_path, index=False)
print(f"Placements saved to {csv_path}")