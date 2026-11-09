import heapq


def dijkstra(graph, start, destination):

    # Store shortest distance from start to every node
    distances = {}

    # Store previous node for reconstructing the path
    previous = {}

    for node in graph.nodes:

        distances[node] = float("inf")
        previous[node] = None

    # Distance from start to itself is 0
    distances[start] = 0

    # Priority queue
    priority_queue = []

    heapq.heappush(
        priority_queue,
        (0, start)
    )

    # Continue until priority queue becomes empty
    while priority_queue:

        current_distance, current_node = heapq.heappop(
            priority_queue
        )

        # Ignore old/worse distance
        if current_distance > distances[current_node]:
            continue

        # Destination reached
        if current_node == destination:
            break

        # Visit all neighboring nodes
        for neighbor in graph.neighbors(current_node):

            edge_data = graph.get_edge_data(
                current_node,
                neighbor
            )

            # OSMnx graph can have multiple edges
            # between two nodes
            weight = min(
                data.get("length", 1)
                for data in edge_data.values()
            )

            # Calculate new distance
            new_distance = (
                current_distance + weight
            )

            # If shorter path is found
            if new_distance < distances[neighbor]:

                distances[neighbor] = new_distance

                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance,
                        neighbor
                    )
                )

    # No route found
    if distances[destination] == float("inf"):

        return None, float("inf")

    # Reconstruct path
    path = []

    current = destination

    while current is not None:

        path.append(current)

        current = previous[current]

    # Reverse path
    path.reverse()

    return path, distances[destination]