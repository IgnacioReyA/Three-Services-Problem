# k3_3_torus_3d_both_sides_fixed.py
"""
K3,3 en un toro 3D — bandas arriba y abajo (versión corregida).
Corrige mapeos, asignación de bandas y trazado de aristas para evitar solapamientos irracionales.
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
    u, v = np.broadcast_arrays(u, v)
    x = (R + r * np.cos(v)) * np.cos(u)
    y = (R + r * np.cos(v)) * np.sin(u)
    z = r * np.sin(v)
    return np.stack([x, y, z], axis=-1)

# posición de nodos en parámetros (u,v)
# Intercambiamos las bandas: casas en v≈π (inferior), servicios en v≈0 (superior)
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
    """Interpolación en u considerando envoltura en 2π (camino corto). Devuelve valores normalizados en [0,2π)."""
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

# Construir posiciones de bandas poloidales separadas para arriba y abajo
n_top = n_edges // 2
n_bottom = n_edges - n_top
# si uno de los contadores es 0, crear arrays vacíos manejados luego
v_top_positions = np.linspace(0.25, np.pi - 0.25, n_top) if n_top > 0 else np.array([])
v_bottom_positions = np.linspace(np.pi + 0.25, 2*np.pi - 0.25, n_bottom) if n_bottom > 0 else np.array([])

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
    ax.scatter(px, py, pz, s=150, color=house_colors[name], edgecolor='k', zorder=20)
    ax.text(px, py, pz+0.12, f"Casa {name}", ha='center', va='bottom')

for name, (u_s, v_s) in services_param.items():
    p = torus_point(u_s, v_s)
    if p.ndim == 1:
        px, py, pz = p
    else:
        px, py, pz = p.reshape(-1, 3)[0]
    ax.scatter(px, py, pz, s=120, color='red', edgecolor='k', zorder=20)
    ax.text(px, py, pz-0.12, f"Serv {name}", ha='center', va='top')

# para ayudar a ver las bandas: trazar varios círculos toroidales poloidales (sutil)
# hacemos algunos anillos en ambas mitades para referencia
for vb in np.linspace(0.2, np.pi-0.2, max(4, n_top)):
    uu = np.linspace(0, 2*np.pi, 300)
    pts_ring = torus_point(uu, vb)
    ax.plot(pts_ring[:,0], pts_ring[:,1], pts_ring[:,2], color='gray', alpha=0.12, linewidth=1)
for vb in np.linspace(np.pi+0.2, 2*np.pi-0.2, max(5, n_bottom)):
    uu = np.linspace(0, 2*np.pi, 300)
    pts_ring = torus_point(uu, vb)
    ax.plot(pts_ring[:,0], pts_ring[:,1], pts_ring[:,2], color='gray', alpha=0.12, linewidth=1)

# dibujar aristas, asignando bandas alternadas para distribuir conexiones y evitar solapamientos
edge_idx = 0
# indices auxiliares para recorrer las posiciones top/bottom sin agotarlas
it_top = 0
it_bottom = 0
for hn, (u_h, v_h) in houses_param.items():
    for sn, (u_s, v_s) in services_param.items():
        # alternar: si edge_idx par -> usar una banda superior (si existe), si impar -> banda inferior (si existe)
        if len(v_top_positions) > 0 and len(v_bottom_positions) > 0:
            if edge_idx % 2 == 0:
                # tomar siguiente posición top (ciclo si es necesario)
                v_band = v_top_positions[it_top % len(v_top_positions)]
                it_top += 1
            else:
                v_band = v_bottom_positions[it_bottom % len(v_bottom_positions)]
                it_bottom += 1
        else:
            # si solo hay un tipo de banda, repartimos por índice
            all_bands = np.concatenate([v_top_positions, v_bottom_positions])
            v_band = all_bands[edge_idx % len(all_bands)]

        color = house_colors[hn]

        # 1) Subir poloidal desde nodo casa hasta v_band (mantener u_h)
        vs1 = np.linspace(v_h, v_band, 60)
        us1 = np.full_like(vs1, float(u_h) % (2*np.pi))
        pts1 = torus_point(us1, vs1)

        # 2) Desplazamiento en u alrededor del toro en v = v_band (camino corto en u)
        u_s_mod = float(u_s) % (2*np.pi)
        us2 = shortest_u_path(u_h, u_s_mod, n=200)
        vs2 = np.full_like(us2, v_band)
        pts2 = torus_point(us2, vs2)

        # 3) Bajar poloidal desde v_band hasta v_s en u = u_s_mod (usar u_s explícito)
        vs3 = np.linspace(v_band, v_s, 60)
        us3 = np.full_like(vs3, u_s_mod)
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
