import osmnx as ox
import matplotlib.pyplot as plt

# Name of the campus
place = "Graphic Era Deemed to be University, Dehradun, India"

print("Downloading campus data...")

# Download walking network
G = ox.graph.graph_from_place(
    place,
    network_type="walk"
)

print("Campus data downloaded successfully!")

# Display information
print("Number of nodes:", len(G.nodes))
print("Number of edges:", len(G.edges))

# Save graph
ox.io.save_graphml(G, "data/campus_graph.graphml")

print("Campus graph saved successfully!")

# Plot graph with white background
fig, ax = ox.plot.plot_graph(
    G,
    node_size=5,
    node_color="red",
    node_zorder=2,
    edge_color="blue",
    edge_linewidth=1,
    bgcolor="white",
    figsize=(12, 12),
    show=False,
    close=False
)

ax.set_facecolor("white")

plt.show()