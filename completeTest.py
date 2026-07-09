from StringCase.utils import gen_courcelle_alphabet
from courcelleAutomataConstruction import *
from courcelleMSOtoNTA import courcelle_MSO_to_NTA_Parser
from graphLib import Graph, Vertex, make_rich_tree_decomposition, minimal_degree_ordering, minimize_tree_decomposition, permutationToTreeDecomposition, tree_to_rooted_tree
from treeDecomp import RichTreeDecomposition, TreeDecomposition

treewidth = 2
k = 2
alphabet = gen_courcelle_alphabet(treewidth, k)
print(alphabet)

a = Vertex("1")
b = Vertex("2")
c = Vertex("3")
d = Vertex("4")
e = Vertex("5")
f = Vertex("6")
g = Vertex("7")
h = Vertex("8")

a2 = Vertex("1")
b2 = Vertex("2")
c2 = Vertex("3")
d2 = Vertex("4")

v1 = Vertex("1")
v2 = Vertex("2")
v3 = Vertex("3")


#Wikipedia
graph = Graph([v1,v2,v3],[{v1,v2},{v2,v3},{v3,v1}])
graph_copy = Graph(graph.vertices.copy(), graph.edges.copy())
print("Graph: " + str(graph))


graph3 = Graph([a,b,c,d,e,f,g,h],[{a,b},{a,c},{b,f},{f,g},{g,h},{b,e},{b,c},{c,d},{d,e},{e,h},{c,e},{e,g},{b,g}])
graph_copy3 = Graph(graph3.vertices.copy(), graph3.edges.copy())

graph2 = Graph([a2,b2,c2,d2],[{a2,b2},{b2,c2},{c2,d2},{d2,a2}])
graph2_copy = Graph(graph2.vertices.copy(), graph2.edges.copy())

parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)

formula = "∃X(∃Y(bipartite(X,Y)))"

ast = parser.build_ast(formula)
print("AST: " + str(ast))
automaton = parser.build_automaton(ast)


tree = permutationToTreeDecomposition(graph_copy, minimal_degree_ordering(graph_copy))
print("Tree: " + str(tree))
#treeDecomp = TreeDecomposition(tree.I, tree)
#print("Tree Decomp: " + str(treeDecomp))
rooted = tree_to_rooted_tree(tree, tree.I[v1])
print("#Nodes in rooted tree: " + str(len(rooted.nodes)))
print("Rooted tree: " + str(rooted))
minimized_tree = minimize_tree_decomposition(rooted)
print("Minimized rooted tree: " + str(minimized_tree))
rich_tree_mapping = make_rich_tree_decomposition(minimized_tree, graph)
rich_tree = RichTreeDecomposition(minimized_tree, rich_tree_mapping)

rich_tree.print_tree()
rich_tree.print_mapping()
rich_tree.print_treeWidth()
rich_tree.print_sources()
print("Sources dict: " + str(rich_tree.create_sources_dict()))
FHR_tree = rich_tree.create_FHR_term()
print(FHR_tree)
'''
tree2 = permutationToTreeDecomposition(graph2_copy, minimal_degree_ordering(graph2_copy))
treeDecomp2 = TreeDecomposition(tree2.I, tree2)
rooted2 = tree_to_rooted_tree(tree2, tree2.I[v1])
minimized_tree2 = minimize_tree_decomposition(rooted2)
rich_tree_mapping2 = make_rich_tree_decomposition(minimized_tree2, graph2)
rich_tree2 = RichTreeDecomposition(minimized_tree2, rich_tree_mapping2)
FHR_tree2 = rich_tree2.create_FHR_term()


print("FHR tree: " + str(FHR_tree))
print("FHR tree 2: " + str(FHR_tree2)) 

print("")
'''
print("-------------------------------")
print("Final Test 1: Assume False!")
print("Testgraph, bipartite:", automaton.nta_run(FHR_tree))
print("--------------------------------")
'''
print("Final Test 2: Assume True!")
print("Testgraph, bipartite:", automaton.nta_run(FHR_tree2))
'''