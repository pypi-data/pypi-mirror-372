# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from igraph import Graph as _Graph, Vertex, VertexSeq, Edge, EdgeSeq


VERTEX_PARAMETER_TYPE = typing.Union[Vertex, str, int]


class Graph:

    def __init__(self, directed: bool, name: str):

        self._graph: _Graph = _Graph(directed=directed, graph_attrs={r'name': name})
        self._vertices: typing.Dict[str, Vertex] = {}

    def __len__(self):

        return len(self._vertices)

    def __repr__(self):

        return f'<DiGraph: {self.name}, vertices: {self._graph.vcount()}, edges: {self._graph.ecount()}>'

    @property
    def vertices(self) -> typing.Dict[str, Vertex]:

        return self._vertices

    @property
    def name(self) -> str:

        return self._graph[r'name']

    @property
    def data(self) -> _Graph:

        return self._graph

    @property
    def vertex_seq(self) -> VertexSeq:

        return self._graph.vs

    @property
    def edge_seq(self) -> EdgeSeq:

        return self._graph.es

    def clear(self):

        self._graph.clear()
        self._vertices.clear()

    def find_vertex(self, name: str) -> Vertex:

        return self._vertices.get(name)

    def find_vertices(self, names: typing.List[str]) -> typing.List[Vertex]:

        return [self._vertices.get(name) for name in names if name in self._vertices]

    def add_vertex(self, name: str = None, **kwargs) -> Vertex:

        vertex = self._vertices.get(name)

        if vertex is None:
            vertex = self._vertices[name] = self._graph.add_vertex(name, **kwargs)

        return vertex

    def init_edges(self, edges: typing.List[typing.Tuple[VERTEX_PARAMETER_TYPE, VERTEX_PARAMETER_TYPE]]):

        self._graph.add_edges(edges)

    def get_edge(self, source: VERTEX_PARAMETER_TYPE, target: VERTEX_PARAMETER_TYPE) -> Edge:

        eid = self._graph.get_eid(source, target, error=False)

        if eid >= 0:
            return self._graph.es[eid]

    def add_edge(self, source: VERTEX_PARAMETER_TYPE, target: VERTEX_PARAMETER_TYPE):

        eid = self._graph.get_eid(source, target, error=False)

        if eid < 0:
            self._graph.add_edges([(source, target)])

    def del_edge(self, source: VERTEX_PARAMETER_TYPE, target: VERTEX_PARAMETER_TYPE):

        eid = self._graph.get_eid(source, target, error=False)

        if eid >= 0:
            self._graph.delete_edges(eid)

    def del_vertex_edge(self, name: str, mode=r'all'):

        vertex = self.find_vertex(name)

        if vertex is None:
            return

        if mode == r'in':
            edges = vertex.in_edges()
        elif mode == r'out':
            edges = vertex.out_edges()
        else:
            edges = vertex.all_edges()

        if edges:
            self._graph.delete_edges(edges)

    def deep_search(self, name: str, mode=r'all') -> typing.List[str]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return []

        vertices = self._graph.subcomponent(vertex.index, mode=mode)

        return [self._graph.vs[_v][r'name'] for _v in vertices if _v != vertex.index]


class DiGraph(Graph):

    def __init__(self, name: str):

        super().__init__(True, name)

    def find_in(self, name: str) -> typing.List[Vertex]:

        vertex = self.find_vertex(name)

        if vertex is not None:
            return vertex.predecessors()

    def find_out(self, name: str) -> typing.List[Vertex]:

        vertex = self.find_vertex(name)

        if vertex is not None:
            return vertex.successors()

    def find_tree(self, name: str, depth=0xff, mode=r'out') -> typing.Dict[str, typing.List[str]]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return {}

        nodes = {}
        vertices = [vertex]

        for _ in range(depth):

            vertices, _vertices = [], vertices

            for _vertex in _vertices:

                _sub_vertices = _vertex.successors() if mode == r'out' else _vertex.predecessors()

                if _sub_vertices:

                    _nodes = nodes[_vertex[r'name']] = []

                    for _sub_vertex in _sub_vertices:

                        if _sub_vertex[r'name'] not in nodes:
                            vertices.append(_sub_vertex)

                        _nodes.append(_sub_vertex[r'name'])

        return nodes
