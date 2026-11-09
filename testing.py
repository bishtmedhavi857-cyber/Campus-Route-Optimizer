
import unittest
import networkx as nx

from algorithms.dijkstra import dijkstra
from algorithms.astar import astar


class TestRouteAlgorithms(unittest.TestCase):

    def setUp(self):
        # MultiDiGraph matches the structure of an OSMnx graph
        self.graph = nx.MultiDiGraph()

        # Coordinates are kept equal so the A* heuristic is zero
        for node in range(1, 6):
            self.graph.add_node(
                node,
                x=0.0,
                y=0.0
            )

        self.graph.add_edges_from([
            (1, 2, {"length": 1}),
            (1, 3, {"length": 4}),
            (2, 3, {"length": 1}),
            (2, 4, {"length": 5}),
            (3, 4, {"length": 1}),
            (4, 5, {"length": 2})
        ])

    def check_valid_route(self, path, start, destination):
        self.assertIsNotNone(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], destination)

        for i in range(len(path) - 1):
            self.assertTrue(
                self.graph.has_edge(path[i], path[i + 1])
            )

    def test_dijkstra_shortest_path(self):
        path, distance = dijkstra(self.graph, 1, 5)

        self.check_valid_route(path, 1, 5)
        self.assertEqual(distance, 5)

    def test_astar_shortest_path(self):
        path, distance = astar(self.graph, 1, 5)

        self.check_valid_route(path, 1, 5)
        self.assertEqual(distance, 5)

    def test_same_start_and_destination(self):
        for algorithm in (dijkstra, astar):
            path, distance = algorithm(self.graph, 1, 1)

            self.assertEqual(path, [1])
            self.assertEqual(distance, 0)

    def test_unreachable_destination(self):
        # Node 10 has no connecting edges
        self.graph.add_node(10, x=0.0, y=0.0)

        for algorithm in (dijkstra, astar):
            path, distance = algorithm(self.graph, 1, 10)

            self.assertIsNone(path)
            self.assertEqual(distance, float("inf"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
