from networkx import MultiDiGraph, bfs_edges
from typing import List, Tuple, Dict
from numpy.random import randint


class GraphDecompositionWrapper:
    def __init__(self, graph: MultiDiGraph, N: int = 10):
        self.raw_graph = graph.copy()
        self.graph: MultiDiGraph = graph.copy()
        self.N: int = N 
        self.subgraphs: List[MultiDiGraph] = []
        self.multiplied_nodes: Dict[int, List[int]] = {node: [] for node in graph.nodes}
        self._check()

    def _check(self):
        assert self.N > 0, f"Subgraph size should be positive! (currently: N = {self.N})"

    def _generate_nodes(self) -> List[int]:
        nodes: List[int] = []
        while not nodes:
            start_node: int = list(self.graph.nodes)[randint(0, len(self.graph.nodes))]
            raw_edges: List[Tuple[int]] = list(bfs_edges(self.graph, start_node, depth_limit=self.N))
            nodes: List[int] = list(set([start_node] + [v for _, v in raw_edges[:(self.N-1 if len(raw_edges) > self.N-1 else len(raw_edges))]]))
        return nodes

    def _update_nodes_dictionary(self, nodes: List[int]) -> None:
        for node in nodes:
                self.multiplied_nodes[node].append(len(self.subgraphs))

    def _update_subgraphs(self, nodes: List[int]) -> None:
        self.subgraphs.append(self.graph.subgraph(nodes).copy())
                
    def _proceed_nodes_removal(self, nodes: List[int]) -> None:
        seen_graph: MultiDiGraph = self.graph.copy()
        seen_graph.remove_nodes_from(nodes)
        for node in filter(lambda node: all(temp_node not in list(self.graph.neighbors(node)) for temp_node in list(seen_graph.nodes)), nodes):
            self.graph.remove_node(node)

    def decompose(self) -> Tuple[List[MultiDiGraph], Dict[int, List[int]]]:
        while self.graph.nodes:
            new_subgraph_nodes: List[int] = self._generate_nodes()

            self._update_nodes_dictionary(new_subgraph_nodes)
            self._update_subgraphs(new_subgraph_nodes)
            self._proceed_nodes_removal(new_subgraph_nodes)

            if not self.graph.edges: break

        self.subgraphs.append(self.graph)
        return self.subgraphs, self.multiplied_nodes

    def _calculate_alphas(self) -> List[float]:
        return [sum(int(len(self.multiplied_nodes[node])>1) for node in subgraph.nodes)/subgraph.number_of_nodes() for subgraph in self.subgraphs if subgraph.number_of_nodes()]


    def _calcluate_bethas(self) -> List[float]:
        return [(len(set([neigh for node in subgraph.nodes for neigh in self.multiplied_nodes[node]]))-1)/(len(self.subgraphs)-1) for subgraph in self.subgraphs if subgraph.number_of_nodes()]


    def incorporate(self, subgraph_idx: int, node: int) -> None:
        to_remove_subgraph_idxs: List[int] = []
        for possessing_graph in filter(lambda graph_idx: graph_idx!=subgraph_idx, self.multiplied_nodes[node]):
            
            temp_nodes: List[int] = list(self.subgraphs[subgraph_idx].nodes)+[neighbour for neighbour in self.subgraphs[possessing_graph].neighbors(node)]
            new_nodes: List[int] = list(set(temp_nodes).difference(set(self.subgraphs[possessing_graph].nodes)))
            self.subgraphs[subgraph_idx] = self.graph.subgraph(list(set(temp_nodes))).copy()
            self.subgraphs[possessing_graph].remove_node(node)
            to_remove_subgraph_idxs.append(possessing_graph)
            for new_node in new_nodes:
                self.multiplied_nodes[new_node].append(possessing_graph)
        for to_remove_subgraph_idx in to_remove_subgraph_idxs:
            self.multiplied_nodes[node].remove(to_remove_subgraph_idx)

        
    def merge(self, graph_to_idx: int, graph_from_idx: int) -> None:
        if graph_from_idx == graph_to_idx:
            return
        volatile_nodes: List[int] = list(self.subgraphs[graph_from_idx].nodes).copy()
        nodes: List[int] = list(set(list(self.subgraphs[graph_to_idx].nodes).copy() + volatile_nodes))
        subgraph: MultiDiGraph = self.raw_graph.subgraph(nodes).copy()
        self.subgraphs[graph_to_idx] = subgraph
        self.subgraphs[graph_from_idx] = MultiDiGraph()
        for node in volatile_nodes:
            temp_nodes: List[int] = self.multiplied_nodes[node].copy()
            if graph_from_idx in temp_nodes:
                temp_nodes.remove(graph_from_idx)
                temp_nodes.append(graph_to_idx)          
            temp_nodes = list(set(temp_nodes[:]))
            self.multiplied_nodes[node] = temp_nodes
