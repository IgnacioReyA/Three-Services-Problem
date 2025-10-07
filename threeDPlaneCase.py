# k3_3_3d_curved.py
"""
Three dimensional solution of the problem, classical solution. 
"""

import numpy as np
import matplotlib.pyplot as plt

# ======== NODE POSITIONS ========
houses_3d = {"A": (-2.0, 1.0, 1.0), "B": (0.0, 1.0, 1.0), "C": (2.0, 1.0, 1.0)}
services_3d = {"A": (-2.0, -1.0, -1.0), "B": (0.0, -1.0, -1.0), "C": (2.0, -1.0, -1.0)}

# ======== FIGURE SETUP ========
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(111, projection='3d')
ax.set_title("3D solution of the three houses / three services problem (K₃,₃)")

# Draw nodes (blue = houses, red = services)
for name, pos in houses_3d.items():
    ax.scatter(*pos, s=100, color='blue')
    ax.text(*pos, f"House {name}", zdir='y', ha='center', va='bottom')

for name, pos in services_3d.items():
    ax.scatter(*pos, s=100, color='red')
    ax.text(*pos, f"Service {name}", zdir='y', ha='center', va='top')

# ======== CURVED 3D CONNECTIONS ========
def curved_edge(p1, p2, height):
    """Generate a smooth 3D curve between p1 and p2 raising it by 'height'."""
    x = np.linspace(p1[0], p2[0], 50)
    y = np.linspace(p1[1], p2[1], 50)
    z = np.linspace(p1[2], p2[2], 50)
    z = z + height * np.sin(np.linspace(0, np.pi, 50))
    return x, y, z

# Alternate heights to avoid overlaps
heights = [1.5, -1.0, 2.0, -2.0, 1.0, -1.5, 2.5, -2.5, 0.5]

i = 0
for hn, hpos in houses_3d.items():
    for sn, spos in services_3d.items():
        h = heights[i % len(heights)]
        x, y, z = curved_edge(hpos, spos, h)
        ax.plot(x, y, z, linewidth=1, color='gray')
        i += 1

# View and axis bounds
ax.view_init(elev=25, azim=35)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.set_zlim(-3, 3)
ax.axis('off')

plt.tight_layout()
plt.show()
