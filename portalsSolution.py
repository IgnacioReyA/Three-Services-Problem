"""
Two dimensional solution of the problem, using "portal lanes" around the perimeter.
"""

import numpy as np
import matplotlib.pyplot as plt

# ======== CONFIG ========
houses = {"A": (1.0, 4.0), "B": (2.5, 4.0), "C": (4.0, 4.0)}
services = {"A": (1.0, 1.0), "B": (2.5, 1.0), "C": (4.0, 1.0)}

xmax, ymax = 5.0, 5.0  # domain size
num_portals_per_side = 3

# Per-house colors (identify edge sets)
house_colors = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#2ca02c"}

# ======== PORTALS (distributed per side) ========
top_portals = [ (x, ymax) for x in np.linspace(0.5, xmax-0.5, num_portals_per_side) ]
bottom_portals = [ (x, 0.0) for x in np.linspace(0.5, xmax-0.5, num_portals_per_side) ]
left_portals = [ (0.0, y) for y in np.linspace(0.5, ymax-0.5, num_portals_per_side) ]
right_portals = [ (xmax, y) for y in np.linspace(0.5, ymax-0.5, num_portals_per_side) ]

# Store side info together with each portal (useful for mapping onto perimeter)
portals = []
for p in top_portals:    portals.append(("top", p))
for p in bottom_portals: portals.append(("bottom", p))
for p in left_portals:   portals.append(("left", p))
for p in right_portals:  portals.append(("right", p))

# ======== UTILIDADES ========
def euclid(a, b):
    return np.hypot(a[0]-b[0], a[1]-b[1])

def nearest_portal(point):
    """Return (side, portal_coord) of the closest portal to a point."""
    best = None
    bd = float('inf')
    for side, p in portals:
        d = euclid(point, p)
        if d < bd:
            bd = d
            best = (side, p)
    return best

def outer_point(portal_coord, side, offset):
    """Map a portal on the base border to its outward-offset lane position."""
    x, y = portal_coord
    if side == "top":
        return (x, ymax + offset)
    if side == "bottom":
        return (x, 0.0 - offset)
    if side == "left":
        return (0.0 - offset, y)
    if side == "right":
        return (xmax + offset, y)
    return (x, y)

def build_outer_perimeter(offset, n_points_per_edge=200):
    """Build clockwise polyline for an expanded rectangle at a given offset."""
    left = -offset
    right = xmax + offset
    bottom = -offset
    top = ymax + offset

    # sample edges: bottom (left->right), right (bottom->top), top (right->left), left (top->bottom)
    bx = np.linspace(left, right, n_points_per_edge, endpoint=False)
    by = np.full_like(bx, bottom)

    rx = np.full(n_points_per_edge, right)
    ry = np.linspace(bottom, top, n_points_per_edge, endpoint=False)

    tx = np.linspace(right, left, n_points_per_edge, endpoint=False)
    ty = np.full_like(tx, top)

    lx = np.full(n_points_per_edge, left)
    ly = np.linspace(top, bottom, n_points_per_edge, endpoint=False)

    # Construir array Nx2 para todos los bordes concatenados
    perim_pts = np.vstack([
        np.column_stack([bx, by]),
        np.column_stack([rx, ry]),
        np.column_stack([tx, ty]),
        np.column_stack([lx, ly]),
    ])
    return perim_pts


def nearest_index_on_perim(perim_pts, target):
    d = np.hypot(perim_pts[:,0]-target[0], perim_pts[:,1]-target[1])
    return int(np.argmin(d))

def small_curve(p1, p2, n=30, bow=0.15):
    """Smooth bowing curve between p1 and p2 (parabolic via sine shaping)."""
    x = np.linspace(p1[0], p2[0], n)
    y = np.linspace(p1[1], p2[1], n)
    # orientación perpendicular approximate via vector
    vx = p2[0]-p1[0]; vy = p2[1]-p1[1]
    # normal vector for bow (perp)
    nx, ny = -vy, vx
    norm = np.hypot(nx, ny)
    if norm < 1e-9:
        return x, y
    nx, ny = nx/norm, ny/norm
    t = np.sin(np.linspace(0, np.pi, n))
    x = x + nx * bow * t
    y = y + ny * bow * t
    return x, y

# ======== ROUTING: one unique lane per edge (9 edges) ========
edges = []
for hn, hpos in houses.items():
    for sn, spos in services.items():
        edges.append((hn, hpos, sn, spos))
n_edges = len(edges)

