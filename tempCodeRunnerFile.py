import matplotlib.pyplot as plt

# Fundamental square torus coordinates
houses = {"A": (0.2, 0.8), "B": (0.5, 0.8), "C": (0.8, 0.8)}
services = {"A": (0.2, 0.2), "B": (0.5, 0.2), "C": (0.8, 0.2)}
house_colors = {"A": "tab:blue", "B": "tab:orange", "C": "tab:green"}

fig, ax = plt.subplots(figsize=(6,6))
ax.set_xlim(0,1)
ax.set_ylim(0,1)
ax.set_aspect('equal')
ax.set_title("K3,3 on a 2D Topological Torus (Square)")

# Draw square and arrows for identification
ax.plot([0,1,1,0,0],[0,0,1,1,0],'k-', lw=2)
arrow_props = dict(facecolor='black', arrowstyle='->', lw=1.5)
ax.annotate("", xy=(1,0.05), xytext=(0,0.05), arrowprops=arrow_props)  # left-right
ax.annotate("", xy=(0,0.95), xytext=(1,0.95), arrowprops=arrow_props)  # left-right
ax.annotate("", xy=(0.05,1), xytext=(0.05,0), arrowprops=arrow_props)  # top-bottom
ax.annotate("", xy=(0.95,0), xytext=(0.95,1), arrowprops=arrow_props)  # top-bottom

# Draw nodes
for hn,(x,y) in houses.items():
    ax.scatter(x,y, s=200, color=house_colors[hn], edgecolor='k')
    ax.text(x, y+0.03, f"H{hn}", ha='center')
for sn,(x,y) in services.items():
    ax.scatter(x,y, s=200, color='red', edgecolor='k')
    ax.text(x, y-0.03, f"S{sn}", ha='center')

# Function to draw connection with wrap-around if needed
def draw_edge(p1,p2,color):
    x1,y1 = p1
    x2,y2 = p2
    dx = x2-x1
    dy = y2-y1
    # horizontal wrap
    if abs(dx) > 0.5:
        if dx>0:
            # go left across edge
            mid = (x2-1, y2)
        else:
            mid = (x2+1, y2)
        ax.plot([x1, mid[0]], [y1, mid[1]], color=color, lw=2)
        ax.plot([mid[0]%1, x2], [mid[1], y2], color=color, lw=2)
    # vertical wrap
    elif abs(dy) > 0.5:
        if dy>0:
            mid = (x2, y2-1)
        else:
            mid = (x2, y2+1)
        ax.plot([x1, mid[0]], [y1, mid[1]], color=color, lw=2)
        ax.plot([mid[0], x2], [mid[1]%1, y2], color=color, lw=2)
    else:
        ax.plot([x1,x2],[y1,y2], color=color, lw=2)

# Draw all connections, carefully split to avoid crossings
# For clarity, alternate horizontal vs vertical wrapping
edges = [("A","A"),("A","B"),("A","C"),
         ("B","A"),("B","B"),("B","C"),
         ("C","A"),("C","B"),("C","C")]

bend_map = {
    ("A","A"):(0,0), ("A","B"):(1,0), ("A","C"):(-1,0),
    ("B","A"):(0,1), ("B","B"):(0,-1), ("B","C"):(1,1),
    ("C","A"):(-1,-1), ("C","B"):(1,-1), ("C","C"):(-1,1)
}

for hn,sn in edges:
    draw_edge(houses[hn], services[sn], house_colors[hn])

ax.axis('off')
plt.tight_layout()
plt.show()
