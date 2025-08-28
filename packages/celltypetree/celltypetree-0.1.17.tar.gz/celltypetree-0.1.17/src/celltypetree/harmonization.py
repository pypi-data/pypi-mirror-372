import numpy as np
import pandas as pd
import networkx as nx
from anndata import AnnData
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib import rcParams
import re

class CellTypeTree:
    """
    Class for harmonizing cell type annotations in a hierarchical way based on a tree of cell types.
    """
    def __init__(self, tree, mappings=None, root=None, unlabelled="Unclassified"):
        """
        harmonizes different cell type annotations in a hierarchical way
        based on a tree of cell types.

        params:
            tree: networkx.DiGraph, pandas DataFrame, list of tuples or list of lists
                Directed acyclic graph representing the cell type hierarchy, edges must go from
                specific to general (CD4Tcell -> Tcell). Accepted formats are pandas DataFrame,
                list of tuples, list of lists or a networkx DiGraph.
            mappings: dict
                A dictionary with keys corresponding to annotation keys in adata.obs, each annotation
                key should map to a dictionary where keys are cell types in the original annotation
                and values are cell types in the tree. Effectively a dictionary of dictionaries.
                Example: mappings['annotation1'] = {'orig_celltype_label': 'new_celltype_label_in_tree'}
            root: str
                Label of the root of the tree, will try to determine automatically if not provided
            unlabelled: str
                Label to use for marking unlabelled cells, default is "Unclassified".
        """
        # if tree is a pandas DataFrame, read it as an edgelist
        if isinstance(tree, pd.DataFrame):
            # dataframe should have columns 'source' and 'target'
            if not all(col in tree.columns for col in ['source', 'target']):
                raise ValueError("tree must be a pandas DataFrame with columns 'source' and 'target'")
            tree = nx.from_pandas_edgelist(tree, source='source', target='target', create_using=nx.DiGraph())

        # if tree is a list of tuples, read it as an edgelist
        elif isinstance(tree, list) and all(isinstance(t, tuple) and len(t) == 2 for t in tree):
            tree = nx.DiGraph(tree)

        # if tree is a list of lists, read it as an edgelist
        elif isinstance(tree, list) and all(isinstance(t, list) and len(t) == 2 for t in tree):
            tree = nx.DiGraph((t[0], t[1]) for t in tree)

        # Tree must be a directed acyclic graph
        if not nx.is_directed_acyclic_graph(tree):
            raise ValueError("tree must be a directed acyclic graph")
       
        # If root is not set, try to find it as the only node with no outgoing edges
        if root is None:
            indegrees = dict(tree.in_degree())
            outdegrees = dict(tree.out_degree())

            # If there is a single node with no outgoing edges, use it as root 
            # root should also have at least one incoming edge
            possible_roots = [node for node, out_degree in outdegrees.items() if out_degree == 0 and indegrees[node] > 0]
            if len(possible_roots) == 1:
                root = possible_roots[0]
                print(f"Automatically determined root node: {root}")
            elif len(possible_roots) > 1:
                raise ValueError(
                    f"Multiple possible roots found: {possible_roots}. " + \
                    "Please specify the root explicitly. This can also happen " + \
                    "if root has outgoing edges, try inverting source and target of all edges."
                )
        
        # Check if root is in the tree
        if root not in tree.nodes:
            raise ValueError(f"root {root} is not in the tree")

        # Root node should only have incoming edges, if not, invert all edges in the tree
        # Check if all the edges of root are in the right direction 
        if len(tree.out_edges(root)) > 0:
            print(f"Warning: root {root} has outgoing edges, will try to invert all edges in the tree")
            # create a new tree with source and target swapped for each edge in the whole network
            tree = nx.DiGraph((target, source) for source, target in tree.edges)
        
        # Set mappings
        self.mappings = mappings if mappings else {}
        self.unlabelled = unlabelled
        self.G = tree
        self.root = root
        self.max_depth = nx.dag_longest_path_length(self.G)
        self.set_colors()
        
        # Check if mappings is a dictionary of dictionaries
        if mappings is None:
            mappings = {}

        if not isinstance(mappings, dict) or not all(isinstance(v, dict) for v in mappings.values()):
            raise ValueError("mappings must be a dictionary of dictionaries")
   
    def set_colors(self, cmap=None):
        """
        Set a color for each node of the tree. Accepts a colormap or a string
        that can be used to create a colormap. If cmap is None, will try to select
        a suitable colormap based on the number of cell types.
        """
        all_cell_types = set(self.G.nodes).union({self.unlabelled})
        N = len(all_cell_types)
        
        if cmap is None:
            # Choose colormap based on number of cell types
            if N <= 10:
                cmap = plt.get_cmap('tab10')
            elif N <= 20:
                cmap = plt.get_cmap('tab20')
            elif N <= 40:
                cmap1 = plt.get_cmap('tab20b')
                cmap2 = plt.get_cmap('tab20c')
                colors = [cmap1(i) for i in range(20)] + [cmap2(i) for i in range(20)]
                # colormap should be callable
                cmap = lambda i: colors[i]
            else:
                cmap = cm.get_cmap('hsv', N)
        else:
            # If cmap is a string, try to get a colormap by that name
            if isinstance(cmap, str):
                cmap = plt.get_cmap(cmap)
            # If cmap is not a colormap, raise an error
            elif not isinstance(cmap, mcolors.Colormap):
                raise ValueError("cmap must be a matplotlib colormap or a string")

        # Create colors dictionary, convert to hex
        #self.colors = {ct: cmap(i) for i, ct in enumerate(all_cell_types)}
        self.colors = {ct: mcolors.to_hex(cmap(i)) for i, ct in enumerate(all_cell_types)}

    def get_expanded_keys(self):
        """get keys of columns of expanded cell types for each annotation"""
        # Create a list of columns for expanded cell types
        columns = []

        for annot in self.mappings.keys():
            for level in range(1, self.max_depth + 1):
                columns.append(f"{annot}{level}")

        return columns

    #def subset_tree(self, newtree, newroot=None):
    #    """subset tree to a new tree that is a subgraph of the original tree"""
    #    if not nx.is_directed_acyclic_graph(self.G.subgraph(newtree.nodes)):
    #        raise ValueError("newtree must be a subgraph of the original tree")
    #    self.G = newtree
    #    # Update max depth
    #    self.max_depth = nx.dag_longest_path_length(self.G)
    #    self.update_expanded_keys()
    #    # Update root if newroot is provided
    #    if newroot is not None:
    #        self.root = newroot
    #    # TODO: update colors, expanded_keys, mappings, etc. if necessary

    def get_parent(self, cell_type):
        """get parent of a cell type"""
        if cell_type == self.root:
           return
        return list(self.G.out_edges(cell_type))[0][1]

    def get_children(self, cell_type):
        """get childrens of a cell type"""
        # check if cell_type is in tree
        return [child for child, parent in list(self.G.in_edges(cell_type))]
    
    def get_all_in_level(self, level: int):
        """get all cell types at a given level"""
        return [node for node in self.G.nodes if nx.shortest_path_length(self.G, node, self.root) == level]

    def get_annotation_level(self, cell_type):
        """get the level of a cell type"""
        # check if cell_type is in tree
        if cell_type not in self.G.nodes:
            raise ValueError(f"cell_type {cell_type} is not in the tree")
        return nx.shortest_path_length(self.G, cell_type, self.root)

    def expand(self, cell_type):
        """recursively expand a cell type to all its parents"""
        if cell_type == self.root:
            return [cell_type]
        return self.expand(self.get_parent(cell_type)) + [cell_type]

    def rename(self, mapper):
        """
        rename nodes in the tree using a mapper dictionary. This changes the names of the
        target cell types in the tree. To map original cell types to new names in the tree
        use `harmonize` method instead.
        """
        # Check if mapper is a dictionary
        if not isinstance(mapper, dict):
            raise ValueError("mapper must be a dictionary")

        # Check if all keys in mapper are in the tree
        if not set(mapper.keys()).issubset(set(self.G.nodes)):
            raise ValueError(
                "The following keys in mapper are not in the tree: " + \
                str(set(mapper.keys()).difference(set(self.G.nodes)))
            )

