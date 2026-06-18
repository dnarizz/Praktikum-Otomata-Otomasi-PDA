import json

class PDAConfig:
    def __init__(self, state, remaining_input, stack):
        self.state = state
        self.remaining_input = remaining_input
        self.stack = stack # List of strings/chars, top is at the end

    def __repr__(self):
        stack_str = "".join(self.stack) if self.stack else "[Empty]"
        return f"(State: {self.state}, Input: '{self.remaining_input}', Stack: {stack_str})"

class PDA:
    def __init__(self):
        self.states = []
        self.input_alphabet = []
        self.stack_alphabet = []
        self.start_state = ""
        self.start_stack_symbol = ""
        self.accept_states = []
        # transitions: dict mapping (state, input_sym, stack_top) -> list of (next_state, push_string)
        self.transitions = {}

    def add_transition(self, state, input_sym, stack_top, next_state, push_string):
        key = (state, input_sym, stack_top)
        if key not in self.transitions:
            self.transitions[key] = []
        if (next_state, push_string) not in self.transitions[key]:
            self.transitions[key].append((next_state, push_string))

    def remove_transition(self, state, input_sym, stack_top, next_state, push_string):
        key = (state, input_sym, stack_top)
        if key in self.transitions:
            try:
                self.transitions[key].remove((next_state, push_string))
                if not self.transitions[key]:
                    del self.transitions[key]
            except ValueError:
                pass

    def process_string(self, input_string):
        """
        Process the string and return (is_accepted, trace)
        """
        start_config = PDAConfig(self.start_state, input_string, [self.start_stack_symbol])
        
        # Stack for DFS: stores tuples of (config, current_trace)
        stack = [(start_config, [f"Initial: {start_config}"])]
        visited = set()

        longest_trace = []

        while stack:
            curr_config, curr_trace = stack.pop()
            
            # Acceptance condition: Empty input AND current state is an accept state
            if curr_config.remaining_input == "" and curr_config.state in self.accept_states:
                curr_trace.append(f"Accepted: Reached accept state '{curr_config.state}' with empty input.")
                return True, curr_trace

            # Loop detection to prevent infinite recursion on epsilon loops
            state_key = (curr_config.state, curr_config.remaining_input, tuple(curr_config.stack))
            if state_key in visited:
                continue
            visited.add(state_key)

            if len(curr_trace) > len(longest_trace):
                longest_trace = curr_trace

            top_stack_sym = curr_config.stack[-1] if curr_config.stack else ""
            
            possible_moves = []
            
            # 1. Epsilon transitions (input_sym == "" or "ε")
            for eps_char in ["", "ε"]:
                eps_key = (curr_config.state, eps_char, top_stack_sym)
                if eps_key in self.transitions:
                    possible_moves.extend([(eps_key, next_state, push_string) for next_state, push_string in self.transitions[eps_key]])
            
            # 2. Input consuming transitions
            if curr_config.remaining_input:
                in_key = (curr_config.state, curr_config.remaining_input[0], top_stack_sym)
                if in_key in self.transitions:
                    possible_moves.extend([(in_key, next_state, push_string) for next_state, push_string in self.transitions[in_key]])

            for key, next_state, push_string in possible_moves:
                _, input_sym, _ = key
                
                new_remaining = curr_config.remaining_input[1:] if input_sym not in ["", "ε"] else curr_config.remaining_input
                new_stack = list(curr_config.stack)
                
                # Pop the top symbol if stack is not empty
                if new_stack:
                    new_stack.pop()
                
                # Push the new symbols
                if push_string and push_string != "ε":
                    for char in reversed(push_string):
                        new_stack.append(char)
                
                next_config = PDAConfig(next_state, new_remaining, new_stack)
                display_input = input_sym if input_sym not in ["", "ε"] else "ε"
                display_push = push_string if push_string else "ε"
                action_desc = f"Transition: δ({curr_config.state}, {display_input}, {top_stack_sym}) -> ({next_state}, {display_push})"
                
                # Add to stack
                stack.append((next_config, curr_trace + [action_desc, f"Current: {next_config}"]))

        longest_trace.append("Rejected: No valid accepting path found.")
        return False, longest_trace

    def to_dict(self):
        # Convert transitions to a list of strings/dicts for JSON serialization
        trans_list = []
        for (state, inp, top), outputs in self.transitions.items():
            for next_state, push in outputs:
                trans_list.append({
                    "state": state, "input": inp, "top": top,
                    "next_state": next_state, "push": push
                })
        
        return {
            "states": self.states,
            "input_alphabet": self.input_alphabet,
            "stack_alphabet": self.stack_alphabet,
            "start_state": self.start_state,
            "start_stack_symbol": self.start_stack_symbol,
            "accept_states": self.accept_states,
            "transitions": trans_list
        }

    def from_dict(self, data):
        self.states = data.get("states", [])
        self.input_alphabet = data.get("input_alphabet", [])
        self.stack_alphabet = data.get("stack_alphabet", [])
        self.start_state = data.get("start_state", "")
        self.start_stack_symbol = data.get("start_stack_symbol", "")
        self.accept_states = data.get("accept_states", [])
        
        self.transitions = {}
        for t in data.get("transitions", []):
            self.add_transition(t["state"], t["input"], t["top"], t["next_state"], t["push"])

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.from_dict(data)

