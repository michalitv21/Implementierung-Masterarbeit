from treeAutomata import TreeAutomaton
from treeAutomataConstruction import singl,symb

alphabet = {"and":2, "or":2, "not":1, "1":0, "0":0}

singleton = singl(1, alphabet, 1)
symb_and = symb("and", 1, alphabet, 1)

combined = singleton.cut(symb_and)

print(combined.transitions)