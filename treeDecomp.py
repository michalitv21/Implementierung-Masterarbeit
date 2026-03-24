
def treeWidth_from_rooted_tree(rooted_tree:RootedTree):
    # Compute the tree width of a rooted tree decomposition
    max_bag_size = 0
    for node in rooted_tree.nodes:
        bag_size = len(node.label.vertices)
        if bag_size > max_bag_size:
            max_bag_size = bag_size
    return max_bag_size - 1

class Bag:
    def __init__(self, label, vertices:set):
        self.label = label
        self.vertices = vertices if isinstance(vertices, set) else set(vertices)
        
        
    def add_vertex(self, v):
        self.vertices.add(v)

    def __str__(self):
        return str(self.vertices)

    def __repr__(self):
        return str(self.vertices)

class Tree:
    def __init__(self, I, F):
        self.I = I
        self.F = F

    def __str__(self):
        return "bags: " + str(self.I) +"\nedges: " + str(self.F)

    def __repr__(self):
        return "bags: " + str(self.I) +"\nedges: " + str(self.F)

    def add_edge(self, b1:Bag, b2:Bag):
        self.F.append(set([b1,b2]))


class TreeDecomposition:
    def __init__(self, bags, tree:Tree):
        self.bags = bags
        self.tree = tree

    def __str__(self):
        return "bags: " + str(self.bags) +"\nedges: " + str(self.tree.F)

    def __repr__(self):
        return "bags: " + str(self.bags) +"\nedges: " + str(self.tree.F)
    
    def combine_bags(self, into, remove):
        # Combine the vertices of remove into into
        into.vertices = into.vertices.union(remove.vertices)
        # Update tree edges
        for e in self.tree.F.copy():
            if remove in e:
                other_bag = (e - set([remove])).pop()
                self.tree.F.remove(e)
                if other_bag != into:
                    self.tree.add_edge(into, other_bag)
        # Remove the bag
        if remove in self.bags:
            self.bags.remove(remove)
        if remove in self.tree.I:
            del self.tree.I[remove.label]

class Node():
    def __init__(self, label, id, children:list):
        self.label = label
        self.id = id
        self.children = children

    def __str__(self):
        return (str(self.label) + "(" + ", ".join([str(c) for c in self.children]) + ")")
        #label is Bag then we need the label of the bag

    def add_child(self, child:Node):
        self.children.append(child)
    
    def remove_child(self, child:Node):
        self.children.remove(child)

    def is_leaf(self):
        return len(self.children) == 0

    def parent(self, root):
        # Find the parent of this node in the tree rooted at root
        if self == root:
            return None
        worklist = [root]
        while worklist:
            current = worklist.pop()
            for child in current.children:
                if child == self:
                    return current
                worklist.append(child)
        return None

class RootedTree():
    def __init__(self, root:Node, nodes):
        self.root = root
        self.nodes = nodes
        # Add contruction of tree with parent - children relation
    def __str__(self):
        return str(self.root)

    def __repr__(self):
        return str(self.root)
    
    def add_node(self, node:Node):  
        self.nodes.append(node)

    def set_root(self, root:Node):
        self.root = root
    
    def add_edge(self, parent:Node, child:Node):
        parent.add_child(child)

    def build_subtree(tree:Tree, bag:Bag, visited:set):
        visited.add(bag)
        node = Node(bag,1, [])
        for edge in tree.F:
            if bag in edge:
                other_bag = (edge - set([bag])).pop()
                if other_bag not in visited:
                    child_node = RootedTree.build_subtree(tree, other_bag, visited)
                    node.add_child(child_node)
        return node
    
    def parent_dict(self):
        parent_dict = {}
        for node in self.nodes:
            parent = node.parent(self.root)
            parent_dict[node] = parent
        return parent_dict

class BinaryTree(RootedTree):
    def __init__(self, root:Node, nodes):
        super().__init__(root, nodes)

class RootedBinaryDecomposition(TreeDecomposition):
    def __init__(self, bags:Node, tree, ):
        super().__init__(bags, tree)

