# k3_3_torus_3d_both_sides_fixed.py
"""
K3,3 en un toro 3D — bandas arriba y abajo (versión corregida).
corrige el ValueError al mapear arrays y escalares en torus_point.
"""

import numpy as np
import matplotlib.pyplot as plt

# parámetros del toro
R = 3.0
r = 1.0

def torus_point(u, v):
    """
    Mapea (u,v) a (x,y,z). Acepta escalares o arrays; devuelve array con shape (...,3).
    Usa broadcast para garantizar que u y v tengan la misma forma antes de operar.
    """
    u = np.asarray(u)
    v = np.asarray(v)
    # Broadcast u and v to the same shape (handles scalar vs array)
    u, v = np.broadcast_arrays(u, v)
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return np.stack([x, y, z], axis=-1)

# posición de nodos en parámetros (u,v)
# Originalmente las "casas" estaban en la banda superior (v≈0) y los "servicios" en la inferior (v≈π).
# Se solicita invertir: ahora las CASAS deben ser los puntos que antes eran servicios (v≈π) y
# los SERVICIOS deben ocupar las posiciones superiores (v≈0), preservando la conectividad completa.

# Posiciones nuevas (swap lógico):
houses_param = {  # ahora en la banda inferior (antes services_param)
    "A": (0.2, np.pi),
    "B": (2.0 * np.pi / 3.0 + 0.2, np.pi),
    "C": (4.0 * np.pi / 3.0 + 0.2, np.pi),
}
services_param = {  # ahora en la banda superior (antes houses_param)
    "A": (0.0, 0.0),
    "B": (2.0 * np.pi / 3.0, 0.0),
    "C": (4.0 * np.pi / 3.0, 0.0),
}

# Colores se asocian a cada casa (quienes ahora están en la parte inferior).
house_colors = {"A": "tab:blue", "B": "tab:orange", "C": "tab:green"}

# número de aristas
n_edges = len(houses_param) * len(services_param)

def shortest_u_path(u0, u1, n=120):
    """Interpolación en u considerando envoltura en 2π (camino corto)."""
    u0 = float(u0) % (2*np.pi)
    u1 = float(u1) % (2*np.pi)
    diff = u1 - u0
    if diff > np.pi:
        diff -= 2*np.pi
    elif diff < -np.pi:
        diff += 2*np.pi
    return np.linspace(u0, u0 + diff, n)

# Construir bandas poloidales en DOS caras:
n_top = n_edges // 2
n_bottom = n_edges - n_top
v_top = np.linspace(0.25, np.pi - 0.25, n_top) if n_top>0 else np.array([])
v_bottom = np.linspace(np.pi + 0.25, 2*np.pi - 0.25, n_bottom) if n_bottom>0 else np.array([])
v_bands = np.concatenate([v_top, v_bottom])

# mallas del toro para la superficie
u = np.linspace(0, 2*np.pi, 100)
v = np.linspace(0, 2*np.pi, 60)
U, V = np.meshgrid(u, v)
surf_pts = torus_point(U, V)
X, Y, Z = surf_pts[...,0], surf_pts[...,1], surf_pts[...,2]

fig = plt.figure(figsize=(11,9))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("K₃,₃ sobre un toro — bandas arriba y abajo (corregido)")

# superficie del toro
ax.plot_surface(X, Y, Z, rstride=4, cstride=4, color='lightgray', alpha=0.25, linewidth=0)

# dibujar nodos (usa torus_point y desempaqueta robustamente)
for name, (u_h, v_h) in houses_param.items():
    p = torus_point(u_h, v_h)
    if p.ndim == 1:
        px, py, pz = p
    else:
        px, py, pz = p.reshape(-1, 3)[0]
    # Casas ahora en la parte inferior (v≈π) se etiquetan igual
    ax.scatter(px, py, pz, s=150, color=house_colors[name], edgecolor='k', zorder=20)
    ax.text(px, py, pz+0.12, f"Casa {name}", ha='center', va='bottom')

for name, (u_s, v_s) in services_param.items():
    p = torus_point(u_s, v_s)
    if p.ndim == 1:
        px, py, pz = p
    else:
        px, py, pz = p.reshape(-1, 3)[0]
    # Servicios ahora en la parte superior (v≈0) en rojo
    ax.scatter(px, py, pz, s=120, color='red', edgecolor='k', zorder=20)
    ax.text(px, py, pz-0.12, f"Serv {name}", ha='center', va='top')

# para ayudar a ver las bandas: trazar círculos toroidales poloidales (sutil)
for vb in v_bands:
    uu = np.linspace(0, 2*np.pi, 300)
    pts_ring = torus_point(uu, vb)   # ahora funciona con uu array y vb escalar
    ax.plot(pts_ring[:,0], pts_ring[:,1], pts_ring[:,2], color='gray', alpha=0.12, linewidth=1)

# dibujar aristas, asignando una banda distinta a cada arista
edge_idx = 0
for hn, (u_h, v_h) in houses_param.items():
    for sn, (u_s, v_s) in services_param.items():
        v_band = v_bands[edge_idx]
        color = house_colors[hn]

        # subir poloidal desde nodo casa hasta v_band (mantener u_h)
        vs1 = np.linspace(v_h, v_band, 60)
        us1 = np.full_like(vs1, u_h)
        pts1 = torus_point(us1, vs1)

        # desplazamiento en u alrededor del toro en v = v_band (camino corto en u)
        us2 = shortest_u_path(u_h, u_s, n=200)
        vs2 = np.full_like(us2, v_band)
        pts2 = torus_point(us2, vs2)

        # bajar poloidal desde v_band hasta v_s en u = u_s
        vs3 = np.linspace(v_band, v_s, 60)
        us3 = np.full_like(vs3, us2[-1] % (2*np.pi))
        pts3 = torus_point(us3, vs3)

        edge_pts = np.vstack([pts1, pts2, pts3])
        ax.plot(edge_pts[:,0], edge_pts[:,1], edge_pts[:,2],
                color=color, linewidth=2.4, solid_capstyle='round', zorder=15)

        edge_idx += 1

# estética
ax.set_box_aspect([1,1,0.6])
ax.view_init(elev=28, azim=40)
ax.axis('off')
plt.tight_layout()
plt.show()
