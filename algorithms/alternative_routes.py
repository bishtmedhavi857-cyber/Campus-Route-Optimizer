
import heapq
import itertools
import networkx as nx


# --------------------------------------------------
# 1. DIJKSTRA'S SHORTEST PATH
# --------------------------------------------------

def shortest_path(
    graph,
    source,
    destination,
    banned_nodes=None,
    banned_edges=None
):
    """
    Finds the shortest path using Dijkstra's algorithm.

    banned_nodes: Nodes temporarily excluded.
    banned_edges: Edges temporarily excluded.
    """

    if banned_nodes is None:
        banned_nodes = set()

    if banned_edges is None:
        banned_edges = set()

    if source not in graph or destination not in graph:
        return None

    if source in banned_nodes or destination in banned_nodes:
        return None

    # Priority queue
    counter = itertools.count()

    priority_queue = []

    heapq.heappush(
        priority_queue,
        (0, next(counter), source)
    )

    distances = {source: 0}
    previous = {}

    while priority_queue:

        current_distance, _, current_node = heapq.heappop(
            priority_queue
        )

        # Ignore outdated queue entries
        if current_distance > distances.get(
            current_node, float("inf")
        ):
            continue

        # Destination reached
        if current_node == destination:

            path = []
            node = destination

            while node != source:

                path.append(node)

                if node not in previous:
                    return None

                node = previous[node]

            path.append(source)

            return path[::-1]

        # Explore neighbouring nodes
        for neighbour in graph.neighbors(current_node):

            if neighbour in banned_nodes:
                continue

            if (current_node, neighbour) in banned_edges:
                continue

            weight = float(
                graph[current_node][neighbour]["weight"]
            )

            new_distance = current_distance + weight

            if new_distance < distances.get(
                neighbour, float("inf")
            ):

                distances[neighbour] = new_distance

                previous[neighbour] = current_node

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance,
                        next(counter),
                        neighbour
                    )
                )

    return None


# --------------------------------------------------
# 2. CALCULATE TOTAL PATH DISTANCE
# --------------------------------------------------

def path_distance(graph, path):
    """
    Calculates the total distance of a path.
    """

    if not path or len(path) < 2:
        return 0.0

    total_distance = 0.0

    for i in range(len(path) - 1):

        u = path[i]
        v = path[i + 1]

        if not graph.has_edge(u, v):
            return float("inf")

        total_distance += float(
            graph[u][v]["weight"]
        )

    return total_distance


# --------------------------------------------------
# 3. YEN'S K-SHORTEST PATHS ALGORITHM
# --------------------------------------------------

def yen_k_shortest_paths(
    graph,
    source,
    destination,
    k=3
):
    """
    Finds up to K shortest loop-free paths.

    Parameters:
        graph       : Weighted NetworkX graph
        source      : Starting node
        destination : Destination node
        k           : Number of paths required

    Returns:
        List of paths ordered by increasing distance.
    """

    if k <= 0:
        return []

    if source not in graph or destination not in graph:
        return []

    if source == destination:
        return [[source]]

    # First shortest path
    first_path = shortest_path(
        graph,
        source,
        destination
    )

    if first_path is None:
        return []

    # Accepted paths
    accepted_paths = [first_path]

    accepted_set = {
        tuple(first_path)
    }

    # Candidate paths
    candidate_heap = []

    candidate_set = set()

    counter = itertools.count()

    # Generate additional paths
    for _ in range(1, k):

        previous_path = accepted_paths[-1]

        # Examine each node of the previous path
        for i in range(len(previous_path) - 1):

            # Root path
            root_path = previous_path[:i + 1]

            banned_edges = set()

            # Temporarily remove edges used by
            # accepted paths sharing the same root
            for path in accepted_paths:

                if (
                    len(path) > i + 1
                    and path[:i + 1] == root_path
                ):

                    banned_edges.add(
                        (path[i], path[i + 1])
                    )

            # Avoid revisiting root nodes
            banned_nodes = set(root_path[:-1])

            # Spur node
            spur_node = root_path[-1]

            # Find spur path
            spur_path = shortest_path(
                graph,
                spur_node,
                destination,
                banned_nodes=banned_nodes,
                banned_edges=banned_edges
            )

            if spur_path is None:
                continue

            # Combine root and spur paths
            total_path = (
                root_path[:-1] + spur_path
            )

            path_tuple = tuple(total_path)

            # Avoid duplicate paths
            if (
                path_tuple not in accepted_set
                and path_tuple not in candidate_set
            ):

                distance = path_distance(
                    graph,
                    total_path
                )

                if distance == float("inf"):
                    continue

                heapq.heappush(
                    candidate_heap,
                    (
                        distance,
                        next(counter),
                        total_path
                    )
                )

                candidate_set.add(path_tuple)

        # No more alternative paths
        if not candidate_heap:
            break

        # Select the shortest candidate
        distance, _, next_path = heapq.heappop(
            candidate_heap
        )

        accepted_paths.append(next_path)

        accepted_set.add(
            tuple(next_path)
        )

    return accepted_paths


# --------------------------------------------------
# 4. PREPARE CAMPUS GRAPH
# --------------------------------------------------

def prepare_campus_graph(original_graph):
    """
    Converts an OSMnx MultiDiGraph into a
    weighted NetworkX DiGraph.

    Keeps the shortest edge between two nodes.
    """

    graph = nx.DiGraph()

    graph.add_nodes_from(original_graph.nodes(data=True))

    for u, v, data in original_graph.edges(data=True):

        distance = float(
            data.get("length", 1)
        )

        if (
            not graph.has_edge(u, v)
            or distance < graph[u][v]["weight"]
        ):

            graph.add_edge(
                u,
                v,
                weight=distance
            )

    return graph


# --------------------------------------------------
# 5. DISPLAY ALTERNATIVE ROUTES
# --------------------------------------------------

def display_routes(graph, routes):
    """
    Prints all calculated alternative routes
    with their distances.
    """

    if not routes:

        print("No alternative routes available.")

        return

    print("\n========== ALTERNATIVE ROUTES ==========")

    for index, route in enumerate(
        routes,
        start=1
    ):

        distance = path_distance(
            graph,
            route
        )

        print(f"\nRoute {index}")

        print("Path:", " -> ".join(
            str(node) for node in route
        ))

        print(f"Distance: {distance:.2f} metres")

    print("\n========================================")


# --------------------------------------------------
# 6. TESTING
# --------------------------------------------------

if __name__ == "__main__":

    # Create a sample weighted graph
    test_graph = nx.DiGraph()

    test_graph.add_weighted_edges_from([
        ("A", "B", 100),
        ("B", "D", 150),
        ("A", "C", 120),
        ("C", "D", 180),
        ("A", "E", 200),
        ("E", "D", 200),
        ("B", "C", 80),
        ("C", "E", 100)
    ])

    # Select source and destination
    source = "A"
    destination = "D"

    # Calculate three routes
    routes = yen_k_shortest_paths(
        test_graph,
        source,
        destination,
        k=3
    )

    # Display results
    display_routes(
        test_graph,
        routes
    )
