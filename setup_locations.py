import osmnx as ox
import json

print("Loading campus graph...")

G = ox.io.load_graphml(
    "data/campus_graph.graphml"
)

print("Campus graph loaded successfully.")

with open(
    "data/locations.json",
    "r"
) as file:

    locations = json.load(file)

for name, location in locations.items():

    latitude = location["lat"]
    longitude = location["lon"]

    if latitude == 0 or longitude == 0:

        print(
            name,
            "-> Coordinates not entered"
        )

        continue

    node, distance = ox.distance.nearest_nodes(
        G,
        X=longitude,
        Y=latitude,
        return_dist=True
    )

    locations[name]["node"] = int(node)

    locations[name]["nearest_node_distance"] = round(
        float(distance),
        2
    )

    print(
        name,
        "-> Node:",
        node,
        "| Distance:",
        round(float(distance), 2),
        "meters"
    )

with open(
    "data/locations.json",
    "w"
) as file:

    json.dump(
        locations,
        file,
        indent=4
    )

print("\n--------------------------------")
print("LOCATION DATA UPDATED")
print("--------------------------------")

print(
    "Saved to: data/locations.json"
)