#        # Check if multiple keys in mapper map to the same value
#        if len(set(mapper.values())) < len(mapper.values()):
#            duplicates = defaultdict(list)
#            for k, v in mapper.items():
#                duplicates[k].append(v)
#            duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
#            # Raise a Warning and rename one of the keys by adding a ' at the end
#            print("Warning: the following mappings are not unique:" + str(duplicates.keys()))
#            # Create new mapping by adding ', '' etc. at the end of the values
#            reverse_duplicates = {v: [] for v in duplicates.values()}
#            for k, v in duplicates.items():
#                reverse_duplicates[v].append(k)
#            for k, v in reverse_duplicates.items(): 
#                if len(v) > 1:
#                    for i in range(len(v)):
#                        # Add a ' at the end of the key
#                        new_key = v[i] + "'" * (i + 1)
#                        mapper[new_key] = k
#                        # Remove the old key from the mapper
#                        del mapper[v[i]]
       

        # Check if multiple keys in mapper map to the same value
        if len(set(mapper.values())) < len(mapper.values()):
            duplicates = defaultdict(list)
            for k, v in mapper.items():
                duplicates[v].append(k)  # group by value, not key
            
            # Keep only duplicates (values mapped by multiple keys)
            duplicates = {val: keys for val, keys in duplicates.items() if len(keys) > 1}

            print("Warning: the following mappings are not unique:")
            for val, keys in duplicates.items():
                print(f"  Value '{val}' is mapped by multiple keys: {keys}")

            # Group duplicates by value and  rename values by adding * at the end
            # e.g is 3 labels map to Fibroblast, have them map to Fibroblast, Fibroblast*
            # Fibroblast**. Inform the user of each change
            all_values_to_rename = {k: 0 for k in duplicates.keys()}
            print("Adding suffixes to target labels to ensure uniqueness:")
            for key, value in mapper.items():
                if value in all_values_to_rename:
                    suffix = "*" * (all_values_to_rename[value])
                    new_value = f"{value}{suffix}"
                    print(f"\"{key}'\" → \"{new_value}\"") 
                    mapper[key] = new_value
                    all_values_to_rename[value] += 1

        # Rename nodes in the tree
        self.G = nx.relabel_nodes(self.G, mapper)

        # Update mappings to reflect the new names
        for annot in self.mappings.keys():
            self.mappings[annot] = {k: mapper.get(v, v) for k, v in self.mappings[annot].items()}

        # Update root if it was renamed
        if self.root in mapper.keys():
            self.root = mapper[self.root]

        # Update colors to reflect the new names
        new_colors = {}
        for k, v in self.colors.items():
            if k in mapper:
                new_colors[mapper[k]] = v
            else:
                new_colors[k] = v
        self.colors = new_colors

    def rewire(self, nodes, new_parent):
        """Disconnects list of nodes from their current parent and connects them to a new parent"""
        # If node is a string, convert it to a list
        if isinstance(nodes, str):
            nodes = [nodes]

        # Root node can't be reparented
        if self.root in nodes:
            raise ValueError(f"Root node {self.root} cannot be rewired")
        
        # Check if nodes and new_parent are in the tree
        if not set(nodes).union([new_parent]).issubset(set(self.G.nodes)):
            raise ValueError(
                "The following nodes are not in the tree: " + \
                str(set(nodes).union([new_parent]).difference(set(self.G.nodes)))
            )
        
        # Check that new_parent is not in nodes
        if new_parent in nodes:
            raise ValueError(f"New parent {new_parent} cannot be one of the nodes to rewire")

        # For each node, disconnect it from its current parent
        for node in nodes:
            parent = self.get_parent(node)
            if parent is not None:
                self.G.remove_edge(node, parent)

        # Connect nodes to the new parent
        for node in nodes:
            self.G.add_edge(node, new_parent)

        # Update max depth if necessary
        self.max_depth = nx.dag_longest_path_length(self.G)

    def add_nodes(self, nodes, parent=None):
        """
        Add one or more nodes to the tree, optionally with a parent.
        If parent is not specified, the new node will be added as a child of the root.
        """
        # If nodes is a string, convert it to a list
        if isinstance(nodes, str):
            nodes = [nodes]

        # Check if nodes are already in the tree
        if any(node in self.G.nodes for node in nodes):
            raise ValueError("Nodes " + ','.join(set(nodes).intersection(set(self.G.nodes))) + " are already in the tree")

        # If parent is not specified, use the root
        if parent is None:
            parent = self.root

        # Check if parent is in the tree
        if parent not in self.G.nodes:
            raise ValueError(f"Parent {parent} is not in the tree")

        # Add nodes to the tree
        for node in nodes:
            if node in self.G.nodes:
                raise ValueError(f"Node {node} is already in the tree")
            self.G.add_node(node)
            self.G.add_edge(node, parent)
        
        # Update max depth if necessary
        self.max_depth = nx.dag_longest_path_length(self.G)

    def remove_nodes(self, nodes, remove_children=False):
        """
        Remove a one of more nodes from the tree, by default children
        are rewired to the parent of the removed node. Use remove_children=True
        to remove the node and all its children.
        """
        # If nodes is a string, convert it to a list
        if isinstance(nodes, str):
            nodes = [nodes]

        # Check if nodes are missing from the tree 
        if any(node not in self.G.nodes for node in nodes): 
            raise ValueError("Nodes " + ','.join(set(nodes).difference(set(self.G.nodes))) + " are not in the tree")
        
        # Root node can't be removed
        if self.root in nodes:
            raise ValueError(f"Root node {self.root} cannot be removed")
        
        # Remove the node and all its children
        for node in nodes:
            # Get all children of the node
            children = self.get_children(node)
            if remove_children:
                for child in children:
                    self.G.remove_node(child) 
            else:
                # If not removing children, rewire them to the parent of the node
                parent = self.get_parent(node)
                self.rewire(children, parent)
            # Remove the node itself 
            self.G.remove_node(node)

        # Update
        self.max_depth = nx.dag_longest_path_length(self.G)
        self.set_colors()
        
        # Also remove the node from mappings and colors
        if node in self.mappings:
            for annot in self.mappings.keys():
                if node in self.mappings[annot]:
                    del self.mappings[annot][node]
        if node in self.colors:
            del self.colors[node]

    def print(self, root=None, indent="", last=True):
        """
        Print the tree
        Example:
            └── A
                ├── B
                │   ├── E
                │   └── F
                │       └── H
                ├── C
                │   └── G
                └── D

        FOllow this generic example, but make it work with our tree

        def print_tree(tree, root, indent="", last=True):
            #Pretty-prints a tree given as adjacency dict.

            #Parameters:
            #    tree (dict): Adjacency dictionary {node: [children]}.
            #    root (str): Starting root node.
            #    indent (str): Used internally for indentation.
            #    last (bool): Used internally to track last child.
            # Print current node with tree structure characters
            prefix = indent + ("└── " if last else "├── ")
            print(prefix + str(root))

            # Update indentation for children
            indent += "    " if last else "│   "

            # Recurse on children
            children = tree.get(root, [])
            for i, child in enumerate(children):
                print_tree(tree, child, indent, i == len(children)-1)


        # Example usage
        if __name__ == "__main__":
            tree = {
                "A": ["B", "C", "D"],
                "B": ["E", "F"],
                "C": ["G"],
                "D": [],
                "E": [],
                "F": ["H"],
                "G": [],
                "H": []
            }

            print_tree(tree, "A")
        """
        prefix = indent + ("└── " if last else "├── ")
        print(prefix + str(root if root is not None else self.root))
        if root is None:
            root = self.root

        children = self.get_children(root)
        for i, child in enumerate(children):
            # Determine if this is the last child
            is_last = (i == len(children) - 1)
            # Call print recursively for each child
            self.print(child, indent + ("    " if last else "│   "), is_last)

    def plot(
        self,
        colors=None,
        mapping=None,
        fontsize=10,
        offset=0.3,
        jitter=False,
        expand_horizontal_pos=True, 
        scale=1, 
        sep='|',
        ax=None, 
        random_state=0
    ):
        """
        Hierarchical visualization of the tree

        params:
            colors: bool
                whether to color nodes according to their cell type, by default colors
                are not used unless a mapping is provided.
            mapping: str
                if a valid annotation key is provided, will also show and highlight
                the original cell type labels in the plot.
            fontsize: int
                fontsize for the node labels
            offset: float
                fraction of vertical gap to use for offsetting nodes at the same level
            jitter: bool
                wether to add random jitter to the vertical positions of the nodes
            expand_horizontal_pos: bool
                whether to expand each level to fill the total width of the plot
            scale: float
                scaling factor for figure size
            sep: str
                string that separates cell types in the labels. Will be replaced with
                a newline character in the plot
            ax: matplotlib axis
                matplotlib axis to draw on, if None, create a new figure and axis
            random_state: int
                random seed for reproducibility of jitter
        """
        max_depth = self.max_depth

        # If mapping is provided, check if it is a valid key in the mappings
        if mapping is not None:
            if mapping not in self.mappings:
                raise ValueError(f"Mapping {mapping} is not in the mappings")
            # Check if all cell types in the mapping are in the tree (exclude unlabelled)
            all_targets = set(self.mappings[mapping].values()).difference({self.unlabelled})
            if not all_targets.issubset(set(self.G.nodes)):
                raise ValueError(
                    "The following cell types in mapping are not in the tree: " + \
                    str(set(self.mappings[mapping].values()).difference(set(self.G.nodes)))
                )
            # Create reverse mapping with a list of all nodes that map to the same cell type
            #reverse_mapping = {v: k for k, v in self.mappings[mapping].items()}
            reverse_mapping = defaultdict(list)
            for k, v in self.mappings[mapping].items():
                reverse_mapping[v].append(k)
            reverse_mapping = dict(reverse_mapping)

        # If color is not set, set it to True only if mapping is provided
        if colors is None:
            if mapping is None:
                colors = False
            else:
                colors = True

        # If colors are set, but not all cell types in the tree have colors, raise a warning
        if colors and not set(self.G.nodes).issubset(set(self.colors.keys())):
            missing_colors = set(self.G.nodes).difference(set(self.colors.keys()))
            print(
                "Warning: the following cell types in the tree don't have colors assigned: " + \
                str(missing_colors), ". Reassigning all colors."
            )
            self.set_colors()

        # Recursively get positions
        def hierarchy_pos(G, root=None, width=1, vertical_gap=1/max_depth, vertical_loc=0, xcenter=0.5):
            '''
            Adapted from Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
            Licensed under Creative Commons Attribution-Share Alike 
            '''
            def _hierarchy_pos(G, root, width=1., vert_gap=1., vert_loc=0, xcenter=0.5, pos=None, parent=None):

                if pos is None:
                    pos = {root:(xcenter,vert_loc)}
                else:
                    pos[root] = (xcenter, vert_loc)
                children = [child for child, parent in list(G.in_edges(root))]
                if not isinstance(G, nx.DiGraph) and parent is not None:
                    children.remove(parent)
                if len(children)!=0:
                    dx = width/len(children)
                    nextx = xcenter - width/2 - dx/2
                    for child in children:
                        nextx += dx
                        pos = _hierarchy_pos(
                            G,
                            child, 
                            width = dx,
                            vert_gap = vert_gap,
                            vert_loc = vert_loc-vert_gap,
                            xcenter=nextx,
                            pos=pos,
                            parent = root
                        )
                return pos
            return _hierarchy_pos(G=G, root=root)
    
        def expand_horizontal_positions(pos):
            '''
            Expand horizontal positions of nodes with in the same level (same vertical position)
            to fill the total width of the plot. Mantain original left-to-right order
            '''
            tolerance = 1e-5
            y_groups = defaultdict(list)

            # Group nodes by approximate y position
            for node, (x, y) in pos.items():
                rounded_y = round(y / tolerance) * tolerance
                y_groups[rounded_y].append((node, x))

            new_pos = pos.copy()
            for group_y, nodes in y_groups.items():
                if len(nodes) == 1:
                   # if there is only one node, set it's position to 0.5  
                   new_pos[nodes[0][0]] = (0.5, group_y)
                else:
                    # if there are multiple nodes, make them evenly spaced
                    nodes.sort(key=lambda item: item[1])
                    grid = np.linspace(0, 1, len(nodes))
                    for i, (node, _) in enumerate(nodes):
                        new_pos[node] = (grid[i], group_y)

            return new_pos

        def add_vertical_offset(pos, vert_gap=1/max_depth, offset=0.1, jitter=True):
            '''
            Adjust node y-positions to reduce label overlap by applying alternating vertical offsets
            for nodes at the same hierarchical level.
            '''
            tolerance = 1e-5
            y_groups = defaultdict(list)

            if jitter:
                # Set random seed for reproducibility
                np.random.seed(random_state)

            # Group nodes by approximate y position
            for node, (x, y) in pos.items():
                rounded_y = round(y / tolerance) * tolerance
                y_groups[rounded_y].append((node, x))

            new_pos = pos.copy()
            for group_y, nodes in y_groups.items():
                nodes.sort(key=lambda item: item[1])  # sort by x
                for i, (node, x) in enumerate(nodes):
                    direction = (-1)**i
                    y_offset = direction * offset* vert_gap
                    if jitter:
                        # Multiply jitter by random number between -1 and 1
                        random_jitter = np.random.uniform(-1, 1)*offset*vert_gap
                        y_offset += random_jitter
                    orig_x, orig_y = pos[node]
                    new_pos[node] = (orig_x, orig_y + y_offset)

            return new_pos 
       
        pos = hierarchy_pos(self.G, root=self.root)
        if expand_horizontal_pos:
            pos = expand_horizontal_positions(pos)
        pos = add_vertical_offset(pos, offset=offset, jitter=jitter, vert_gap=1/max_depth)
       
        # Create a new figure and axis if ax is not provided
        if ax is None:
            show = True
            # determine figsize as number of nodes in biggest level x number of levels
            width = scale*2*max([len(self.get_all_in_level(i)) for i in range(self.max_depth)])
            height = scale*2*self.max_depth
            # create figure and axis
            fig, ax = plt.subplots(1, 1, figsize=(width, height))
        else:
            show = False 

        # Draw graph without labels
        nx.draw(self.G, pos, with_labels=False, node_size=0, node_color='none', arrows=False, ax=ax)

        # Draw labels
        text_items = {}
        for node, (x, y) in pos.items():
            # By default plot node labels, use colors if colors is True
            color = self.colors.get(node, 'black') if colors else 'black'
            fontweight = 'normal'
            text = node  # Default text is the node name
            if mapping:
                # If plotting a mapping, only color nodes that are in the mapping
                color = 'black'
                text = f'{node}'
                if node in reverse_mapping:
                    labels = reverse_mapping[node]
                    color = self.colors.get(node, 'black') if colors else 'black'
                    fontweight = 'bold'
                    text = f"{node}"
                    for label in labels:
                        text += f"\n({label})"

            if sep is not None:
                # Replace separator with newline character
                text = text.replace(sep, '\n')
            text_items[node] = ax.text(x, y, text, fontsize=fontsize, ha='center', va='center', color=color, fontweight=fontweight)

        # Apply white outline to each label
        for text in text_items.values():
            text.set_path_effects([
                withStroke(linewidth=5, foreground='white', alpha=0.95)
            ])

        if show:
            # show the plot if no axis was provided
            plt.show()

    def harmonize(self, adata, cmap=None):
        """
        add harmonized cell types to adata.obs. Cell types will be added as new columns
        with keys in the format <annotation><level>, where <annotation> is the name of the
        annotation and <level> is the level in the tree (0 is root, 1 is first level, etc.).

        params:
            adata: AnnData object
            cmap: str or matplotlib colormap, optional
                color map to use when harmonizing colors in adata.uns.
                If None, will try to determine a suitable colormap based on the number of cell types
        """
        # Check if adata is an AnnData object
        if not isinstance(adata, AnnData):
            raise ValueError("adata must be an AnnData object")
        
        # Read adata.obs
        obs = adata.obs

        # Check if all annotations are in adata.obs
        if not set(self.mappings.keys()).issubset(set(adata.obs.columns)):
            raise ValueError(
                "The following annotations are not columns of adata.obs: " + \
                set(self.mappings.keys()).difference(set(adata.obs.columns))
            )

        # Loop over each annotation
        for annot in self.mappings.keys():
            # For each annotation, check if all the new cell types are in the tree
            all_celltypes = set(self.mappings[annot].values())
            if self.unlabelled in all_celltypes:
                all_celltypes.remove(self.unlabelled)
            if not all_celltypes.issubset(set(self.G.nodes)):
                raise ValueError(
                    "Annotation: " + annot + " has cell types that are not in the tree: " + \
                    ",".join(set(self.mappings[annot].values()).difference(set(self.G.nodes)))
                )

            # For each annotation, check if all original cell types in adata are mapped somewhere in the tree,
            # those that are not will be ignored and the user will be warned
            unmapped = set(adata.obs[annot].unique()).difference(set(self.mappings[annot].keys()))
            if self.unlabelled in unmapped:
                unmapped.remove(self.unlabelled)
            if unmapped:
                print(
                    f"Warning: the following cell types in {annot}" + \
                      f" are not mapped to the tree: {unmapped} and will be ignored"
                )
       
            # Create list of celltypes to ignore
            ignore = []
            # Add unmapped cell types to ignore
            if unmapped:
                ignore += list(unmapped)
            # Add unlabelled cell type to ignore
            if self.unlabelled not in ignore:
                ignore.append(self.unlabelled)
            # Add cell types that map to unlabelled to ignore
            ignore += [k for k, v in self.mappings[annot].items() if v == self.unlabelled]
            
            # create dict of expanded cell types
            ct_dict_exp = {}
            for k, v in self.mappings[annot].items():
                if v not in ignore:
                    ct_dict_exp[k] = self.expand(v)

            # max_depth is number of links, add 1 to get number of levels
            depth = self.max_depth + 1 

            # extend all to max detected length by repeating last element
            for k, v in ct_dict_exp.items():
                ct_dict_exp[k] = v + [v[-1]] * (depth - len(v))

            # cell types in ignore are expanded to unlabelled
            for k in ignore:
                ct_dict_exp[k] = [self.unlabelled] * depth

            # add new_keys to ad.obs
            new_keys = [annot + str(i) for i in range(depth)]
            for k in new_keys:
                obs[k] = self.unlabelled

            # populate new_keys with expanded cell types
            obs[new_keys] = obs.apply(
                lambda x: ct_dict_exp[x[annot]], axis=1, result_type="expand"
            )
           
        # Set matching colors for each annotation
        self.set_colors(cmap=cmap)
        self.set_adata_colors(adata)

    def set_adata_colors(self, adata, keys=None):
        '''
        Make sure that the same cell type has the same color across the different
        colorschemes saved for different keys in adata.uns.
        
        params:
            adata: AnnData object
            keys: list of keys in adata.obs to set colors for, if None, will get_expanded_keys
        '''
        # Check if colors are set
        if not hasattr(self, 'colors'):
            raise ValueError("Colors are not set, call set_colors() first")
            self.set_colors(cmap=cmap)
        # Check if all cell types in the tree have colors
        if not set(self.G.nodes).issubset(set(self.colors.keys())):
            # Raise a warining and set colors
            missing_colors = set(self.G.nodes).difference(set(self.colors.keys()))
            print(
                "Warning: the following cell types in the tree don't have colors assigned: " + \
                str(missing_colors), ". Reassigning all colors."
                )
            self.set_colors()
        
        if keys is None:
            # Use expanded_keys if no keys are provided
            keys = self.get_expanded_keys()
        else:
            # Check if keys are in adata.obs
            if not set(keys).issubset(set(adata.obs.columns)):
                raise ValueError(
                    "The following keys are not in adata.obs: " + \
                    str(set(keys).difference(set(adata.obs.columns)))
                )
            # Check if keys contain cell types that are not in the tree
            all_cell_types = set(adata.obs[keys].values.flatten())
            if not set(all_cell_types).issubset(set(self.G.nodes).union({self.unlabelled})):
                raise ValueError(
                    "The following cell types in keys are not in the tree: " + \
                    str(set(adata.obs[keys].values.flatten()).difference(set(self.G.nodes)))
                )

        # Get corresponding color keys for each key
        color_keys = [key + '_colors' for key in keys]
       
        # For each annotation, go through the cell types alphabetically and assign color
        for key, color_key in zip(keys, color_keys):
            # If key is not categorical, convert it to categorical
            adata.obs[key] = pd.Categorical(adata.obs[key])
            # Get sorted cell types in the annotation, by reading categories
            sorted_cell_types = adata.obs[key].cat.categories.tolist()
            # Only consider cell types that are actually present in adata
            present_cell_types = adata.obs[key].unique().tolist() 
            sorted_cell_types = [ct for ct in sorted_cell_types if ct in present_cell_types]
            # Create a list of colors for the cell types in the annotation
            colors_list = [self.colors[ct] for ct in sorted_cell_types]
            # Add colors to adata.uns
            adata.uns[color_key] = colors_list

    def aggregate(self, adata, new_key, aggregate_func=None):
        """
        Aggregate different annotation sources to get the final cell type annotation.

        params:
            adata: AnnData object
            new_key: str
                Key in adata.obs to store the aggregated cell type annotation.
            aggregate_func: function
                Function to use for aggregating cell type annotations, if None, defaults
                to built-in majority voting. Wrappers for MajorityVote, Wawa and DawidSkene
                methods from Crowd-Kit can be selected by passing strings 'majority', 'wawa'
                or 'dawidskene' respectively. User defined functions can also be used, as long
                as the function takes two arguments: this CellTypeTree instance and a DataFrame
                with a column for each annotation source. The function should return a pandas
                series with indexes compatible with adata.obs_names and values corresponding to the
                aggregated cell type annotations.
        """
        # Set aggregate function
        if aggregate_func is None:
            def aggregate_func(self, df):
                """
                Default aggregate function, majority voting. Unlabelled cells are discarded
                """
                df = df.copy()
                # Replace unlabelled cells with NaN
                df.replace(self.unlabelled, np.nan, inplace=True)
                # Get the most common value in each row, ignoring NaN values
                modes = df.mode(axis=1, dropna=True)
                # Randomly select one non-na value from each row
                winners = modes.apply(
                    lambda x: x.dropna().sample(n=1, random_state=0).values[0] if not x.dropna().empty else self.unlabelled,
                    axis=1
                )
                # If there are no votes, set to unlabelled
                return winners

        elif isinstance(aggregate_func, str):
            # Clean string, lowercase, remove all non-alphabetic characters
            aggregate_func = re.sub(r'[^a-z]', '', aggregate_func.lower())
            if aggregate_func == 'majority': 
                from celltypetree.aggregation import majority
                aggregate_func = majority
            elif aggregate_func == 'wawa':
                from celltypetree.aggregation import wawa
                aggregate_func = wawa
            elif aggregate_func == 'dawidskene':
                from celltypetree.aggregation import dawidskene
                aggregate_func = dawidskene
        elif not callable(aggregate_func):    
            raise ValueError("aggregate_func must be a callable function or a string ('majority', 'wawa', 'dawidskene')")

        # organize columns by level
        cols_by_level = {}
        for level in range(1, self.max_depth + 1):
            cols_by_level[level] = [k + str(level) for k in self.mappings.keys()]

        # create columns for the new annotation
        # first winner is root by default
        adata.obs[new_key + str(0)] = self.root
        for i in range(1, self.max_depth + 1):
            adata.obs[new_key + str(i)] = self.unlabelled

        for i in range(1, self.max_depth + 1):
            # get columns of the next level and current winner
            df = adata.obs[cols_by_level[i]+[new_key + str(i-1)]].copy()
            # determine if cell types of current level are a children of the previous winner,
            # if not, set to unlabelled, to avoid interfering with the voting
            for col in cols_by_level[i]:
                df[col] = df.apply(
                    lambda x: x[col] if x[col] in self.get_children(x[new_key + str(i-1)]) else self.unlabelled,
                    axis=1
                )
            # drop the previous winner column (should already be in adata.obs)
            df.drop(new_key + str(i-1), axis=1, inplace=True)
            # exclude rows in which all values are unlabelled
            df = df[~(df == self.unlabelled).all(axis=1)]
            winners = aggregate_func(self, df)

            adata.obs.loc[winners.index, new_key + str(i)] = winners
            
            # Replace unlabelled with annotation from previous column
            adata.obs[new_key + str(i)] = np.where(
                adata.obs[new_key + str(i)] == self.unlabelled,
                adata.obs[new_key + str(i-1)],
                adata.obs[new_key + str(i)])
        
            # If a cell typs is assigned to the root node change it to unlabelled
            adata.obs[new_key + str(i)] = np.where(
                adata.obs[new_key + str(i)] == self.root,
                self.unlabelled,
                adata.obs[new_key + str(i)]
            )

        # Set colors for the new annotation
        self.set_adata_colors(adata, keys=[new_key + str(i) for i in range(self.max_depth + 1)])

    #def annotate_cells(
    #    self, 
    #    adata, 
    #    new_key, 
    #    markers, 
    #    func,
    #    *,
    #    new_root=None,
    #    verbose=True):
    #    """
    #    run a cell type annotation function on the tree

    #    params:
    #        adata: adata object
    #        markers of each cell type and returns the cell type annotation
    #        new_key: adata.obs keys in which to store the annotation
    #        markers: dictionary of markers for each cell type
    #        func: cell type annotation function that takes an AnnData object
    #        and a dictionary with markers for each cell type as input and returns
    #        the cell type annotation
    #        new_root: new node to use as root of the tree (if None, use self.root)
    #        verbose: whether to print information about the annotation
    #    """
    #    # get cell types from markers 
    #    cts = set(markers.keys())
    #    # check if all cell types in markers are in the tree
    #    if not cts.issubset(set(self.G.nodes).difference([self.root])):
    #        raise ValueError("The following cell types in markers are not in the tree: " + str(cts.difference(set(self.G.nodes))))
    #    # check if all cell types in the tree are in markers
    #    if not (set(self.G.nodes).difference([self.root]).issubset(cts)) and verbose:
    #        print("The following cell types in the tree are not in markers: " + str(set(self.G.nodes).difference(cts)))
    #    # create new columns for the annotation
    #    for i in range(1, self.max_depth):
    #        adata.obs[new_key+str(i)] = self.unlabelled

    #    # subset to markers in adata.var_names
    #    for ct in cts:
    #        markers[ct] = list(set(markers[ct]).intersection(set(adata.var_names)))
    #    # check if all cell types actually have markers after subsetting
    #    if not all([len(markers[ct]) > 0 for ct in cts]):
    #        raise ValueError("The following cell types have no markers: " + str([ct for ct in cts if len(markers[ct]) == 0]))
    #
    #    # get children of root
    #    if new_root is None:
    #        parent_ct = self.root
    #        startfrom = 1 # start annotation from level 1
    #    else:
    #        parent_ct = new_root
    #        startfrom = nx.shortest_path_length(self.G, parent_ct, self.root) + 1
    #        # expand new_root and fill previous columns with its parents
    #        previous = self.expand(new_root)
    #        for i in range(startfrom):
    #            adata.obs[new_key+str(i)] = previous[i]
    #        if verbose:
    #            print("starting from level " + str(startfrom))
    #        
    #    #TODO: get depth of new_root, fill previous columns and continue from there
    #        
    #    children = self.get_children(parent_ct)
    #    # subset markers
    #    markers_subset = {k: v for k, v in markers.items() if k in children}
    #    
    #    if verbose:
    #        print("Maximum depth: " + str(self.max_depth))
    #        print()
    #        print()
    #        print("Annotation of " + str(parent_ct) + ". Cell types: " + str(children))
    #        print("Cells :" + str(adata.obs.shape[0]))
    #    # run annotation function
    #    result = func(adata, markers_subset)
    #    # annotate adata.obs
    #    adata.obs[new_key+str(startfrom)] = result

    #    # continue by subsetting adata based on the annotation
    #    # and running the annotation function on the subset using
    #    # only the markers of the child cell types
    #    for i in range(startfrom+1, self.max_depth):
    #        if verbose:
    #            print()
    #            print()
    #            print("Annotation of level " + str(i))
    #        # get cell types in subset (exclude unlabelled)
    #        cts_subset = set(adata.obs[new_key+str(i-1)].unique()).difference([self.unlabelled])
    #        # for each cell type, subset adata
    #        for parent_ct in cts_subset:
    #            # get child cell types
    #            children = self.get_children(parent_ct)
    #            if not children:
    #                continue
    #            if verbose:
    #                print()
    #                print("Annotation of " + str(parent_ct) + ". Cell types: " + str(children))
    #                print("Cells :" + str(adata.obs[new_key+str(i-1)].value_counts()[parent_ct]))
    #            # subset markers
    #            markers_subset = {k: v for k, v in markers.items() if k in children}
    #            # if no cells
    #            if adata.obs[new_key+str(i-1)].value_counts()[parent_ct] == 0:
    #                continue
    #            # run annotation function on subset
    #            result = func(adata[adata.obs[new_key+str(i-1)] == parent_ct, :], markers_subset)
    #            # annotate adata.obs
    #            adata.obs.loc[adata.obs[new_key+str(i-1)] == parent_ct, new_key+str(i)] = result
    #    
    #    # replace unlabelled with annotation from previous column
    #    for i in range(startfrom+1, self.max_depth):
    #        adata.obs[new_key + str(i)] = np.where(
    #            adata.obs[new_key + str(i)] == self.unlabelled,
    #            adata.obs[new_key + str(i-1)],
    #            adata.obs[new_key + str(i)])

    #def annotate_genes(
    #    self, 
    #    adata, 
    #    new_key, 
    #    func,
    #    *,
    #    new_root=None,
    #    verbose=True):
    #    """
    #    run a gene annotation function on the tree

    #    params:
    #        adata: adata object
    #        new_key: adata.var keys in which to store the annotation
    #        func: gene annotation function that takes an AnnData object
    #        and returns the gene annotation
    #        new_root: new node to use as root of the tree (if None, use self.root)
    #        verbose: whether to print information about the annotation
    #    """
    #    # TODO: this first part is the same as the annotate_cells function, make it a separate function
    #    # get children of root
    #    if new_root is None:
    #        parent_ct = self.root
    #        startfrom = 1
    #    else:
    #        parent_ct = new_root
    #        # get distance of new_root from self.root
    #        startfrom = nx.shortest_path_length(self.G, parent_ct, self.root)
    #        # expand new_root and fill previous columns with its parents
    #        previous = self.expand(new_root)
    #        for i in range(startfrom):
    #            adata.var[new_key+str(i)] = previous[i]
    #        if verbose:
    #            print("starting from level " + str(startfrom))
    #        
    #    children = self.get_children(parent_ct)

    #    if verbose:
    #        print("Maximum depth: " + str(self.max_depth))
    #        print()
    #        print()
    #        print("Subsetting to " + str(parent_ct) + ". Cell types: " + str(children))
    #        print("Cells :" + str(adata.obs.shape[0]))
    #    # subset adata
    #    adata_subset = adata[adata.obs[new_key+str(startfrom-1)] == parent_ct, :]
    #    # run annotation function
    #    result = func(adata_subset)
    #    # annotate adata.var
    #    adata.var[new_key+str(startfrom)] = result

    #    # continue by subsetting adata based on the annotation
    #    # and running the annotation function on the subset using
    #    # only the markers of the child cell types
    #    for i in range(startfrom+1, self.max_depth):
    #        if verbose:
    #            print()
    #            print()
    #            print("Subsetting to level " + str(i))
    #        # get cell types in subset (exclude unlabelled)
    #        cts_subset = set(adata.var[new_key+str(i-1)].unique()).difference([self.unlabelled])
    #        # for each cell type, subset adata
    #        for parent_ct in cts_subset:
    #            # get child cell types
    #            children = self.get_children(parent_ct)
    #            if not children:
    #                continue
    #            if verbose:
    #                print()
    #                print("Subsetting to " + str(parent_ct) + ". Cell types: " + str(children))
    #                print("Cells :" + str(adata.var[new_key+str(i-1)].value_counts()[parent_ct]))
    #            # subset adata
    #            adata_subset = adata[adata.obs[new_key+str(i-1)] == parent_ct, :]
    #            # run annotation function on subset
    #            result = func(adata_subset)
    #            # annotate adata.var
    #            adata.var.loc[adata.obs[new_key+str(i-1)] == parent_ct, new_key+str(i)] = result
    #            
    #    # replace unlabelled with annotation from previous column
    #    # TODO: make this a function too!
    #    for i in range(startfrom+1, self.max_depth):
    #        adata.var[new_key + str(i)] = np.where(
    #            adata.var[new_key + str(i)] == self.unlabelled,
    #            adata.var[new_key + str(i-1)],
    #            adata.var[new_key + str(i)])

    def pick_celltypes(self,
        adata: AnnData,
        annotation_key: str,
        celltypes: list = None,
        new_key: str = None,
    ):
        """
        Select a subset of cell types from the tree, cells that don't match any of them are set to unlabelled.

        params:
            adata: AnnData object
            annotation_key: str 
                prefix of the annotation keys to use for selecting cell types, e.g. set to 'celltype'
                to use columns 'celltype1', 'celltype2', etc. in adata.obs.
            celltypes: list
                list of cell types to keep, defaults to maximum possible resolution (cell types without
                children in the tree).
            new_key: str
                adata.obs key in which to store the new annotation, defaults to the annotation_key
        """
        # If celltypes is not provided, find nodes that don't have children in the tree
        if celltypes is None:
            celltypes = [
                node for node in self.G.nodes if self.get_children(node) == []
            ]
            print(f'celltypes not provided, using maximum possible resolution')

        # If new_key is not provided, use annotation_key
        if new_key is None:
            print(f"new_key not provided, using {annotation_key} as new_key")
            new_key = annotation_key
        
        # Check if all cell types are in the tree
        if not set(celltypes).issubset(set(self.G.nodes)):
            raise ValueError("The following cell types in celltypes are not in the tree: " + str(set(celltypes).difference(set(self.G.nodes))))

        # Expand cell types to their full hierarchy
        expanded = {ct: self.expand(ct) for ct in celltypes}

        # get columns starting with annotation_keys and ending with numbers from 1 to max_depth
        cols = [f"{annotation_key}{i}" for i in range(1, self.max_depth + 1)]

        # Check if cols are actually in adata.obs
        if not set(cols).issubset(set(adata.obs.columns)):
            raise ValueError(
                "Couldn't find some of the following columns in adata.obs: " + \
                str(cols)
            )

        if new_key in adata.obs.columns:
            print(f"Warning: {new_key} already in adata.obs, overwriting")

        if self.unlabelled in celltypes:
            raise ValueError(f"{self.unlabelled} cannot be in celltypes")
       
        # create new column for the annotation
        adata.obs[new_key] = self.unlabelled
       
         # copy annotation columns
        df = adata.obs[cols].copy() 
        # substitute all values not in celltypes with unlabelled
        df = df.applymap(lambda x: x if x in celltypes else self.unlabelled)
        # remove rows in which all values are unlabelled
        df = df[~(df == self.unlabelled).all(axis=1)]
        # get max level containing a valid cell type for each cell
        max_level = df.apply(
            lambda x: max([
                self.get_annotation_level(x[col]) for col in cols \
                if x[col] != self.unlabelled
            ]),
            axis=1
        )
        # convert level to column name by prefixing the annotation_key
        df['max_level'] = max_level.apply(lambda x: f"{annotation_key}{x}")
        # get max level for each cell
        adata.obs.loc[df.index, new_key] = df.apply(lambda x: x[x["max_level"]], axis=1) 
        
        # Set colors for the new annotation
        self.set_adata_colors(adata, keys=[new_key])

