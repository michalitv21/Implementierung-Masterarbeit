from collections import deque
from treeDecomp import Node, RootedTree
from StringCase.utils import gen_courcelle_alphabet, gen_new_alphabet, powerset
import random
import time

class TreeAutomaton:    
    def __init__(self, states, input_symbols, final_states, transitions):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.final_states = final_states
    
    # Tree must be ordered from leaves to root
    def nta_run(self, tree: RootedTree):
        state_dict = {}  # Maps each node to a list of all possible states
        #print(self.transitions)
        for node in tree.nodes:
            if node.label in self.input_symbols.keys():
                if self.input_symbols[node.label] == 0:
                    # Leaf node: collect all possible states
                    state = self.transitions[node.label]
                    if isinstance(state, list):
                        state_dict[node] = state  # Already a list of states
                    else:
                        state_dict[node] = [state]  # Wrap single state in a list
                elif self.input_symbols[node.label] == 1:
                    # Unary node: compute transitions for all child states
                    child_states_list = state_dict[node.children[0]]
                    possible_states = []
                    for child_state in child_states_list:
                        if child_state is None or child_state not in self.transitions[node.label]:
                            continue
                        result = self.transitions[node.label][child_state]
                        if isinstance(result, list):
                            possible_states.extend(result)
                        else:
                            possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
                elif self.input_symbols[node.label] == 2:
                    # Binary node: compute transitions for all combinations of child states
                    child_states_list_0 = state_dict[node.children[0]]
                    child_states_list_1 = state_dict[node.children[1]]
                    possible_states = []
                    for child_state_0 in child_states_list_0:
                        if child_state_0 is None or child_state_0 not in self.transitions[node.label]:
                            continue
                        for child_state_1 in child_states_list_1:
                            if child_state_1 is None or child_state_1 not in self.transitions[node.label][child_state_0]:
                                continue
                            result = self.transitions[node.label][child_state_0][child_state_1]
                            if isinstance(result, list):
                                possible_states.extend(result)
                            else:
                                possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
                else:
                    # Handle higher arity nodes (generalized)
                    import itertools
                    child_states_lists = [state_dict[child] for child in node.children]
                    possible_states = []
                    for child_state_combination in itertools.product(*child_states_lists):
                        state = self.transitions[node.label]
                        for child_state in child_state_combination[:-1]:
                            state = state[child_state]
                        result = state[child_state_combination[-1]]
                        if isinstance(result, list):
                            possible_states.extend(result)
                        else:
                            possible_states.append(result)
                    # Remove duplicates while preserving all unique states
                    state_dict[node] = list(set(possible_states))
            else:
                print(node.label, " not in input symbols!")
                state_dict[node] = []
        
        #print("Final state dict: ", [{x.label: state_dict[x]} for x in state_dict.keys()])
        #print("Possible states at root: ", state_dict[tree.root])
        
        # Check if any of the possible states at the root is an accepting state
        return any(state in self.final_states for state in state_dict[tree.root])


    def run(self, tree: RootedTree):
        state_dict = {}
        #print(self.transitions)
        for node in tree.nodes:
            if node.label in self.input_symbols.keys():
                state = self.transitions[node.label]
                if self.input_symbols[node.label] == 0:
                    # Leaf node: state is either a single state or a tuple from union/cut
                    if isinstance(state, list):
                        print("Nondeterministic transition found, picking random option.")
                        state_dict[node] = random.choice(state)
                    else:
                        state_dict[node] = state

                elif self.input_symbols[node.label] == 1:
                    child_state = state_dict[node.children[0]]
                    if isinstance(child_state, list):
                        print("Nondeterministic child states found, picking random option.")
                        child_state = random.choice(child_state)    
                    state_dict[node] = state[child_state]

                elif self.input_symbols[node.label] == 2:
                    #print("Children : ", node.children)
                    child_state_0 = state_dict[node.children[0]]
                    child_state_1 = state_dict[node.children[1]]
                    #print("Child states: ", child_state_0, child_state_1)
                    if isinstance(child_state_0, list):
                        print("Nondeterministic child states found, picking random option.")
                        child_state_0 = random.choice(child_state_0)
                    if isinstance(child_state_1, list):
                        print("Nondeterministic child states found, picking random option.")
                        child_state_1 = random.choice(child_state_1)
                    state_dict[node] = state[child_state_0][child_state_1]
                    
                else:
                    print("Higher arity nodes not implemented yet")
        
        # Check if any of the possible states at the root is an accepting state
        root_states = state_dict[tree.root]
        if isinstance(root_states, list):
            return any(state in self.final_states for state in root_states)
        else:
            return root_states in self.final_states
    
    def determinize(self):
        """
        Convert NTA to DTA using powerset construction.
        Uses frozensets to represent DTA states (sets of NTA states).
        Includes progress monitoring and detailed console output.
        """
        import time
        start_time = time.time()
        
        print("\n" + "="*70)
        print("STARTING DETERMINIZATION (Powerset Construction) of Tree Automaton")
        print("="*70)
        
        # Step 1: Generate all possible subsets (powerset) of NTA states
        print(f"\nStep 1: Generating powerset of {len(self.states)} NTA states...")
        step1_start = time.time()
        elems = list(self.states)
        new_states = set()

        # Calculate total subsets for progress tracking
        total_subsets = 2 ** len(elems)
        print(f"  → Total possible subsets: {total_subsets:,}")
        
        subset_count = 0
        last_update = time.time()
        for subset in powerset(elems):
            new_states.add(frozenset(subset))
            subset_count += 1
            # Show progress more frequently
            current_time = time.time()
            if total_subsets <= 20 or subset_count % max(1, total_subsets // 100) == 0 or (current_time - last_update) > 0.5:
                progress = (subset_count / total_subsets) * 100
                bar_length = 30
                filled = int(bar_length * subset_count / total_subsets)
                bar = "█" * filled + "░" * (bar_length - filled)
                elapsed = current_time - step1_start
                if subset_count > 0 and progress > 0:
                    estimated_total = elapsed / (progress / 100)
                    remaining = estimated_total - elapsed
                    eta_str = f"ETA: {remaining:.1f}s" if remaining < 3600 else f"ETA: {remaining/60:.1f}m"
                else:
                    eta_str = "ETA: calculating..."
                print(f"\r  [{bar}] {progress:5.1f}% ({subset_count:,}/{total_subsets:,}) | {eta_str}          ", end="", flush=True)
                last_update = current_time
        
        step1_time = time.time() - step1_start
        print(f"\r  ✓ Generated {len(new_states):,} DTA states in {step1_time:.2f}s                                      ")
        
        # Step 2: Identify final states
        print(f"\nStep 2: Identifying final states...")
        step2_start = time.time()
        new_final_states = set()
        state_check_count = 0
        for state in new_states:
            state_check_count += 1
            if any(s in self.final_states for s in state):
                new_final_states.add(state)
            # Progress for large state sets
            if len(new_states) > 100 and state_check_count % max(1, len(new_states) // 20) == 0:
                progress = (state_check_count / len(new_states)) * 100
                print(f"\r  Checking states... {progress:5.1f}% ({state_check_count:,}/{len(new_states):,})", end="", flush=True)
        
        step2_time = time.time() - step2_start
        print(f"\r  ✓ Final states: {len(new_final_states):,} (checked in {step2_time:.2f}s)                    ")

        # Step 3: Build transitions
        print(f"\nStep 3: Building transition function...")
        print(f"  Processing {len(self.input_symbols)} symbols...")
        step3_start = time.time()
        new_transitions = {}
        
        symbol_count = 0
        total_symbols = len(self.input_symbols)
        
        for char in self.input_symbols.keys():
            symbol_count += 1
            symbol_start = time.time()
            
            # Progress indicator for symbols
            char_display = str(char)[:30]
            arity = self.input_symbols[char]
            print(f"\n  Symbol {symbol_count}/{total_symbols}: '{char_display}' (arity={arity})")
            
            if self.input_symbols[char] == 0:
                # Leaf transitions
                new_transitions[char] = frozenset(self.transitions[char])
                symbol_time = time.time() - symbol_start
                print(f"    ✓ Leaf transition built in {symbol_time:.3f}s")
            elif self.input_symbols[char] == 1:
                # Unary transitions
                print(f"    ⚠ Unary transitions not implemented yet")
                pass
            elif self.input_symbols[char] == 2:
                # Binary transitions
                new_transitions[char] = {}
                transition_count = 0
                total_transitions = len(new_states) * len(new_states)
                print(f"    Building {total_transitions:,} transitions ({len(new_states):,} × {len(new_states):,})...")
                
                last_update = time.time()
                state1_count = 0
                for state1 in new_states:
                    state1_count += 1
                    new_transitions[char][state1] = {}
                    for state2 in new_states:
                        transition_count += 1
                        resulting_states = set()
                        for s1 in state1:
                            for s2 in state2:
                                result = self.transitions[char][s1][s2]
                                if isinstance(result, list):
                                    resulting_states.update(result)
                                else:
                                    resulting_states.add(result)
                        new_transitions[char][state1][state2] = frozenset(resulting_states)
                        
                        # Update progress more frequently
                        current_time = time.time()
                        if transition_count % max(1, total_transitions // 200) == 0 or (current_time - last_update) > 0.5:
                            progress = (transition_count / total_transitions) * 100
                            bar_length = 25
                            filled = int(bar_length * transition_count / total_transitions)
                            bar = "█" * filled + "░" * (bar_length - filled)
                            elapsed = current_time - symbol_start
                            if progress > 0:
                                estimated_total = elapsed / (progress / 100)
                                remaining = estimated_total - elapsed
                                eta_str = f"ETA: {remaining:.1f}s" if remaining < 3600 else f"ETA: {remaining/60:.1f}m"
                            else:
                                eta_str = "ETA: calculating..."
                            print(f"\r    [{bar}] {progress:5.1f}% ({transition_count:,}/{total_transitions:,}) | {eta_str}    ", end="", flush=True)
                            last_update = current_time
                
                symbol_time = time.time() - symbol_start
                print(f"\r    ✓ Binary transitions built in {symbol_time:.2f}s                                              ")
            else:
                # Handle higher arity nodes (generalized)
                print(f"    ⚠ Higher arity ({self.input_symbols[char]}) not implemented yet")
                pass
        
        step3_time = time.time() - step3_start
        print(f"\n  ✓ All transitions built in {step3_time:.2f}s")
        
        # Step 4: Summary
        total_time = time.time() - start_time
        print(f"\nStep 4: Creating DTA...")
        print(f"  ✓ Total DTA states: {len(new_states):,}")
        print(f"  ✓ Final states: {len(new_final_states):,}")
        print(f"  ✓ Input symbols: {len(self.input_symbols)}")
        print(f"  ✓ Total time: {total_time:.2f}s")
        
        print("\n" + "="*70)
        print("DETERMINIZATION COMPLETE!")
        print("="*70 + "\n")
        
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )

    def determinize_reachable(self):
        """
        Convert NTA to DTA using powerset construction.
        Only reachable transitions/states are included here.
        """
        start_time = time.time()
        
        print("\n" + "="*70)
        print("STARTING DETERMINIZATION (Reachable States Only)")
        print("="*70)
        
        # Calculate total possible powerset states for comparison
        total_powerset_states = 2 ** len(self.states)
        print(f"\nOriginal NTA has {len(self.states)} states")
        print(f"Full powerset would have {total_powerset_states:,} states\n")
        
        reachable_states = set()
        new_transitions = {}
        queue = deque()

        # Step 1: Initialize with leaf states
        print("Step 1: Initializing with leaf states...")
        step1_start = time.time()
        leaf_symbols = [(symbol, arity) for symbol, arity in self.input_symbols.items() if arity == 0]
        print(f"  Found {len(leaf_symbols)} leaf symbols")
        
        for idx, (symbol, arity) in enumerate(leaf_symbols):
            leaf_states = self.transitions[symbol]
            if isinstance(leaf_states, list):
                new_state = frozenset(leaf_states)
            else:
                new_state = frozenset([leaf_states])
            
            new_transitions[symbol] = new_state
            reachable_states.add(new_state)
            queue.append(new_state)
            #print(f"  [{idx+1}/{len(leaf_symbols)}] Symbol '{symbol}' → state {new_state}")
        
        step1_time = time.time() - step1_start
        #print(f"  ✓ Initial reachable states: {len(reachable_states)} (in {step1_time:.3f}s)\n")
        
        # Step 2: BFS to explore reachable states
        print("Step 2: Exploring reachable states via BFS...")
        step2_start = time.time()
        
        processed_count = 0
        last_update = time.time()
        last_state_count = len(reachable_states)
        
        unary_symbols = [symbol for symbol, arity in self.input_symbols.items() if arity == 1]
        binary_symbols = [symbol for symbol, arity in self.input_symbols.items() if arity == 2]
        
        #print("Binary symbols: ", binary_symbols)
        #print("Unary symbols: ", unary_symbols)

        print(f"  Processing {len(unary_symbols)} unary and {len(binary_symbols)} binary symbols")
        
        while queue:
            current_state = queue.popleft()
            processed_count += 1
            
            # Progress update
            current_time = time.time()
            if (current_time - last_update) > 1.0:  # Update every second
                states_added = len(reachable_states) - last_state_count
                print(f"  Processed: {processed_count:,} | Queue: {len(queue):,} | Reachable: {len(reachable_states):,} (+{states_added} new)")
                last_update = current_time
                last_state_count = len(reachable_states)
            
            # Process unary transitions
            for symbol in unary_symbols:
                if symbol not in new_transitions:
                    print("Symbol not in new_transitions, initializing: ", symbol)
                    new_transitions[symbol] = {}
                
                if current_state not in new_transitions[symbol]:
                    resulting_states = set()
                    #print("Current state: ", current_state)
                    for nta_state in current_state:
                        if nta_state in self.transitions[symbol]:
                            result = self.transitions[symbol][nta_state]
                            if isinstance(result, list):
                                resulting_states.update(result)
                            else:
                                resulting_states.add(result)
                    
                    new_state = frozenset(resulting_states)
                    new_transitions[symbol][current_state] = new_state
                    
                    if new_state not in reachable_states:
                        reachable_states.add(new_state)
                        queue.append(new_state)
            
            # Process binary transitions
            for symbol in binary_symbols:
                if symbol not in new_transitions:
                    new_transitions[symbol] = {}
                
                # Only build transitions for combinations of reachable states
                for left in list(reachable_states):  # Use list to avoid modification during iteration
                    if left not in new_transitions[symbol]:
                        new_transitions[symbol][left] = {}
                    
                    for right in list(reachable_states):
                        if right not in new_transitions[symbol][left]:
                            resulting_states = set()
                            for s1 in left:
                                for s2 in right:
                                    if s1 in self.transitions[symbol] and s2 in self.transitions[symbol][s1]:
                                        result = self.transitions[symbol][s1][s2]
                                        if isinstance(result, list):
                                            resulting_states.update(result)
                                        else:
                                            resulting_states.add(result)
                            
                            new_state = frozenset(resulting_states)
                            new_transitions[symbol][left][right] = new_state
                            
                            if new_state not in reachable_states:
                                reachable_states.add(new_state)
                                queue.append(new_state)
        
        step2_time = time.time() - step2_start
        print(f"  ✓ BFS complete: {processed_count:,} states processed in {step2_time:.2f}s\n")
        
        # Step 3: Identify final states
        print("Step 3: Identifying final states...")
        step3_start = time.time()
        new_final_states = {state for state in reachable_states 
                            if any(s in self.final_states for s in state)}
        step3_time = time.time() - step3_start
        print(f"  ✓ Final states: {len(new_final_states):,} (in {step3_time:.3f}s)\n")
        
        # Step 4: Comparison Summary
        total_time = time.time() - start_time
        reduction_percent = ((total_powerset_states - len(reachable_states)) / total_powerset_states * 100) if total_powerset_states > 0 else 0
        
        print("="*70)
        print("DETERMINIZATION COMPLETE - COMPARISON SUMMARY")
        print("="*70)
        print(f"\n{'Metric':<40} {'Value':>20}")
        print("-"*70)
        print(f"{'Original NTA states':<40} {len(self.states):>20,}")
        print(f"{'Full powerset states (theoretical)':<40} {total_powerset_states:>20,}")
        print(f"{'Reachable DTA states (actual)':<40} {len(reachable_states):>20,}")
        print(f"{'States avoided by reachability':<40} {total_powerset_states - len(reachable_states):>20,}")
        print(f"{'Reduction percentage':<40} {reduction_percent:>19.2f}%")
        print(f"{'Final states':<40} {len(new_final_states):>20,}")
        print(f"{'Input symbols':<40} {len(self.input_symbols):>20}")
        print(f"{'Total processing time':<40} {total_time:>19.2f}s")
        print("="*70 + "\n")
        
        return TreeAutomaton(
            states=reachable_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )

    def complement(self):
        # Determinize and get the NEW automaton
        dta = self.determinize_reachable()
        # Complement the DTA's final states
        new_final_states = dta.states - dta.final_states
        return TreeAutomaton(
            states=dta.states,
            input_symbols=dta.input_symbols,
            final_states=new_final_states,
            transitions=dta.transitions
        )
    
    def union(self, other):
        print("Constructing union automaton")
        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        #print(new_states)
        new_final_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.final_states or s2 in other.final_states}
        #print(new_final_states)
        new_transitions = {}
        
        for char in self.input_symbols.keys():  # Assuming both automata have the same input symbols
            new_transitions[char] = {}
            if self.input_symbols[char] == 0:
                # Handle leaf transitions - combine states from both automata
                states1 = self.transitions[char]
                states2 = other.transitions[char]
                # Create list of combined states
                combined = []
                if isinstance(states1, list) and isinstance(states2, list):
                    for s1 in states1:
                        for s2 in states2:
                            combined.append((s1, s2))
                elif isinstance(states1, list):
                    for s1 in states1:
                        combined.append((s1, states2))
                elif isinstance(states2, list):
                    for s2 in states2:
                        combined.append((states1, s2))
                else:
                    combined.append((states1, states2))
                new_transitions[char] = combined if len(combined) > 1 else combined[0] if combined else None
            elif self.input_symbols[char] == 1:
                 # Handle unary transitions
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    child_s1 = self.transitions[char][s1]
                    child_s2 = other.transitions[char][s2]

                    combined = []
                    if isinstance(child_s1, list) and isinstance(child_s2, list):
                        for cs1 in child_s1:
                            for cs2 in child_s2:
                                combined.append((cs1, cs2))
                    elif isinstance(child_s1, list):
                        for cs1 in child_s1:
                            combined.append((cs1, child_s2))
                    elif isinstance(child_s2, list):
                        for cs2 in child_s2:
                            combined.append((child_s1, cs2))
                    else:
                        combined.append((child_s1, child_s2))
                    
                    new_transitions[char][(s1, s2)] = combined if len(combined) > 1 else combined[0] if combined else None
                
            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        # Handle lists in transitions
                        if isinstance(next_s1, list) or isinstance(next_s2, list):
                            combined_next = []
                            states1 = next_s1 if isinstance(next_s1, list) else [next_s1]
                            states2 = next_s2 if isinstance(next_s2, list) else [next_s2]
                            for ns1 in states1:
                                for ns2 in states2:
                                    combined_next.append((ns1, ns2))
                            new_transitions[char][(s1, s2)][(t1, t2)] = combined_next if len(combined_next) > 1 else (combined_next[0] if combined_next else None)
                        else:
                            new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print("New Transitions: ",new_transitions)
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )  

    def cut(self, other):
        print("Constructing cut automaton...")
        self_keys = set(self.input_symbols.keys())
        other_keys = set(other.input_symbols.keys())
        if self_keys != other_keys:
            only_self = sorted(self_keys - other_keys, key=str)[:8]
            only_other = sorted(other_keys - self_keys, key=str)[:8]
            raise ValueError(
                f"Cannot cut automata with different input symbol sets. Only in left: {only_self}; only in right: {only_other}"
            )

        new_states = {(s1, s2) for s1 in self.states for s2 in other.states}
        #print(new_states)
        new_final_states = {(s1, s2) for s1 in self.states for s2 in other.states if s1 in self.final_states and s2 in other.final_states}
        #print(new_final_states)
        new_transitions = {}
        #print("self symbols: ", self.input_symbols)
        #print("---------------------------")
        #print("other symbols: ", other.input_symbols)
        for char in self.input_symbols.keys():  # Assuming both automata have the same input symbols
            new_transitions[char] = {}
            if self.input_symbols[char] == 0:
                # Handle leaf transitions - combine states from both automata
                trans1 = self.transitions[char]
                trans2 = other.transitions[char]
                # Extract states from lists if present (nondeterministic case)
                states1 = trans1 if not isinstance(trans1, list) else trans1
                states2 = trans2 if not isinstance(trans2, list) else trans2
                # Create list of combined states
                combined = []
                if isinstance(states1, list) and isinstance(states2, list):
                    for s1 in states1:
                        for s2 in states2:
                            combined.append((s1, s2))
                elif isinstance(states1, list):
                    for s1 in states1:
                        combined.append((s1, states2))
                elif isinstance(states2, list):
                    for s2 in states2:
                        combined.append((states1, s2))
                else:
                    combined.append((states1, states2))
                new_transitions[char] = combined if len(combined) > 1 else combined[0] if combined else None
            elif self.input_symbols[char] == 1:
                 # Handle unary transitions
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    child_s1 = self.transitions[char][s1]
                    child_s2 = other.transitions[char][s2]

                    combined = []
                    if isinstance(child_s1, list) and isinstance(child_s2, list):
                        for cs1 in child_s1:
                            for cs2 in child_s2:
                                combined.append((cs1, cs2))
                    elif isinstance(child_s1, list):
                        for cs1 in child_s1:
                            combined.append((cs1, child_s2))
                    elif isinstance(child_s2, list):
                        for cs2 in child_s2:
                            combined.append((child_s1, cs2))
                    else:
                        combined.append((child_s1, child_s2))
                    
                    new_transitions[char][(s1, s2)] = combined if len(combined) > 1 else combined[0] if combined else None
                


            else:
                new_transitions[char] = {}
                for (s1, s2) in new_states:
                    new_transitions[char][(s1, s2)] = {}
                    for (t1, t2) in new_states:
                        next_s1 = self.transitions[char][s1][t1]
                        next_s2 = other.transitions[char][s2][t2]
                        # Handle lists in transitions
                        if isinstance(next_s1, list) or isinstance(next_s2, list):
                            combined_next = []
                            states1 = next_s1 if isinstance(next_s1, list) else [next_s1]
                            states2 = next_s2 if isinstance(next_s2, list) else [next_s2]
                            for ns1 in states1:
                                for ns2 in states2:
                                    combined_next.append((ns1, ns2))
                            new_transitions[char][(s1, s2)][(t1, t2)] = combined_next if len(combined_next) > 1 else (combined_next[0] if combined_next else None)
                        else:
                            new_transitions[char][(s1, s2)][(t1, t2)] = (next_s1, next_s2)
        #print(new_transitions)
        return TreeAutomaton(
            states=new_states,
            input_symbols=self.input_symbols,
            final_states=new_final_states,
            transitions=new_transitions
        )  

    def project(self, alphabet, j, verbose=False):
        print("Projecting automaton by removing last coordinate...")
        """
        Project away the LAST coordinate from tuple-based alphabet symbols.
        This removes the rightmost element representing set membership.
        Creates nondeterministic transitions when multiple symbols project to the same one.
        
        Args:
            alphabet: Set of base alphabet symbols (e.g., {'a', 'b'})
            j: Depth level for generating the new alphabet using gen_new_alphabet
            verbose: If True, print detailed debug output during projection
        
        Examples:
            ("b", 0, 1) → ("b", 0)
            ("b", 0) → "b"
        """

        if verbose:
            print("\n" + "="*70)
            print(f"STARTING PROJECTION (removing last coordinate)")
            print(f"Base alphabet: {alphabet}, depth level j={j}")
            print("="*70)
        
        new_input_symbols = {}
        new_transitions = {}
        
        # Determine the new alphabet based on projection depth
        if j - 1 == 0:
            # After projection, we're at the base alphabet level
            new_alphabet = alphabet
            if verbose:
                print(f"New alphabet (j=1): {new_alphabet}")
        else:
            # Generate new alphabet for projection depth j-1
            new_alphabet = gen_new_alphabet(alphabet, j - 1)
            if verbose:
                print(f"New alphabet (j={j}): {new_alphabet}")
        
        # Build mapping from old chars to new chars (removing LAST coordinate)
        char_mapping = {}
        if verbose:
            print(f"\nStep 1: Building character mapping (removing last coordinate)...")
        
        for old_char in self.input_symbols.keys():
            if isinstance(old_char, tuple):
                # Remove LAST element
                new_char = old_char[:-1]
                # If only one element left, unwrap the tuple
                if len(new_char) == 1:
                    new_char = new_char[0]
                char_mapping[old_char] = new_char
                if new_char in new_alphabet or (isinstance(new_char, tuple) and new_char in new_alphabet):
                    new_input_symbols[new_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {new_char} (arity: {self.input_symbols[old_char]})")
            else:
                # Not a tuple, keep as is if in new alphabet
                if old_char in new_alphabet:
                    char_mapping[old_char] = old_char
                    new_input_symbols[old_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {old_char} (unchanged, arity: {self.input_symbols[old_char]})")
        
        # Build new transitions by grouping old transitions that map to same new char
        if verbose:
            print("\nStep 2: Building new transitions...")
        for new_char in new_input_symbols.keys():
            arity = new_input_symbols[new_char]
            
            # Find all old chars that project to this new char
            old_chars_for_new = [oc for oc, nc in char_mapping.items() if nc == new_char]
            if verbose:
                print(f"\n  Processing '{new_char}' (arity={arity}):")
                print(f"    Old chars projecting to this: {old_chars_for_new}")
            
            if arity == 0:
                # Leaf transitions: collect all states from old chars
                collected_states = []
                for old_char in old_chars_for_new:
                    old_transition = self.transitions[old_char]
                    if verbose:
                        print(f"      From '{old_char}': {old_transition}")
                    if isinstance(old_transition, list):
                        collected_states.extend(old_transition)
                    else:
                        collected_states.append(old_transition)
                
                # Store as list if multiple states, single state otherwise
                if len(collected_states) > 1:
                    new_transitions[new_char] = collected_states
                    if verbose:
                        print(f"    → Result (nondeterministic): {collected_states}")
                elif len(collected_states) == 1:
                    new_transitions[new_char] = collected_states[0]
                    if verbose:
                        print(f"    → Result (deterministic): {collected_states[0]}")
                else:
                    new_transitions[new_char] = []
            
            elif arity == 1:
                # Unary transitions
                new_transitions[new_char] = {}
                print("New char: ", new_char)
                if verbose:
                    print(f"    Building unary transitions...")
                for state in self.states:
                    combined_results = []
                    for old_char in old_chars_for_new:
                        if state in self.transitions[old_char]:
                            result = self.transitions[old_char][state]
                            if isinstance(result, list):
                                combined_results.extend(result)
                            else:
                                combined_results.append(result)
                    
                    if len(combined_results) > 1:
                        new_transitions[new_char][state] = combined_results
                        if verbose:
                            print(f"      δ({state}) = {combined_results} (nondeterministic)")
                    elif len(combined_results) == 1:
                        new_transitions[new_char][state] = combined_results[0]
                        if verbose:
                            print(f"      δ({state}) = {combined_results[0]}")
            
            elif arity == 2:
                # Binary transitions
                new_transitions[new_char] = {}
                if verbose:
                    print(f"    Building binary transitions...")
                transition_count = 0
                for state1 in self.states:
                    new_transitions[new_char][state1] = {}
                    for state2 in self.states:
                        combined_results = []
                        for old_char in old_chars_for_new:
                            if state1 in self.transitions[old_char] and state2 in self.transitions[old_char][state1]:
                                result = self.transitions[old_char][state1][state2]
                                if isinstance(result, list):
                                    combined_results.extend(result)
                                else:
                                    combined_results.append(result)
                        
                        if len(combined_results) > 1:
                            new_transitions[new_char][state1][state2] = combined_results
                            transition_count += 1
                            if verbose and transition_count <= 5:  # Only print first few to avoid clutter
                                print(f"      δ({state1}, {state2}) = {combined_results} (nondeterministic)")
                        elif len(combined_results) == 1:
                            new_transitions[new_char][state1][state2] = combined_results[0]
                            transition_count += 1
                            if verbose and transition_count <= 5:
                                print(f"      δ({state1}, {state2}) = {combined_results[0]}")
                if verbose and transition_count > 5:
                    print(f"      ... and {transition_count - 5} more transitions")
        
        if verbose:
            print("\n" + "="*70)
            print("PROJECTION COMPLETE")
            print(f"New alphabet: {set(new_input_symbols.keys())}")
            print(f"States: {self.states}")
            print(f"Final states: {self.final_states}")
            print("="*70 + "\n")
        
        return TreeAutomaton(
            states=self.states,
            input_symbols=new_input_symbols,
            final_states=self.final_states,
            transitions=new_transitions
        )

    def project_courcelle(self, alphabet, treewidth, j,  verbose=False):
        print("Projecting automaton by removing last coordinate...")
        """
        Project away the LAST coordinate from tuple-based alphabet symbols.
        This removes the rightmost element representing set membership.
        Creates nondeterministic transitions when multiple symbols project to the same one.
        
        Difference for courcelle: "//" Element has no

        Args:
            alphabet: Set of base alphabet symbols (e.g., {'a', 'b'})
            j: Depth level for generating the new alphabet using gen_new_alphabet
            verbose: If True, print detailed debug output during projection
        
        Examples:
            ("b", 0, 1) → ("b", 0)
            ("b", 0) → "b"
        """

        if verbose:
            print("\n" + "="*70)
            print(f"STARTING PROJECTION (removing last coordinate)")
            print(f"Base alphabet: {alphabet}, depth level j={j}")
            print("="*70)
        
        new_input_symbols = {}
        new_transitions = {}
        
        # Determine the new alphabet based on projection depth
        if j - 1 == 0:
            # After projection, we're at the base alphabet level
            new_alphabet = gen_courcelle_alphabet(treewidth, 0)
            if verbose:
                print(f"New alphabet (j=1): {new_alphabet}")
        else:
            # Generate new alphabet for projection depth j-1
            new_alphabet = gen_courcelle_alphabet(treewidth, j - 1)
            if verbose:
                print(f"New alphabet (j={j}): {new_alphabet}")
        
        # Build mapping from old chars to new chars (removing LAST coordinate)
        char_mapping = {}
        if verbose:
            print(f"\nStep 1: Building character mapping (removing last coordinate)...")
        
        for old_char in self.input_symbols.keys():
            if isinstance(old_char, tuple):
                # Remove LAST element
                new_char = old_char[:-1]
                # If only one element left, unwrap the tuple
                if len(new_char) == 1:
                    new_char = new_char[0]
                char_mapping[old_char] = new_char
                if new_char in new_alphabet or (isinstance(new_char, tuple) and new_char in new_alphabet):
                    new_input_symbols[new_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {new_char} (arity: {self.input_symbols[old_char]})")
            else:
                # Not a tuple, keep as is if in new alphabet
                if old_char in new_alphabet:
                    char_mapping[old_char] = old_char
                    new_input_symbols[old_char] = self.input_symbols[old_char]
                    if verbose:
                        print(f"  {old_char} → {old_char} (unchanged, arity: {self.input_symbols[old_char]})")
        
        # Build new transitions by grouping old transitions that map to same new char
        if verbose:
            print("\nStep 2: Building new transitions...")
        for new_char in new_input_symbols.keys():
            arity = new_input_symbols[new_char]
            
            # Find all old chars that project to this new char
            old_chars_for_new = [oc for oc, nc in char_mapping.items() if nc == new_char]
            if verbose:
                print(f"\n  Processing '{new_char}' (arity={arity}):")
                print(f"    Old chars projecting to this: {old_chars_for_new}")
            
            if arity == 0:
                # Leaf transitions: collect all states from old chars
                collected_states = []
                for old_char in old_chars_for_new:
                    old_transition = self.transitions[old_char]
                    if verbose:
                        print(f"      From '{old_char}': {old_transition}")
                    if isinstance(old_transition, list):
                        collected_states.extend(old_transition)
                    else:
                        collected_states.append(old_transition)
                
                # Store as list if multiple states, single state otherwise
                if len(collected_states) > 1:
                    new_transitions[new_char] = collected_states
                    if verbose:
                        print(f"    → Result (nondeterministic): {collected_states}")
                elif len(collected_states) == 1:
                    new_transitions[new_char] = collected_states[0]
                    if verbose:
                        print(f"    → Result (deterministic): {collected_states[0]}")
            
            elif arity == 1:
                # Unary transitions
                new_transitions[new_char] = {}
                print("New char: ", new_char)
                if verbose:
                    print(f"    Building unary transitions...")
                for state in self.states:
                    combined_results = []
                    for old_char in old_chars_for_new:
                        if state in self.transitions[old_char]:
                            result = self.transitions[old_char][state]
                            if isinstance(result, list):
                                combined_results.extend(result)
                            else:
                                combined_results.append(result)
                    
                    if len(combined_results) > 1:
                        new_transitions[new_char][state] = combined_results
                        if verbose:
                            print(f"      δ({state}) = {combined_results} (nondeterministic)")
                    elif len(combined_results) == 1:
                        new_transitions[new_char][state] = combined_results[0]
                        if verbose:
                            print(f"      δ({state}) = {combined_results[0]}")
                    else:
                        new_transitions[new_char][state] = []
            
            elif arity == 2:
                # Binary transitions
                new_transitions[new_char] = {}
                if verbose:
                    print(f"    Building binary transitions...")
                transition_count = 0
                for state1 in self.states:
                    new_transitions[new_char][state1] = {}
                    for state2 in self.states:
                        combined_results = []
                        for old_char in old_chars_for_new:
                            if state1 in self.transitions[old_char] and state2 in self.transitions[old_char][state1]:
                                result = self.transitions[old_char][state1][state2]
                                if isinstance(result, list):
                                    combined_results.extend(result)
                                else:
                                    combined_results.append(result)
                        
                        if len(combined_results) > 1:
                            new_transitions[new_char][state1][state2] = combined_results
                            transition_count += 1
                            if verbose and transition_count <= 5:  # Only print first few to avoid clutter
                                print(f"      δ({state1}, {state2}) = {combined_results} (nondeterministic)")
                        elif len(combined_results) == 1:
                            new_transitions[new_char][state1][state2] = combined_results[0]
                            transition_count += 1
                            if verbose and transition_count <= 5:
                                print(f"      δ({state1}, {state2}) = {combined_results[0]}")
                        else:
                            new_transitions[new_char][state1][state2] = []
                if verbose and transition_count > 5:
                    print(f"      ... and {transition_count - 5} more transitions")
        if verbose:
            print("\n" + "="*70)
            print("PROJECTION COMPLETE")
            print(f"New alphabet: {set(new_input_symbols.keys())}")
            print(f"States: {self.states}")
            print(f"Final states: {self.final_states}")
            print("="*70 + "\n")
        
        return TreeAutomaton(
            states=self.states,
            input_symbols=new_input_symbols,
            final_states=self.final_states,
            transitions=new_transitions
        )