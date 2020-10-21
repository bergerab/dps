import copy
from collections import defaultdict

from .exceptions import CyclicGraphException

class Graph:
    def __init__(self):
        self.edges_in = defaultdict(list)
        ''' Which vertices are connected to this vertex (the key). 
            Identifies the names of vertices that have an arrow pointing at this one. 
        '''
        self.edges_out = defaultdict(list)        
        self.vertices = set()

    def connect(self, u, v):
        '''Make a connection (an edge) from node `n1` to `n2` (directed).'''
        self.edges_in[v].append(u)
        self.edges_out[u].append(v)        
        self.vertices.add(u)
        self.vertices.add(v)

    def add_vertex(self, name):
        '''Adds a vertex to the graph with no edges'''
        self.vertices.add(name)

    def get_starting_vertices(self):
        ''' Returns all vertices that have no incoming edge. '''
        vertices = set()
        for edge in self.vertices:
            if edge not in self.edges_in or not self.edges_in[edge]:
                vertices.add(edge)
        return vertices

    def remove_edge(self, u, v):
        self.edges_out[u].remove(v)
        self.edges_in[v].remove(u)

    def has_edges(self):
        for vertex, connections in self.edges_in.items():
            if connections:
                return True
        return False

    def clone(self):
        G = Graph()
        G.edges_out = copy.deepcopy(self.edges_out)
        G.edges_in = copy.deepcopy(self.edges_in)
        G.vertices = self.vertices.copy()
        return G

    def prune(self, *vertices):
        '''
        Creates a new graph that only has the vertices in `vertices` (and also all of the connections to `vertices`).
        '''
        vertices = list(vertices)
        
        G = Graph()
        for vertex in vertices:
            G.add_vertex(vertex)
        
        work_list = vertices
        while work_list:
            u = work_list.pop()
            for v in self.edges_in[u]:
                if v not in G.edges_in[u]:
                    G.connect(v, u)
            work_list += self.edges_in[u]
        return G

    def get_topological_ordering(self):
        '''
        Kahn's Algorithm for topological sorting
        '''
        L = []
        S = list(self.get_starting_vertices())

        restore = []

        while S:
            n = S.pop()
            L.append(n)
            out_edges = list(self.edges_out[n])
            for m in out_edges:
                self.remove_edge(n, m)
                restore.append((n, m))
                if not self.edges_in[m]:
                    S.append(m)

        has_edges = self.has_edges()

        # Restore the edges that were removed
        for (n, m) in restore:
            self.connect(n, m)
                    
        if has_edges:
            raise CyclicGraphException('Topological ordering failed because graph has at least one cycle.')

        return L
