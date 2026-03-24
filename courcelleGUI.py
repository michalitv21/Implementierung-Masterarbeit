import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import math
import json
import os
import traceback
from graphLib import Graph, Vertex, minimal_degree_ordering, permutationToTreeDecomposition, tree_to_rooted_tree, minimize_tree_decomposition, make_rich_tree_decomposition, make_binary_tree
from treeDecomp import TreeDecomposition, RootedTree, Node, RichTreeDecomposition
from graph_loader import load_graph_from_adjacency_list, load_graph_from_edge_list

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tree Decomposition Visualizer")
        self.root.geometry("1400x800")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # File persistence
        self.graphs_file = os.path.join(os.path.dirname(__file__), "saved_graphs.json")
        
        # Data structures
        self.vertices = {}  # label -> Vertex
        self.edges = []  # list of sets {v1, v2}
        self.graph = None
        self.tree_decomposition = None
        self.rooted_tree = None  # RootedTree representation
        self.minimized_tree = None
        self.rich_tree = None
        self.rich_tree_mapping = None
        self.fhr_tree = None
        self.pipeline_graph = None
        self.root_bag = None  # Selected root bag for rooted tree
        self.saved_graphs = {}  # name -> (vertices, edges)
        
        # Canvas positions for dragging
        self.vertex_positions = {}  # label -> (x, y)
        self.bag_positions = {}  # bag_label -> (x, y)
        self.node_positions = {}  # node_label -> (x, y) for rooted tree
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.rooted_drag_node = None
        self.rooted_view_tree = None
        self.rooted_view_title = "Rooted Tree"
        self.rooted_positions = {}
        self.rooted_nodes_by_key = {}
        
        # Load graphs from file
        self.load_graphs_from_file()
        
        self.setup_ui()

    def _append_pipeline_output(self, title, content):
        self.pipeline_output.insert("end", "[" + title + "]\n")
        self.pipeline_output.insert("end", str(content) + "\n\n")
        self.pipeline_output.see("end")

    def _require_decomposition(self):
        if not self.tree_decomposition:
            self.compute_tree_decomposition()
        return self.tree_decomposition is not None

    def _require_root_bag(self):
        if not self.root_bag:
            messagebox.showwarning("No Root Selected", "Please select a root bag from the dropdown")
            return False
        return True
        
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)  # Left: fixed width
        main_frame.columnconfigure(1, weight=1)  # Middle-left: expandable
        main_frame.columnconfigure(2, weight=1)  # Middle-right: expandable
        main_frame.columnconfigure(3, weight=0)  # Right: fixed width
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Controls
        control_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        control_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 15))
        
        # Title
        title_label = ctk.CTkLabel(control_frame, text="Graph Editor", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(20, 15))
        
        # Vertex input section
        vertex_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        vertex_section.grid(row=1, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(vertex_section, text="Vertex:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.vertex_entry = ctk.CTkEntry(vertex_section, width=120, placeholder_text="Label")
        self.vertex_entry.grid(row=0, column=1, pady=5, padx=5)
        ctk.CTkButton(vertex_section, text="Add", command=self.add_vertex, width=70, fg_color="#1f6aa5", hover_color="#144870").grid(row=0, column=2, padx=2, pady=5)
        ctk.CTkButton(vertex_section, text="Delete", command=self.delete_vertex, width=70, fg_color="#d32f2f", hover_color="#9a0007").grid(row=0, column=3, padx=2, pady=5)
        
        # Edge input section
        edge_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        edge_section.grid(row=3, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(edge_section, text="Edge:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        edge_inputs = ctk.CTkFrame(edge_section, fg_color="transparent")
        edge_inputs.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.edge_v1_entry = ctk.CTkEntry(edge_inputs, width=50, placeholder_text="v1")
        self.edge_v1_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(edge_inputs, text="-", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.edge_v2_entry = ctk.CTkEntry(edge_inputs, width=50, placeholder_text="v2")
        self.edge_v2_entry.pack(side="left", padx=(5, 0))
        ctk.CTkButton(edge_section, text="Add", command=self.add_edge, width=70, fg_color="#1f6aa5", hover_color="#144870").grid(row=0, column=2, padx=2, pady=5)
        ctk.CTkButton(edge_section, text="Delete", command=self.delete_edge, width=70, fg_color="#d32f2f", hover_color="#9a0007").grid(row=0, column=3, padx=2, pady=5)
        
        # List of vertices and edges
        ctk.CTkLabel(control_frame, text="Vertices:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 5))
        self.vertex_list = ctk.CTkTextbox(control_frame, width=300, height=80, font=ctk.CTkFont(family="Consolas", size=10))
        self.vertex_list.grid(row=6, column=0, columnspan=4, padx=20, pady=(0, 10))
        
        ctk.CTkLabel(control_frame, text="Edges:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, columnspan=4, sticky="w", padx=20, pady=(5, 5))
        self.edge_list = ctk.CTkTextbox(control_frame, width=300, height=80, font=ctk.CTkFont(family="Consolas", size=10))
        self.edge_list.grid(row=8, column=0, columnspan=4, padx=20, pady=(0, 15))
        
        # Action buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.grid(row=10, column=0, columnspan=4, padx=20, pady=15)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all, width=80, fg_color="#d32f2f", hover_color="#9a0007").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Compute", command=self.compute_tree_decomposition, width=80, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Courcelle Pipeline", command=self.compute_full_pipeline, width=140, fg_color="#6a1b9a", hover_color="#4a148c").pack(side="left", padx=3)

        step_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        step_frame.grid(row=11, column=0, columnspan=4, padx=20, pady=(0, 10), sticky="w")
        ctk.CTkLabel(step_frame, text="Pipeline Steps:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(step_frame, text="1 Root", command=self.compute_step_rooted_tree, width=65, fg_color="#1565c0", hover_color="#0d47a1").pack(side="left", padx=2)
        ctk.CTkButton(step_frame, text="2 Min", command=self.compute_step_minimized_tree, width=65, fg_color="#00838f", hover_color="#006064").pack(side="left", padx=2)
        ctk.CTkButton(step_frame, text="3 Rich", command=self.compute_step_rich_mapping, width=65, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=2)
        ctk.CTkButton(step_frame, text="4 FHR", command=self.compute_step_fhr_tree, width=65, fg_color="#6a1b9a", hover_color="#4a148c").pack(side="left", padx=2)
        
        # Ordering options
        ctk.CTkLabel(control_frame, text="Vertex Ordering:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=12, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 5))
        self.ordering_var = tk.StringVar(value="minimal_degree")
        
        radio_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        radio_frame.grid(row=13, column=0, columnspan=4, sticky="w", padx=20)
        ctk.CTkRadioButton(radio_frame, text="Minimal Degree", variable=self.ordering_var, value="minimal_degree").pack(anchor="w", pady=3)
        ctk.CTkRadioButton(radio_frame, text="Custom Order", variable=self.ordering_var, value="custom").pack(anchor="w", pady=3)
        
        ctk.CTkLabel(control_frame, text="Custom order (comma-separated):", font=ctk.CTkFont(size=10)).grid(row=14, column=0, columnspan=4, sticky="w", padx=20, pady=(10, 2))
        self.custom_order_entry = ctk.CTkEntry(control_frame, width=300, placeholder_text="v1, v2, v3, ...")
        self.custom_order_entry.grid(row=15, column=0, columnspan=4, padx=20, pady=(0, 20))
        
        # Right panel - Visualizations (column 1-2 for tree decomposition and rooted tree)
        viz_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        viz_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=(0, 15))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.columnconfigure(2, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
        
        # Original graph canvas
        graph_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        graph_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(graph_frame, text="Original Graph", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.graph_canvas = ctk.CTkCanvas(graph_frame, bg="#1a1a1a", width=800, height=350, highlightthickness=0)
        self.graph_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.graph_canvas.bind("<Button-1>", self.on_graph_click)
        self.graph_canvas.bind("<B1-Motion>", self.on_graph_drag)
        self.graph_canvas.bind("<ButtonRelease-1>", self.on_graph_release)
        
        # Tree decomposition canvas
        tree_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        tree_frame.grid(row=0, column=1, columnspan=2, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=1)
        
        tree_header_frame = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        ctk.CTkLabel(tree_header_frame, text="Tree Decomposition", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Root selection
        ctk.CTkLabel(tree_header_frame, text="Root:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(20, 5))
        self.root_var = tk.StringVar(value="")
        self.root_combo = ctk.CTkComboBox(tree_header_frame, variable=self.root_var, width=100, 
                                          values=[], command=self.on_root_changed, font=ctk.CTkFont(size=10))
        self.root_combo.pack(side="left", padx=5)
        ctk.CTkButton(tree_header_frame, text="Rooted", command=self.convert_to_rooted_tree,
                     width=70, fg_color="#1565c0", hover_color="#0d47a1").pack(side="left", padx=5)
        ctk.CTkButton(tree_header_frame, text="Pipeline", command=self.compute_full_pipeline,
                 width=80, fg_color="#c62828", hover_color="#ad1457").pack(side="left", padx=2)
        
        self.tree_canvas = ctk.CTkCanvas(tree_frame, bg="#1a1a1a", width=400, height=350, highlightthickness=0)
        self.tree_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.tree_canvas.bind("<Button-1>", self.on_tree_click)
        self.tree_canvas.bind("<B1-Motion>", self.on_tree_drag)
        self.tree_canvas.bind("<ButtonRelease-1>", self.on_tree_release)
        
        # Rooted tree canvas
        rooted_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        rooted_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        rooted_frame.columnconfigure(0, weight=1)
        rooted_frame.rowconfigure(1, weight=1)
        
        self.rooted_title_label = ctk.CTkLabel(rooted_frame, text="Rooted Tree", font=ctk.CTkFont(size=16, weight="bold"))
        self.rooted_title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.rooted_canvas = ctk.CTkCanvas(rooted_frame, bg="#1a1a1a", width=400, height=350, highlightthickness=0)
        self.rooted_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.rooted_canvas.bind("<Button-1>", self.on_rooted_click)
        self.rooted_canvas.bind("<B1-Motion>", self.on_rooted_drag)
        self.rooted_canvas.bind("<ButtonRelease-1>", self.on_rooted_release)
        
        # Pipeline output panel
        pipeline_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        pipeline_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        pipeline_frame.columnconfigure(0, weight=1)
        pipeline_frame.rowconfigure(1, weight=1)

        ctk.CTkLabel(pipeline_frame, text="Courcelle Pipeline Output", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.pipeline_output = ctk.CTkTextbox(pipeline_frame, width=400, height=350, font=ctk.CTkFont(family="Consolas", size=10))
        self.pipeline_output.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Right panel - Save/Load
        save_load_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        save_load_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=(15, 0))
        save_load_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(save_load_frame, text="Save / Load", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))
        
        # File loading section
        ctk.CTkLabel(save_load_frame, text="Load from File", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        self.file_path_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text=".lst or .txt file")
        self.file_path_entry.grid(row=2, column=0, padx=20, pady=5)
        
        file_button_frame = ctk.CTkFrame(save_load_frame, fg_color="transparent")
        file_button_frame.grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(file_button_frame, text="Browse", command=self.browse_file, width=95, fg_color="#9c27b0", hover_color="#6a1b9a").pack(side="left", padx=3)
        ctk.CTkButton(file_button_frame, text="Load", command=self.load_from_file, width=95, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        
        # Save section
        ctk.CTkLabel(save_load_frame, text="Save Graph", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", padx=20, pady=(15, 5))
        self.save_name_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text="Graph name")
        self.save_name_entry.grid(row=5, column=0, padx=20, pady=5)
        ctk.CTkButton(save_load_frame, text="Save Graph", command=self.save_graph, width=200, fg_color="#1f6aa5", hover_color="#144870").grid(row=6, column=0, padx=20, pady=10)
        
        # Saved graphs list
        ctk.CTkLabel(save_load_frame, text="Saved Graphs", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, sticky="w", padx=20, pady=(15, 5))
        self.saved_graphs_list = ctk.CTkTextbox(save_load_frame, width=220, height=120, font=ctk.CTkFont(family="Consolas", size=9))
        self.saved_graphs_list.grid(row=8, column=0, padx=20, pady=5)
        
        # Load section
        ctk.CTkLabel(save_load_frame, text="Load Saved Graph", font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, sticky="w", padx=20, pady=(15, 5))
        self.load_name_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text="Graph name to load")
        self.load_name_entry.grid(row=10, column=0, padx=20, pady=5)
        
        button_frame = ctk.CTkFrame(save_load_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, padx=20, pady=10)
        ctk.CTkButton(button_frame, text="Load", command=self.load_graph, width=70, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Delete", command=self.delete_graph, width=70, fg_color="#d32f2f", hover_color="#9a0007").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Refresh", command=self.refresh_saved_graphs, width=70, fg_color="#f57c00", hover_color="#e65100").pack(side="left", padx=3)
        
        # Initialize saved graphs display
        self.refresh_saved_graphs()
        
    def add_vertex(self):
        label = self.vertex_entry.get().strip()
        if not label:
            messagebox.showwarning("Input Error", "Please enter a vertex label")
            return
        if label in self.vertices:
            messagebox.showwarning("Duplicate", f"Vertex '{label}' already exists")
            return
        
        self.vertices[label] = Vertex(label)
        self.vertex_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
        
    def add_edge(self):
        v1_label = self.edge_v1_entry.get().strip()
        v2_label = self.edge_v2_entry.get().strip()
        
        if not v1_label or not v2_label:
            messagebox.showwarning("Input Error", "Please enter both vertex labels")
            return
        if v1_label not in self.vertices or v2_label not in self.vertices:
            messagebox.showwarning("Invalid Vertices", "Both vertices must exist")
            return
        if v1_label == v2_label:
            messagebox.showwarning("Invalid Edge", "Self-loops are not allowed")
            return
        
        edge = {self.vertices[v1_label], self.vertices[v2_label]}
        if edge in self.edges:
            messagebox.showwarning("Duplicate", "This edge already exists")
            return
        
        self.edges.append(edge)
        self.edge_v1_entry.delete(0, tk.END)
        self.edge_v2_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
    
    def delete_vertex(self):
        label = self.vertex_entry.get().strip()
        if not label:
            messagebox.showwarning("Input Error", "Please enter a vertex label")
            return
        if label not in self.vertices:
            messagebox.showwarning("Not Found", f"Vertex '{label}' does not exist")
            return
        
        # Remove the vertex
        vertex = self.vertices[label]
        del self.vertices[label]
        
        # Remove all edges containing this vertex
        self.edges = [e for e in self.edges if vertex not in e]
        
        # Remove position data
        if label in self.vertex_positions:
            del self.vertex_positions[label]
        
        self.vertex_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
    
    def delete_edge(self):
        v1_label = self.edge_v1_entry.get().strip()
        v2_label = self.edge_v2_entry.get().strip()
        
        if not v1_label or not v2_label:
            messagebox.showwarning("Input Error", "Please enter both vertex labels")
            return
        if v1_label not in self.vertices or v2_label not in self.vertices:
            messagebox.showwarning("Invalid Vertices", "Both vertices must exist")
            return
        
        edge = {self.vertices[v1_label], self.vertices[v2_label]}
        if edge not in self.edges:
            messagebox.showwarning("Not Found", "This edge does not exist")
            return
        
        self.edges.remove(edge)
        self.edge_v1_entry.delete(0, tk.END)
        self.edge_v2_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
        
    def clear_all(self):
        self.vertices.clear()
        self.edges.clear()
        self.vertex_positions.clear()
        self.bag_positions.clear()
        self.node_positions.clear()
        self.tree_decomposition = None
        self.rooted_tree = None
        self.minimized_tree = None
        self.rich_tree = None
        self.rich_tree_mapping = None
        self.fhr_tree = None
        self.pipeline_graph = None
        self.rooted_drag_node = None
        self.rooted_view_tree = None
        self.rooted_positions.clear()
        self.rooted_nodes_by_key.clear()
        self.update_lists()
        self.draw_graph()
        self.tree_canvas.delete("all")
        self.rooted_canvas.delete("all")
        self.pipeline_output.delete("1.0", "end")
        self.rooted_title_label.configure(text="Rooted Tree")
        
    def update_lists(self):
        self.vertex_list.delete("1.0", "end")
        self.vertex_list.insert("1.0", ", ".join(sorted(self.vertices.keys())))
        
        self.edge_list.delete("1.0", "end")
        edge_strs = [f"({sorted([str(v) for v in e])[0]}, {sorted([str(v) for v in e])[1]})" 
                    for e in self.edges]
        self.edge_list.insert("1.0", "\n".join(edge_strs))
        
    def draw_graph(self):
        self.graph_canvas.delete("all")
        if not self.vertices:
            return
        
        # Initialize positions for any new vertices
        n = len(self.vertices)
        radius = min(self.graph_canvas.winfo_width(), self.graph_canvas.winfo_height()) / 3
        if radius == 0:
            radius = 150
        center_x = self.graph_canvas.winfo_width() / 2
        center_y = self.graph_canvas.winfo_height() / 2
        if center_x == 0:
            center_x = 400
        if center_y == 0:
            center_y = 175
        
        for i, label in enumerate(sorted(self.vertices.keys())):
            if label not in self.vertex_positions:
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.vertex_positions[label] = (x, y)
        
        # Draw edges with modern style
        for edge in self.edges:
            vertices_list = list(edge)
            v1_label = str(vertices_list[0])
            v2_label = str(vertices_list[1])
            x1, y1 = self.vertex_positions[v1_label]
            x2, y2 = self.vertex_positions[v2_label]
            self.graph_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
        
        # Draw vertices with modern style and gradient effect
        for label, (x, y) in self.vertex_positions.items():
            r = 25
            # Outer shadow
            self.graph_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill="#0d47a1", outline="", tags=f"vertex_{label}")
            # Main circle
            self.graph_canvas.create_oval(x-r, y-r, x+r, y+r, fill="#1976d2", 
                                          outline="#42a5f5", width=2, tags=f"vertex_{label}")
            # Text
            self.graph_canvas.create_text(x, y, text=label, font=("Segoe UI", 12, "bold"), 
                                         fill="white", tags=f"vertex_{label}")
            
    def on_graph_click(self, event):
        item = self.graph_canvas.find_closest(event.x, event.y)[0]
        tags = self.graph_canvas.gettags(item)
        for tag in tags:
            if tag.startswith("vertex_"):
                self.dragging = tag.replace("vertex_", "")
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                break
                
    def on_graph_drag(self, event):
        if self.dragging and self.dragging in self.vertex_positions:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            x, y = self.vertex_positions[self.dragging]
            self.vertex_positions[self.dragging] = (x + dx, y + dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.draw_graph()
            
    def on_graph_release(self, event):
        self.dragging = None
        
    def compute_tree_decomposition(self):
        if not self.vertices:
            messagebox.showwarning("No Graph", "Please add vertices first")
            return
        
        # Clear previous tree decomposition artifacts
        self.bag_positions.clear()
        self.tree_decomposition = None
        self.tree_canvas.delete("all")
        
        # Create NEW vertex objects (not references) for the computation
        vertex_map = {label: Vertex(label) for label in self.vertices.keys()}
        vertex_list = list(vertex_map.values())
        
        # Create edges with the new vertex objects
        edge_list = []
        for edge in self.edges:
            edge_vertices = list(edge)
            v1_label = str(edge_vertices[0])
            v2_label = str(edge_vertices[1])
            new_edge = {vertex_map[v1_label], vertex_map[v2_label]}
            edge_list.append(new_edge)
        
        graph_copy = Graph(vertex_list, edge_list)
        
        # Get vertex ordering
        if self.ordering_var.get() == "minimal_degree":
            ordering = minimal_degree_ordering(graph_copy)
            # Ensure ordering includes ALL vertices (append any missing ones)
            if len(ordering) != len(vertex_list):
                have = {v for v in ordering}
                missing = [v for v in vertex_list if v not in have]
                if missing:
                    # Append missing vertices in a stable label order
                    for mv in sorted(missing, key=lambda x: x.label):
                        ordering.append(mv)
            print(str([v.label for v in ordering]))
        else:
            custom_str = self.custom_order_entry.get().strip()
            if not custom_str:
                messagebox.showwarning("Input Error", "Please enter a custom ordering")
                return
            labels = [l.strip() for l in custom_str.split(",")]
            if set(labels) != set(self.vertices.keys()):
                messagebox.showwarning("Invalid Ordering", "Ordering must include all vertices exactly once")
                return
            ordering = [vertex_map[l] for l in labels]
        
        # Create fresh vertices for decomposition and keep the same vertex identities
        # for the untouched pipeline graph used by rich-tree mapping.
        vertex_map2 = {label: Vertex(label) for label in self.vertices.keys()}
        vertex_list2 = list(vertex_map2.values())
        edge_list2 = []
        for edge in self.edges:
            edge_vertices = list(edge)
            v1_label = str(edge_vertices[0])
            v2_label = str(edge_vertices[1])
            new_edge = {vertex_map2[v1_label], vertex_map2[v2_label]}
            edge_list2.append(new_edge)
        
        # Convert ordering to use vertices from vertex_map2
        ordering2 = [vertex_map2[v.label] for v in ordering]

        # Keep an unmodified graph for step 3 rich decomposition.
        self.pipeline_graph = Graph(vertex_list2.copy(), [e.copy() for e in edge_list2])

        # Use a separate mutable graph for permutationToTreeDecomposition.
        graph_copy2 = Graph(vertex_list2.copy(), [e.copy() for e in edge_list2])
        self.tree = permutationToTreeDecomposition(graph_copy2, ordering2)
        print("Tree Decomposition computed.")
        print(self.tree)
        self.tree_decomposition = TreeDecomposition(self.tree.I, self.tree)
        
        # Update root selection combobox with bag labels
        bag_labels = [bag.label for bag in self.tree_decomposition.tree.I.values()]
        self.root_combo.configure(values=bag_labels)
        if bag_labels:
            self.root_var.set(bag_labels[0])
            # Find the actual bag object by label
            for vertex, bag in self.tree_decomposition.tree.I.items():
                if bag.label == bag_labels[0]:
                    self.root_bag = bag
                    break
        
        self.draw_tree_decomposition()
    
    def on_root_changed(self, choice):
        """Called when root selection combobox changes"""
        if self.tree_decomposition and choice:
            # Find the actual bag object by label
            for vertex, bag in self.tree_decomposition.tree.I.items():
                if bag.label == choice:
                    self.root_bag = bag
                    break
            self.draw_tree_decomposition()
    
    def draw_tree_decomposition(self):
        self.tree_canvas.delete("all")
        if not self.tree_decomposition:
            return
        
        bags = self.tree_decomposition.tree.I
        edges = self.tree_decomposition.tree.F
        
        if not bags:
            return
        
        # Initialize bag positions if needed
        if not self.bag_positions:
            n = len(bags)
            canvas_width = self.tree_canvas.winfo_width()
            canvas_height = self.tree_canvas.winfo_height()
            
            # Use actual canvas size or fallback to reasonable defaults
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 350
            
            # Calculate radius and center
            radius = min(canvas_width, canvas_height) / 3.5
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            
            for i, (vertex, bag) in enumerate(bags.items()):
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.bag_positions[bag.label] = (x, y)
        
        # Draw edges between bags with modern style
        for edge in edges:
            bags_list = list(edge)
            b1_label = bags_list[0].label
            b2_label = bags_list[1].label
            if b1_label in self.bag_positions and b2_label in self.bag_positions:
                x1, y1 = self.bag_positions[b1_label]
                x2, y2 = self.bag_positions[b2_label]
                self.tree_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
        
        # Draw bags with modern style
        for vertex, bag in bags.items():
            if bag.label not in self.bag_positions:
                continue
            x, y = self.bag_positions[bag.label]
            
            # Bag content
            content = "{" + ", ".join([str(v) for v in bag.vertices]) + "}"
            
            # Calculate size based on content
            r = max(35, len(content) * 4.5)
            
            # Highlight root in different color
            is_root = self.root_bag and bag.label == self.root_bag.label
            if is_root:
                shadow_color = "#ff6f00"  # Orange shadow for root
                main_color = "#ffa726"     # Orange for root
                outline_color = "#ffb74d"  # Light orange outline
            else:
                shadow_color = "#1b5e20"
                main_color = "#2e7d32"
                outline_color = "#66bb6a"
            
            # Outer shadow
            self.tree_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill=shadow_color, 
                                         outline="", tags=f"bag_{bag.label}")
            # Main circle
            self.tree_canvas.create_oval(x-r, y-r, x+r, y+r, fill=main_color, 
                                         outline=outline_color, width=2, tags=f"bag_{bag.label}")
            # Text
            self.tree_canvas.create_text(x, y, text=content, font=("Segoe UI", 10, "bold"), 
                                        fill="white", tags=f"bag_{bag.label}")
            
    def on_tree_click(self, event):
        item = self.tree_canvas.find_closest(event.x, event.y)[0]
        tags = self.tree_canvas.gettags(item)
        for tag in tags:
            if tag.startswith("bag_"):
                self.dragging = tag.replace("bag_", "")
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                break
                
    def on_tree_drag(self, event):
        if self.dragging and self.dragging in self.bag_positions:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            x, y = self.bag_positions[self.dragging]
            self.bag_positions[self.dragging] = (x + dx, y + dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.draw_tree_decomposition()
            
    def on_tree_release(self, event):
        self.dragging = None
    
    def convert_to_rooted_tree(self):
        """Convert the current tree decomposition to a rooted tree and display it"""
        if not self._require_decomposition():
            return

        if not self._require_root_bag():
            return
        
        try:
            # Use the graphLib tree_to_rooted_tree function
            self.rooted_tree = tree_to_rooted_tree(self.tree_decomposition.tree, self.root_bag)
            print("Rooted tree converted successfully")
            self.node_positions.clear()

            # Draw the rooted tree
            self.draw_rooted_tree(self.rooted_tree, "Rooted Tree")
            self._append_pipeline_output("STEP 1 ROOTED", "#Nodes: " + str(len(self.rooted_tree.nodes)) + "\n" + str(self.rooted_tree))
            messagebox.showinfo("Success", f"Tree decomposition converted to rooted tree with root '{self.root_bag.label}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error converting to rooted tree: {str(e)}")
    
    def draw_rooted_tree(self, tree=None, title="Rooted Tree", recompute_layout=True):
        """Draw the rooted tree in hierarchical layout on the rooted tree canvas"""
        self.rooted_canvas.delete("all")
        tree_to_draw = tree if tree is not None else self.rooted_tree
        if not tree_to_draw:
            return

        self.rooted_view_tree = tree_to_draw
        self.rooted_view_title = title
        self.rooted_title_label.configure(text=title)
        is_fhr_view = "fhr" in title.lower()
        
        # Calculate hierarchical positions
        canvas_width = self.rooted_canvas.winfo_width()
        canvas_height = self.rooted_canvas.winfo_height()
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 350

        if recompute_layout or (not self.rooted_positions):
            self.rooted_positions.clear()
            leaf_count = self._count_tree_leaves(tree_to_draw.root)
            tree_depth = self._tree_depth(tree_to_draw.root)
            if is_fhr_view:
                layer_width = max(45, min(110, int((canvas_width - 60) / max(1, leaf_count))))
                layer_height = max(50, min(85, int((canvas_height - 70) / max(1, tree_depth))))
            else:
                layer_width = max(45, min(150, int((canvas_width - 80) / max(1, leaf_count - 1))))
                layer_height = max(50, min(90, int((canvas_height - 70) / max(1, tree_depth))))

            self._calculate_node_positions(tree_to_draw.root,
                                           x=(canvas_width / 2),
                                           y=30,
                                           layer_height=layer_height,
                                           layer_width=layer_width)

            # Ensure the entire tree is visible inside the canvas after layout.
            fit_margin = 20 if is_fhr_view else 28
            self._fit_rooted_positions_to_canvas(canvas_width, canvas_height, fit_margin)

        self.rooted_nodes_by_key.clear()
        self._collect_rooted_node_keys(tree_to_draw.root)
        
        # Draw edges (parent to children)
        self._draw_node_edges(tree_to_draw.root)
        
        # Draw nodes
        self._draw_nodes(tree_to_draw.root)

    def _count_tree_leaves(self, node):
        if not node.children:
            return 1
        return sum(self._count_tree_leaves(child) for child in node.children)

    def _tree_depth(self, node):
        if not node.children:
            return 1
        return 1 + max(self._tree_depth(child) for child in node.children)

    def on_rooted_click(self, event):
        items = self.rooted_canvas.find_closest(event.x, event.y)
        if not items:
            return
        item = items[0]
        tags = self.rooted_canvas.gettags(item)
        self.rooted_drag_node = None
        for tag in tags:
            if tag in self.rooted_nodes_by_key:
                self.rooted_drag_node = self.rooted_nodes_by_key[tag]
                break
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_rooted_drag(self, event):
        if self.rooted_drag_node is None:
            return
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        x, y = self.rooted_positions[self.rooted_drag_node]
        self.rooted_positions[self.rooted_drag_node] = (x + dx, y + dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        if self.rooted_view_tree:
            self.draw_rooted_tree(self.rooted_view_tree, self.rooted_view_title, recompute_layout=False)

    def on_rooted_release(self, event):
        self.rooted_drag_node = None

    def _node_key(self, node):
        return "rooted_node_" + str(id(node))

    def _collect_rooted_node_keys(self, node):
        self.rooted_nodes_by_key[self._node_key(node)] = node
        for child in node.children:
            self._collect_rooted_node_keys(child)
    
    def _calculate_node_positions(self, node, x, y, layer_height=80, layer_width=200):
        """Calculate positions for nodes in a hierarchical tree layout"""
        self.rooted_positions[node] = (x, y)
        
        if not node.children:
            return
        
        # Calculate spacing for children
        num_children = len(node.children)
        total_width = (num_children - 1) * layer_width if num_children > 1 else 0
        start_x = x - total_width / 2
        
        for i, child in enumerate(node.children):
            child_x = start_x + i * layer_width
            child_y = y + layer_height
            self._calculate_node_positions(child, child_x, child_y, layer_height, layer_width)

    def _fit_rooted_positions_to_canvas(self, canvas_width, canvas_height, margin):
        if not self.rooted_positions:
            return

        xs = [pos[0] for pos in self.rooted_positions.values()]
        ys = [pos[1] for pos in self.rooted_positions.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        available_x = max(canvas_width - (2 * margin), 1)
        available_y = max(canvas_height - (2 * margin), 1)

        scale = min(available_x / span_x, available_y / span_y, 1.0)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        target_center_x = canvas_width / 2
        target_center_y = canvas_height / 2

        for node, (x, y) in list(self.rooted_positions.items()):
            new_x = (x - center_x) * scale + target_center_x
            new_y = (y - center_y) * scale + target_center_y
            self.rooted_positions[node] = (new_x, new_y)
    
    def _draw_node_edges(self, node):
        """Draw edges from parent to children on rooted_canvas"""
        if node in self.rooted_positions:
            x1, y1 = self.rooted_positions[node]
            
            for child in node.children:
                if child in self.rooted_positions:
                    x2, y2 = self.rooted_positions[child]
                    self.rooted_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
                    self._draw_node_edges(child)
    
    def _draw_nodes(self, node):
        """Recursively draw nodes with their labels on rooted_canvas"""
        if node not in self.rooted_positions:
            return
        
        x, y = self.rooted_positions[node]
        is_fhr_view = "fhr" in self.rooted_view_title.lower()
        r = 16 if is_fhr_view else 28
        font_size = 8 if is_fhr_view else 10
        label_text = str(node.label)
        if is_fhr_view and len(label_text) > 10:
            label_text = label_text[:10]
        
        # Check if this is the root node
        is_root = self.rooted_view_tree and node == self.rooted_view_tree.root
        
        if is_root:
            # Highlight root in orange/golden color
            shadow_color = "#ff6f00"
            main_color = "#ffa726"
            outline_color = "#ffb74d"
        else:
            # Regular green color for other nodes
            shadow_color = "#1b5e20"
            main_color = "#2e7d32"
            outline_color = "#66bb6a"
        
        # Outer shadow
        self.rooted_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill=shadow_color, 
                                     outline="", tags=(self._node_key(node), "rooted_node"))
        # Main circle
        self.rooted_canvas.create_oval(x-r, y-r, x+r, y+r, fill=main_color, 
                                     outline=outline_color, width=2, tags=(self._node_key(node), "rooted_node"))
        # Text
        self.rooted_canvas.create_text(x, y, text=label_text, font=("Segoe UI", font_size, "bold"), 
                                    fill="white", tags=(self._node_key(node), "rooted_node"))
        
        # Recursively draw children
        for child in node.children:
            self._draw_nodes(child)

    def _format_rich_mapping(self):
        if not self.rich_tree_mapping:
            return "{}"
        lines = []
        for node, edges in self.rich_tree_mapping.items():
            edge_text = []
            for e in edges:
                edge_vertices = sorted([str(v) for v in e])
                if len(edge_vertices) == 2:
                    edge_text.append("(" + edge_vertices[0] + ", " + edge_vertices[1] + ")")
                else:
                    edge_text.append(str(tuple(edge_vertices)))
            lines.append(str(node.label) + ": " + str(edge_text))
        return "\n".join(lines)

    def compute_full_pipeline(self):
        self.pipeline_output.delete("1.0", "end")
        if not self.compute_step_rooted_tree(show_message=False):
            return
        if not self.compute_step_minimized_tree(show_message=False):
            return
        if not self.compute_step_rich_mapping(show_message=False):
            return
        if not self.compute_step_fhr_tree(show_message=False):
            return
        messagebox.showinfo("Success", "Complete Courcelle pipeline computed successfully")

    def compute_step_rooted_tree(self, show_message=True):
        if not self.vertices:
            messagebox.showwarning("No Graph", "Please add vertices first")
            return False
        if not self._require_decomposition():
            return False
        if not self._require_root_bag():
            return False
        try:
            self.rooted_tree = tree_to_rooted_tree(self.tree_decomposition.tree, self.root_bag)
            self.draw_rooted_tree(self.rooted_tree, "Step 1: Rooted Tree")
            self._append_pipeline_output("STEP 1 ROOTED", "#Nodes: " + str(len(self.rooted_tree.nodes)) + "\n" + str(self.rooted_tree))
            if show_message:
                messagebox.showinfo("Step 1", "Rooted tree computed")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error in Step 1 (Rooted): {str(e)}")
            return False

    def compute_step_minimized_tree(self, show_message=True):
        if not self.rooted_tree:
            if not self.compute_step_rooted_tree(show_message=False):
                return False
        try:
            self.minimized_tree = minimize_tree_decomposition(self.rooted_tree)
            self.draw_rooted_tree(self.minimized_tree, "Step 2: Minimized Tree")
            self._append_pipeline_output("STEP 2 MINIMIZED", "#Nodes: " + str(len(self.minimized_tree.nodes)) + "\n" + str(self.minimized_tree))
            if show_message:
                messagebox.showinfo("Step 2", "Minimized rooted tree computed")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error in Step 2 (Minimization): {str(e)}")
            return False

    def compute_step_rich_mapping(self, show_message=True):
        if not self.minimized_tree:
            if not self.compute_step_minimized_tree(show_message=False):
                return False
        if not self.pipeline_graph:
            messagebox.showerror("Error", "Pipeline graph is not available")
            return False
        try:
            self.rich_tree_mapping = make_rich_tree_decomposition(self.minimized_tree, self.pipeline_graph)
            self.rich_tree = RichTreeDecomposition(self.minimized_tree, self.rich_tree_mapping)
            self.draw_rooted_tree(self.minimized_tree, "Step 3: Rich Tree Basis")
            mapping_count = len(self.rich_tree_mapping)
            non_empty_bags = sum(1 for edges in self.rich_tree_mapping.values() if len(edges) > 0)

            try:
                sources_dict_text = str(self.rich_tree.create_sources_dict())
            except Exception as sd_error:
                sources_dict_text = "<sources_dict failed: " + str(sd_error) + ">"

            rich_summary = "Tree width: " + str(self.rich_tree.treeWidth) + "\n"
            rich_summary += "Mapped bags: " + str(mapping_count) + "\n"
            rich_summary += "Non-empty edge bags: " + str(non_empty_bags) + "\n"
            rich_summary += "Sources: " + str(self.rich_tree.sources) + "\n"
            rich_summary += "Sources dict: " + sources_dict_text + "\n\n"
            rich_summary += "Rich tree mapping:\n" + self._format_rich_mapping()
            self._append_pipeline_output("STEP 3 RICH", rich_summary)
            if show_message:
                messagebox.showinfo("Step 3", "Rich tree mapping computed")
            return True
        except Exception as e:
            self._append_pipeline_output("STEP 3 ERROR", traceback.format_exc())
            messagebox.showerror("Error", f"Error in Step 3 (Rich mapping): {str(e)}")
            return False

    def compute_step_fhr_tree(self, show_message=True):
        if not self.rich_tree:
            if not self.compute_step_rich_mapping(show_message=False):
                return False
        try:
            self.fhr_tree = self.rich_tree.create_FHR_term()
            self.draw_rooted_tree(self.fhr_tree, "Step 4: FHR Algebra Tree")
            self._append_pipeline_output("STEP 4 FHR", self.fhr_tree)
            if show_message:
                messagebox.showinfo("Step 4", "FHR algebra tree computed")
            return True
        except Exception as e:
            self._append_pipeline_output("STEP 4 ERROR", traceback.format_exc())
            messagebox.showerror("Error", f"Error in Step 4 (FHR): {str(e)}")
            return False
    
    def _create_binary_compatible_tree(self, rooted_tree):
        """Create a copy of the rooted tree with string labels for binary tree conversion"""
        node_map = {}
        
        def clone_node(node):
            if node in node_map:
                return node_map[node]
            
            # Convert label to string
            new_label = str(node.label)
            new_node = Node(new_label, node.id, [])
            node_map[node] = new_node
            
            # Clone children
            for child in node.children:
                child_clone = clone_node(child)
                new_node.add_child(child_clone)
            
            return new_node
        
        root_clone = clone_node(rooted_tree.root)
        return RootedTree(root_clone, [])
    
    def convert_to_binary_tree(self):
        """Convert the current rooted tree to a binary tree"""
        if not self.rooted_tree:
            messagebox.showwarning("No Rooted Tree", "Please create a rooted tree first")
            return
        
        try:
            # Create a binary-compatible version with string labels
            binary_compatible_tree = self._create_binary_compatible_tree(self.rooted_tree)
            
            # Use graphLib make_binary_tree function
            self.binary_tree = make_binary_tree(binary_compatible_tree)
            print("Binary tree created successfully")
            self.node_positions.clear()
            
            # Draw the binary tree
            self.draw_binary_tree()
            messagebox.showinfo("Success", "Rooted tree converted to binary tree successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error converting to binary tree: {str(e)}")
    
    def draw_binary_tree(self):
        """Draw the binary tree in hierarchical layout on the binary tree canvas"""
        self.binary_canvas.delete("all")
        if not self.binary_tree:
            return
        
        # Calculate hierarchical positions
        self.node_positions.clear()
        canvas_width = self.binary_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 400
        
        leaf_count = self._count_binary_leaves(self.binary_tree.root)
        unit = max(60, min(140, int(canvas_width / (leaf_count + 1))))
        start_x = max(40, (canvas_width - (leaf_count - 1) * unit) / 2)
        self._assign_binary_positions(self.binary_tree.root, depth=0, start_x=start_x, unit=unit, layer_height=70)
        
        # Draw edges (parent to children)
        self._draw_binary_node_edges(self.binary_tree.root)
        
        # Draw nodes
        self._draw_binary_nodes(self.binary_tree.root)
    
    def _count_binary_leaves(self, node):
        if not node.children:
            return 1
        return sum(self._count_binary_leaves(child) for child in node.children)

    def _assign_binary_positions(self, node, depth, start_x, unit, layer_height=80):
        node_key = f"binary_{node.id}"
        y = 30 + depth * layer_height
        
        if not node.children:
            self.node_positions[node_key] = (start_x, y)
            return start_x + unit
        
        if len(node.children) == 1:
            next_x = self._assign_binary_positions(node.children[0], depth + 1, start_x, unit, layer_height)
            child_key = f"binary_{node.children[0].id}"
            child_x = self.node_positions[child_key][0]
            self.node_positions[node_key] = (child_x, y)
            return next_x
        
        next_x = self._assign_binary_positions(node.children[0], depth + 1, start_x, unit, layer_height)
        next_x = self._assign_binary_positions(node.children[1], depth + 1, next_x, unit, layer_height)
        left_key = f"binary_{node.children[0].id}"
        right_key = f"binary_{node.children[1].id}"
        left_x = self.node_positions[left_key][0]
        right_x = self.node_positions[right_key][0]
        self.node_positions[node_key] = ((left_x + right_x) / 2, y)
        return next_x
    
    def _draw_binary_node_edges(self, node):
        """Draw edges from parent to children on binary_canvas"""
        node_key = f"binary_{node.id}"
        if node_key in self.node_positions:
            x1, y1 = self.node_positions[node_key]
            
            for child in node.children:
                child_key = f"binary_{child.id}"
                if child_key in self.node_positions:
                    x2, y2 = self.node_positions[child_key]
                    self.binary_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
                    self._draw_binary_node_edges(child)
    
    def _draw_binary_nodes(self, node):
        """Recursively draw nodes with their labels on binary_canvas"""
        node_key = f"binary_{node.id}"
        if node_key not in self.node_positions:
            return
        
        x, y = self.node_positions[node_key]
        r = 28
        
        # Check if this is a join node (contains "join" in label)
        is_join = "join" in node.label.lower()
        
        if is_join:
            # Join nodes in purple
            shadow_color = "#4a148c"
            main_color = "#7b1fa2"
            outline_color = "#9c27b0"
        else:
            # Regular nodes in green
            shadow_color = "#1b5e20"
            main_color = "#2e7d32"
            outline_color = "#66bb6a"
        
        # Outer shadow
        self.binary_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill=shadow_color, 
                          outline="", tags=f"binary_node_{node.id}")
        # Main circle
        self.binary_canvas.create_oval(x-r, y-r, x+r, y+r, fill=main_color, 
                          outline=outline_color, width=2, tags=f"binary_node_{node.id}")
        # Text - use a shortened label if too long
        label_text = str(node.label)[:10]  # Limit label length
        self.binary_canvas.create_text(x, y, text=label_text, font=("Segoe UI", 9, "bold"), 
                          fill="white", tags=f"binary_node_{node.id}")
        
        # Recursively draw children
        for child in node.children:
            self._draw_binary_nodes(child)
    
    def browse_file(self):
        """Open file dialog to select a graph file"""
        file_types = [("Graph Files", "*.lst *.txt"), ("Adjacency List", "*.lst"), ("Edge List", "*.txt"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types, title="Load Graph File")
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
    
    def load_from_file(self):
        """Load a graph from the selected file"""
        file_path = self.file_path_entry.get().strip()
        if not file_path:
            messagebox.showwarning("Input Error", "Please select a file or enter a file path")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"File '{file_path}' does not exist")
            return
        
        try:
            # Determine file type by extension
            if file_path.endswith('.lst'):
                graph = load_graph_from_adjacency_list(file_path)
            elif file_path.endswith('.txt'):
                graph = load_graph_from_edge_list(file_path)
            else:
                # Try adjacency list first, then edge list
                graph = load_graph_from_adjacency_list(file_path)
                if not graph:
                    graph = load_graph_from_edge_list(file_path)
            
            if not graph:
                messagebox.showerror("Error", "Failed to load graph from file")
                return
            
            # Clear current graph
            self.vertices.clear()
            self.edges.clear()
            self.vertex_positions.clear()
            self.tree_decomposition = None
            self.rooted_tree = None
            self.minimized_tree = None
            self.rich_tree = None
            self.rich_tree_mapping = None
            self.fhr_tree = None
            self.pipeline_graph = None
            self.rooted_drag_node = None
            self.rooted_view_tree = None
            self.rooted_positions.clear()
            self.rooted_nodes_by_key.clear()
            self.bag_positions.clear()
            
            # Load graph data
            self.vertices = {v.label: v for v in graph.vertices}
            self.edges = graph.edges
            
            # Update UI
            self.update_lists()
            self.draw_graph()
            self.tree_canvas.delete("all")
            self.rooted_canvas.delete("all")
            self.pipeline_output.delete("1.0", "end")
            
            messagebox.showinfo("Success", f"Graph loaded successfully!\nVertices: {len(graph.vertices)}, Edges: {len(graph.edges)}")
            self.file_path_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading graph: {str(e)}")
    
    def save_graph(self):
        name = self.save_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if not self.vertices:
            messagebox.showwarning("Empty Graph", "Please add vertices first")
            return
        
        # Convert vertices and edges to serializable format
        vertices_data = {label: label for label in self.vertices.keys()}
        edges_data = [sorted([str(v) for v in e]) for e in self.edges]
        
        self.saved_graphs[name] = {
            "vertices": vertices_data,
            "edges": edges_data
        }
        
        self.save_graphs_to_file()
        messagebox.showinfo("Success", f"Graph '{name}' saved successfully")
        self.save_name_entry.delete(0, tk.END)
        self.refresh_saved_graphs()
    
    def load_graph(self):
        name = self.load_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if name not in self.saved_graphs:
            messagebox.showwarning("Not Found", f"Graph '{name}' not found")
            return
        
        # Clear current graph
        self.vertices.clear()
        self.edges.clear()
        self.vertex_positions.clear()
        self.bag_positions.clear()
        self.node_positions.clear()
        self.tree_decomposition = None
        self.rooted_tree = None
        self.minimized_tree = None
        self.rich_tree = None
        self.rich_tree_mapping = None
        self.fhr_tree = None
        self.pipeline_graph = None
        self.rooted_drag_node = None
        self.rooted_view_tree = None
        self.rooted_positions.clear()
        self.rooted_nodes_by_key.clear()
        
        # Load graph data
        graph_data = self.saved_graphs[name]
        
        # Load vertices
        for label in graph_data["vertices"].keys():
            self.vertices[label] = Vertex(label)
        
        # Load edges
        for edge_data in graph_data["edges"]:
            if len(edge_data) == 2 and edge_data[0] in self.vertices and edge_data[1] in self.vertices:
                self.edges.append({self.vertices[edge_data[0]], self.vertices[edge_data[1]]})
        
        self.update_lists()
        self.draw_graph()
        self.tree_canvas.delete("all")
        self.rooted_canvas.delete("all")
        self.pipeline_output.delete("1.0", "end")
        self.load_name_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Graph '{name}' loaded successfully")
    
    def delete_graph(self):
        name = self.load_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if name not in self.saved_graphs:
            messagebox.showwarning("Not Found", f"Graph '{name}' not found")
            return
        
        del self.saved_graphs[name]
        self.save_graphs_to_file()
        messagebox.showinfo("Success", f"Graph '{name}' deleted successfully")
        self.load_name_entry.delete(0, tk.END)
        self.refresh_saved_graphs()
    
    def refresh_saved_graphs(self):
        self.saved_graphs_list.delete("1.0", "end")
        if not self.saved_graphs:
            self.saved_graphs_list.insert("1.0", "No saved graphs")
        else:
            graphs_text = "\n".join(sorted(self.saved_graphs.keys()))
            self.saved_graphs_list.insert("1.0", graphs_text)
    
    def load_graphs_from_file(self):
        """Load saved graphs from JSON file"""
        if os.path.exists(self.graphs_file):
            try:
                with open(self.graphs_file, 'r') as f:
                    self.saved_graphs = json.load(f)
            except Exception as e:
                print(f"Error loading graphs from file: {e}")
                self.saved_graphs = {}
        else:
            self.saved_graphs = {}
    
    def save_graphs_to_file(self):
        """Save all graphs to JSON file"""
        try:
            with open(self.graphs_file, 'w') as f:
                json.dump(self.saved_graphs, f, indent=2)
        except Exception as e:
            print(f"Error saving graphs to file: {e}")
    
    def on_closing(self):
        """Handle window closing - save graphs before exit"""
        self.save_graphs_to_file()
        self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = GraphGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