class RichTreeDecomposition:
    sources = ["a","b","c","d","e","f","g","h","i","j","k","l","m",
             "n","o","p","q","r","s","t","u","v","w","x","y","z"]
    
    def __init__(self, rich_tree:RootedTree, mapping):
        self.rich_tree = rich_tree
        self.mapping = mapping
        self.treeWidth = treeWidth_from_rooted_tree(rich_tree)
        self.sources = RichTreeDecomposition.sources[:self.treeWidth+1]

    def print_tree(self):
        print(self.rich_tree)

    def print_mapping(self):
        print("Mapping: ")
        print([str(k) + ": " + str(v) for k,v in self.mapping.items()])

    def print_treeWidth(self):
        print("Tree width: " + str(self.treeWidth))

    def print_sources(self):
        print("Sources: " + str(self.sources))

    def create_sources_dict(self):
        sources_dict = {}
        # worlist is a tupel (parent, [children])
        worklist = [(None, [self.rich_tree.nodes[-1]])]
        while worklist:
            parent, children = worklist.pop(0)
            if parent is None:
                # Root node, assign sources to children
                for child in children:
                    sources_dict[child] = {}
                    for i, vertex in enumerate(child.label.vertices):
                        sources_dict[child][vertex] = self.sources[i]
                    worklist.append((child, child.children))
                #print("Worklist after processing root: " + str(worklist))
                #print([child.label for child in children])
                #print([node.label for node in worklist[0][1]])
            else:
                # Non-root node, assign sources to children based on parent's source
                parent_source = sources_dict[parent]
                #print("Parent source: " + str(parent_source))
                for child in children:
                    available_sources = self.sources.copy()
                    sources_dict[child] = {}
                    double_verts = []
                    new_verts = []
                    for vertex in child.label.vertices:
                        ###'TODOOOOOOOO' check if vert in parent source and assign same name els fill
                        #in with left available sources
                        if vertex in parent_source:
                            #print("Vertex " + str(vertex) + " is in parent source")
                            double_verts.append(vertex)
                    #print("Double verts: " + str(double_verts))
                    new_verts = child.label.vertices - set(double_verts)
                    #print("New verts: " + str(new_verts))

                    for vert in double_verts:
                        sources_dict[child][vert] = parent_source[vert]
                        #print("Parent has used source " + str(parent_source[vert]) + " for vertex " + str(vert))
                        #print("Available sources before removing: " + str(available_sources))
                        available_sources.remove(parent_source[vert])
                        #print("Available sources after removing: " + str(available_sources))
                    for new_vert in new_verts:
                        if available_sources:
                            assigned_source = available_sources.pop(0)
                            sources_dict[child][new_vert] = assigned_source
                            #print("Assigned new source " + str(assigned_source) + " to vertex " + str(new_vert))
                        else:
                            print("No more available sources to assign to vertex " + str(new_vert))
                    
                    worklist.append((child, child.children))
        return sources_dict

    def create_atomic_term(self, node:Node, mapping, sources_dict):
        # Create an atomic term for a node by adding edges like "ab" 
        # for vertices a and b in the bag of the node, 
        # if they are connected by an edge in the original graph,
        # and concatenating with "//"
        # Source labels are in the sources dict, edges are in the mapping
        term_parts = []
        node_list = []
        node_edges = mapping.get(node, set())
        if not node_edges:
            #print("No edges in node " + str(node.label) + ", creating empty term")
            pass
        else:
            for edge in node_edges:
                #print("Creating atomic term for edge " + str(edge) + " in node " + str(node.label))
                vert1, vert2 = edge
                source1 = sources_dict[node][vert1]
                source2 = sources_dict[node][vert2]
                term_parts.append(source1 + source2)
            #print("Term parts for node " + str(node.label) + ": " + str(term_parts))
            current_tree = term_parts[0]
            node_list.append(Node(current_tree, 0, []))
            for part in term_parts[1:]:
                part_node = Node(part, 0, [])
                current_tree = Node("//", 0, [node_list[-1], part_node])
                node_list.append(part_node)
                node_list.append(current_tree)
            #print("Current tree for node " + str(node.label) + ": " + str(current_tree))
            #print("Node list for node " + str(node.label) + ": " + str(node_list))
        return node_list

    def merge_terms(self, node, mapping, sources_dict, FHR_nodes_dict):
        #print("")
        new_nodes = []
        # Child must already have an atomic term, parent is empty
        node_term = self.create_atomic_term(node, mapping, sources_dict)
        new_nodes.extend(node_term)
        node_term_root = node_term[-1] if node_term else None
        current_tree = node_term_root
        # Now we need to merge the child term with the parent term by concatenating with "//"
        # and forgetting the sources of the child bag nodes which are not in the parent bag
        #print("Node children: " + str(node.children))
        for child in node.children:
            #print("Iterating child " + str(child.label))
            child_term = FHR_nodes_dict.get(child)
            if child_term is None:
                # Fallback for unexpected traversal orders.
                child_term = self.create_atomic_term(child, mapping, sources_dict)
                FHR_nodes_dict[child] = child_term
                new_nodes.extend(child_term)
            #print("Child term for child " + str(child.label) + ": " + str(child_term))
            if not child_term:
                #print("Child term is empty for child " + str(child.label) + ", skipping child")
                continue
            # Find Vertex which is in child bag but not in parent bag
            #print("-----------Child vertices: " + str(child.label.vertices))
            #print("-----------Parent vertices: " + str(node.label.vertices))
            # Child vertex not in parent vertex:
            child_only_vertices = [vert for vert in child.label.vertices if vert not in node.label.vertices]
            #print("Child only vertices: " + str(child_only_vertices))
            source_of_child_only_vert = [sources_dict[child][vert] for vert in child_only_vertices]
            #print("Sources of child only vertices: " + str(source_of_child_only_vert))

            child_root = child_term[-1]
            current_child_term = child_root

            # Forget all sources that disappear from child to parent
            for source in source_of_child_only_vert:
                forget_node = Node("miv_" + source, 1, [current_child_term])
                new_nodes.append(forget_node)
                #print("Forget node for node " + str(node.label) + ": " + str(forget_node))
                current_child_term = forget_node

            if current_tree is not None:
                current_tree = Node("//", 0, [current_tree, current_child_term])
                new_nodes.append(current_tree)
                #print("Fuse node for node " + str(node.label) + ": " + str(current_tree))
            else:
                # If parent has no atomic edges, child contribution is the term itself.
                #print("Node term is empty for node " + str(node.label) + ", using child contribution directly")
                current_tree = current_child_term

        #print("Current tree after merging with all children for node " + str(node.label) + ": " + str(current_tree))

        if current_tree is not None:
            FHR_nodes_dict[node] = [current_tree]
        elif node_term_root is not None:
            # Internal node with no child contribution still keeps its own atomic part.
            FHR_nodes_dict[node] = [node_term_root]

        return new_nodes

    def create_FHR_term(self):
        sources_dict = self.create_sources_dict()
        parents_dict = self.rich_tree.parent_dict()
        #print("Parents dict: " + str(parents_dict))
        FHR_nodes_dict = {}
        FHR_nodes = []
        # Create an FHR term from the rich tree decomposition
        tree_nodes_copy = self.rich_tree.nodes.copy()
        #print("Tree nodes: " + str([node.label for node in tree_nodes_copy]))
        for node in tree_nodes_copy:
            #print("-------------")
            #print("Processing node " + str(node.label))
            #print("-------------")
            #print("FHR_nodes_dict: " + str(FHR_nodes_dict))
            if node.is_leaf():
                # Create a term for the leaf node
                FHR_nodes_dict[node] = self.create_atomic_term(node, self.mapping, sources_dict)
                #print("Added atomic term for leaf node " + str(node.label) + ": " + str(FHR_nodes_dict[node]))
                FHR_nodes.extend(FHR_nodes_dict[node])
            else:
                #print("In else for node " + str(node.label))
                # Create a term for the internal node
                #print("Mapping for node " + str(node.label) + ": " + str(self.mapping.get(node, set())))
                new_internal_nodes = self.merge_terms(node, self.mapping, sources_dict, FHR_nodes_dict)
                FHR_nodes.extend(new_internal_nodes)
                if node in FHR_nodes_dict:
                    FHR_nodes.extend(FHR_nodes_dict[node])
        # Forget all sources at the end
        if not FHR_nodes:
            raise ValueError("FHR construction produced no nodes")
        for source in self.sources:
            forget_node = Node("miv_" + source, 1, [FHR_nodes[-1]])
            FHR_nodes.append(forget_node)
        #print("FHR nodes: " + str(FHR_nodes[-1]))
        return RootedTree(FHR_nodes[-1], FHR_nodes)

if __name__ == "__main__":
    node1 = Node("0", 1, [])
    node2 = Node("1", 2, [])
    node3 = Node("0", 3, [])
    node4 = Node("or", 4, [node1, node2])
    node5 = Node("1", 5, [])
    node6 = Node("not", 6, [node3])
    node7 = Node("not", 7, [node4])
    node8 = Node("or", 8, [node5, node6])
    node9 = Node("and", 9, [node7, node8])

    print(RootedTree(node9, [node1, node2, node3, node4, node5, node6, node7, node8, node9]))
    
