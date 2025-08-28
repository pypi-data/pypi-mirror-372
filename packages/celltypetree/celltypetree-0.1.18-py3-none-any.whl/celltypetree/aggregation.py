import numpy as np
import pandas as pd

def majority(tree, df):
    '''
    Wrapper for Crowd-Kit MajorityVote aggregation method. 
    https://github.com/Toloka/crowd-kit/tree/main
    
    Crowd-Kit is licensed under the Apache License 2.0.
    http://www.apache.org/licenses/LICENSE-2.0
    
    params:
        tree: CellTypeTree object
        df: dataframe with each column representing a source of annotation and each index representing a cell.
    returns:
        pd.Series with labels.
    '''
    try:
        from crowdkit.aggregation import MajorityVote
    except ImportError:
        raise ImportError(
            "Optional dependency 'crowdkit' is required for this function."
            "Install it using: pip install celltypetree[crowdkit]"
        )
    df = df.copy()

    # Format the DataFrame to Crowd-Kit format
    df, label_mapping = _crowdkit_format_df(tree, df)

    # Apply DawidSkene
    aggregated_labels = MajorityVote().fit_predict(df)

    # Reverse map integer labels back to original categories
    aggregated_labels = aggregated_labels.map(label_mapping)
    
    return aggregated_labels

def wawa(tree, df):
    '''
    Wrapper for Crowd-Kit Wawa aggregation method.
    https://github.com/Toloka/crowd-kit/tree/main
    
    Crowd-Kit is licensed under the Apache License 2.0.
    http://www.apache.org/licenses/LICENSE-2.0
    
    params:
        tree: CellTypeTree object
        df: dataframe with each column representing a source of annotation and each index representing a cell.
    returns:
        pd.Series with labels.
    '''
    try:
        from crowdkit.aggregation import Wawa
    except ImportError:
        raise ImportError(
            "Optional dependency 'crowdkit' is required for this function."
            "Install it using: pip install celltypetree[crowdkit]"
        )
    df = df.copy()

    # Format the DataFrame to Crowd-Kit format
    df, label_mapping = _crowdkit_format_df(tree, df)

    # Apply DawidSkene
    aggregated_labels = Wawa().fit_predict(df)

    # Reverse map integer labels back to original categories
    aggregated_labels = aggregated_labels.map(label_mapping)
    
    return aggregated_labels


def dawidskene(tree, df):
    '''
    Wrapper for Crowd-Kit Dawid-Skene aggregation method.
    https://github.com/Toloka/crowd-kit/tree/main
    
    Crowd-Kit is licensed under the Apache License 2.0.
    http://www.apache.org/licenses/LICENSE-2.0
    
    params:
        tree: CellTypeTree object
        df: dataframe with each column representing a source of annotation and each index representing a cell.
    returns:
        pd.Series with labels.
    '''
    try:
        from crowdkit.aggregation import DawidSkene
    except ImportError:
        raise ImportError(
            "Optional dependency 'crowdkit' is required for this function."
            "Install it using: pip install celltypetree[crowdkit]"
        )
    df = df.copy()

    # Format the DataFrame to Crowd-Kit format
    df, label_mapping = _crowdkit_format_df(tree, df)

    # Apply DawidSkene
    aggregated_labels = DawidSkene().fit_predict(df)

    # Reverse map integer labels back to original categories
    aggregated_labels = aggregated_labels.map(label_mapping)
    
    return aggregated_labels

def _crowdkit_format_df(tree, df):
    '''
    Format the dataframe to be compatible with Crowd-Kit aggregation methods.
    https://github.com/Toloka/crowd-kit/tree/main
    
    Crowd-Kit is licensed under the Apache License 2.0.
    http://www.apache.org/licenses/LICENSE-2.0
    
    params:
        tree: CellTypeTree object
        df: dataframe with each column representing a source of annotation and each index representing a cell.
    returns:
        df: formatted dataframe compatible with Crowd-Kit
        label_mapping: dictionary mapping integer codes to original labels.
    '''
    # Ensure the input DataFrame is a copy to avoid modifying the original
    df = df.copy()
    
    # Reset index to have a column for the cell index
    df['task'] = df.index

    # Convert to long format
    df = pd.melt(df, id_vars='task', var_name='worker', value_name='label')

    # Set unlabelled cells to NaN and remove all rows with missing values
    df.loc[df['label'] == tree.unlabelled, 'label'] = np.nan
    df = df.dropna()
    
    # Convert labels to integer ids and store the mapping
    df['label'] = df['label'].astype('category')
    label_categories = df['label'].cat.categories
    df['label'] = df['label'].cat.codes
    
    # Store the mapping as a dictionary
    label_mapping = dict(enumerate(label_categories))

    return df, label_mapping

