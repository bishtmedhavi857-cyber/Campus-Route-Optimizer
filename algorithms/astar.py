import heapq
import math


def heuristic(graph, node1, node2):

    # Latitude and longitude of node 1
    lat1 = float(graph.nodes[node1]["y"])
    lon1 = float(graph.nodes[node1]["x"])

    # Latitude and longitude of node 2
    lat2 = float(graph.nodes[node2]["y"])
    lon2 = float(graph.nodes[node2]["x"])

    # Difference in latitude
    latitude_difference = (
        lat2 - lat1
    ) * 111320

    # Difference in longitude
    longitude_difference = (
        lon2 - lon1
    ) * 111320 * math.cos(
        math.radians(lat1)
    )

    # Straight-line estimated distance in meters
    distance = math.sqrt(
        latitude_difference ** 2 +
        longitude_difference ** 2
    )

    return distance


def astar(graph, start, destination):

    # Priority queue
    open_set = []

    heapq.heappush(
        open_set,
        (0, start)
    )

    # Actual distance from start
    g_score = {}

    # Previous node
    previous = {}

    for node in graph.nodes:

        g_score[node] = float("inf")
        previous[node] = None

    # Starting node
    g_score[start] = 0

    # Continue searching
    while open_set:

        current_f, current = heapq.heappop(
            open_set
        )

        # Destination reached
        if current == destination:
            break

        # Visit neighboring nodes
        for neighbor in graph.neighbors(current):

            edge_data = graph.get_edge_data(
                current,
                neighbor
            )

            # Get edge distance
            weight = min(
                data.get("length", 1)
                for data in edge_data.values()
            )

            # Actual distance from start
            new_g = (
                g_score[current] + weight
            )

            # If better route is found
            if new_g < g_score[neighbor]:

                g_score[neighbor] = new_g

                previous[neighbor] = current

                # Estimated distance to destination
                h = heuristic(
                    graph,
                    neighbor,
                    destination
                )

                # f(n) = g(n) + h(n)
                f = new_g + h

                heapq.heappush(
                    open_set,
                    (
                        f,
                        neighbor
                    )
                )

    # No route found
    if g_score[destination] == float("inf"):

        return None, float("inf")

    # Reconstruct path
    path = []

    current = destination

    while current is not None:

        path.append(current)

        current = previous[current]

    # Reverse path
    path.reverse()

    return path, g_score[destination]
