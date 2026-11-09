
import os
import json
import math

import osmnx as ox
import matplotlib.pyplot as plt

from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from map_visualization import draw_route_map


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GRAPH_FILE = os.path.join(
    BASE_DIR, "data", "campus_graph.graphml"
)

LOCATIONS_FILE = os.path.join(
    BASE_DIR, "data", "locations.json"
)


def main():
    print("Loading campus graph...")

    graph = ox.io.load_graphml(GRAPH_FILE)

    with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
        locations = json.load(file)

    valid_locations = {
        name: int(data["node"])
        for name, data in locations.items()
        if "node" in data
        and data.get("lat", 0) != 0
        and data.get("lon", 0) != 0
    }

    if len(valid_locations) < 2:
        print("At least two valid locations are required.")
        return

    names = list(valid_locations.keys())

    print("\nCampus locations:")
    for index, name in enumerate(names, start=1):
        print(f"{index}. {name}")

    try:
        start_index = int(input("\nSelect start location number: ")) - 1
        destination_index = int(
            input("Select destination number: ")
        ) - 1

        if not 0 <= start_index < len(names):
            raise ValueError("Invalid start selection.")

        if not 0 <= destination_index < len(names):
            raise ValueError("Invalid destination selection.")

    except ValueError as error:
        print("Input error:", error)
        return

    start_name = names[start_index]
    destination_name = names[destination_index]

    start_node = valid_locations[start_name]
    destination_node = valid_locations[destination_name]

    if start_node == destination_node:
        print(
            "These locations map to the same graph node. "
            "Check their coordinates or nearest-node mapping."
        )
        return

    algorithm = input(
        "Choose algorithm (Dijkstra/A*): "
    ).strip().lower()

    if algorithm == "dijkstra":
        route, distance = dijkstra(
            graph, start_node, destination_node
        )
        algorithm_name = "Dijkstra"

    elif algorithm in ("a*", "astar"):
        route, distance = astar(
            graph, start_node, destination_node
        )
        algorithm_name = "A*"

    else:
        print("Invalid choice. Enter Dijkstra or A*.")
        return

    if route is None or not math.isfinite(float(distance)):
        print("No route found between these locations.")
        return

    distance = float(distance)
    walking_minutes = math.ceil(distance / 80)

    print("\n--- ROUTE RESULTS ---")
    print("Start:", start_name)
    print("Destination:", destination_name)
    print("Algorithm:", algorithm_name)
    print(f"Distance: {distance:.2f} metres")
    print(f"Distance: {distance / 1000:.3f} km")
    print(f"Estimated walking time: {walking_minutes} minutes")

    print("\nRoute:")
    print(" -> ".join([start_name, destination_name]))

    fig, ax = draw_route_map(
        graph=graph,
        locations=locations,
        route=route,
        source_node=start_node,
        destination_node=destination_node
    )

    plt.show()


if __name__ == "__main__":
    main()
