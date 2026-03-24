from treeDecomp import Bag, BinaryTree, RichTreeDecomposition, RootedTree, Tree, Node, TreeDecomposition

class Vertex:
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label
    
    def __repr__(self):
        return self.label

class Graph:
    def __init__(self, vertices:list, edges:list):
        self.vertices = vertices
        self.edges = edges

    def adj(self, v1, v2):
        return set([v1,v2]) in self.edges
    
    def get_adj_verts(self, v:Vertex):
        res = []
        for e in self.edges:
            if v in e:
                for x in e:
                    res.append(x)
        res = set(res)
        if v in res:
            res.remove(v)
        return res

    def get_degree(self, v:Vertex):
        return len(self.get_adj_verts(v))

    def get_degree_dict(self):
        res = {}
        for v in self.vertices:
            res[v] = self.get_degree(v)
        return res

    def add_fill_in_edges(self, v:Vertex):
        adjecent_verts = self.get_adj_verts(v)
        for u in self.vertices:
            if u not in adjecent_verts:
                for w in self.vertices:
                    if w not in adjecent_verts:
                        self.edges.append(set([u,w]))

    def remove_vertex(self, v:Vertex):
        for e in self.edges.copy():
            #print("checking: " + str(e))
            if v in e:
                #print("removing :" + str(e))
                self.edges.remove(e)
        self.vertices.remove(v)

    def eliminate_vertex(self, v:Vertex):
        h = self.remove_vertex(v)
        h = self.add_fill_in_edges(v)
        return h

    def make_neighborhood_clique(self, v:Vertex):
        adjecent_verts = self.get_adj_verts(v)
        for u in adjecent_verts:
            for w in adjecent_verts:
                if u != w and {u, w} not in self.edges:
                    self.edges.append(set([u,w]))

def minimal_degree_ordering(g):
    ordering = []
    #print("g Vertices: " + str(g.vertices))
    h = Graph(g.vertices.copy(), [e.copy()for e in g.edges])
    for i in range(1,len(h.vertices)):
        degrees = h.get_degree_dict()
        min_deg_vert = min(degrees, key=degrees.get)
        #print("Min degree: " + min_deg_vert.label)
        ordering.append(min_deg_vert)
        #h.add_fill_in_edges(min_deg_vert)
        h.make_neighborhood_clique(min_deg_vert)
        h.remove_vertex(min_deg_vert) 
    return ordering

    
def createBags(graph:Graph, vertexList, bags):
    if (len(vertexList) == 1):
        bags[vertexList[0]] = Bag(vertexList[0].label, {vertexList[0]})
        return bags
    next_vert = vertexList[0]
    #print("Vertex 0: " + str(vertexList[0].label))
    #print(vertexList)
    #print(vertexList[0])
    bag = Bag(next_vert.label, {next_vert})
    for n in graph.get_adj_verts(next_vert):
        bag.add_vertex(n)
    bags[next_vert] = bag
    #print([x.vertices for x in bags])
    #print(graph_copy.vertices)
    
    graph.make_neighborhood_clique(next_vert)
    graph.remove_vertex(next_vert)
    
    #print("V after rem: " + str(graph.vertices))
    #print("E after rem: " + str(graph.edges))
    return createBags(graph, vertexList[1:], bags)

def permutationToTreeDecomposition(graph:Graph, vertexList):
    vertexList_copy = vertexList.copy()
    bags = createBags(graph, vertexList_copy, {})
    
    resTree = Tree(bags, [])
    for i in range(len(vertexList)):
        for j in range(i+1, len(vertexList)):
            if vertexList[j] in bags[vertexList[i]].vertices:
                resTree.add_edge(bags[vertexList[i]], bags[vertexList[j]])
                break
    #print("Edges of TD: " + str(resTree.F))
    return resTree