def cellhint_tree(adata, annotation_keys, unlabelled='Unclassified'):
    """
    Creates a CellTypeTree object from an AnnData object containing
    multiple cell type annotations using CellHint.
    
    https://github.com/Teichlab/cellhint/

    Expects adata.X to contain raw counts. Will overwrite cell types in annotation_keys with
    harmonized cell type annotations, copy them if you want to avoid overwriting original annotations.
    
    params:
        adata: AnnData object 
        annotation_keys: list of str
            list of keys in adata.obs that contain cell type annotations
        unlabelled: str
            string to use for unlabelled cells, defaults to 'Unclassified'
    returns:
        CellTypeTree object
    """
    try:
        import cellhint
        import scanpy as sc
        import anndata
        import re
    except ImportError:
        raise ImportError(
            "Optional dependency 'cellhint' is required for this function."
            "Install it using: pip install celltypetree[cellhint]"
        )
    # 'NONE' and 'UNRESOLVED' are already used by CellHint
    if 'NONE' in annotation_keys or 'UNRESOLVED' in annotation_keys:
        raise ValueError("Annotation keys cannot contain strings 'NONE' and 'UNRESOLVED'")
    
    # Annotation keys can't contain nans, change them to unlabelled
    if any(pd.isna(adata.obs[annotation_keys]).any()):
        print(f"Warning: NaN values found in {annotation_keys}, replacing with '{unlabelled}'")
        adata.obs[annotation_keys] = adata.obs[annotation_keys].fillna(unlabelled)

    # Check if annotation_keys are in adata.obs
    if not set(annotation_keys).issubset(set(adata.obs.columns)):
        raise ValueError(
            "The following annotation keys are not columns of adata.obs: " + \
            str(set(annotation_keys).difference(set(adata.obs.columns)))
        )

    # Get CellHint alignment (self-match)
    alignment = cellhint.selfmatch(adata, annotation_keys)
    
    # Save the new alignment ordering as annotation_keys
    annotation_keys = list(alignment.aligned_datasets)

    group_annots = alignment.reannotation.groupby('group')['reannotation'].unique()
    
    # Create edgelist, each meta cell type annotation is connected to its group and each group to the root
    edgelist = []
    for group, annotations in group_annots.items():
        if len(annotations) == 1:
            # if there's only one annotation in the group, connect it directly to the root  
            edgelist.append((annotations[0], 'root'))
        else:
            for annot in annotations:
                # else connect each annotation to the group
                edgelist.append((annot, group)) 
                # then connect the group to the root
            edgelist.append((group, 'root'))

    # Convert edgelist to a DataFrame
    edgelist = pd.DataFrame(edgelist, columns=['source', 'target'])

    # Get the mapping between each cell type and its meta cell type
    mappings = alignment.reannotation[['dataset', 'cell_type', 'reannotation']].drop_duplicates()
    # Drop unlabelled cells from the reannotation dataset
    mappings = mappings[mappings['cell_type'] != unlabelled]
    mappings = (
        mappings
        .groupby('dataset')
        .apply(lambda x: dict(zip(x['cell_type'], x['reannotation'])))
        .to_dict()
    )

    # Cell types that contain other cell types must be mapped to the group instead of the meta cell type
    # Initialize empty sets of conflicting cell types for each annotation
    conflicts = {annot: set() for annot in annotation_keys}

    for i, annot in enumerate(annotation_keys[:-1]): 
        # Find ∈ (contained in)
        mask = alignment.relation.iloc[:, 2*i+1] == '∈'
        # Get the cell type (right of operator)
        annot_col = alignment.relation[mask].iloc[:, 2*i+2].name
        conflicts[annot_col].update(set(alignment.relation[mask].iloc[:, 2*i+2]))
        
        # Find ∋ (contains)
        mask = alignment.relation.iloc[:, 2*i+1] == '∋'
        # Get the cell type (left of operator)
        annot_col = alignment.relation[mask].iloc[:, 2*i].name
        conflicts[annot_col].update(set(alignment.relation[mask].iloc[:, 2*i]))
   
    # For each annotation, change conflicting cell types to the group that contains their key
    for annot, cells in conflicts.items():
        if cells == set():
            continue
        if annot not in mappings:
            continue
        for celltype in cells:
            if celltype == unlabelled:
                continue
            # Get corresponding meta cell type
            meta_celltype = mappings[annot].get(celltype, None)
            if meta_celltype is None:
                print(f"Warning: {celltype} not found in mappings for {annot}")
                continue
            # Get the group that contains the meta cell type
            group = edgelist[edgelist['source'] == meta_celltype]['target'].unique()
            if len(group) != 1:
                print(f"Warning: {meta_celltype} has multiple groups: {group}")
                continue
            group = group[0]
            # Change the mapping to the group
            mappings[annot][celltype] = group
    
    # Reorder mappings to follow the order of annotation_keys
    mappings = {annot: mappings.get(annot, {}) for annot in annotation_keys}

    # Create CellTypeTree from the edgelist
    tree = CellTypeTree(edgelist, mappings, root='root')
   
    # Rename each node of the tree to make it easier to read, instead of the full
    # meta cell type string, get the set of all cell types that map to it from the mappings
    # and join them like this B cell|B cells|B

    rename_dict = {}
    for node in tree.G.nodes:
        # Get all cell types that map to this node
        celltypes = set()
        for annot, mapping in mappings.items():
            for ct, meta_ct in mapping.items():
                if (meta_ct == node) & (ct != unlabelled):
                    celltypes.add(ct)
        # Join cell types with '|'
        if len(celltypes) > 0:
            new_name = '|'.join(sorted(celltypes))
        else:
            new_name = node
        rename_dict[node] = new_name
    
    # For each node get all the labels that map to it like in the CellTypeTree.plot method
    # If only unlabelled point to it remove the node
    reverse_mapping = {}
    for annot, mapping in mappings.items():
        for ct, meta_ct in mapping.items():
            if meta_ct not in reverse_mapping:
                reverse_mapping[meta_ct] = []
            reverse_mapping[meta_ct].append(ct)

    # If only unlabelled points to it, remove the node
    for node in list(rename_dict.keys()):
        if node in reverse_mapping and len(reverse_mapping[node]) == 1 and reverse_mapping[node][0] == unlabelled:
            print(f'Only {unlabelled} points to {node}, removing it from the tree')
            # preserve children
            tree.remove_nodes(node, preserve_children=True)

    # Rename all nodes
    tree.rename(rename_dict)

    return tree

