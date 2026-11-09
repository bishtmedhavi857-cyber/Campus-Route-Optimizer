import osmnx as ox
import os

address = (
    "Graphic Era Deemed to be University, "
    "566/6 Bell Road, Clement Town, "
    "Dehradun, Uttarakhand, India"
)

print("Downloading GEU walking network...")
print("Please wait...")

G = ox.graph.graph_from_address(
    address,
    dist=700,
    network_type="walk",
    simplify=True
)

print("\nDownload completed!")

print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))

# Create data folder
os.makedirs("data", exist_ok=True)

# Save graph
ox.io.save_graphml(
    G,
    "data/campus_graph.graphml"
)

print("\nGraph saved successfully!")
print("data/campus_graph.graphml")