def tree_to_rooted_tree(tree:Tree, root_bag:Bag):
    #print("Building rooted tree with root bag: " + str(root_bag))
    #print("Tree: " + str(tree))
    node_dict = {}
    counter = 1
    
    # Create nodes for all bags
    for bag in tree.I.values():
        #print("Bag: " + str(bag))
        node_dict[bag] = Node(bag, counter, [])
        counter += 1
    
    #print("Node dict: " + str(node_dict))
    
    # Build tree structure using BFS from root (avoid cycles)
    visited = set([root_bag])
    worklist = [root_bag]
    node_list = [root_bag]
    while len(worklist) > 0:
        current_bag = worklist.pop(0)
        #print("Processing bag: " + str(current_bag))
        
        for edge in tree.F:
            if current_bag in edge:
                other_bag = (edge.copy() - set([current_bag])).pop()
                #print("Edge: " + str(edge) + " | Other bag: " + str(other_bag))
                
                if other_bag not in visited:
                    visited.add(other_bag)
                    node_dict[current_bag].add_child(node_dict[other_bag])
                    #print("Added edge from " + str(current_bag.label) + " to " + str(other_bag.label))
                    worklist.append(other_bag)
                    node_list.append(other_bag)
    
    root_node = node_dict[root_bag]
    #print("Root node: " + str(root_node.label))
    #print("Nodes: " + str(node_dict))
    #print("Node list: " + str(node_list))
    return RootedTree(root_node, [node_dict[n] for n in node_list[::-1]])


def make_binary_tree(rooted_tree:RootedTree):
    worklist = [rooted_tree.root]
    result_nodes = [rooted_tree.root]
    node_id_counter = 1000
    
    while len(worklist) > 0:
        current_node = worklist.pop(0)
        num_children = len(current_node.children)
        
        if num_children <= 2:
            # Already binary or leaf
            for child in current_node.children:
                worklist.append(child)
                result_nodes.append(child)
            continue
        
        if num_children > 2:
            # Save original children before modifying
            children = current_node.children.copy()
            current_node.children = [children[0]]  # Keep only first child
            
            # Build right-associative join chain from right to left
            # For [c0, c1, c2, c3]: keeps c0, creates join(c1, join(c2, c3))
            right_subtree = None
            for i in range(len(children) - 1, 1, -1):
                node_id_counter += 1
                if right_subtree is None:
                    # Last two children
                    right_subtree = Node(current_node.label, node_id_counter, 
                                        [children[i-1], children[i]])
                else:
                    # Chain with previous join
                    right_subtree = Node(current_node.label, node_id_counter, 
                                        [children[i-1], right_subtree])
                result_nodes.append(right_subtree)
            
            # Attach join subtree as second child
            if right_subtree:
                current_node.add_child(right_subtree)
            
            # Enqueue ALL original children for processing
            for child in children:
                worklist.append(child)
                result_nodes.append(child)
    
    return BinaryTree(rooted_tree.root, result_nodes)

def get_tree_width(tree:RootedTree):
    max_width = 0
    for node in tree.nodes:
        bag_size = len(node.label.vertices)
        if bag_size > max_width:
            max_width = bag_size
    return max_width - 1

def extended_bags(tree:RootedTree):
    # Every Bag e.g. {v1, v2} is mapped to a tuple of the size treewidth + 1,
    # where the tuple is filled with the vertices of the bag (repeatedly until the tuple is full)
    width = get_tree_width(tree)
    bag_mapping = {}
    #print("Nodes in tree: " + str(tree.nodes))
    for node in tree.nodes:
        vertices = list(node.label.vertices)
        bag_tuple = tuple(vertices[i % len(vertices)] for i in range(width + 1))
        bag_mapping[node] = bag_tuple
    return bag_mapping

