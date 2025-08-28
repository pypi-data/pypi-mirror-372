import numpy as np
import pandas as pd
import networkx as nx
from anndata import AnnData

class CellTypeTree:
    """
    harmonizes different cell type annotations in a hierarchical way
    based on a tree of cell types.

    params:
        tree: directed networkx tree of cell types, edges must go from
              specific to general (CD4Tcell -> Tcell)
        root: label of the root of the tree
        unlabelled: how to mark unlabelled cells
    """

    def __init__(self, tree, root, unlabelled="Unclassified"):
        # check if tree is a directed acyclic graph
        if not nx.is_directed_acyclic_graph(tree):
            raise ValueError("tree must be a directed acyclic graph")
        self.G = tree
        self.root = root
        self.unlabelled = unlabelled
        self.max_depth = nx.dag_longest_path_length(self.G)

    def subset_tree(self, newtree, newroot=None):
        """subset tree to a new tree that is a subgraph of the original tree"""
        if not nx.is_directed_acyclic_graph(self.G.subgraph(newtree.nodes)):
            raise ValueError("newtree must be a subgraph of the original tree")
        self.G = newtree
        self.max_depth = nx.dag_longest_path_length(self.G)
        if newroot is not None:
            self.root = newroot

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

    def harmonize(self, adata, orig_key, new_key, ct_dict, ignore = [], inplace=False):
        """
        add harmonized cell types to adata.obs

        params:
            adata: adata object
            original_key: adata.obs kye with annotation to harmonize
            new_key: adata.obs key in which to store harmonized annotation
            ct_dict: dictionary of corresponding cell types
                     keys are sources and vals are targets
            ignore:  list of cell types from original_key that should not
                     be labelled
            inplace: if True, modify adata.obs in place, otherwise return a copy
        returns:
            adata.obs with new_key added, only if inplace=False
        """
        ad = adata if inplace else adata.copy()

        # Add self.unlabelled to ignore
        if not self.unlabelled in ignore:
            ignore.append(self.unlabelled)

        # Add all keys of ct_dict that have self.unlabelled as value to ignore and remove them from ct_dict
        ignore += [k for k, v in ct_dict.items() if v == self.unlabelled]
        ct_dict = {k: v for k, v in ct_dict.items() if v != self.unlabelled}
    
        cts_orig = set(ct_dict.keys())
        cts_new = set(ct_dict.values())

        # check correspondence between cell types in tree and in ct_dict (exclude those in ignore)
        if not cts_new.difference(ignore).issubset(set(self.G.nodes)):
            raise ValueError("The following cell types in ct_dict are not in the tree: " + str(cts_new.difference(set(self.G.nodes))))
        # check if all (not in ignore) cell types in original_key are in ct_dict
        if not set(ad.obs[orig_key]).difference(ignore).issubset(cts_orig):
            raise ValueError("The following cell types in original_key are not in ct_dict: " + \
                             str(set(ad.obs[orig_key]).difference(ignore).difference(cts_orig)) + \
                             " try adding them to ignore")

        # create dict of expanded cell types
        ct_dict_exp = {}
        for k, v in ct_dict.items():
            if v not in ignore:
                ct_dict_exp[k] = self.expand(v)

        # remove root
        #for k, v in ct_dict_exp.items():
        #    ct_dict_exp[k] = v[1:]

        # find max length of expanded cell types
        depth = max([len(v) for v in ct_dict_exp.values()])
        # extend all to max length by repeating last element
        for k, v in ct_dict_exp.items():
            ct_dict_exp[k] = v + [v[-1]] * (depth - len(v))

        # cell types in ignore are expanded to unlabelled
        for k in ignore:
            ct_dict_exp[k] = [self.unlabelled] * depth

        # add new_keys to ad.obs
        new_keys = [new_key + str(i) for i in range(depth)]
        for k in new_keys:
            ad.obs[k] = self.unlabelled

        # populate new_keys with expanded cell types
        ad.obs[new_keys] = ad.obs.apply(
            lambda x: ct_dict_exp[x[orig_key]], axis=1, result_type="expand"
        )

        if not inplace:
            return ad.obs

    def set_cluster_to_winner(self, adata, cluster_key, ct_key, min_fraction=0.8, new_key=None, inplace=False):
        """
        set celltype in each cluster to the most frequent cell type
        if at least min_fraction of cells in a cluster have the same cell type
        
        params:
            adata: adata object
            cluster_key: adata.obs key with cluster annotations
            ct_key: adata.obs key with cell type annotations
            min_fraction: minimum fraction of cells in a cluster that must have the same cell type
            new_key: adata.obs key in which to store the new annotation
            inplace: if True, modify adata.obs in place, otherwise return a copy
        returns:
            adata.obs with new_key added, only if inplace=False
        """
    
        ad = adata if inplace else adata.copy()

        if new_key is None:
            new_key = cluster_key + "_celltype"

        # get all cluster names
        clusters = ad.obs[cluster_key].unique()
        # create new column for the annotation
        ad.obs[new_key] = self.unlabelled
        # for each cluster
        for cluster in clusters:
            # get all cell types in the cluster
            cts = ad.obs[ct_key][ad.obs[cluster_key] == cluster]
            # get the most frequent cell type
            winner = cts.mode().values[0]
            # get fraction of cells with the most frequent cell type
            fraction = cts[cts == winner].shape[0] / cts.shape[0]
            # if fraction is at least min_fraction, assign the most frequent cell type
            if fraction >= min_fraction:
                ad.obs.loc[ad.obs[cluster_key] == cluster, new_key] = winner

        if not inplace:
            return ad.obs[new_key]
        
    def get_winner(self, x):
        """get winner for majority vote"""
        counts = x.value_counts()
        results = (counts / self.weights).sort_values(ascending=False).dropna()
        tie = False
        if results.shape[0] > 0:
        # Check if there are any votes
            if results.shape[0] > 1:
                tie = results.iloc[0] == results.iloc[1]
            winner = results.index[0] 
            if counts[winner] >= self.n_votes:
            # Check if winner has at least n_votes votes
                return pd.Series([winner, counts[winner], tie], index=['winner', 'votes', 'tie'])
        return pd.Series([self.unlabelled, 0, False], index=['winner', 'votes', 'tie'])

    def majority(self, adata, keys, new_key, min_votes=1, weights=None, inplace=False):
        """
        assign cell types based on majority vote of multiple annotations.
        Annotations must end with numbers.
        e.g. "cell_type" means that "cell_type1", "cell_type2", etc. are used.

        params:
            adata: adata object
            keys: adata.obs keys with cell type annotations (no final number)
            new_key: adata.obs key in which to store the majority-vote annotation
            weights: dictionary of weights multiplying the votes for each cell type
            min_votes: minimum number of votes for a cell type to be considered
            weights: dictionary of weights for each cell type, if None, all cell types are weighted equally
            inplace: if True, modify adata.obs in place, otherwise return a copy

        returns:
            adata.obs with new_key added, only if inplace=False
        """
        ad = adata if inplace else adata.copy()

        #get all cols starting with keys and ending with numbers
        all_cols = [col for col in ad.obs.columns if col.startswith(tuple(keys)) and col[-1].isdigit()]

        # get annotation columns
        cols_by_annot = {}

        for k in keys:
            cols_by_annot[k] = [col for col in all_cols if col.startswith(k)]
        depth = max([len(v) for v in cols_by_annot.values()]) # max depth

        # organize columns by ending number
        cols_by_num = {}

        for num in range(1, depth):
            cols_by_num[num] = [col for col in all_cols if col.endswith(str(num))]

        # TODO: check that cols end with consecutive numbers
        # TODO: check that max(last number of keys) == depth

        self.n_votes = min_votes

        # create columns for the new annotation
        # first winner is root by default
        ad.obs[new_key + str(0)] = self.root
        for i in range(1, depth):
            ad.obs[new_key + str(i)] = self.unlabelled

        if weights is None:
            self.weights = pd.Series({ct: 1 for ct in self.G.nodes})
        else:
            self.weights = pd.Series(weights)
            # if some cell types are not in weights, print warning
            if not set(self.G.nodes).issubset(set(weights.keys())): 
                print("Warning: not all cell types have weights")

        for i in range(1, depth):
            # get columns for current depth
            df = ad.obs[cols_by_num[i]+[new_key + str(i-1)]].copy()
            # determine if the i-th cell type is a child of the previous winner, if not, set to unlabelled
            for col in cols_by_num[i]:
                df[col] = df.apply(
                    lambda x: x[col] if x[col] in self.get_children(x[new_key + str(i-1)]) else self.unlabelled,
                    axis=1
                )
            # drop new column
            df.drop(new_key + str(i-1), axis=1, inplace=True)
            # exclude rows in which all values are unlabelled
            df = df[~(df == self.unlabelled).all(axis=1)]
            # create dataframe with all cells of ad set to unlabelled, columns are winner, votes and tie
            winners = df.apply(self.get_winner, axis=1)
            #winners = pd.DataFrame(index=ad.obs.index, columns=['winner', 'votes', 'tie'])
            #winners['winner'], winners['votes'], winners['tie'] = df.apply(self.get_winner, axis=1)

            # assign winners to new_key
            #ad.obs[new_key + str(i)] = np.where(ad.obs.index.isin(df.index), winners, self.unlabelled)
            ad.obs.loc[df.index, new_key + str(i)] = winners.loc[df.index, 'winner'].astype(str)
            ad.obs[new_key + str(i) + '_votes'] = winners.loc[df.index, 'votes'].astype(int)
            ad.obs[new_key + str(i) + '_tie'] = winners.loc[df.index, 'tie'].astype(str)

        for i in range(1, depth):
        # replace unlabelled with annotation from previous column
            ad.obs[new_key + str(i)] = np.where(
                ad.obs[new_key + str(i)] == self.unlabelled,
                ad.obs[new_key + str(i-1)],
                ad.obs[new_key + str(i)])

        # replace root with unlabelled
            ad.obs[new_key + str(i)] = np.where(
                ad.obs[new_key + str(i)] == self.root,
                self.unlabelled,
                ad.obs[new_key + str(i)])
        
        if not inplace:
            return ad.obs

    def annotate_cells(
        self, 
        adata, 
        new_key, 
        markers, 
        func,
        *,
        new_root=None,
        verbose=True):
        """
        run a cell type annotation function on the tree

        params:
            adata: adata object
            markers of each cell type and returns the cell type annotation
            new_key: adata.obs keys in which to store the annotation
            markers: dictionary of markers for each cell type
            func: cell type annotation function that takes an AnnData object
            and a dictionary with markers for each cell type as input and returns
            the cell type annotation
            new_root: new node to use as root of the tree (if None, use self.root)
            verbose: whether to print information about the annotation
        """
        # get cell types from markers 
        cts = set(markers.keys())
        # check if all cell types in markers are in the tree
        if not cts.issubset(set(self.G.nodes).difference([self.root])):
            raise ValueError("The following cell types in markers are not in the tree: " + str(cts.difference(set(self.G.nodes))))
        # check if all cell types in the tree are in markers
        if not (set(self.G.nodes).difference([self.root]).issubset(cts)) and verbose:
            print("The following cell types in the tree are not in markers: " + str(set(self.G.nodes).difference(cts)))
        # create new columns for the annotation
        for i in range(1, self.max_depth):
            adata.obs[new_key+str(i)] = self.unlabelled

        # subset to markers in adata.var_names
        for ct in cts:
            markers[ct] = list(set(markers[ct]).intersection(set(adata.var_names)))
        # check if all cell types actually have markers after subsetting
        if not all([len(markers[ct]) > 0 for ct in cts]):
            raise ValueError("The following cell types have no markers: " + str([ct for ct in cts if len(markers[ct]) == 0]))
    
        # get children of root
        if new_root is None:
            parent_ct = self.root
            startfrom = 1 # start annotation from level 1
        else:
            parent_ct = new_root
            startfrom = nx.shortest_path_length(self.G, parent_ct, self.root) + 1
            # expand new_root and fill previous columns with its parents
            previous = self.expand(new_root)
            for i in range(startfrom):
                adata.obs[new_key+str(i)] = previous[i]
            if verbose:
                print("starting from level " + str(startfrom))
            
        #TODO: get depth of new_root, fill previous columns and continue from there
            
        children = self.get_children(parent_ct)
        # subset markers
        markers_subset = {k: v for k, v in markers.items() if k in children}
        
        if verbose:
            print("Maximum depth: " + str(self.max_depth))
            print()
            print()
            print("Annotation of " + str(parent_ct) + ". Cell types: " + str(children))
            print("Cells :" + str(adata.obs.shape[0]))
        # run annotation function
        result = func(adata, markers_subset)
        # annotate adata.obs
        adata.obs[new_key+str(startfrom)] = result

        # continue by subsetting adata based on the annotation
        # and running the annotation function on the subset using
        # only the markers of the child cell types
        for i in range(startfrom+1, self.max_depth):
            if verbose:
                print()
                print()
                print("Annotation of level " + str(i))
            # get cell types in subset (exclude unlabelled)
            cts_subset = set(adata.obs[new_key+str(i-1)].unique()).difference([self.unlabelled])
            # for each cell type, subset adata
            for parent_ct in cts_subset:
                # get child cell types
                children = self.get_children(parent_ct)
                if not children:
                    continue
                if verbose:
                    print()
                    print("Annotation of " + str(parent_ct) + ". Cell types: " + str(children))
                    print("Cells :" + str(adata.obs[new_key+str(i-1)].value_counts()[parent_ct]))
                # subset markers
                markers_subset = {k: v for k, v in markers.items() if k in children}
                # if no cells
                if adata.obs[new_key+str(i-1)].value_counts()[parent_ct] == 0:
                    continue
                # run annotation function on subset
                result = func(adata[adata.obs[new_key+str(i-1)] == parent_ct, :], markers_subset)
                # annotate adata.obs
                adata.obs.loc[adata.obs[new_key+str(i-1)] == parent_ct, new_key+str(i)] = result
        
        # replace unlabelled with annotation from previous column
        for i in range(startfrom+1, self.max_depth):
            adata.obs[new_key + str(i)] = np.where(
                adata.obs[new_key + str(i)] == self.unlabelled,
                adata.obs[new_key + str(i-1)],
                adata.obs[new_key + str(i)])

    def annotate_genes(
        self, 
        adata, 
        new_key, 
        func,
        *,
        new_root=None,
        verbose=True):
        """
        run a gene annotation function on the tree

        params:
            adata: adata object
            new_key: adata.var keys in which to store the annotation
            func: gene annotation function that takes an AnnData object
            and returns the gene annotation
            new_root: new node to use as root of the tree (if None, use self.root)
            verbose: whether to print information about the annotation
        """
        # TODO: this first part is the same as the annotate_cells function, make it a separate function
        # get children of root
        if new_root is None:
            parent_ct = self.root
            startfrom = 1
        else:
            parent_ct = new_root
            # get distance of new_root from self.root
            startfrom = nx.shortest_path_length(self.G, parent_ct, self.root)
            # expand new_root and fill previous columns with its parents
            previous = self.expand(new_root)
            for i in range(startfrom):
                adata.var[new_key+str(i)] = previous[i]
            if verbose:
                print("starting from level " + str(startfrom))
            
        children = self.get_children(parent_ct)

        if verbose:
            print("Maximum depth: " + str(self.max_depth))
            print()
            print()
            print("Subsetting to " + str(parent_ct) + ". Cell types: " + str(children))
            print("Cells :" + str(adata.obs.shape[0]))
        # subset adata
        adata_subset = adata[adata.obs[new_key+str(startfrom-1)] == parent_ct, :]
        # run annotation function
        result = func(adata_subset)
        # annotate adata.var
        adata.var[new_key+str(startfrom)] = result

        # continue by subsetting adata based on the annotation
        # and running the annotation function on the subset using
        # only the markers of the child cell types
        for i in range(startfrom+1, self.max_depth):
            if verbose:
                print()
                print()
                print("Subsetting to level " + str(i))
            # get cell types in subset (exclude unlabelled)
            cts_subset = set(adata.var[new_key+str(i-1)].unique()).difference([self.unlabelled])
            # for each cell type, subset adata
            for parent_ct in cts_subset:
                # get child cell types
                children = self.get_children(parent_ct)
                if not children:
                    continue
                if verbose:
                    print()
                    print("Subsetting to " + str(parent_ct) + ". Cell types: " + str(children))
                    print("Cells :" + str(adata.var[new_key+str(i-1)].value_counts()[parent_ct]))
                # subset adata
                adata_subset = adata[adata.obs[new_key+str(i-1)] == parent_ct, :]
                # run annotation function on subset
                result = func(adata_subset)
                # annotate adata.var
                adata.var.loc[adata.obs[new_key+str(i-1)] == parent_ct, new_key+str(i)] = result
                
        # replace unlabelled with annotation from previous column
        # TODO: make this a function too!
        for i in range(startfrom+1, self.max_depth):
            adata.var[new_key + str(i)] = np.where(
                adata.var[new_key + str(i)] == self.unlabelled,
                adata.var[new_key + str(i-1)],
                adata.var[new_key + str(i)])

    def pick_celltypes(
        self,
        adata: AnnData,
        celltypes: list,
        annotation_keys: str,
        new_key: str,
        inplace: bool = True):
        """
        pick cell types from a cell type annotation column, other cell types are set to unlabelled

        params:
            adata: adata object
            celltypes: list of cell types to keep
            annotation_key: adata.obs key that identifies comuns with cell type annotations
            new_key: adata.obs key in which to store the new annotation
            inplace: if True, modify adata.obs in place, otherwise return a copy
        returns:
            adata.obs with new_key added, only if inplace=False
        """
        ad = adata if inplace else adata.copy()

        # check if all cell types are in the tree
        if not set(celltypes).issubset(set(self.G.nodes)):
            raise ValueError("The following cell types in celltypes are not in the tree: " + str(set(celltypes).difference(set(self.G.nodes))))

        expanded = {ct: self.expand(ct) for ct in celltypes}

        # get columns starting with annotation_keys and ending with numbers from 1 to max_depth
        cols = [col for col in ad.obs.columns if col.startswith(annotation_keys) and col[-1].isdigit()]
        cols = [col for col in cols if int(col[-1]) <= self.max_depth and int(col[-1]) > 0]
        
        # cols by level
        cols_by_level = {}
        for i in range(1, self.max_depth + 1):
            # TODO: This only works if you have 1 digit in the col name
            cols_by_level[i] = [col for col in cols if int(col[-1]) == i][0]

        if new_key in ad.obs.columns:
            print(f"Warning: {new_key} already in ad.obs, overwriting")

        if cols == []:
            raise ValueError("No columns matching annotation_keys found")
        
        if self.unlabelled in celltypes:
            raise ValueError(f"{self.unlabelled} cannot be in celltypes")
        
        # create new column for the annotation
        ad.obs[new_key] = self.unlabelled
       
         # copy annotation columns
        df = ad.obs[cols].copy() 
        # substitute all values not in celltypes with unlabelled
        df = df.applymap(lambda x: x if x in celltypes else self.unlabelled)
        # remove rows in which all values are unlabelled
        df = df[~(df == self.unlabelled).all(axis=1)]
        # get level for each cell type
        #df["max_level"] = [self.get_annotation_level(ct) for ct in df[cols].values if ct != self.unlabelled].max()
        #df["max_level"] = df.apply(lambda x: \
        #                           max([(self.get_annotation_level(x[col]) for col in cols \
        #                           if x[col] != self.unlabelled)])
        #                          )
        df["max_level"] = df.apply(lambda x: \
            cols_by_level[max([self.get_annotation_level(x[col]) for col in cols \
                               if x[col] != self.unlabelled])], axis=1)
        # get max level for each cell
        ad.obs.loc[df.index, new_key] = df.apply(lambda x: x[x["max_level"]], axis=1) 

        if not inplace:
            return ad.obs[new_key]

