import osmnx as ox
import json
import csv

from algorithms.dijkstra import dijkstra


# -------------------------------------------------
# 1. LOAD CAMPUS GRAPH
# -------------------------------------------------

print("Loading campus graph...")

G = ox.io.load_graphml(
    "data/campus_graph.graphml"
)

print("Campus graph loaded successfully.")


# -------------------------------------------------
# 2. LOAD LOCATION DATA
# -------------------------------------------------

with open(
    "data/locations.json",
    "r"
) as file:

    locations = json.load(file)


# -------------------------------------------------
# 3. GET LOCATIONS WITH VALID NODE NUMBERS
# -------------------------------------------------

valid_locations = {}

for name, data in locations.items():

    if "node" in data:

        valid_locations[name] = data["node"]

    else:

        print(
            name,
            "-> Skipped because node is not available."
        )


print("\nValid locations:")

for name, node in valid_locations.items():

    print(
        name,
        "->",
        node
    )


# -------------------------------------------------
# 4. CALCULATE DISTANCES
# -------------------------------------------------

results = []

location_names = list(
    valid_locations.keys()
)


print("\n--------------------------------")
print("CALCULATING DISTANCES")
print("--------------------------------")


for i in range(
    len(location_names)
):

    source_name = location_names[i]

    source_node = valid_locations[
        source_name
    ]


    for j in range(
        i + 1,
        len(location_names)
    ):

        destination_name = location_names[j]

        destination_node = valid_locations[
            destination_name
        ]


        print(
            "\nCalculating:",
            source_name,
            "->",
            destination_name
        )


        # Run Dijkstra
        route, distance = dijkstra(
            G,
            source_node,
            destination_node
        )


        # Check whether route exists
        if route is None:

            print(
                "No route found."
            )

            continue


        # Convert meters to kilometers
        distance_km = distance / 1000


        print(
            "Distance:",
            round(distance, 2),
            "meters"
        )


        # Store result
        results.append(
            [
                source_name,
                destination_name,
                round(distance, 2),
                round(distance_km, 3)
            ]
        )


# -------------------------------------------------
# 5. CREATE distances.csv
# -------------------------------------------------

output_file = (
    "data/distances.csv"
)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)


    # Header
    writer.writerow(
        [
            "Source",
            "Destination",
            "Distance_m",
            "Distance_km"
        ]
    )


    # Data
    writer.writerows(
        results
    )


# -------------------------------------------------
# 6. FINISH
# -------------------------------------------------

print("\n--------------------------------")
print("DISTANCE CALCULATION COMPLETED")
print("--------------------------------")

print(
    "Total routes calculated:",
    len(results)
)

print(
    "File saved at:",
    output_file
)