def label_bags(tree:RootedTree, graph:Graph):
    # Label each bag with the edge relation of the indices of the vertices
    # in the bag, the repeating vertices and the indices of the vertices which are also in the parent bag
    # e.g. for bag (v1,v2,v1) assuming v1 and v2 are adjacent and the parent bag is (v1,v3,v4) the label would be:
    # [[(0,1), (2,1)], [(1,3)], [(0,0), (2,0)]]
    bagmapping = extended_bags(tree)
    labels = {}
    for node in tree.nodes:
        bag_tuple = bagmapping[node]
        edge_relations = []
        for i in range(len(bag_tuple)):
            for j in range(len(bag_tuple)):
                #print("Checking adjacency for bag " + str(bag_tuple) + ": " + str(bag_tuple[i]) + " and " + str(bag_tuple[j]) + " : " + str(graph.adj(bag_tuple[i], bag_tuple[j])))
                #print("Type of vertices: " + str(type(bag_tuple[i])) + " and " + str(type(bag_tuple[j])))
                if i != j and graph.adj(bag_tuple[i], bag_tuple[j]):
                    print("Adjacent vertices in bag " + str(bag_tuple) + ": " + str(bag_tuple[i]) + " and " + str(bag_tuple[j]) + "? : " + str(graph.adj(bag_tuple[i], bag_tuple[j])))
                    edge_relations.append((i, j))
        #print("Edge relations for bag " + str(bag_tuple) + ": " + str(edge_relations))
        parent = node.parent(tree.root)
        parent_indices = []
        if parent:
            parent_bag_tuple = bagmapping[parent]
            for i in range(len(bag_tuple)):
                for j in range(len(parent_bag_tuple)):
                    if bag_tuple[i] == parent_bag_tuple[j]:
                        parent_indices.append((i,j))
        repeating_vertices = []
        for i in range(len(bag_tuple)):
            for j in range(i+1, len(bag_tuple)):
                if bag_tuple[i] == bag_tuple[j]:
                    repeating_vertices.append((i,j))
        labels[node] = (edge_relations, repeating_vertices, parent_indices)
    return labels

def U(i, vert_set, tree:RootedTree, graph:Graph):
    # this function returns the set of vertices of the tree which have a vertex from the 
    # given set of vertices from the graph in the i-th position of the extended bag representation of the bag of the node
    res = set()
    extended = extended_bags(tree)
    for node in tree.nodes:
        bag_tuple = extended[node]
        if bag_tuple[i] in vert_set:
            res.add(node)
    return res

def U_all(vert_set, tree:RootedTree, graph:Graph):
    # U_all = [U(i, vert_set, tree, graph) for i in range(get_tree_width(tree) + 1)]
    return [U(i, vert_set, tree, graph) for i in range(get_tree_width(tree) + 1)]

def compute_all_labels(treewidth):
    pass
"""
def minimize_tree_decomposition(tree:RootedTree):
    # if a child bag is a subset of its parent bag, child bag (branch) is removed
    tree_nodes = tree.nodes.copy()
    print("Tree nodes before minimization: " + str([node.label for node in tree_nodes]))
    tree_root = Node(tree.root.label, tree.root.id, tree.root.children.copy())
    worklist = [tree_nodes[-1]] # start with root node
    while len(worklist) > 0:
        current_node = worklist.pop(0)
        for child in current_node.children:
            if child.label.vertices.issubset(current_node.label.vertices):
                # Remove child from tree
                current_node.children.remove(child)
                tree_nodes.remove(child)
            else:
                worklist.append(child)
    print("Tree nodes after minimization: " + str([node.label for node in tree_nodes]))
    return RootedTree(tree_root, tree_nodes)
"""
def minimize_tree_decomposition(tree: RootedTree):
    # Remove child bags that are subsets of their parent by bypassing them.
    # This preserves decomposition validity and keeps the structure a rooted tree.

    def clone_subtree(node):
        cloned = Node(node.label, node.id, [])
        for child in node.children:
            cloned.children.append(clone_subtree(child))
        return cloned

    def minimize_subtree(node):
        # First minimize descendants
        for child in node.children:
            minimize_subtree(child)

        # Then contract all subset-children under this node.
        # Repeat because promoted grandchildren may also be subsets of node.
        changed = True
        while changed:
            changed = False
            new_children = []
            for child in node.children:
                if child.label.vertices.issubset(node.label.vertices):
                    # Bypass child: attach its children directly to node
                    new_children.extend(child.children)
                    changed = True
                else:
                    new_children.append(child)
            node.children = new_children

    def collect_postorder(node, out):
        for child in node.children:
            collect_postorder(child, out)
        out.append(node)  # root ends up last, matching your current convention

    #print("Tree nodes before minimization: " + str([n.label for n in tree.nodes]))

    # Work on a cloned rooted tree to avoid accidental side effects
    minimized_root = clone_subtree(tree.root)
    minimize_subtree(minimized_root)

    minimized_nodes = []
    collect_postorder(minimized_root, minimized_nodes)

    #print("Tree nodes after minimization: " + str([n.label for n in minimized_nodes]))
    return RootedTree(minimized_root, minimized_nodes)

