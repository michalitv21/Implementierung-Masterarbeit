import tempfile, os
from StringCase.utils import gen_courcelle_alphabet
from courcelleMSOtoNTA import courcelle_MSO_to_NTA_Parser
from graphLib import Graph, Vertex, make_rich_tree_decomposition, minimize_tree_decomposition, minimize_tree_decomposition, permutationToTreeDecomposition, tree_to_rooted_tree, minimal_degree_ordering
from treeDecomp import RichTreeDecomposition, TreeDecomposition
from graph_loader import load_graph_from_adjacency_list as _load_single_graph
from treeDecomp import treeWidth_from_rooted_tree

def load_graphs_from_file(file_path):
    """Split a multi-graph adjacency list file into individual graphs using graph_loader."""
    graphs = []
    current_block = []
    try:
        with open(file_path, 'r') as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    if current_block:
                        # Write block to a temp file and load via graph_loader
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.lst', delete=False) as tmp:
                            tmp.write('\n'.join(current_block))
                            tmp_path = tmp.name
                        graph = _load_single_graph(tmp_path)
                        os.unlink(tmp_path)
                        if graph is not None:
                            graphs.append(graph)
                        current_block = []
                    continue
                if not line.startswith('#'):
                    current_block.append(line)
        # Flush last block
        if current_block:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.lst', delete=False) as tmp:
                tmp.write('\n'.join(current_block))
                tmp_path = tmp.name
            graph = _load_single_graph(tmp_path)
            os.unlink(tmp_path)
            if graph is not None:
                graphs.append(graph)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error loading graphs from file: {e}")
    return graphs
    
if __name__ == "__main__":
    #file_path1 = "list_293_graphs.lst"
    #file_path2 = "list_402_graphs.lst"
    
    file_path1 = "list_887_graphs.lst"
    file_path2 = "list_1589_graphs.lst"
    
    graphs1 = load_graphs_from_file(file_path1)
    graphs2 = load_graphs_from_file(file_path2)
    
    #formula = "∃X(∃Y(and(and(and(vertices(X),singleton(X)),vertices(Y)),subset(X,Y))))"
    formula = "∃X(∃Y(bipartite(X,Y)))"
    #formula = "∃X(∃Y(and(and(biVert(X,Y),closure(X)),closure(Y))))"
    #formula = "∃X(∃Y(and(biVert(X,Y),and(and(sub(X),noEdgeInv(X)),and(sub(Y),noEdgeInv(Y))))))"
    #formula = "∃X(and(sub(X),noEdgeInv(X)))"

    treewidth = 3
    #k = 2
    k = formula.count("∃") + formula.count("∀")
    print("k:", k)
    alphabet = gen_courcelle_alphabet(treewidth, k)

    parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)


    

    ast = parser.build_ast(formula)
    automaton = parser.build_automaton(ast)

    res1 = []
    res2 = []

    #print(automaton.states)

    for i, graph in enumerate(graphs1):
        graph_copy = Graph(graph.vertices.copy(), [e.copy() for e in graph.edges])
        ordering = minimal_degree_ordering(graph_copy)
        tree = permutationToTreeDecomposition(graph_copy, ordering)
        treeDecomp = TreeDecomposition(tree.I, tree)
        rooted = tree_to_rooted_tree(tree, tree.I[graph.vertices[0]])
        decomp_treeWidth = treeWidth_from_rooted_tree(rooted)
        #print(f"Graph {i+1} treewidth: {decomp_treeWidth}")
        if decomp_treeWidth > treewidth or decomp_treeWidth < 1:
             #print(f"Graph {i+1} exceeds treewidth {treewidth}, skipping.")
             res1.append("twd error")  # Assume False for graphs that exceed treewidth
             continue
        minimized_tree = rooted #minimize_tree_decomposition(rooted)
        rich_tree_mapping = make_rich_tree_decomposition(minimized_tree, graph)
        rich_tree = RichTreeDecomposition(minimized_tree, rich_tree_mapping)
        FHR_tree = rich_tree.create_FHR_term()
        result = automaton.nta_run(FHR_tree)
        res1.append(result)
        if result == False:
            print(f"Graph {i+1} wrong bipartite result:", result)
            print("Graph vertices:", graph.vertices)
            print("Graph edges:", graph.edges)


    for i, graph in enumerate(graphs2):
        graph_copy = Graph(graph.vertices.copy(), [e.copy() for e in graph.edges])
        ordering = minimal_degree_ordering(graph_copy)
        tree = permutationToTreeDecomposition(graph_copy, ordering)
        treeDecomp = TreeDecomposition(tree.I, tree)
        rooted = tree_to_rooted_tree(tree, tree.I[graph.vertices[0]])
        decomp_treeWidth = treeWidth_from_rooted_tree(rooted)
        #print(f"Graph {i+1} treewidth: {decomp_treeWidth}")
        if decomp_treeWidth > treewidth or decomp_treeWidth < 1:
             #print(f"Graph {i+1} exceeds treewidth {treewidth}, skipping.")
             res2.append("twd error")  # Assume False for graphs that exceed treewidth
             continue
        minimized_tree = rooted #minimize_tree_decomposition(rooted)
        rich_tree_mapping = make_rich_tree_decomposition(minimized_tree, graph)
        rich_tree = RichTreeDecomposition(minimized_tree, rich_tree_mapping)
        FHR_tree = rich_tree.create_FHR_term()
        result = automaton.nta_run(FHR_tree)
        res2.append(result)
        if result == True:
             print(f"Graph {i+1} wrong bipartite result:", result)

    print("Results for file 1: ")
    print("Length:", len(res1))
    print("#True:", sum(1 for r in res1 if r == True))
    print("#False:", sum(1 for r in res1 if r == False))
    print("#TWD error:", sum(1 for r in res1 if r == "twd error"))
    print("Results for file 2: ")
    print("Length:", len(res2))
    print("#True:", sum(1 for r in res2 if r == True))
    print("#False:", sum(1 for r in res2 if r == False))
    print("#TWD error:", sum(1 for r in res2 if r == "twd error"))
