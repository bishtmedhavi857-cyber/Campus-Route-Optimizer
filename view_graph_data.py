import osmnx as ox

# Load saved campus graph
G = ox.io.load_graphml("data/campus_graph.graphml")

print("Number of nodes:", len(G.nodes))
print("Number of edges:", len(G.edges))

print("\nFirst 5 nodes:")

for node in list(G.nodes)[:5]:

    data = G.nodes[node]

    print("Node ID:", node)
    print("Latitude:", data["y"])
    print("Longitude:", data["x"])
    print("-----------------------")