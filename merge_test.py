import unittest
from graph_decomposition import GraphDecompositionWrapper
from osmnx import graph_from_xml

class MergeTest(unittest.TestCase):
    def test_output_shape(self):
        chicago = graph_from_xml('chicago.osm')
        gdw = GraphDecompositionWrapper(chicago)
        subgraphs, _ = gdw.decompose()
        for idx, _ in enumerate(subgraphs):
            gdw.merge(0, idx)

        self.assertEqual(len(list(chicago.nodes)), len(set([node for subgraph in gdw.subgraphs for node in subgraph.nodes])))
        self.assertEqual(len(list(chicago.nodes)), len(list(gdw.subgraphs[0].nodes)))
        self.assertEqual(len(list(chicago.edges)), len(list(gdw.subgraphs[0].edges)))

        for node in chicago.nodes:
            self.assertFalse(set(chicago.neighbors(node))^set(gdw.subgraphs[0].neighbors(node)))

if __name__ == '__main__':
    unittest.main()