"""
Explore PCA results. In the future will contain more algorithms.
Includes:
    - Variance visualization
    - Importance of each feature (how much each feature contributes to the PCA variance explained)
    - PCA components visualization in 2D.
"""
import numpy as np
try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
except:
    pass
try:
    import plotly.graph_objects as go
    from .plots.plotly_utils import get_figure
except:
    pass
    
def pca_fit(X):
    x = StandardScaler().fit_transform(X)    
    pca = PCA()
    pca.fit(x)
    return pca

def pca_variance(X, cummulative=True):
    """Variance explained by each PCA component."""
    pca = pca_fit(X)
    y = pca.explained_variance_ratio_.cumsum() if cummulative else pca.explained_variance_ratio_
    fig = get_figure(yaxis_title_text="Variance explained", yaxis_range=[0,1], xaxis_title_text="PCA component")
    fig.add_trace(go.Bar(x=np.arange(len(pca.components_))+1, y=y, showlegend=False))
    if cummulative:
        fig.add_hline(y=0.9, line=dict(color='orange', width=5, dash='dot'))
        fig.add_hline(y=0.95, line=dict(color='red', width=5, dash='dot'))
    return fig

def pca_feature_importance(df, xaxis_tickfont_size=20, yaxis_range=None):
    """PCA importance of feature Z_i = sum(|PCA projections of Z_i| * explained_variance of each projection)."""
    pca = pca_fit(df.values)
    col_importance = []
    for pca_comp in pca.components_.T:
        col_importance.append(np.sum(np.abs(pca_comp) * pca.explained_variance_ratio_))
    col_importance = np.array(col_importance)
    # Alternatively: col_importance = (np.abs(pca.components_) * pca.explained_variance_ratio_[:, None]).sum(axis=0)
    col_importance /= col_importance.sum()
    fig = get_figure(yaxis_title_text="PCA importance", yaxis_range=yaxis_range, xaxis_title_text="Feature", xaxis_tickfont_size=xaxis_tickfont_size)
    fig.add_trace(go.Bar(x=df.columns, y=col_importance, showlegend=False))
    return fig

def visualize_pca_components(df, features, dx=[-15, 10], dy=[-10, 10], **fig_kwargs):
    """Visualize pca components projections in 2D. dx, dy are offset values for the x and y axes."""
    pca = pca_fit(df.values)
    feature_map = {f: i for i, f in enumerate(df.columns)}
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    fig = get_figure(xaxis_title="PCA 1", yaxis_title="PCA 2", **fig_kwargs)
    for feature in features:
        i = feature_map[feature]
        fig.add_shape(type='line', x0=0, y0=0, x1=loadings[i, 0], y1=loadings[i, 1])
        fig.add_annotation(x=loadings[i, 0], 
                           y=loadings[i, 1] if loadings[i,1] > 0 else loadings[i,1] - 4,
                           ax=0, ay=0, xanchor="center", yanchor="bottom", text=feature,
        )
    fig.update_layout(xaxis=dict(range=[dx[0] + loadings.min(axis=0)[0], dx[1]+loadings.max(axis=0)[0]], 
                             showgrid=False, zeroline=False, visible=True, tickvals=[]),
                  yaxis=dict(range=[dy[0] + loadings.min(axis=0)[1], dy[1]+loadings.max(axis=0)[1]],
                             showgrid=False, zeroline=False, visible=True, tickvals=[]),
                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
                 )
    return fig
