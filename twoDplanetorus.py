"""
Two dimensional solution of the problem, using the topology of a torus.
"""

import matplotlib.pyplot as plt
import numpy as np

# ---------- NODE POSITIONS ----------
houses = {"A": (0.2, 0.8), "B": (0.5, 0.8), "C": (0.8, 0.8)}
services = {"A": (0.2, 0.2), "B": (0.5, 0.2), "C": (0.8, 0.2)}
house_colors = {"A": "tab:blue", "B": "tab:orange", "C": "tab:green"}

# ---------- FIGURE SETUP ----------
fig, ax = plt.subplots(figsize=(7,7))
ax.set_xlim(0,1)
ax.set_ylim(0,1)
ax.set_aspect('equal')
ax.set_title("K3,3 on a 2D Torus — Visual Curved Connections")

# Draw fundamental square
ax.plot([0,1,1,0,0],[0,0,1,1,0],'k-', lw=2)

# Draw boundary identification arrows
arrow_props = dict(facecolor='black', arrowstyle='->', lw=1.5)
ax.annotate("", xy=(1,0.05), xytext=(0,0.05), arrowprops=arrow_props)  # left-right
ax.annotate("", xy=(0,0.95), xytext=(1,0.95), arrowprops=arrow_props)
ax.annotate("", xy=(0.05,1), xytext=(0.05,0), arrowprops=arrow_props)  # top-bottom
ax.annotate("", xy=(0.95,0), xytext=(0.95,1), arrowprops=arrow_props)

# Draw nodes
for hn,(x,y) in houses.items():
    ax.scatter(x,y, s=200, color=house_colors[hn], edgecolor='k', zorder=10)
    ax.text(x, y+0.03, f"H{hn}", ha='center')
for sn,(x,y) in services.items():
    ax.scatter(x,y, s=200, color='red', edgecolor='k', zorder=10)
    ax.text(x, y-0.03, f"Service {sn}", ha='center')

# ---------- CURVED CONNECTION UTILITY ----------
def curved_edge(p1, p2, color, bend=0.1):
    """Draw a curved connection, splitting if wrapping is needed."""
    x1,y1 = p1
    x2,y2 = p2
    
    dx = x2 - x1
    dy = y2 - y1
    
    segments = []

    # Horizontal wrap (passes through left/right boundary)
    if abs(dx) > 0.5:
        if dx > 0:
            mid = (x2-1, y2)
        else:
            mid = (x2+1, y2)
        segments.append((p1, mid))
        segments.append(((mid[0]%1, mid[1]), p2))
    # Vertical wrap (passes through top/bottom boundary)
    elif abs(dy) > 0.5:
        if dy > 0:
            mid = (x2, y2-1)
        else:
            mid = (x2, y2+1)
        segments.append((p1, mid))
        segments.append(((mid[0], mid[1]%1), p2))
    else:
        segments.append((p1, p2))
    
    for seg in segments:
        x_start, y_start = seg[0]
        x_end, y_end = seg[1]
        # Perpendicular vector for bending
        dxs = x_end - x_start
        dys = y_end - y_start
        perp = np.array([-dys, dxs])
        if np.linalg.norm(perp)==0:
            perp = np.array([0,0])
        else:
            perp = perp / np.linalg.norm(perp)
        midx = (x_start + x_end)/2 + bend*perp[0]
        midy = (y_start + y_end)/2 + bend*perp[1]
        t = np.linspace(0,1,50)
        xs = (1-t)**2*x_start + 2*(1-t)*t*midx + t**2*x_end
        ys = (1-t)**2*y_start + 2*(1-t)*t*midy + t**2*y_end
        ax.plot(xs, ys, color=color, lw=2)

# ---------- DRAW ALL EDGES ----------
for hn,hp in houses.items():
    for sn,sp in services.items():
        curved_edge(hp, sp, house_colors[hn], bend=0.08)

# ---------- FINALIZE ----------
ax.axis('off')
plt.tight_layout()
plt.show()
