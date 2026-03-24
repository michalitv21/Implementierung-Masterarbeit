from StringCase.utils import gen_courcelle_alphabet
from courcelleMSOtoNTA import courcelle_MSO_to_NTA_Parser
from graphLib import Graph, Vertex, make_rich_tree_decomposition, minimize_tree_decomposition, minimize_tree_decomposition, permutationToTreeDecomposition, tree_to_rooted_tree, minimal_degree_ordering
from treeDecomp import RichTreeDecomposition, TreeDecomposition

def build_graph_from_block(adjacency_map):
        vertices_dict = {}

        # Create vertex objects for all keys and neighbors in this block
        for vertex_label, neighbors in adjacency_map.items():
            if vertex_label not in vertices_dict:
                vertices_dict[vertex_label] = Vertex(vertex_label)
            for neighbor in neighbors:
                if neighbor not in vertices_dict:
                    vertices_dict[neighbor] = Vertex(neighbor)

        # Create unique edges
        edges = []
        processed_edges = set()
        for vertex_label, neighbors in adjacency_map.items():
            for neighbor in neighbors:
                edge_key = tuple(sorted([vertex_label, neighbor]))
                if edge_key not in processed_edges:
                    edges.append({vertices_dict[vertex_label], vertices_dict[neighbor]})
                    processed_edges.add(edge_key)

        return Graph(list(vertices_dict.values()), edges)

def load_graph_from_adjacency_list(file_path):
    
    graphs = []
    adjacency_map = {}
    
    try:
        with open(file_path, 'r') as f:
            for raw_line in f:
                line = raw_line.strip()

                # Graph separator: close current block and start a new graph
                if not line:
                    if adjacency_map:
                        graphs.append(build_graph_from_block(adjacency_map))
                        adjacency_map = {}
                    continue

                # Skip comments
                if line.startswith('#'):
                    continue

                parts = line.split()
                if not parts:
                    continue

                vertex_label = parts[0].rstrip(':')
                neighbors = parts[1:]
                adjacency_map[vertex_label] = neighbors

        # Flush the final graph block if file does not end with an empty line
        if adjacency_map:
            graphs.append(build_graph_from_block(adjacency_map))

        return graphs
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error loading graph from file: {e}")
        return []
    
if __name__ == "__main__":
    file_path1 = "list_293_graphs.lst"
    file_path2 = "list_402_graphs.lst"
    graphs1 = load_graph_from_adjacency_list(file_path1)
    graphs2 = load_graph_from_adjacency_list(file_path2)
    
    v1 = Vertex("1")
    v2 = Vertex("2")
    v3 = Vertex("3")

    graphs2.append(Graph([v1, v2, v3], 
                         [{v1, v2}, 
                          {v2, v3}, 
                          {v1, v3}]))

    treewidth = 2
    k = 2
    alphabet = gen_courcelle_alphabet(treewidth, k)

    parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)

    formula = "∃X(∃Y(bipartite(X,Y)))"

    ast = parser.build_ast(formula)
    automaton = parser.build_automaton(ast)

    res1 = []
    res2 = []

    for i, graph in enumerate(graphs1):
        #print(f"Graph {i+1}:")
        #print("Vertices:", [v.label for v in graph.vertices])
        #print("Edges:", [{v.label for v in edge} for edge in graph.edges])
        graph_copy = Graph(graph.vertices.copy(), graph.edges.copy())
        tree = permutationToTreeDecomposition(graph_copy, minimal_degree_ordering(graph_copy))
        treeDecomp = TreeDecomposition(tree.I, tree)
        rooted = tree_to_rooted_tree(tree, tree.I[graph.vertices[0]])
        minimized_tree = minimize_tree_decomposition(rooted)
        rich_tree_mapping = make_rich_tree_decomposition(minimized_tree, graph)
        rich_tree = RichTreeDecomposition(minimized_tree, rich_tree_mapping)
        FHR_tree = rich_tree.create_FHR_term()
        result = automaton.nta_run(FHR_tree)
        res1.append(result)
        print(f"Graph {i+1} bipartite:", result)


    for i, graph in enumerate(graphs2):
        #print(f"Graph {i+1}:")
        #print("Vertices:", [v.label for v in graph.vertices])
        #print("Edges:", [{v.label for v in edge} for edge in graph.edges])
        graph_copy = Graph(graph.vertices.copy(), graph.edges.copy())
        tree = permutationToTreeDecomposition(graph_copy, minimal_degree_ordering(graph_copy))
        treeDecomp = TreeDecomposition(tree.I, tree)
        rooted = tree_to_rooted_tree(tree, tree.I[graph.vertices[0]])
        minimized_tree = minimize_tree_decomposition(rooted)
        rich_tree_mapping = make_rich_tree_decomposition(minimized_tree, graph)
        rich_tree = RichTreeDecomposition(minimized_tree, rich_tree_mapping)
        FHR_tree = rich_tree.create_FHR_term()
        result = automaton.nta_run(FHR_tree)
        res2.append(result)
        print(f"Graph {i+1} bipartite:", result)

    print("Results for file 1: ")
    print("Length:", len(res1))
    print("#True:", sum(res1))
    print("#False:", len(res1) - sum(res1))
    print("Results for file 2: ")
    print("Length:", len(res2))
    print("#True:", sum(res2))
    print("#False:", len(res2) - sum(res2))