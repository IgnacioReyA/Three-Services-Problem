# k3_3_2d_portals_tracks.py
"""
K3,3 usando 'pistas perimetrales' (portal lanes) — un enfoque distinto y 100% gráfico.
Cada conexión:
  Casa -> portal_entrada -> pista_perimetral_unica -> portal_salida -> Servicio
Las pistas perimetrales son concéntricas (offsets) alrededor del rectángulo, por lo
que no se cruzan entre sí.
"""

import numpy as np
import matplotlib.pyplot as plt

# ======== CONFIG ========
houses = {"A": (1.0, 4.0), "B": (2.5, 4.0), "C": (4.0, 4.0)}
services = {"A": (1.0, 1.0), "B": (2.5, 1.0), "C": (4.0, 1.0)}

xmax, ymax = 5.0, 5.0  # tamaño del dominio
num_portals_per_side = 3

# colores por casa (para identificar fácilmente las aristas)
house_colors = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#2ca02c"}  # azul, naranja, verde

# ======== PORTALES (distribuidos por lado) ========
top_portals = [ (x, ymax) for x in np.linspace(0.5, xmax-0.5, num_portals_per_side) ]
bottom_portals = [ (x, 0.0) for x in np.linspace(0.5, xmax-0.5, num_portals_per_side) ]
left_portals = [ (0.0, y) for y in np.linspace(0.5, ymax-0.5, num_portals_per_side) ]
right_portals = [ (xmax, y) for y in np.linspace(0.5, ymax-0.5, num_portals_per_side) ]

# guardamos también el lado para cada portal (útil para mapear al perímetro)
portals = []
for p in top_portals:    portals.append(("top", p))
for p in bottom_portals: portals.append(("bottom", p))
for p in left_portals:   portals.append(("left", p))
for p in right_portals:  portals.append(("right", p))

# ======== UTILIDADES ========
def euclid(a, b):
    return np.hypot(a[0]-b[0], a[1]-b[1])

def nearest_portal(point):
    """Devuelve (side, portal_coord) del portal más cercano al punto"""
    best = None
    bd = float('inf')
    for side, p in portals:
        d = euclid(point, p)
        if d < bd:
            bd = d
            best = (side, p)
    return best

def outer_point(portal_coord, side, offset):
    """
    Mapear el portal en la frontera (por ejemplo (x, ymax)) a la coordenada
    en la pista perimetral con 'offset' (offset > 0 hacia afuera).
    """
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
    """
    Construir polilínea del perímetro exterior (clockwise) con un offset.
    Devuelve array de puntos (Nx2).
    """
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
    """
    Curva suave entre p1 y p2; bow controla cuán arqueada es (parábola).
    Devuelve arrays x,y.
    """
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

# ======== RUTAS: asignar una pista única por arista (9 aristas) ========
edges = []
for hn, hpos in houses.items():
    for sn, spos in services.items():
        edges.append((hn, hpos, sn, spos))
n_edges = len(edges)

# pista offsets (concéntricas); cada arista tiene su pista única
base_offset = 0.25
delta = 0.15
lane_offsets = [ base_offset + i*delta for i in range(n_edges) ]

# Prepara figura
fig, ax = plt.subplots(figsize=(8,8))
ax.set_title("K₃,₃ — enrutamiento por pistas perimetrales (sin cruces entre pistas)")

# Dibujar rectángulo base (dominio)
rect = plt.Rectangle((0,0), xmax, ymax, facecolor='white', edgecolor='k', zorder=0)
ax.add_patch(rect)

# Dibujar nodos
for name,pos in houses.items():
    ax.scatter(*pos, s=140, color=house_colors[name], zorder=10)
    ax.text(pos[0], pos[1]+0.18, f"Casa {name}", ha='center', va='bottom', fontsize=10)

for name,pos in services.items():
    ax.scatter(*pos, s=120, color='red', zorder=10)
    ax.text(pos[0], pos[1]-0.18, f"Serv {name}", ha='center', va='top', fontsize=10)

