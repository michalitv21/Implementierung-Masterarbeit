from courcelleAutomataConstruction import *
from treeAutomata import *
import re
from StringCase.utils import gen_courcelle_alphabet

class courcelle_MSO_to_NTA_Parser:
    def __init__(self, alphabet, twd, k):
        self.base_alphabet = alphabet
        self.alphabet = gen_courcelle_alphabet(twd, k)
        self.k = k
        self.twd = twd
        self.variable_counter = 1
        self.bound_variables = {}
        self.variable_types = {}

    def get_variable(self, var_name):
        if var_name not in self.bound_variables:
            raise ValueError(f"Unbound variable: {var_name}")
        return self.bound_variables[var_name]

    def create_temp_var(self):
        temp_var_name = f"temp_{self.variable_counter}"
        self.bound_variables[temp_var_name] = self.variable_counter
        self.variable_types[temp_var_name] = 'second'  # Default type for temporary variables
        self.variable_counter += 1
        self.k += 1  # Increment k for the new variable
        return temp_var_name

    def _project_last_coordinate(self, automaton):
        projected = automaton.project_courcelle(self.base_alphabet, self.twd, self.k, verbose=False)
        self.k -= 1
        self.alphabet = projected.input_symbols
        return projected

    def _split_at_comma(self, s, n=2):
        parts = []
        depth = 0
        start = 0
        for i, char in enumerate(s):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                parts.append(s[start:i].strip())
                start = i + 1
                if len(parts) == n - 1:
                    break
        parts.append(s[start:].strip())
        if len(parts) != n:
            raise ValueError(f"Expected {n} parts but found {len(parts)} in: {s}")
        return parts
    
    def build_ast(self, formula):
        formula = formula.strip()
        if formula.startswith('∃'):
            fo_match = re.match(r'∃([a-z_]\w*)\((.*)\)', formula)
            so_match = re.match(r'∃([A-Z_]\w*)\((.*)\)', formula)
            quant_match = fo_match or so_match
            if quant_match:
                var_name = quant_match.group(1).strip()
                print(f"Processing quantifier for variable: {var_name}")
                subformula = quant_match.group(2).strip()
                var_type = 'first' if fo_match else 'second'
                ast_type = 'exists_first' if fo_match else 'exists_second'
                self.bound_variables[var_name] = self.variable_counter
                self.variable_types[var_name] = var_type
                self.variable_counter += 1
                return {
                    'type': ast_type,
                    'var': var_name,
                    'var_type': var_type,
                    'subformula': self.build_ast(subformula)
                }
        # in the case of universal quantifier we replace it with negated existential (∀x:f -> ¬∃x:¬f)
        elif formula.startswith('∀'):
            fo_match = re.match(r'∀([a-z_]\w*)\((.*)\)', formula)
            so_match = re.match(r'∀([A-Z_]\w*)\((.*)\)', formula)
            quant_match = fo_match or so_match
            if quant_match:
                var_name = quant_match.group(1).strip()
                subformula = quant_match.group(2).strip()
                var_type = 'first' if fo_match else 'second'
                exists_type = 'exists_first' if fo_match else 'exists_second'
                self.bound_variables[var_name] = self.variable_counter
                self.variable_types[var_name] = var_type
                self.variable_counter += 1
                if var_type == "first":
                    return {
                            'type': 'not',
                            'subformula': {
                                'type': 'exists_second',
                                'var': var_name,
                                'var_type': 'second',
                                'subformula': {
                                    'type': 'and',
                                    'left': {'type': 'singleton', 'var': var_name},
                                    'right': {'type': 'not', 'subformula': self.build_ast(subformula)}
                                }
                            }
                        }
                                            
                if var_type == "second":    
                    return {
                    'type': 'not',
                    'subformula': {
                        'type': exists_type,
                        'var': var_name,
                        'var_type': "second",
                        'subformula': {'type' : 'not', 'subformula': self.build_ast(subformula)}
                        }
                    }

        # Boolean connectives
        elif formula.startswith('not'):
            if formula.startswith('not(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
            else:
                inner = formula[3:].strip()
            return {
                'type': 'not',
                'subformula': self.build_ast(inner)
            }
        elif formula.startswith('and'):
            if formula.startswith('and(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'and',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('or'):
            if formula.startswith('or(') and formula.endswith(')'):
                inner = formula[3:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'or',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('->'):
            if formula.startswith('->(') and formula.endswith(')'):
                inner = formula[3:-1].strip()
                left, right = self._split_at_comma(inner)
                return {
                    'type': 'implies',
                    'left': self.build_ast(left),
                    'right': self.build_ast(right)
                }
        elif formula.startswith('<->'):
            if formula.startswith('<->(') and formula.endswith(')'):
                inner = formula[4:-1]  # Remove '<->(' and ')'
                left, right = self._split_at_comma(inner)
                #print(f"<-> with left: {left}, right: {right}")
                # A <-> B is equivalent to (A -> B) and (B -> A)
                return {
                    'type': 'and',
                    'left': {
                        'type': 'implies',
                        'left': self.build_ast(left),
                        'right': self.build_ast(right)
                    },
                    'right': {
                        'type': 'implies',
                        'left': self.build_ast(right),
                        'right': self.build_ast(left)
                    }
                }
        elif formula.startswith('=(') and formula.endswith(')'):
            inner = formula[2:-1].strip()
            left, right = self._split_at_comma(inner)
            return {
                'type': 'and',
                'left': {
                     'type': 'subset',
                     'set1_var': left,
                     'set2_var': right
                },
                'right': {
                     'type': 'subset',
                     'set1_var': right,
                     'set2_var': left
                }
            }
        # Set operations
        elif formula.startswith('singleton(') and formula.endswith(')'):
                inner = formula[10:-1].strip()
                set_var = inner
                return {
                    'type': 'singleton',
                    'var': set_var
                }
        elif formula.startswith('in1(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in1',
                    'set_var': set_var,
                    'elem_var': elem_var
                }
        elif formula.startswith('in2(') and formula.endswith(')'):
                inner = formula[4:-1].strip()
                set_var, elem_var = self._split_at_comma(inner)
                return {
                    'type': 'in2',
                    'set_var': set_var,
                    'elem_var': elem_var
                }
        elif formula.startswith('subset(') and formula.endswith(')'):
                inner = formula[7:-1].strip()
                set1_var, set2_var = self._split_at_comma(inner)
                return {
                    'type': 'subset',
                    'set1_var': set1_var,
                    'set2_var': set2_var
                }
        # Graph predicates
        elif formula.startswith('vertices(') and formula.endswith(')'):
                inner = formula[9:-1].strip()
                set_var = inner
                return {
                    'type': 'vertices',
                    'set_var': set_var
                }
        elif formula.startswith('edges(') and formula.endswith(')'):
                inner = formula[6:-1].strip()
                set_var = inner
                return {
                    'type': 'edges',
                    'set_var': set_var
                }
        elif formula.startswith('biVert(') and formula.endswith(')'):
                inner = formula[7:-1].strip()
                set_var1, set_var2 = self._split_at_comma(inner)
                return {
                    'type': 'biVert',
                    'set_var1': set_var1,
                    'set_var2': set_var2
                }
        elif formula.startswith('closure(') and formula.endswith(')'):
                inner = formula[8:-1].strip()
                set_var = inner
                return {
                    'type': 'closure',
                    'set_var': set_var
                }
        elif formula.startswith('edg(') and formula.endswith(')'):
                
                inner = formula[4:-1].strip()
                set_var1, set_var2 = self._split_at_comma(inner)
                temp_var = self.create_temp_var()
                return {
                            'type': 'exists_second',
                            'var': temp_var,
                            'var_type': 'second',
                            'subformula': {
                                    'type': 'or',
                                    'left': {'type': 'and', 
                                             'left': {'type': 'in1', 'set_var': temp_var, 'elem_var': set_var1}, 
                                             'right': {'type': 'in2', 'set_var': temp_var, 'elem_var': set_var2}},
                                    'right': {'type': 'and', 
                                              'left': {'type': 'in2', 'set_var': temp_var, 'elem_var': set_var1}, 
                                              'right': {'type': 'in1', 'set_var': temp_var, 'elem_var': set_var2}}
                                }
                            }
        elif formula.startswith('bipartite(') and formula.endswith(')'):
                inner = formula[10:-1].strip()
                set_var1, set_var2 = self._split_at_comma(inner)
                return {
                    'type': 'bipartite',
                    'set_var1': set_var1,
                    'set_var2': set_var2
                }
        elif formula.startswith('sub(') and formula.endswith(')'):
             inner = formula[4:-1].strip()
             set_var = inner
             return {
                  'type' : 'sub',
                  'set_var' : set_var
             }
        elif formula.startswith('noEdge(') and formula.endswith(')'):
             inner = formula[7:-1].strip()
             set_var = inner
             return {
                  'type' : 'noEdge',
                  'set_var' : set_var
             }
        
        elif formula.startswith('noEdgeInv(') and formula.endswith(')'):
             inner = formula[10:-1].strip()
             set_var = inner
             return {
                  'type' : 'noEdgeInv',
                  'set_var' : set_var
             }
        elif formula.startswith('inc(') and formula.endswith(')'):
             inner = formula[4:-1].strip()
             set_var1, set_var2, set_var3 = self._split_at_comma(inner, n=3)
             return {
                  'type' : 'inc',
                  'set_var1' : set_var1,
                  'set_var2' : set_var2,
                  'set_var3' : set_var3
             }
        elif formula.startswith('evenVertices(') and formula.endswith(')'):
             inner = formula[13:-1].strip()
             set_var = inner
             return {
                  'type' : 'evenVertices',
                  'set_var' : set_var
             }
        raise ValueError(f"Unrecognized formula: {formula}")
    
    def build_automaton(self, ast):
        print(f"Building automaton for AST node: {ast}")
        if ast['type'] in ('exists', 'exists_first'):
            var = ast['var']
            var_idx = self.get_variable(var)
            sub_automaton = self.build_automaton(ast['subformula'])
            self.alphabet = sub_automaton.input_symbols

            if var_idx != self.k:
                raise ValueError(
                    f"Projection order mismatch: variable {var} has index {var_idx}, active width is {self.k}"
                )

            singleton = singl(var_idx, self.alphabet, self.twd, self.k)

            combined = singleton.cut(sub_automaton)
            return self._project_last_coordinate(combined)
        
        elif ast['type'] == 'exists_second':
            var = ast['var']
            var_idx = self.get_variable(var)
            sub_automaton = self.build_automaton(ast['subformula'])
            self.alphabet = sub_automaton.input_symbols

            if var_idx != self.k:
                raise ValueError(
                    f"Projection order mismatch: variable {var} has index {var_idx}, active width is {self.k}"
                )
            return self._project_last_coordinate(sub_automaton)
        
        elif ast['type'] == 'singleton':
            var = ast['var']
            var_idx = self.get_variable(var)
            return singl(var_idx, self.alphabet, self.twd, self.k)

        elif ast['type'] == 'not':
            sub_automaton = self.build_automaton(ast['subformula'])
            #print(sub_automaton.input_symbols)
            return sub_automaton.complement()
        
        elif ast['type'] == 'and':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            return left_automaton.cut(right_automaton)

        elif ast['type'] == 'or':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            return left_automaton.union(right_automaton)

        elif ast['type'] == 'implies':
            left_automaton = self.build_automaton(ast['left'])
            right_automaton = self.build_automaton(ast['right'])
            left_complement = left_automaton.complement()
            return left_complement.union(right_automaton)

        elif ast['type'] == 'in1':
            set_var = ast['set_var']
            elem_var = ast['elem_var']
            set_idx = self.get_variable(set_var)
            elem_idx = self.get_variable(elem_var)
            return in1(set_idx, elem_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'in2':
            set_var = ast['set_var']
            elem_var = ast['elem_var']
            set_idx = self.get_variable(set_var)
            elem_idx = self.get_variable(elem_var)
            return in2(set_idx, elem_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'subset':
            set1_var = ast['set1_var']
            set2_var = ast['set2_var']
            set1_idx = self.get_variable(set1_var)
            set2_idx = self.get_variable(set2_var)
            return subset(set1_idx, set2_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'vertices':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return vertices(set_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'edges':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return edges(set_idx, self.alphabet, self.twd, self.k)
        elif ast['type'] == 'biVert':
            set_var1 = ast['set_var1']
            set_var2 = ast['set_var2']
            set_idx1 = self.get_variable(set_var1)
            set_idx2 = self.get_variable(set_var2)
            return only_vert_2_partition(set_idx1, set_idx2, self.alphabet, self.twd, self.k)
        elif ast['type'] == 'closure':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return closure(set_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'bipartite':
            set_var1 = ast['set_var1']
            set_var2 = ast['set_var2']
            set_idx1 = self.get_variable(set_var1)
            set_idx2 = self.get_variable(set_var2)
            return bipartite(set_idx1, set_idx2, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'sub':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return sub(set_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'noEdge':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return noEdge(set_idx, self.alphabet, self.twd, self.k)
        
        elif ast['type'] == 'noEdgeInv':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return noEdgeInv(set_idx, self.alphabet, self.twd, self.k)
        elif ast['type'] == 'inc':
            set_var1 = ast['set_var1']
            set_var2 = ast['set_var2']
            set_var3 = ast['set_var3']
            set_idx1 = self.get_variable(set_var1)
            set_idx2 = self.get_variable(set_var2)
            set_idx3 = self.get_variable(set_var3)
            return inc(set_idx1, set_idx2, set_idx3, self.alphabet, self.twd, self.k)
        elif ast['type'] == 'evenVertices':
            set_var = ast['set_var']
            set_idx = self.get_variable(set_var)
            return evenVertices(set_idx, self.alphabet, self.twd, self.k)
if __name__ == "__main__":
   
    treewidth = 2
    k = 2
    alphabet = gen_courcelle_alphabet(treewidth, 0)

    print(alphabet)
    print("------------------------------")
    

    a1 = Node("ab", 1, [])
    a2 = Node("ba", 2, [])
    a3 = Node("bc", 3, [])
    a4 = Node("cb", 4, [])
    a5 = Node("ac", 5, [])
    a6 = Node("ca", 6, [])
    a7 = Node("//", 7, [a1, a2])
    a8 = Node("//", 8, [a3, a4])
    a9 = Node("//", 9, [a5, a6])
    a10 = Node("//", 10, [a8, a9])
    a11 = Node("//", 11, [a7, a10])
    a12 = Node("miv_c", 12, [a11])
    a13 = Node("miv_b", 13, [a12])
    a14 = Node("miv_a", 14, [a13])

    #Quad Graph in F^HR given the belongings to the sets 
    b1 = Node("ab", 1, [])
    b2 = Node("ba", 2, [])
    b3 = Node("bc", 3, [])
    b4 = Node("cb", 4, [])
    b5 = Node("ab", 5, [])
    b6 = Node("ba", 6, [])
    b7 = Node("bc", 7, [])
    b8 = Node("cb", 8, [])
    b9 = Node("//", 9, [b1, b2])
    b10 = Node("//", 10, [b3, b4])
    b11 = Node("//", 11, [b5, b6])
    b12 = Node("//", 12, [b7, b8])
    b13 = Node("//", 13, [b9, b10])
    b14 = Node("//", 14, [b11, b12])
    b15 = Node("miv_b", 15, [b13])
    b16 = Node("miv_b", 16, [b14])
    b17 = Node("//", 17, [b15, b16])
    b18 = Node("miv_c", 17, [b17])
    b19 = Node("miv_a", 18, [b18])

    c1 = Node("ab", 1, [])
    c2 = Node("bc", 2, [])
    c3 = Node("//", 3, [c1, c2])
    c4 = Node("miv_b", 4, [c3])
    c5 = Node("cb", 5, [])
    c6 = Node("//", 6, [c4, c5])
    c7 = Node("miv_c", 7, [c6])
    c8 = Node("bc", 8, [])
    c9 = Node("//", 9, [c7, c8])
    c10 = Node("miv_b", 10, [c9])
    c11 = Node("cb", 11, [])
    c12 = Node("//", 12, [c10, c11])
    c13 = Node("miv_c", 13, [c12])
    c14 = Node("ba", 14, [])
    c15 = Node("//", 15, [c13, c14])
    c16 = Node("miv_a", 16, [c15])
    c17 = Node("miv_b", 17, [c16])

    tree_triangle = RootedTree(a14, [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14])
    tree_quad = RootedTree(b19, [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19])
    tree_toolbox = RootedTree(c17, [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17])

    """
    parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)
    #formula = "∃X1(∃X2(∃X3(and(in1(X3, X1),in2(X3, X2)))))"

    #formula = "∃X(∀y(->(edges(y),∀u(∀v(->(and(in1(y,u),in2(y,v)),not(<->(subset(u,X),subset(v,X)))))))))"

    formula = "∃X(∃Y(bipartite(X,Y)))"

    #formula = "∃a(∃b(∃c(∃X(∃Y(∃Z(and(   and(in1(X, a), in2(X, b) ),  " \
    #"                                and(and(in1(Y, a), in2(Y, c))," \
    #"                                    and(in1(Z, b), in2(Z, c))))))))))"

    ast = parser.build_ast(formula)
    #print("Constructed AST: ", ast)

    automaton = parser.build_automaton(ast)

    #print("automaton transitions: ", automaton.transitions)

    #print(automaton.input_symbols)

    #print("Quad Graph, triangle exsists:", automaton.nta_run(tree_quad))
    #print("Triangle Graph, traiangle exists:", automaton.nta_run(tree_triangle))

    #bipartite_aut = bipartite(1, alphabet, treewidth, k)
    print("Quad Graph, bipartite:", automaton.nta_run(tree_quad))
    print("Triangle Graph, bipartite:", automaton.nta_run(tree_triangle))
    print("Toolbox Graph, bipartite:", automaton.nta_run(tree_toolbox))
    """
    parser = courcelle_MSO_to_NTA_Parser(alphabet, treewidth, k)

    formula = "∃X( and(∀y(subset(y,X)),evenNodes(X)) )"
    ast = parser.build_ast(formula)
    automaton = parser.build_automaton(ast)

    print("Quad Graph, even nodes:", automaton.nta_run(tree_quad))
    print("Triangle Graph, even nodes:", automaton.nta_run(tree_triangle))

    print("Automaton states: ", len(automaton.final_states))