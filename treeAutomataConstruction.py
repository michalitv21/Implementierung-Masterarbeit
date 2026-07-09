from treeAutomata import TreeAutomaton
from StringCase.utils import gen_new_alphabet
from treeDecomp import Node, RootedTree

def singl(i, alphabet, k):
    print("Constructing singl automaton for position ", i)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"s0", "s1", "s2"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"s1"},
        transitions={
            char: 
            {
                "s0": { #no '1' at position i yet in left branch
                    "s0": "s0" if char[i] == 0 else "s1",
                    "s1": "s1" if char[i] == 0 else "s2",
                    "s2": "s2",
                },
                "s1": { # '1' at position i in left branch, so we need to make sure we don't get another '1' at position i in right branch
                    "s0": "s1" if char[i] == 0 else "s2",
                    "s1": "s2",
                    "s2": "s2",
                },
                "s2": { # Capture State
                    "s0": "s2",
                    "s1": "s2",
                    "s2": "s2",
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | {
            char: 
            {
                "s0": "s0" if char[i] == 0 else "s1",
                "s1": "s1" if char[i] == 0 else "s2",
                "s2": "s2",
            } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "s0" if char[i] == 0 else "s1" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def sub(i, j, alphabet, k):
    print("Constructing sub automaton for positions ", i, " and ", j)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"t0", "t1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"t0"},
        transitions={
            char: 
            {
                "t1": { # Rejection State
                    "t0": "t1",
                    "t1": "t1",
                },
                "t0": { # Accepting State
                    "t0": "t1" if char[i] == 1 and char[j] == 0 else "t0",
                    "t1": "t1",
                }
            } for char in new_alphabet if alphabet [char[0]] == 2
        } | {
            char:
                {
                    "t1": "t1",
                    "t0": "t1" if char[i] == 1 and char[j] == 0 else "t0",
                } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "t0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def symb(symbol, i, alphabet, k):
    print("Constructing symb automaton for symbol ", symbol, " at position ", i)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"p0", "p1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"p0"},
        transitions={
            char: 
            {
                 "p1": { # Rejectiong State
                    "p0": "p1",
                    "p1": "p1",
                },
                "p0": { # Accepting State
                    "p0": "p1" if (char[0] != symbol) and char[i] == 1 else "p0",
                    "p1": "p1",
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | {
            char: 
                {
                    "p1": "p1",
                    "p0": "p1" if (char[0] != symbol) and char[i] == 1 else "p0",
                } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "p1" if (char[0] != symbol) and char[i] == 1 else "p0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def left(i, j, alphabet, k):
    print("Constructing left automaton for positions ", i, " and ", j)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"l0", "l1", "l2", "l3"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"l3"},
        transitions={
            char: 
            {
                "l0": {
                    "l0": "l2" if char[i] == 1 and char[j] == 0 else "l0" if char[i] == 0 and char[j] == 0 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l3" if char[i] == 0 and char[j] == 0 else "l1",
                },
                "l1": {
                    "l0": "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                },
                "l2": {
                    "l0": "l3" if char[i] == 0 and char[j] == 1 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                },
                "l3": {
                    "l0": "l3" if char[i] == 0 and char[j] == 0 else "l1",
                    "l1": "l1",
                    "l2": "l1",
                    "l3": "l1"
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | { # I assume in unary symbols we do not need to worry about left and right child since we only have one child, so we propagate the state to the top
            char:
                {
                    "l0": "l0",
                    "l1": "l1",
                    "l2": "l2",
                    "l3": "l3",
                } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "l0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def right(i, j, alphabet, k):
    print("Constructing right automaton for positions ", i, " and ", j)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"r0", "r1", "r2", "r3"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"r3"},
        transitions={
            char: 
            {
                "r0": {
                    "r0": "r2" if char[i] == 1 and char[j] == 0 else "r0" if char[i] == 0 and char[j] == 0 else "r1",
                    "r1": "r1",
                    "r2": "r3" if char[i] == 0 and char[j] == 1 else "r1",
                    "r3": "r3" if char[i] == 0 and char[j] == 0 else "r1",
                },
                "r1": {
                    "r0": "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                },
                "r2": {
                    "r0": "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                },
                "r3": {
                    "r0": "r3" if char[j] == 0 and char[i] == 0 else "r1",
                    "r1": "r1",
                    "r2": "r1",
                    "r3": "r1"
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | {
                char:
                    {
                        "r0": "r0",
                        "r1": "r1",
                        "r2": "r2",
                        "r3": "r3",
                    } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "r0" for char in new_alphabet if alphabet[char[0]] == 0}
    )

def in_Set(set_idx, elem_idx, alphabet, k):
    print("Constructing in_Set automaton for set index ", set_idx, " and element index ", elem_idx)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"i0", "i1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"i0"},
        transitions={
            char: 
            {
                "i0": {
                    "i0": "i0" if not (char[elem_idx] == 1 and char[set_idx] == 0) else "i1",
                    "i1": "i1",
                },
                "i1": {
                    "i0": "i1",
                    "i1": "i1",
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | {
            char:
                {
                    "i0": "i0" if not (char[elem_idx] == 1 and char[set_idx] == 0) else "i1",
                    "i1": "i1",
                } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: 
             "i0" if not (char[elem_idx] == 1 and char[set_idx] == 0) else "i1" for char in new_alphabet if alphabet[char[0]] == 0}

    )

def even(i, alphabet, k):
    print("Constructing even automaton for position ", i)
    new_alphabet = gen_new_alphabet(alphabet, k)
    return TreeAutomaton(
        states={"e0", "e1"},
        input_symbols={char:alphabet[char[0]] for char in new_alphabet},
        final_states={"e0"},
        transitions={
            char: 
            {
                "e0": {
                    "e0": "e0" if char[i] == 0 else "e1",
                    "e1": "e1" if char[i] == 0 else "e0",
                },
                "e1": {
                    "e0": "e1" if char[i] == 0 else "e0",
                    "e1": "e0" if char[i] == 0 else "e1",
                }
            } for char in new_alphabet if alphabet[char[0]] == 2
        } | {
            char:
                {
                    "e0": "e0" if char[i] == 0 else "e1",
                    "e1": "e1" if char[i] == 0 else "e0",
                } for char in new_alphabet if alphabet[char[0]] == 1
        } | {char: "e0" if char[i] == 0 else "e1" for char in new_alphabet if alphabet[char[0]] == 0}
    )