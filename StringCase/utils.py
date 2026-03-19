symbols = ["a", "b", "c", "d", "e", "f", "g"]

def powerset(elems):
    powerset_size = 2**len(elems)
    counter = 0
    j = 0
 
    for counter in range(0, powerset_size):
        results = []
        for j in range(0, len(elems)):
            # take the element if on bit position j it says to take it (i.e. 1 appears)
            if((counter & (1 << j)) > 0):
                results.append(elems[j])
        yield results

        

def gen_new_alphabet(alphabet, k):
    """
    Docstring for gen_new_alphabet
    
    :param alphabet: Symbols that are used
    :param k: Depth of Quantors

    Example: gen_new_alphabet({'a','b'}, 2) -> {('a',0,0), ('a',0,1), ('a',1,0), ('a',1,1), ('b',0,0), ('b',0,1), ('b',1,0), ('b',1,1)}
    """
    
    new_alphabet = set()
    for symbol in alphabet:
        def generate_tuples(current_tuple, depth):
            if depth == k:
                new_alphabet.add((symbol,) + current_tuple)
                return
            for i in range(2):
                generate_tuples(current_tuple + (i,), depth + 1)
        generate_tuples((), 0)
    return new_alphabet

"""
Works for treewidth up to 6, k is number of quantors
Alphabet will be of form ({a, b, c, d, e, f, g} x {0, 1}^k + "//" + ren_ and miv_ for every symbol x {0,1}^k
Leafs represent the edge introductions and have arity 0
so we have symbols like ("ab", 0, 1) or ("miv_a", 1, 0) or // (parallel composition) or ren_ab (renaming a to b)
Form:
    ({a, b, c, d, e, f, g} x {0,1}^k for edge symbols like "ab")
    + ("miv_x" x {0,1}^k)
    + ("ren_xy")
    + {"//"}.

"""
def gen_courcelle_alphabet(treewidth, k):
    from itertools import product

    sym_k = symbols[:treewidth + 1]
    bit_vectors = list(product((0, 1), repeat=k))

    ranked_alphabet = {}

    if k == 0:
        for s1 in sym_k:
            for s2 in sym_k:
                if s1 == s2:
                    continue
                edge = s1 + s2
                ranked_alphabet[edge] = 0
        for x in sym_k:
            ranked_alphabet[f"miv_{x}"] = 1
        ranked_alphabet["//"] = 2
        return ranked_alphabet

    # Arity-0 leaves: edge introductions ("ab", b1, ..., bk)
    for s1 in sym_k:
        for s2 in sym_k:
            if s1 == s2:
                continue
            edge = s1 + s2
            for bits in bit_vectors:
                ranked_alphabet[(edge,) + bits] = 0

    # Arity-1: miv_x x {0,1}^k
    for x in sym_k:
        for bits in bit_vectors:
            ranked_alphabet[(f"miv_{x}",) + bits] = 1
    """ No rename yet
    # Arity-1: ren_xy (no bit vector)
    for s1 in sym_k:
        for s2 in sym_k:
            if s1 != s2:
                ranked_alphabet[f"ren_{s1}{s2}"] = 1
    """
    # Arity-2: parallel composition
    ranked_alphabet["//"] = 2

    return ranked_alphabet

def powerset(frozenset_input):
    power_set = [[]]

    for element in frozenset_input:
        new_subsets = []
        for subset in power_set:
            new_subset = subset + [element]
            new_subsets.append(new_subset)
        power_set.extend(new_subsets)

    return [frozenset(subset) for subset in power_set]


if __name__ == "__main__":
    print(gen_courcelle_alphabet(2, 2))


