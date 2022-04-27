import numpy as np
from numpy import ndarray


class Graph:
    _vertices: set
    _edges: set

    def __init__(self, vertices=[], edges=[]):
        self._vertices = set(vertices)
        self._edges = set(edges)

    def add_vertex(self, vertex):
        if vertex not in self._vertices:
            self._vertices.add(vertex)

    def add_edge(self, edge: tuple):
        if edge not in self._edges:
            self._edges.add(edge)
            for v in edge:
                self.add_vertex(vertex=v)

    @property
    def n(self):
        return len(self._vertices)

    @property
    def m(self):
        return len(self._edges)

    def matrix(self) -> ndarray:
        matrix = np.zeros((self.n, self.n), dtype=int)
        v_list = list(self._vertices)
        for edge in self._edges:
            idx_x = v_list.index(edge[0])
            idx_y = v_list.index(edge[1])
            matrix[idx_x][idx_y] += 1
            matrix[idx_y][idx_x] += 1
        return matrix
