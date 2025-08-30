"""
Hierarchical clustering. In the future will include more algorithms
"""
import pandas as pd
import numpy as np
from .stats import corr
try:
    from scipy.cluster import hierarchy
    import matplotlib.pyplot as plt
except:
    pass
try:
    import plotly.express as px
    from .plots.plotly_utils import get_figure, set_multicategory_from_df
except:
    pass
try:
    import networkx as nx
except:
    pass

def graph_cluster(X, threshold, exclude_singleton=True, labels=None):
    """
    Creates a graph from a 2D data matrix and returns the clusters. Nodes u, v are connected if X[u, v] > threshold.

    Parameters:
    X (numpy.ndarray or pandas.DataFrame): 2D data
    threshold (float): The threshold for the edge weights. Edges with weights greater than this value are included in the graph.
    exclude_singleton (bool, optional): If True, singleton clusters (clusters with only one node) are excluded. Defaults to True.
    labels (list, optional): A list of labels for the nodes. If None, the nodes are labeled with their indices. Defaults to None.

    Returns:
    dict: A dictionary where the keys are cluster indices and the values are lists of nodes in the cluster.
    """
    is_df = isinstance(X, pd.core.frame.DataFrame)
    if labels is not None:
        idx_to_label = {i: l for i, l in enumerate(labels)}
    elif is_df: # extract from index
        idx_to_label = {i: l for i, l in enumerate(X.index)}
    else:
        idx_to_label = None

    i, j = np.where(X > threshold)
    G = nx.Graph()
    G.add_edges_from(zip(i, j))
    clusters = list(nx.connected_components(G))

    if idx_to_label is None:
        if exclude_singleton:
            clusters = [cluster for cluster in clusters if len(cluster) > 1]
        clusters = {k: cluster for k, cluster in enumerate(clusters)}
        return clusters
    else:
        clusters_dict = {}
        k = 0
        for cluster in clusters:
            if len(cluster) > 1 or not exclude_singleton:
                clusters_dict[k] = [idx_to_label[i] for i in cluster]
                k += 1
        return clusters_dict

def hierarchy_dendrogram(X, fontsize=30, out='data', method='average'):
    """
    Notes on the linkage matrix:
    This matrix represents a dendrogram, where elements
        1, 2: two clusters merged at each step,
        3: distance between these clusters,
        4: size of the new cluster - the number of original data points included.
    """
    if method not in ['ward', 'single', 'complete', 'average', 'weighted', 'centroid', 'median']:
        raise ValueError(f"method '{method}' not valid. Available: 'ward', 'single', 'complete', 'average', 'weighted', 'centroid', 'median'.")
    is_df = isinstance(X, pd.core.frame.DataFrame)
    if is_df:
        labels = X.columns.to_list()
    else:
        labels = [*range(X.shape[1])] if len(X.shape) > 1 else None #int(-1 + np.sqrt(1 + 8*X.size)/2))]

    fig = plt.figure(figsize=(8, 12))
    ax = plt.subplot(111)


    corr_linkage = hierarchy.linkage(X.values if is_df else X, method=method)
    dendro = hierarchy.dendrogram(
        corr_linkage, labels=labels, ax=ax, leaf_rotation=90 #orientation="left"
    )
    if out == 'data':
        plt.close()
        return corr_linkage, dendro
    elif out == 'fig':
        if not is_df:
            plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        else:
            plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        return fig
    else:
        raise ValueError(f"out '{out}' not valid. Available: 'data', 'fig'.")

def dendrogram_sort(df, to_distance = lambda x: 1 - x, **kwargs):
    """
    Attempts to sort the rows and columns of a matrix according to the dendrogram.

    Attributes:
        df: pandas DataFrame or numpy array
        to_distance: function to convert the input df to a distance matrix

        lambda x: 1 - x is useful when dealing with probabilities in a confusion matrix.

    Returns a pandas DataFrame or numpy array with the rows and columns ordered according to the dendrogram
    """
    _, dendro = hierarchy_dendrogram(to_distance(df), **kwargs)
    order = dendro["leaves"]
    if isinstance(df, pd.core.frame.DataFrame):
        df = df.iloc[order,:].iloc[:, order]
    elif isinstance(df, np.ndarray):
        df = df[order,:][:, order]
    else:
        raise ValueError("df must be a pandas DataFrame or a numpy array")
    return df


def hierarchical_cluster_matrix(df, title, colorbar_x=0.9, ticksize=16, cmin=-1, cmax=1, cmap='inferno', **kwargs):
    _, dendro = hierarchy_dendrogram(df, **kwargs)
    order = dendro["leaves"]
    #corr = X.corr() if isinstance(X, pd.core.frame.DataFrame) else np.corrcoef(X)
    df_ordered = df.iloc[order,:].iloc[:, order]
    fig = px.imshow(df_ordered, color_continuous_scale=cmap)
    fig.update_layout(margin=dict(l=0, b=30, r=60, t=10, pad=1), xaxis_tickfont_size=ticksize, yaxis_tickfont_size=ticksize,
                      coloraxis=dict(cmin=cmin, cmax=cmax, colorbar=dict(title_text=title, tickfont_size=16, title_font_size=20, x=colorbar_x)),
                      height=800, width=1000, font_size=20, hovermode=False)
    if isinstance(df.index, pd.core.indexes.multi.MultiIndex):
        set_multicategory_from_df(fig, df_ordered)
    return fig

def corr_cluster_matrix(df, method='spearman', alpha=0.05, absolute_value=False, correct_by_multiple_comp='by', linkage='average', **kwargs):
    """"
    corr:  spearman, pearson.
    """
    df_corr = corr.corr_pruned(df, method=method, alpha=alpha, correct_by_multiple_comp=correct_by_multiple_comp, ns_to_nan=True)[0]
    df_corr = df_corr.fillna(0)
    title = method.capitalize()
    if absolute_value:
        df_corr = df_corr.abs()
        title = f"|{title}|"
    return hierarchical_cluster_matrix(df_corr, title, method=linkage, **kwargs)
