# chimeclassifier/chime.py

import numpy as np
import pandas as pd

class CHIMEClassifier:
    """
    CHIME classifier (fast vectorized version) using hierarchical clustering logic.

    Parameters
    ----------
    base_cluster_max : int, default=5
        Threshold for splitting columns into low/high cardinality clusters.
    """

    def __init__(self, base_cluster_max=5):
        self.base_cluster_max = base_cluster_max
        self.hybrid_col_order = None
        self.cluster_predictions = None
        self.global_majority = None
        self.target_col = None

    def fit(self, df, target_col):
        self.target_col = target_col
        df_copy = df.copy()
        cols = [c for c in df_copy.columns if c != self.target_col]

        # Hybrid column ordering
        phase1 = [c for c in cols if df_copy[c].nunique() <= self.base_cluster_max]
        phase1_sorted = sorted(phase1, key=lambda x: df_copy[x].nunique(), reverse=True)
        phase2 = [c for c in cols if df_copy[c].nunique() > self.base_cluster_max]
        phase2_sorted = sorted(phase2, key=lambda x: df_copy[x].nunique())
        self.hybrid_col_order = phase1_sorted + phase2_sorted

        # Convert to categorical codes
        for col in self.hybrid_col_order:
            df_copy[col] = df_copy[col].astype('category').cat.codes

        arr = df_copy[self.hybrid_col_order].to_numpy()
        target_arr = df_copy[self.target_col].to_numpy()

        dtype = np.dtype([('f'+str(i), arr.dtype) for i in range(arr.shape[1])])
        structured_arr = arr.view(dtype)

        unique_clusters, inverse = np.unique(structured_arr, return_inverse=True)

        self.cluster_predictions = {}
        for i, cluster in enumerate(unique_clusters):
            indices = np.where(inverse == i)[0]
            majority = pd.Series(target_arr[indices]).mode()[0]
            self.cluster_predictions[tuple(arr[indices[0]])] = majority

        self.global_majority = pd.Series(target_arr).mode()[0]
        return self

    def predict(self, df):
        df_copy = df.copy()
        for col in self.hybrid_col_order:
            df_copy[col] = df_copy[col].astype('category').cat.codes

        arr = df_copy[self.hybrid_col_order].to_numpy()
        cluster_keys = [tuple(row) for row in arr]
        preds = [self.cluster_predictions.get(k, self.global_majority) for k in cluster_keys]
        return pd.Series(preds, index=df.index)