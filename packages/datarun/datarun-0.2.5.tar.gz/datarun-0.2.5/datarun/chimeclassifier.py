import pandas as pd
import numpy as np

class CHIMEClassifier:
    def __init__(self, base_cluster_max=None):
        self.base_cluster_max = base_cluster_max
        self.hybrid_col_order = None
        self.cluster_predictions = None
        self.global_majority = None
        self.target_col = None

    def fit(self, X, y):
        df_copy = X.copy()
        self.target_col = y.name if y is not None else "target"
        df_copy[self.target_col] = y
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

        # Build cluster keys as tuples (row-wise)
        cluster_keys = [tuple(row) for row in arr]

        self.cluster_predictions = {}
        df_copy['_cluster_key'] = cluster_keys
        for key, group in df_copy.groupby('_cluster_key'):
            majority = group[self.target_col].mode()[0]
            self.cluster_predictions[key] = majority

        # Global majority fallback
        self.global_majority = df_copy[self.target_col].mode()[0]
        return self

    def predict(self, df):
        df_copy = df.copy()
        for col in self.hybrid_col_order:
            df_copy[col] = df_copy[col].astype('category').cat.codes

        cluster_keys = [tuple(row) for row in df_copy[self.hybrid_col_order].to_numpy()]
        preds = [self.cluster_predictions.get(k, self.global_majority) for k in cluster_keys]
        return pd.Series(preds, index=df.index)