# Dibujar portales (marcadores en la frontera)
for side,p in portals:
    ax.scatter(p[0], p[1], s=80, color='limegreen', zorder=9, edgecolor='k', linewidth=0.6)

# Para cada arista: calcular portales de entrada/salida (los más cercanos) y trazar ruta
for i, (hn, hpos, sn, spos) in enumerate(edges):
    color = house_colors[hn]
    lane = lane_offsets[i]

    # elegir portal más cercano a casa y más cercano a servicio (entrada/ salida)
    side_in, p_in = nearest_portal(hpos)
    side_out, p_out = nearest_portal(spos)

    # puntos en la pista exterior correspondientes a esos portales y a este lane
    out_in = outer_point(p_in, side_in, lane)
    out_out = outer_point(p_out, side_out, lane)

    # construir perímetro para esta pista
    perim_pts = build_outer_perimeter(offset=lane, n_points_per_edge=200)

    # encontrar índices más cercanos a out_in / out_out
    idx_in = nearest_index_on_perim(perim_pts, out_in)
    idx_out = nearest_index_on_perim(perim_pts, out_out)

    # construir segmento perimetral (clockwise desde idx_in hasta idx_out)
    if idx_out >= idx_in:
        perim_segment = perim_pts[idx_in:idx_out+1]
    else:
        perim_segment = np.vstack([perim_pts[idx_in:], perim_pts[:idx_out+1]])

    # Dibujar: casa -> portal_in (pequeña curva), portal_in -> pista (muy corto), pista (perim_segment),
    # pista -> portal_out (muy corto), portal_out -> servicio (pequeña curva)
    # 1) casa -> portal_in (curva hacia el borde)
    x1, y1 = small_curve(hpos, p_in, n=25, bow=0.12)
    ax.plot(x1, y1, color=color, linewidth=1.6, zorder=6)

    # 2) portal_in -> out_in (tiny outward curve)
    xi, yi = small_curve(p_in, out_in, n=12, bow=0.03)
    ax.plot(xi, yi, color=color, linewidth=1.6, zorder=6)

    # 3) perimetral (la pista) — dibujar con línea continua más gruesa
    ax.plot(perim_segment[:,0], perim_segment[:,1], color=color, linewidth=2.4, zorder=5, solid_capstyle='round')

    # 4) out_out -> portal_out (tiny inward curve)
    xo, yo = small_curve(out_out, p_out, n=12, bow=0.03)
    ax.plot(xo, yo, color=color, linewidth=1.6, zorder=6)

    # 5) portal_out -> servicio (curva)
    x2, y2 = small_curve(p_out, spos, n=25, bow=0.12)
    ax.plot(x2, y2, color=color, linewidth=1.6, zorder=6)

    # Opcional: marcar la pista con un label pequeño (índice)
    mid_idx = len(perim_segment)//2
    mx, my = perim_segment[mid_idx]
    ax.text(mx, my, f"{i+1}", fontsize=8, ha='center', va='center', color='white', zorder=7,
            bbox=dict(boxstyle="circle,pad=0.2", fc=color, ec='none', alpha=0.9))

# Ajustes visuales
ax.set_xlim(-1.0, xmax+1.0)
ax.set_ylim(-1.0, ymax+1.0)
ax.set_aspect('equal')
ax.axis('off')

# Leyenda manual
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0],[0], marker='o', color='w', label='Casa A', markerfacecolor=house_colors['A'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='Casa B', markerfacecolor=house_colors['B'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='Casa C', markerfacecolor=house_colors['C'], markersize=10),
    Line2D([0],[0], marker='o', color='w', label='Servicios', markerfacecolor='red', markersize=8),
    Line2D([0],[0], marker='o', color='w', label='Portales', markerfacecolor='limegreen', markersize=8),
]
ax.legend(handles=legend_elems, loc='upper right')

plt.tight_layout()
plt.show()