# Concentric lane offsets; each edge uses a unique lane
base_offset = 0.25
delta = 0.15
lane_offsets = [ base_offset + i*delta for i in range(n_edges) ]

# Figure setup
fig, ax = plt.subplots(figsize=(8,8))
ax.set_title("K₃,₃ — perimeter portal lane routing (no lane crossings)")

# Base rectangle (domain)
rect = plt.Rectangle((0,0), xmax, ymax, facecolor='white', edgecolor='k', zorder=0)
ax.add_patch(rect)

# Draw nodes
for name,pos in houses.items():
    ax.scatter(*pos, s=140, color=house_colors[name], zorder=10)
    ax.text(pos[0], pos[1]+0.18, f"House {name}", ha='center', va='bottom', fontsize=10)

for name,pos in services.items():
    ax.scatter(*pos, s=120, color='red', zorder=10)
    ax.text(pos[0], pos[1]-0.18, f"Service {name}", ha='center', va='top', fontsize=10)

# Draw portals (markers on base border)
for side,p in portals:
    ax.scatter(p[0], p[1], s=80, color='limegreen', zorder=9, edgecolor='k', linewidth=0.6)

# For each edge: choose nearest entry/exit portals and build route
for i, (hn, hpos, sn, spos) in enumerate(edges):
    color = house_colors[hn]
    lane = lane_offsets[i]

    # nearest portals to house / service nodes
    side_in, p_in = nearest_portal(hpos)
    side_out, p_out = nearest_portal(spos)

    # outward lane points corresponding to those portals
    out_in = outer_point(p_in, side_in, lane)
    out_out = outer_point(p_out, side_out, lane)

    # build perimeter polyline for this lane
    perim_pts = build_outer_perimeter(offset=lane, n_points_per_edge=200)

    # nearest perimeter indices to in/out points
    idx_in = nearest_index_on_perim(perim_pts, out_in)
    idx_out = nearest_index_on_perim(perim_pts, out_out)

    # build perimeter segment (clockwise traversal idx_in -> idx_out)
    if idx_out >= idx_in:
        perim_segment = perim_pts[idx_in:idx_out+1]
    else:
        perim_segment = np.vstack([perim_pts[idx_in:], perim_pts[:idx_out+1]])

    # Draw sequence:
    #   house -> entry portal (curved)
    #   entry portal -> outer lane point (short curve)
    #   perimeter lane segment
    #   outer lane point -> exit portal (short curve)
    #   exit portal -> service (curved)
    # 1) house -> entry portal
    x1, y1 = small_curve(hpos, p_in, n=25, bow=0.12)
    ax.plot(x1, y1, color=color, linewidth=1.6, zorder=6)

    # 2) entry portal -> outward lane point
    xi, yi = small_curve(p_in, out_in, n=12, bow=0.03)
    ax.plot(xi, yi, color=color, linewidth=1.6, zorder=6)

    # 3) lane segment (thicker line)
    ax.plot(perim_segment[:,0], perim_segment[:,1], color=color, linewidth=2.4, zorder=5, solid_capstyle='round')

    # 4) outward lane point -> exit portal
    xo, yo = small_curve(out_out, p_out, n=12, bow=0.03)
    ax.plot(xo, yo, color=color, linewidth=1.6, zorder=6)

    # 5) exit portal -> service
    x2, y2 = small_curve(p_out, spos, n=25, bow=0.12)
    ax.plot(x2, y2, color=color, linewidth=1.6, zorder=6)

    # Optional: numeric lane label
    mid_idx = len(perim_segment)//2
    mx, my = perim_segment[mid_idx]
    ax.text(mx, my, f"{i+1}", fontsize=8, ha='center', va='center', color='white', zorder=7,
            bbox=dict(boxstyle="circle,pad=0.2", fc=color, ec='none', alpha=0.9))

# Visual adjustments
ax.set_xlim(-1.0, xmax+1.0)
ax.set_ylim(-1.0, ymax+1.0)
ax.set_aspect('equal')
ax.axis('off')

# Legend
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0],[0], marker='o', color='w', label='House A', markerfacecolor=house_colors['A'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='House B', markerfacecolor=house_colors['B'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='House C', markerfacecolor=house_colors['C'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='Services', markerfacecolor='red', markersize=8),
    Line2D([0],[0], marker='o', color='w', label='Portals', markerfacecolor='limegreen', markersize=8),
]
ax.legend(handles=legend_elems, loc='upper right')

plt.tight_layout()
plt.show()
