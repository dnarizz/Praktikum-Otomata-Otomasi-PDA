import customtkinter as ctk
from tkinter import filedialog, messagebox
from pda_logic import PDA

class PDAGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.pda = PDA()
        
        self.title("Pushdown Automaton (PDA) Simulator")
        self.geometry("950x650")
        
        # Grid layout (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_top_bar()
        self._create_left_panel()
        self._create_right_panel()

    def _create_top_bar(self):
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        
        self.example_var = ctk.StringVar(value="Load Example...")
        self.example_dropdown = ctk.CTkOptionMenu(
            self.top_frame, 
            variable=self.example_var,
            values=[
                "Load Example...", 
                "a^n b^n", 
                "Balanced Parentheses ()", 
                "Palindrome (even/odd)", 
                "0^n 1^2n", 
                "Equal 0s and 1s",
                "a^n b^m c^{n+m}"
            ],
            command=self.load_example
        )
        self.example_dropdown.pack(side="left", padx=10, pady=10)
        
        self.save_btn = ctk.CTkButton(self.top_frame, text="Save PDA Config", command=self.save_pda)
        self.save_btn.pack(side="right", padx=10, pady=10)
        
        self.load_btn = ctk.CTkButton(self.top_frame, text="Load PDA Config", command=self.load_pda)
        self.load_btn.pack(side="right", padx=10, pady=10)

    def _create_left_panel(self):
        self.left_frame = ctk.CTkScrollableFrame(self, label_text="PDA Definition")
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Basic config
        self.states_entry = self._create_label_entry(self.left_frame, "States (comma separated):")
        self.start_state_entry = self._create_label_entry(self.left_frame, "Start State:")
        self.accept_states_entry = self._create_label_entry(self.left_frame, "Accept States (comma separated):")
        self.start_stack_entry = self._create_label_entry(self.left_frame, "Start Stack Symbol:")
        
        # Transitions
        self.trans_label = ctk.CTkLabel(self.left_frame, text="Transitions:", font=("Arial", 14, "bold"))
        self.trans_label.pack(pady=(15, 5), anchor="w")
        
        # Transition input
        self.trans_input_frame = ctk.CTkFrame(self.left_frame)
        self.trans_input_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.trans_input_frame, text="State").grid(row=0, column=0, padx=2)
        self.t_state = ctk.CTkEntry(self.trans_input_frame, width=70)
        self.t_state.grid(row=1, column=0, padx=2)
        
        ctk.CTkLabel(self.trans_input_frame, text="In (ε=blank)").grid(row=0, column=1, padx=2)
        self.t_input = ctk.CTkEntry(self.trans_input_frame, width=70)
        self.t_input.grid(row=1, column=1, padx=2)
        
        ctk.CTkLabel(self.trans_input_frame, text="Stack").grid(row=0, column=2, padx=2)
        self.t_stack = ctk.CTkEntry(self.trans_input_frame, width=70)
        self.t_stack.grid(row=1, column=2, padx=2)
        
        ctk.CTkLabel(self.trans_input_frame, text="-> Next").grid(row=0, column=3, padx=2)
        self.t_next = ctk.CTkEntry(self.trans_input_frame, width=70)
        self.t_next.grid(row=1, column=3, padx=2)
        
        ctk.CTkLabel(self.trans_input_frame, text="Push").grid(row=0, column=4, padx=2)
        self.t_push = ctk.CTkEntry(self.trans_input_frame, width=70)
        self.t_push.grid(row=1, column=4, padx=2)
        
        self.add_trans_btn = ctk.CTkButton(self.left_frame, text="Add Transition", command=self.add_transition)
        self.add_trans_btn.pack(pady=10)
        
        self.trans_textbox = ctk.CTkTextbox(self.left_frame, height=150)
        self.trans_textbox.pack(fill="x", pady=5)
        self.trans_textbox.configure(state="disabled")
        
        self.del_trans_btn = ctk.CTkButton(self.left_frame, text="Clear All Transitions", command=self.clear_transitions, fg_color="red", hover_color="darkred")
        self.del_trans_btn.pack(pady=5)

    def _create_right_panel(self):
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.right_frame, text="Simulation", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.test_str_entry = ctk.CTkEntry(self.right_frame, placeholder_text="Enter string to test...", width=300)
        self.test_str_entry.pack(padx=20, pady=10)
        
        self.run_btn = ctk.CTkButton(self.right_frame, text="Run Simulation", command=self.run_simulation, fg_color="green", hover_color="darkgreen")
        self.run_btn.pack(pady=10)
        
        self.result_label = ctk.CTkLabel(self.right_frame, text="Waiting...", font=("Arial", 20, "bold"))
        self.result_label.pack(pady=10)
        
        ctk.CTkLabel(self.right_frame, text="Trace:").pack(anchor="w", padx=20)
        self.trace_textbox = ctk.CTkTextbox(self.right_frame)
        self.trace_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.trace_textbox.configure(state="disabled")

    def _create_label_entry(self, parent, text):
        ctk.CTkLabel(parent, text=text).pack(anchor="w", pady=(5, 0))
        entry = ctk.CTkEntry(parent)
        entry.pack(fill="x", pady=(0, 5))
        return entry

    def update_pda_from_ui(self):
        self.pda.states = [s.strip() for s in self.states_entry.get().split(',') if s.strip()]
        self.pda.start_state = self.start_state_entry.get().strip()
        self.pda.accept_states = [s.strip() for s in self.accept_states_entry.get().split(',') if s.strip()]
        self.pda.start_stack_symbol = self.start_stack_entry.get().strip()

    def update_ui_from_pda(self):
        self.states_entry.delete(0, ctk.END)
        self.states_entry.insert(0, ",".join(self.pda.states))
        
        self.start_state_entry.delete(0, ctk.END)
        self.start_state_entry.insert(0, self.pda.start_state)
        
        self.accept_states_entry.delete(0, ctk.END)
        self.accept_states_entry.insert(0, ",".join(self.pda.accept_states))
        
        self.start_stack_entry.delete(0, ctk.END)
        self.start_stack_entry.insert(0, self.pda.start_stack_symbol)
        
        self.refresh_transitions_display()

    def add_transition(self):
        state = self.t_state.get().strip()
        inp = self.t_input.get().strip()
        top = self.t_stack.get().strip()
        next_st = self.t_next.get().strip()
        push = self.t_push.get().strip()
        
        if not state or not top or not next_st:
            messagebox.showerror("Error", "State, Stack Top, and Next State are required.")
            return
            
        self.pda.add_transition(state, inp, top, next_st, push)
        
        for e in [self.t_state, self.t_input, self.t_stack, self.t_next, self.t_push]:
            e.delete(0, ctk.END)
            
        self.refresh_transitions_display()

    def clear_transitions(self):
        self.pda.transitions = {}
        self.refresh_transitions_display()

    def refresh_transitions_display(self):
        self.trans_textbox.configure(state="normal")
        self.trans_textbox.delete("1.0", ctk.END)
        
        for (state, inp, top), outputs in self.pda.transitions.items():
            for next_st, push in outputs:
                display_inp = inp if inp else "ε"
                display_push = push if push else "ε"
                line = f"δ({state}, {display_inp}, {top}) -> ({next_st}, {display_push})\n"
                self.trans_textbox.insert(ctk.END, line)
                
        self.trans_textbox.configure(state="disabled")

    def load_example(self, choice):
        if choice == "Load Example...": return
        
        self.pda = PDA()
        
        if choice == "a^n b^n":
            self.pda.states = ["q0", "q1", "q2"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q2"]
            self.pda.add_transition("q0", "a", "Z", "q0", "AZ")
            self.pda.add_transition("q0", "a", "A", "q0", "AA")
            self.pda.add_transition("q0", "b", "A", "q1", "")
            self.pda.add_transition("q1", "b", "A", "q1", "")
            self.pda.add_transition("q1", "", "Z", "q2", "Z")
            self.pda.add_transition("q0", "", "Z", "q2", "Z")
            
        elif choice == "Balanced Parentheses ()":
            self.pda.states = ["q0", "q1"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q1"]
            self.pda.add_transition("q0", "(", "Z", "q0", "XZ")
            self.pda.add_transition("q0", "(", "X", "q0", "XX")
            self.pda.add_transition("q0", ")", "X", "q0", "")
            self.pda.add_transition("q0", "", "Z", "q1", "Z")
            
        elif choice == "Palindrome (even/odd)":
            self.pda.states = ["q0", "q1", "q2"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q2"]
            self.pda.add_transition("q0", "a", "Z", "q0", "aZ")
            self.pda.add_transition("q0", "b", "Z", "q0", "bZ")
            self.pda.add_transition("q0", "a", "a", "q0", "aa")
            self.pda.add_transition("q0", "a", "b", "q0", "ab")
            self.pda.add_transition("q0", "b", "a", "q0", "ba")
            self.pda.add_transition("q0", "b", "b", "q0", "bb")
            self.pda.add_transition("q0", "", "Z", "q1", "Z")
            self.pda.add_transition("q0", "", "a", "q1", "a")
            self.pda.add_transition("q0", "", "b", "q1", "b")
            self.pda.add_transition("q0", "a", "Z", "q1", "Z")
            self.pda.add_transition("q0", "b", "Z", "q1", "Z")
            self.pda.add_transition("q0", "a", "a", "q1", "a")
            self.pda.add_transition("q0", "b", "a", "q1", "a")
            self.pda.add_transition("q0", "a", "b", "q1", "b")
            self.pda.add_transition("q0", "b", "b", "q1", "b")
            self.pda.add_transition("q1", "a", "a", "q1", "")
            self.pda.add_transition("q1", "b", "b", "q1", "")
            self.pda.add_transition("q1", "", "Z", "q2", "Z")
            
        elif choice == "0^n 1^2n":
            self.pda.states = ["q0", "q1", "q2"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q2"]
            self.pda.add_transition("q0", "0", "Z", "q0", "XXZ")
            self.pda.add_transition("q0", "0", "X", "q0", "XXX")
            self.pda.add_transition("q0", "1", "X", "q1", "")
            self.pda.add_transition("q1", "1", "X", "q1", "")
            self.pda.add_transition("q1", "", "Z", "q2", "Z")
            self.pda.add_transition("q0", "", "Z", "q2", "Z")
            
        elif choice == "Equal 0s and 1s":
            self.pda.states = ["q0", "q1"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q1"]
            self.pda.add_transition("q0", "0", "Z", "q0", "0Z")
            self.pda.add_transition("q0", "1", "Z", "q0", "1Z")
            self.pda.add_transition("q0", "0", "0", "q0", "00")
            self.pda.add_transition("q0", "1", "1", "q0", "11")
            self.pda.add_transition("q0", "1", "0", "q0", "")
            self.pda.add_transition("q0", "0", "1", "q0", "")
            self.pda.add_transition("q0", "", "Z", "q1", "Z")
            
        elif choice == "a^n b^m c^{n+m}":
            self.pda.states = ["q0", "q1", "q2", "q3"]
            self.pda.start_state = "q0"
            self.pda.start_stack_symbol = "Z"
            self.pda.accept_states = ["q3"]
            self.pda.add_transition("q0", "a", "Z", "q0", "AZ")
            self.pda.add_transition("q0", "a", "A", "q0", "AA")
            self.pda.add_transition("q0", "", "A", "q1", "A")
            self.pda.add_transition("q0", "", "Z", "q1", "Z")
            self.pda.add_transition("q1", "b", "A", "q1", "AA")
            self.pda.add_transition("q1", "b", "Z", "q1", "AZ")
            self.pda.add_transition("q1", "", "A", "q2", "A")
            self.pda.add_transition("q1", "", "Z", "q2", "Z")
            self.pda.add_transition("q0", "", "A", "q2", "A")
            self.pda.add_transition("q0", "", "Z", "q2", "Z")
            self.pda.add_transition("q2", "c", "A", "q2", "")
            self.pda.add_transition("q2", "", "Z", "q3", "Z")
            
        self.update_ui_from_pda()
        messagebox.showinfo("Loaded", f"{choice} example loaded!")

    def save_pda(self):
        self.update_pda_from_ui()
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filepath:
            self.pda.save_to_file(filepath)
            messagebox.showinfo("Saved", "PDA configuration saved successfully!")

    def load_pda(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filepath:
            self.pda = PDA()
            self.pda.load_from_file(filepath)
            self.update_ui_from_pda()
            messagebox.showinfo("Loaded", "PDA configuration loaded successfully!")

    def run_simulation(self):
        self.update_pda_from_ui()
        test_str = self.test_str_entry.get().strip()
        
        # Validate that the PDA is fully defined
        if not self.pda.start_state or not self.pda.start_stack_symbol:
            messagebox.showerror("Error", "Start state and start stack symbol must be defined!")
            return
            
        is_accepted, trace = self.pda.process_string(test_str)
        
        if is_accepted:
            self.result_label.configure(text="ACCEPTED", text_color="green")
        else:
            self.result_label.configure(text="REJECTED", text_color="red")
            
        self.trace_textbox.configure(state="normal")
        self.trace_textbox.delete("1.0", ctk.END)
        for step in trace:
            self.trace_textbox.insert(ctk.END, step + "\n")
        self.trace_textbox.configure(state="disabled")

