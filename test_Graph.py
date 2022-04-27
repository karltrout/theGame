from unittest import TestCase

from Graph import Graph


class Test(TestCase):
    def setUp(self) -> None:
        self.graph = Graph(vertices=[0, 1, 2], edges=[(0, 1), (1, 2)])

    def test_graph(self):
        assert self.graph.n == 3

    def test_add_vertex_no_edge(self):
        self.graph.add_vertex(4)
        assert self.graph.n == 4 and self.graph.m == 2
        print([self.graph.matrix()])

    def test_add_edge(self):
        edge = (1, 2)
        g = Graph()
        g.add_edge(edge=edge)
        assert g.n == 2 and g.m == 1
        # try again
        edge = (2, 3)
        g.add_edge(edge=edge)
        assert g.n == 3 and g.m == 2

    def test_matrix(self):
        print([self.graph.matrix()])



