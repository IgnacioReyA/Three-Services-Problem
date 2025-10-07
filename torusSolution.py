
"""
Three dimensional solution of the problem, using a torus topology.
"""

import numpy as np
import matplotlib.pyplot as plt

# Torus parameters
R = 3.0
r = 1.0

def torus_point(u, v):
    """Map (u,v) to (x,y,z). Accepts scalars or arrays; returns array shape (...,3)."""
    u = np.asarray(u)
    v = np.asarray(v)
    u, v = np.broadcast_arrays(u, v)
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return np.stack([x, y, z], axis=-1)

# Node positions (u,v). Houses on lower band (v≈π), services on upper band (v≈0)
houses_param = {  # lower band
    "A": (0.2, np.pi),
    "B": (2.0 * np.pi / 3.0 + 0.2, np.pi),
    "C": (4.0 * np.pi / 3.0 + 0.2, np.pi),
}
services_param = {  # upper band
    "A": (0.0, 0.0),
    "B": (2.0 * np.pi / 3.0, 0.0),
    "C": (4.0 * np.pi / 3.0, 0.0),
}

# Color per house (used for its 3 incident edges)
house_colors = {"A": "tab:blue", "B": "tab:orange", "C": "tab:green"}

# Number of edges
n_edges = len(houses_param) * len(services_param)

def shortest_u_path(u0, u1, n=120):
    """Shortest interpolation in u (handles 2π wrap). Returns values in [0, 2π)."""
    u0 = float(u0) % (2*np.pi)
    u1 = float(u1) % (2*np.pi)
    diff = u1 - u0
    # elegir la dirección más corta alrededor del toro
    if diff > np.pi:
        diff -= 2*np.pi
    elif diff < -np.pi:
        diff += 2*np.pi
    path = np.linspace(u0, u0 + diff, n)
    # normalizar al rango [0,2π) para evitar saltos al trazar
    path = np.mod(path, 2*np.pi)
    return path

# Build poloidal band positions (top / bottom sets)
n_top = n_edges // 2
n_bottom = n_edges - n_top
# si uno de los contadores es 0, crear arrays vacíos manejados luego
v_top_positions = np.linspace(0.25, np.pi - 0.25, n_top) if n_top > 0 else np.array([])
v_bottom_positions = np.linspace(np.pi + 0.25, 2*np.pi - 0.25, n_bottom) if n_bottom > 0 else np.array([])

# Surface mesh for torus
u = np.linspace(0, 2*np.pi, 100)
v = np.linspace(0, 2*np.pi, 60)
U, V = np.meshgrid(u, v)
surf_pts = torus_point(U, V)
X, Y, Z = surf_pts[...,0], surf_pts[...,1], surf_pts[...,2]

fig = plt.figure(figsize=(11,9))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("K₃,₃ on a torus — alternating band routing")

# Torus surface
ax.plot_surface(X, Y, Z, rstride=4, cstride=4, color='lightgray', alpha=0.25, linewidth=0)

# Draw nodes
for name, (u_h, v_h) in houses_param.items():
    p = torus_point(u_h, v_h)
    if p.ndim == 1:
        px, py, pz = p
    else:
        px, py, pz = p.reshape(-1, 3)[0]
    ax.scatter(px, py, pz, s=150, color=house_colors[name], edgecolor='k', zorder=20)
    ax.text(px, py, pz+0.12, f"House {name}", ha='center', va='bottom')

for name, (u_s, v_s) in services_param.items():
    p = torus_point(u_s, v_s)
    if p.ndim == 1:
        px, py, pz = p
    else:
        px, py, pz = p.reshape(-1, 3)[0]
    ax.scatter(px, py, pz, s=120, color='red', edgecolor='k', zorder=20)
    ax.text(px, py, pz-0.12, f"Service {name}", ha='center', va='top')

    # Reference poloidal rings (subtle)
for vb in np.linspace(0.2, np.pi-0.2, max(4, n_top)):
    uu = np.linspace(0, 2*np.pi, 300)
    pts_ring = torus_point(uu, vb)
    ax.plot(pts_ring[:,0], pts_ring[:,1], pts_ring[:,2], color='gray', alpha=0.12, linewidth=1)
for vb in np.linspace(np.pi+0.2, 2*np.pi-0.2, max(5, n_bottom)):
    uu = np.linspace(0, 2*np.pi, 300)
    pts_ring = torus_point(uu, vb)
    ax.plot(pts_ring[:,0], pts_ring[:,1], pts_ring[:,2], color='gray', alpha=0.12, linewidth=1)

# Draw edges assigning alternating bands to distribute and reduce overlaps
edge_idx = 0
# Helper indices to traverse top/bottom band position arrays
it_top = 0
it_bottom = 0
for hn, (u_h, v_h) in houses_param.items():
    for sn, (u_s, v_s) in services_param.items():
        # Alternate bands: even index -> upper band (if any), odd -> lower band (if any)
        if len(v_top_positions) > 0 and len(v_bottom_positions) > 0:
            if edge_idx % 2 == 0:
                # take next upper band position (cyclic)
                v_band = v_top_positions[it_top % len(v_top_positions)]
                it_top += 1
            else:
                v_band = v_bottom_positions[it_bottom % len(v_bottom_positions)]
                it_bottom += 1
        else:
            # Fallback: only one band set available
            all_bands = np.concatenate([v_top_positions, v_bottom_positions])
            v_band = all_bands[edge_idx % len(all_bands)]

        color = house_colors[hn]

    # 1) Poloidal segment from house to chosen band (keep u constant)
        vs1 = np.linspace(v_h, v_band, 60)
        us1 = np.full_like(vs1, float(u_h) % (2*np.pi))
        pts1 = torus_point(us1, vs1)

    # 2) Toroidal (u) shortest path along band
        u_s_mod = float(u_s) % (2*np.pi)
        us2 = shortest_u_path(u_h, u_s_mod, n=200)
        vs2 = np.full_like(us2, v_band)
        pts2 = torus_point(us2, vs2)

    # 3) Poloidal descent to service node
        vs3 = np.linspace(v_band, v_s, 60)
        us3 = np.full_like(vs3, u_s_mod)
        pts3 = torus_point(us3, vs3)

        edge_pts = np.vstack([pts1, pts2, pts3])
        ax.plot(edge_pts[:,0], edge_pts[:,1], edge_pts[:,2],
                color=color, linewidth=2.4, solid_capstyle='round', zorder=15)

        edge_idx += 1

# Aesthetics
ax.set_box_aspect([1,1,0.6])
ax.view_init(elev=28, azim=40)
ax.axis('off')
plt.tight_layout()
plt.show()
