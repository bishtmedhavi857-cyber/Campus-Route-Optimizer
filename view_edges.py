import osmnx as ox

G = ox.io.load_graphml("data/campus_graph.graphml")

print("First 10 edges:\n")

count = 0

for u, v, data in G.edges(data=True):

    print("From:", u)
    print("To:", v)
    print("Distance:", data.get("length"), "meters")
    print("-----------------------")

    count += 1

    if count == 10:
        break