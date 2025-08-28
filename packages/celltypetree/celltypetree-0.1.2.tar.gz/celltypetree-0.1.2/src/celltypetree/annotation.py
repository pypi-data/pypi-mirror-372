import scanpy as sc
import numpy as np
import pandas as pd

def set_cluster_to_winner(adata, celltype_key, cluster_key='leiden', min_fraction=0.8):
    """
    set celltype in each cluster to the most frequent cell type
    if at least min_fraction of cells in a cluster have the same cell type
    
    params:
        adata: adata object
        cluster_key: adata.obs key with cluster annotations
        celltype_key: adata.obs key with cell type annotations
        min_fraction: minimum fraction of cells in a cluster that must have the same cell type
    """

    ad = adata.copy()

    # get all cluster names
    clusters = ad.obs[cluster_key].unique()
    # initialize results
    results = pd.Series(ad.obs[celltype_key].values, index=ad.obs_names, name='cluster_winner')

    # for each cluster
    for cluster in clusters:
        # get all cell types in the cluster
        cts = ad.obs.loc[ad.obs[cluster_key] == cluster, celltype_key]
        # get the most frequent cell type
        winner = cts.mode().values[0]
        # get fraction of cells with the most frequent cell type
        fraction = cts[cts == winner].shape[0] / cts.shape[0]
        # if fraction is at least min_fraction, assign the most frequent cell type
        if fraction >= min_fraction:
            results[ad.obs[cluster_key] == cluster] = winner
    
    return results

def decoupler(adata, cluster_key='leiden', markers=None):
    '''
    Wrapper for decoupler cell type annotation from marker genes:
    https://decoupler-py.readthedocs.io/en/latest/notebooks/cell_annotation.html
    
    Expects adata.X to contain raw counts.
    
    params:
        cluster_key: `adata.obs` key containing cell clusters. If missing, a new clustering will be generated 
        markers: decoupler formatted network of marker genes. If None, will use canonical markers from PanglaoDB.
    returns:
        predicted_celltypes: pd.Series of cell type predictions
    '''
    try:
        import decoupler as dc
    except ImportError:
        raise ImportError(
            "Optional dependency 'decoupler' is required for this function."
            "Install it using: pip install celltypetree[decoupler]"
        )

    ad = adata.copy()

    # Normalize the data
    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)
    ad.layers['log_norm'] = ad.X.copy()
    
    # Highly variable genes
    if not 'highly_variable' in ad.var.columns:
        sc.pp.highly_variable_genes(ad)

    # Regress and scale the data
    regress_cols = ['total_counts', 'pct_counts_mt']
    regress_cols = list(set(regress_cols).intersection(ad.obs.columns))
    sc.pp.regress_out(ad, regress_cols)
    sc.pp.scale(ad, max_value=10)

    if cluster_key not in ad.obs.columns:
        sc.tl.pca(ad)
        dc.swap_layer(ad, 'log_norm', X_layer_key=None, inplace=True)
        sc.pp.neighbors(ad)
        sc.tl.leiden(ad, key_added=cluster_key)
    else:
        dc.swap_layer(ad, 'log_norm', X_layer_key=None, inplace=True)

    if markers is None:
        markers = dc.get_resource(
            name='PanglaoDB',
            organism='human',
        )
        markers = markers[
            markers['human'].astype(bool) &
            markers['canonical_marker'].astype(bool) &
            (markers['human_sensitivity'].astype(float) > 0.5)
        ]
        markers = markers[~markers.duplicated(['cell_type', 'genesymbol'])]

    dc.run_ora(
        mat=ad,
        net=markers,
        source='cell_type',
        target='genesymbol',
        min_n=3,
        verbose=True,
        use_raw=False
    )
    
    acts = dc.get_acts(ad, obsm_key='ora_estimate')

    # Replace non-finite values
    acts_v = acts.X.ravel()
    max_e = np.nanmax(acts_v[np.isfinite(acts_v)])
    acts.X[~np.isfinite(acts.X)] = max_e

    df = dc.rank_sources_groups(acts, groupby=cluster_key, reference='rest', method='t-test_overestim_var')
    annotation_dict = df.groupby('group').head(1).set_index('group')['names'].to_dict()
    
    predicted_celltypes = [annotation_dict[clust] for clust in ad.obs[cluster_key]]
    predicted_celltypes = pd.Series(predicted_celltypes, index=ad.obs_names, name='celltype_decoupler')
    
    return predicted_celltypes

def celltypist(adata=None, model=None, majority_voting = True):
    """
    Wrapper for celltypist cell type annotation:
    https://celltypist.org/
    
    Expects adata.X to contain raw counts.

    params:
        model: celltypist model to use for annotation, leave None to download and list all models.
        majority_voting: If True, uses majority voting to refine cell type predictions.
    returns:
        predicted_celltypes: pd.Series of cell type predictions
    """
    try:
        import celltypist
    except ImportError:
        raise ImportError(
            "Optional dependency 'celltypist' is required for this function."
            "Install it using: pip install celltypetree[celltypist]"
        )
    # adata can only be None if model is None, otherwise it must be provided
    if adata is None and model is not None:
        raise ValueError("adata must be provided if model is specified.")

    # if model is None, download and list all models
    if model is None:
        print('model argument is None, will try to download and list all available models.')
        print('Downloading models')
        models_path = celltypist.models.models_path
        celltypist.models.download_models(force_update=True)
        print('Models downloaded to:', models_path)
        print('Models descriptions are available at https://celltypist.org/models')
        return

    ad = adata.copy()
    
    # Normalize and log1p the data
    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)

    predictions = celltypist.annotate(ad, model=model, majority_voting=majority_voting)
    predicted_celltypes = predictions.predicted_labels['predicted_labels']
    predicted_celltypes = pd.Series(predicted_celltypes, index=ad.obs_names, name='celltype_celltypist')

    return predicted_celltypes