def make_rich_tree_decomposition(tree:RootedTree, graph:Graph):
    # Given a tree decomposition with its graph, make it rich by going
    # top down and introducing every edge (unique) in the bags it first appears in the tree decomposition
    # A dict with a mapping from Nodes to the set of edges in their bag is returned
    graph_edges = graph.edges.copy()
    graph_edges_available = graph.edges.copy()
    #print("Graph edges: " + str(graph_edges))
    edge_mapping = {}
    worklist = [tree.nodes[-1]] # start with root node
    while len(worklist) > 0:
        node = worklist.pop(0)
        edge_mapping[node] = set()
        for e in graph_edges:
            #print("Checking edge " + str(e) + " for bag " + str(node.label.vertices))
            if e.issubset(node.label.vertices) and e in graph_edges_available:
                #print("Adding edge " + str(e) + " to bag " + str(node.label.vertices))
                edge_mapping[node].add(frozenset(e))
                graph_edges_available.remove(e)
        for child in node.children:
            worklist.append(child)

    return edge_mapping


if __name__ == "__main__":
    a = Vertex("1")
    b = Vertex("2")
    c = Vertex("3")
    d = Vertex("4")
    e = Vertex("5")
    f = Vertex("6")
    g = Vertex("7")
    h = Vertex("8")

    #Paper1
    graph = Graph([a,b,c,d,e,f,g,h],[{a,b},{a,c},{b,f},{f,g},{g,h},{b,e},{b,c},{c,d},{d,e},{e,h},{c,e},{e,g},{b,g}])
    graph_copy = Graph(graph.vertices.copy(), graph.edges.copy())
    print("Adj a and b adjacent? : " + str(graph.adj(a,b)))
    print("Adj b and a adjacent? : " + str(graph.adj(b,a)))

    #Paper2
    v1 = Vertex("v1")
    v2 = Vertex("v2")
    v3 = Vertex("v3")
    v4 = Vertex("v4")
    v5 = Vertex("v5")
    v6 = Vertex("v6")
    v7 = Vertex("v7")
    v8 = Vertex("v8")
    v9 = Vertex("v9")
    v10 = Vertex("v10")

    n1 = Vertex("n1")
    n2 = Vertex("n2")
    n3 = Vertex("n3")
    n4 = Vertex("n4")
    n5 = Vertex("n5")
    n6 = Vertex("n6")
    n7 = Vertex("n7")
    n8 = Vertex("n8")
    n9 = Vertex("n9")
    n10 = Vertex("n10")
    n11 = Vertex("n11")

    test_binary_graph = Graph([n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11], 
                              [{n1,n2}, {n1,n3}, {n2,n3}, {n1,n4},
                               {n3,n4}, {n4,n5}, {n4,n7}, {n4,n8},
                               {n5,n6}, {n5,n9}, {n6,n8}, {n6,n9},
                               {n7,n8}, {n7,n9}, {n10,n7}, {n10,n9},
                               {n11,n8}, {n11,n5}])
    
    test_binary_graph_copy = Graph(test_binary_graph.vertices.copy(), [e.copy() for e in test_binary_graph.edges])

    graph2 = Graph([v1,v2,v3,v4,v5,v6,v7,v8,v9,v10],[{v1,v2},{v2,v3},{v7,v10},{v1,v3},{v1,v4},{v3,v4},{v4,v5},{v4,v7},{v4,v8},
                                                     {v5,v6},{v5,v9},{v6,v8},{v6,v9},{v7,v8},{v7,v9}, {v9,v10}])
    graph2_copy = Graph(graph2.vertices.copy(), graph2.edges.copy())
    #print("a and b adjacent? : " + str(graph.adj(a,b)))
    #print("a and h adjacent? : " + str(graph.adj(a,h)))
    #print("Neighbours of a: " + str([x.label for x in graph.get_adj_verts(a)]))
    #print("Neighbours of e: " + str([x.label for x in graph.get_adj_verts(e)]))
    #for v in graph.vertices:
    #    print("#Neigbours of " + v.label + " : " + str(graph.get_degree(v)))
    #print(graph2.get_degree_dict())
    #print([x.label for x in graph.mininal_degree_ordering()])
    #print(graph.vertices)
    #print([x.label for x in minimal_degree_ordering(graph2)])
    #print(permutationToTreeDecomposition(graph2, minimal_degree_ordering(graph2), []))
    #print(graph2_copy.edges)
    """
    tree = permutationToTreeDecomposition(test_binary_graph_copy, minimal_degree_ordering(test_binary_graph_copy))
    treeDecomp = TreeDecomposition(tree.I, tree)
    rooted = tree_to_rooted_tree(tree, tree.I[n5])
    print("#Nodes in rooted tree: " + str(len(rooted.nodes)))
    print("Rooted tree: " + str(rooted))
    binary_tree = make_binary_tree(rooted)
    print("#Nodes in binary tree: " + str(len(binary_tree.nodes)))
    print("Binary tree: " + str(binary_tree))
    print("Tree Structure Type: " + str(type(binary_tree)))
    tree_width = get_tree_width(binary_tree)
    print("Tree width: " + str(tree_width))
    bagmapping = extended_bags(binary_tree)
    print("Bag mapping: " + str(bagmapping))
    labels = label_bags(binary_tree, test_binary_graph_copy)
    print([str(bagmapping[k]) + " : " + str(v) for k,v in labels.items()])
    u = U(2, {n1, n4}, binary_tree, test_binary_graph_copy)
    print("U(2, {n1, n4}): " + str(u))
    u_all = U_all({n1, n4}, binary_tree, test_binary_graph_copy)
    print("U_all({n1, n4}): " + str(u_all))
    for i in u_all:
        for j in list(i):
            print(extended_bags(binary_tree)[j])
        print("----") 
    """
    tree = permutationToTreeDecomposition(graph_copy, minimal_degree_ordering(graph_copy))
    treeDecomp = TreeDecomposition(tree.I, tree)
    rooted = tree_to_rooted_tree(tree, tree.I[b])
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
    rich_tree.create_FHR_term()


    #binary_tree = make_binary_tree(rooted)
    #print("#Nodes in binary tree: " + str(len(binary_tree.nodes)))
    #print("Binary tree: " + str(binary_tree))
    #print("Tree Structure Type: " + str(type(binary_tree)))
    #tree_width = get_tree_width(binary_tree)
    #print("Tree width: " + str(tree_width))
    #bagmapping = extended_bags(binary_tree)
    #print("Bag mapping: " + str(bagmapping))
    #labels = label_bags(binary_tree, graph)
    #print([str(bagmapping[k]) + " : " + str(v) for k,v in labels.items()])
    #u = U(2, {a, d}, binary_tree, graph)
    #print("U(2, {a, d}): " + str(u))
    #u_all = U_all({a, d}, binary_tree, graph)
    #print("U_all({a, d}): " + str(u_all))
    #for i in u_all:
    #   for j in list(i):
    #       print(extended_bags(binary_tree)[j])
    #   print("----") 