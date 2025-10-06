"""
Visualización del problema de las tres casas y tres servicios (K3,3) en 2D.
Muestra las intersecciones entre las conexiones (imposibilidad de solución en el plano).
"""

import matplotlib.pyplot as plt

def draw_k33_2d():
    # Posiciones de los nodos (casas arriba, servicios abajo)
    houses = {"A": (-2.0, 1.0), "B": (0.0, 1.0), "C": (2.0, 1.0)}
    services = {"A": (-2.0, -1.0), "B": (0.0, -1.0), "C": (2.0, -1.0)}

    # Generar lista de aristas (cada arista es ((x1,y1),(x2,y2)))
    edges = [(hpos, spos) for hpos in houses.values() for spos in services.values()]

    # --- Función para calcular intersecciones ---
    def seg_intersection(p1, p2, p3, p4):
        (x1,y1),(x2,y2) = p1,p2
        (x3,y3),(x4,y4) = p3,p4
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(denom) < 1e-9:
            return None
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
        u = ((x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)) / denom
        if 1e-9 < t < 1-1e-9 and 1e-9 < u < 1-1e-9:
            ix = x1 + t*(x2-x1)
            iy = y1 + t*(y2-y1)
            return (ix, iy)
        return None

    # --- Calcular intersecciones ---
    intersections = []
    for i in range(len(edges)):
        p1,p2 = edges[i]
        for j in range(i+1, len(edges)):
            q1,q2 = edges[j]
            if p1==q1 or p1==q2 or p2==q1 or p2==q2:
                continue
            pt = seg_intersection(p1,p2,q1,q2)
            if pt:
                intersections.append(pt)

    # --- Dibujar el gráfico ---
    fig, ax = plt.subplots(figsize=(6,6))
    hx = [p[0] for p in houses.values()]
    hy = [p[1] for p in houses.values()]
    sx = [p[0] for p in services.values()]
    sy = [p[1] for p in services.values()]

    ax.scatter(hx, hy, s=200)
    ax.scatter(sx, sy, s=200)

    for name, pos in houses.items():
        ax.text(pos[0], pos[1]+0.12, f"Casa {name}", ha="center", va="bottom")
    for name, pos in services.items():
        ax.text(pos[0], pos[1]-0.12, f"Serv {name}", ha="center", va="top")

    for p1,p2 in edges:
        xs = [p1[0], p2[0]]
        ys = [p1[1], p2[1]]
        ax.plot(xs, ys, linewidth=1)

    if intersections:
        ix_coords = [p[0] for p in intersections]
        iy_coords = [p[1] for p in intersections]
        ax.scatter(ix_coords, iy_coords, s=50, marker='x')
        ax.set_title(f"K3,3 en 2D — intersecciones: {len(intersections)}")
    else:
        ax.set_title("K3,3 en 2D — sin intersecciones")

    ax.set_aspect('equal')
    ax.set_xlim(-3, 3)
    ax.set_ylim(-2, 2)
    ax.axis('off')

    plt.tight_layout()
    plt.show()

# Permite ejecutar directamente el archivo
if __name__ == "__main__":
    draw_k33_2d()
