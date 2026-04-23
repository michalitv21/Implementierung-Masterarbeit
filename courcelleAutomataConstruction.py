from itertools import combinations, permutations, product

from treeAutomata import TreeAutomaton
from StringCase.utils import gen_courcelle_alphabet, gen_new_alphabet
from treeDecomp import Node, RootedTree
from StringCase.utils import powerset

symbols = ["a", "b", "c", "d", "e", "f", "g"]
"""
Assume the alphabet is already in correct form
"""
def singl(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s0", "s1", "sErr"},
        input_symbols=alphabet,
        final_states={"s1"},
        transitions={
            char: "s0" if char[i] == 0 else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s0": {
                    "s0": "s0",
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "s1": {
                    "s0": "s1",
                    "s1": "sErr",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s0": "sErr",
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s0": "s1" if char[i] == 1 else "s0",
                "s1": "sErr" if char[i] == 1 else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def subset(i, j, alphabet, twd, k):
    # X1 <= X2
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"subAcc", "subErr"},
        input_symbols=alphabet,
        final_states={"subAcc"},
        transitions={
            # Leaf symbols (arity 0)
            char: "subErr" if char[i] == 1 and char[j] == 0
            else "subAcc"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition — merge states from left and right child
            char: {
                "subAcc": {
                    "subAcc": "subAcc",
                    "subErr": "subErr",
                },
                "subErr": {
                    "subAcc": "subErr",
                    "subErr": "subErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            # miv_ (arity 1): if the miv symbol matches the state's symbol, go to sI
            char: {
                "subAcc" : "subErr" if char[i] == 1 and char[j] == 0 else "subAcc",
                "subErr": "subErr"
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def in1(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    aut_states = {"p0", "pOk", "pErr"} | {f"p_{x}" for x in symbols[:twd + 1]}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={"pOk"},
        transitions={
            char: "p0" if char[i] == 0 and char[j]== 0 else
                  "p_" + char[0][0] if char[i] == 1 and char[j] == 0 else
                   "pErr"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition
            char: {
                s1: {
                    s2: s2 if s1 == "p0" else s1 if s2 == "p0" else "pErr"
                    for s2 in aut_states
                }
                for s1 in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            ## miv_ (arity 1):
            char: {
                q: q         if char[i] == 0 and char[j] == 0 and q != "p_" + char[0][-1]
                else "pOk"   if char[i] == 0 and char[j] == 1 and q == "p_" + char[0][-1]
                else "pErr"
                for q in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1 #and char[0].startswith("miv_") no rename yet
        } 
    )
def in2(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    aut_states = {"p0", "pOk", "pErr"} | {f"p_{x}" for x in symbols[:twd + 1]}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={"pOk"},
        transitions={
            char: "p0" if char[i] == 0 and char[j]== 0 else
                  "p_" + char[0][1] if char[i] == 1 and char[j] == 0 else
                   "pErr"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            # // (arity 2): parallel composition
            char: {
                s1: {
                    s2: s2 if s1 == "p0" else s1 if s2 == "p0" else "pErr"
                    for s2 in aut_states
                }
                for s1 in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            # miv_ (arity 1):
            char: {
                q: q         if char[i] == 0 and char[j] == 0 and q != "p_" + char[0][-1]
                else "pOk"   if char[i] == 0 and char[j] == 1 and q == "p_" + char[0][-1]
                else "pErr"
                for q in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1 #and char[0].startswith("miv_") no rename yet
        }
    )

def edges(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s1", "sErr"},
        input_symbols=input_symbols,
        final_states={"s1"},
        transitions={
            char: "sErr" if char[i] == 1 and char[0].startswith("miv_") else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s1": {
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s1": "sErr" if char[i] == 1 and char[0].startswith("miv_") else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def vertices(i, alphabet, twd, k):
    #print("Constructing singl automaton for position ", i)
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    return TreeAutomaton(
        states={"s1", "sErr"},
        input_symbols=input_symbols,
        final_states={"s1"},
        transitions={
            char: "sErr" if char[i] == 1 and not (char[0].startswith("miv_")) else "s1"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "s1": {
                    "s1": "s1",
                    "sErr": "sErr",
                },
                "sErr": {
                    "s1": "sErr",
                    "sErr": "sErr",
                }
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "s1": "sErr" if char[i] == 1 and not (char[0].startswith("miv_")) else "s1",
                "sErr": "sErr",
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def only_vert_2_partition(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    aut_states = {"dAcc", "dErr"}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={"dAcc"},
        transitions={
            char: "dAcc" if char[i] == 0 and char[j] == 0 else "dErr"
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                "dAcc": {
                    "dAcc": "dAcc",
                    "dErr": "dErr",
                },
                "dErr": {
                    "dAcc": "dErr",
                    "dErr": "dErr",
                }
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                "dAcc": "dAcc" if (char[i] == 0 and char[j] == 1) or (char[i] == 1 and char[j] == 0) else "dErr",
                "dErr": "dErr"
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

# Does not work: Powerset explosion
# a,b € Xi -> ab or ba € Xi
def closure(i, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    symbols_twd = symbols[:twd + 1]
    frozen_set = frozenset(symbols_twd)
    subsets = powerset(frozen_set)
    #print("Subsets of symbols: ", subsets)
    tuple_list = list(permutations(symbols_twd, 2))
    tuple_subsets = powerset(tuple_list)
    #print("Subsets of tuples: ", tuple_subsets)
    combined_states = set(product(subsets, tuple_subsets))
    
    #print("Combined states: ", combined_states)
    return TreeAutomaton(
        states=combined_states,
        input_symbols=input_symbols,
        final_states={(frozenset(), frozenset())},
        transitions={
            char: (frozenset(),frozenset((char[0][0], char[0][1])))
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                s1: {
                    s2: 
                    (s1[0].union(s2[0]), s1[1].union(s2[1]))
                    for s2 in combined_states
                } for s1 in combined_states
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                s: (frozenset([x[1] for x in s[1] if x[0] == char[0][-1]] + ([x[0] for x in s[1] if x[1] == char[0][-1]])), frozenset([t for t in s[1] if char[0][-1] not in t])) if char[i] == 1 else
                    (frozenset(x for x in s[0] if x != char[0][-1]), frozenset([t for t in s[1] if char[0][-1] not in t]))
                for s in combined_states
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

# States (inSet, notInset, OrderFix)
def bipartite(i, j, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    symbols_twd = symbols[:twd + 1]
    #print("Symbols for treewidth ", twd, ": ", symbols_twd)
    frozen_set = frozenset(symbols_twd)
    subsets = powerset(frozen_set)
    #print("Subsets of symbols: ", subsets)
    tuples = []
    for b in [True, False]:
        for s1 in subsets:
            for s2 in subsets:
                tuples.append((s1, s2, b))
    #print("Tuples: ", set(tuples))
    aut_states = set(tuples) | {"Err"}
    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={(frozenset(), frozenset(), True)},
        transitions={
            char: (frozenset(char[0][0]), frozenset(char[0][1]), False) if char[0][0] < char[0][1] else 
                  (frozenset(char[0][1]), frozenset(char[0][0]), False)
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                tup1: {
                    tup2:
                        "Err" if tup1 == "Err" or tup2 == "Err" or tup1[0].intersection(tup1[1]) != frozenset() or tup2[0].intersection(tup2[1]) != frozenset() else
                        # tup1 False, tup2 False:
                        (tup1[0].union(tup2[1]), tup1[1].union(tup2[0]), False) if not tup1[2] and not tup2[2] and (tup1[0].intersection(tup2[1]) != frozenset() or tup1[1].intersection(tup2[0]) != frozenset()) else
                        (tup1[0].union(tup2[0]), tup1[1].union(tup2[1]), False) if not tup1[2] and not tup2[2] else
                        # tup1 True, tup2 False:
                        (tup1[0].union(tup2[1]), tup1[1].union(tup2[0]), True) if tup1[2] and not tup2[2] and (tup1[0].intersection(tup2[1]) != frozenset() or tup1[1].intersection(tup2[0]) != frozenset()) else
                        (tup1[0].union(tup2[0]), tup1[1].union(tup2[1]), True) if tup1[2] and not tup2[2] else
                        # tup1 False, tup2 True:
                        (tup1[1].union(tup2[0]), tup1[0].union(tup2[1]), True) if not tup1[2] and tup2[2] and (tup1[0].intersection(tup2[1]) != frozenset() or  tup1[1].intersection(tup2[0]) != frozenset()) else
                        (tup1[0].union(tup2[0]), tup1[1].union(tup2[1]), True) if not tup1[2] and tup2[2] else
                        # tup1 True, tup2 True:
                        (tup1[0].union(tup2[0]), tup1[1].union(tup2[1]), True)
                    for tup2 in tuples                }               for tup1 in tuples
            } for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                tup: 
                    "Err" if tup == "Err" or tup[0].intersection(tup[1]) != frozenset() else
                    # vert add to i set
                    (tup[1].difference(frozenset(char[0][-1])), tup[0], True) if char[i] == 1 and char[j] == 0 and char[0][-1] in tup[1] and not tup[2] else
                    (tup[0].difference(frozenset(char[0][-1])), tup[1], True) if char[i] == 1 and char[j] == 0 and char[0][-1] in tup[0] else
                    # vert add to j set
                    (tup[1], tup[0].difference(frozenset(char[0][-1])), True) if char[i] == 0 and char[j] == 1 and char[0][-1] in tup[0] and not tup[2] else
                    (tup[0], tup[1].difference(frozenset(char[0][-1])), True) if char[i] == 0 and char[j] == 1 else
                    "Err" # Error state
                for tup in tuples
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def sub(i, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    symbols_twd = symbols[:twd + 1]
    frozen_set = frozenset(symbols_twd)
    subsets = powerset(frozen_set)
    states = set(subsets)|{"Err"}
    return TreeAutomaton(
        states=states,
        input_symbols=input_symbols,
        final_states={frozenset()},
        transitions={
            char: frozenset() if char[i] == 0 else frozenset([char[0][0], char[0][1]])
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                a: {
                    b: a.union(b) if a != "Err" and b != "Err" else "Err"
                    for b in states                } for a in states
                }
            
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                a:  "Err" if a == "Err" else
                    a if char[i] == 0 and char[0][-1] not in a else
                    a.difference(frozenset([char[0][-1]])) if char[i] == 1 else "Err"
                for a in states
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def noEdge(i, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    symbols_twd = symbols[:twd + 1]
    #print("Symbols for treewidth ", twd, ": ", symbols_twd)
    frozen_set = frozenset(symbols_twd)
    subsets = powerset(frozen_set)
    #print("Subsets of symbols: ", subsets)
    tuple_list = [frozenset(c) for c in combinations(symbols_twd, 2)]
    tuple_subsets = powerset(tuple_list)
    #print("Subsets of tuples: ", tuple_subsets)
    combined_states = set(product(subsets, subsets ,tuple_subsets))
    
    #print("Tuples: ", set(tuples))
    aut_states = set(combined_states) | {"Err"}


    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={(frozenset(), frozenset(), frozenset())},
        transitions={
            char: (frozenset(), frozenset(), frozenset()) if char[i] == 1 else
                  (frozenset(), frozenset(), frozenset(frozenset([char[0][-1], char[0][-2]])))  
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                t1: {
                    t2:  "Err" if t1 == "Err" or t2 == "Err"  else
                        (t1[0].union(t2[0]), t1[1].union(t2[1]), t1[2].union(t2[2]))
                     for t2 in aut_states
                } for t1 in aut_states
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                t:  "Err" if t == "Err" else
                    (t[0].difference(char[0][-1]),t[1].difference(char[0][-1]), frozenset([r for r in t[2] if char[0][-1] not in r])) if char[i] == 1 else
                    (t[0], t[1].union({b for fs in t[2] for b in fs if char[0][-1] in fs and b != char[0][-1]}), frozenset([fs for fs in t[2] if char[0][-1] not in fs])) 
                                if char[i] == 0 and char[0][-1] not in (t[0].union(t[1])) else "Err" for t in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

def noEdgeInv(i, alphabet, twd, k):
    input_symbols = gen_courcelle_alphabet(treewidth=twd, k=k)
    symbols_twd = symbols[:twd + 1]
    #print("Symbols for treewidth ", twd, ": ", symbols_twd)
    frozen_set = frozenset(symbols_twd)
    subsets = powerset(frozen_set)
    #print("Subsets of symbols: ", subsets)
    tuple_list = [frozenset(c) for c in combinations(symbols_twd, 2)]
    print("Tuples: ", tuple_list)
    tuple_subsets = powerset(tuple_list)
    print("Tuples subsets: ", tuple_subsets)
    #print("Subsets of tuples: ", tuple_subsets)
    combined_states = set(product(subsets, subsets ,tuple_subsets))
    print()
    print("Combined states: ", combined_states)
    #print("Tuples: ", set(tuples))
    aut_states = set(combined_states) | {"Err"}


    return TreeAutomaton(
        states=aut_states,
        input_symbols=input_symbols,
        final_states={(frozenset(), frozenset(), frozenset())},
        transitions={
            char: (frozenset(), frozenset(), frozenset()) if char[i] == 0 else
                  (frozenset(), frozenset(), frozenset([frozenset([char[0][-1], char[0][-2]])]))  
            for char in input_symbols.keys() if input_symbols[char] == 0
        } | {
            char: {
                t1: {
                    t2:  "Err" if t1 == "Err" or t2 == "Err"  else
                        (t1[0].union(t2[0]), t1[1].union(t2[1]), t1[2].union(t2[2]))
                     for t2 in aut_states
                } for t1 in aut_states
            }
            for char in input_symbols.keys() if input_symbols[char] == 2
        } | {
            char: {
                t:  "Err" if t == "Err" else
                    (t[0].difference(char[0][-1]),t[1].difference(char[0][-1]), frozenset([r for r in t[2] if char[0][-1] not in r])) if char[i] == 0 else
                    (t[0], t[1].union({b for fs in t[2] for b in fs if char[0][-1] in fs and b != char[0][-1]}), frozenset([fs for fs in t[2] if char[0][-1] not in fs])) 
                                if char[i] == 1 and char[0][-1] not in (t[0].union(t[1])) else "Err" for t in aut_states
            } for char in input_symbols.keys() if input_symbols[char] == 1
        }
    )

if __name__ == "__main__":
    bipartite(1, 2, gen_courcelle_alphabet(2, 3), 2, 3)