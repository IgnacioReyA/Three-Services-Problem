# k3_3_3d_curved.py
"""
Visualización en 3D del problema de las 3 casas y 3 servicios (K₃,₃)
Usa curvas 3D para que las conexiones no se crucen, con colores consistentes con el 2D.
"""

import numpy as np
import matplotlib.pyplot as plt

# ======== POSICIONES ========
houses_3d = {"A": (-2.0, 1.0, 1.0), "B": (0.0, 1.0, 1.0), "C": (2.0, 1.0, 1.0)}
services_3d = {"A": (-2.0, -1.0, -1.0), "B": (0.0, -1.0, -1.0), "C": (2.0, -1.0, -1.0)}

# ======== FIGURA ========
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("Solución 3D del problema de las 3 casas y 3 servicios (K₃,₃)")

# Dibujar nodos con colores
for name, pos in houses_3d.items():
    ax.scatter(*pos, s=100, color='blue')  # casas en azul
    ax.text(*pos, f"Casa {name}", zdir='y', ha='center', va='bottom')

for name, pos in services_3d.items():
    ax.scatter(*pos, s=100, color='red')  # servicios en rojo
    ax.text(*pos, f"Serv {name}", zdir='y', ha='center', va='top')

# ======== CONEXIONES CURVAS 3D ========
def curved_edge(p1, p2, height):
    """Genera una curva 3D suave entre dos puntos, elevándola según 'height'."""
    x = np.linspace(p1[0], p2[0], 50)
    y = np.linspace(p1[1], p2[1], 50)
    z = np.linspace(p1[2], p2[2], 50)
    z = z + height * np.sin(np.linspace(0, np.pi, 50))
    return x, y, z

# Conexiones: se alternan alturas para evitar cruces
heights = [1.5, -1.0, 2.0, -2.0, 1.0, -1.5, 2.5, -2.5, 0.5]

i = 0
for hn, hpos in houses_3d.items():
    for sn, spos in services_3d.items():
        h = heights[i % len(heights)]
        x, y, z = curved_edge(hpos, spos, h)
        ax.plot(x, y, z, linewidth=1, color='gray')
        i += 1

# Ajustar vista y límites
ax.view_init(elev=25, azim=35)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(-3, 3)
ax.axis('off')

plt.tight_layout()
plt.show()
