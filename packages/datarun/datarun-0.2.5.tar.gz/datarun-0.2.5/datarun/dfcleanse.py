import pandas as pd

class dfcleanse:
    def __init__(self, df, drop_duplicates=False, handle_nulls=None, drop_constant_columns=None, convert_types=None):
        self.df = df.copy()

        if drop_duplicates  == True:
            self.df.drop_duplicates(inplace=True)
        
        if handle_nulls:
            self.df = self._handle_nulls(self.df, handle_nulls)
        
        if drop_constant_columns:
            self.df = self._drop_constant_columns(self.df)
        
        if convert_types:
            self.df = self._convert_types(self.df)
    
    def _handle_nulls(self, df, config):
        if isinstance(config, str):
            if config == "drop":
                df = df.dropna()
            elif config in ["mean", "median", "mode"]:
                for col in df.columns:
                    if df[col].isnull().sum() == 0:
                        continue
                    if config in ["mean", "median"] and not pd.api.types.is_numeric_dtype(df[col]):
                        continue
                    if config == "mean":
                        df[col] = df[col].fillna(df[col].mean())
                    elif config == "median":
                        df[col] = df[col].fillna(df[col].median())
                    elif config == "mode":
                        df[col] = df[col].fillna(df[col].mode()[0])

        elif isinstance(config, dict):
            for col, strategy in config.items():
                if col not in df.columns or df[col].isnull().sum() == 0:
                    continue
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif strategy == "drop":
                    df = df.dropna(subset=[col])
        return df
    
    def _drop_constant_columns(self, df):
        constant_cols = []

        for col in df.columns:
            non_null_values = df[col].dropna().unique()
            if len(non_null_values) == 1:
                constant_cols.append(col)

        return df.drop(columns=constant_cols)
    
    def _convert_types(self, df):
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    converted = pd.to_numeric(df[col])
                    df[col] = converted
                except:
                    pass
        return df

    def result(self):
        return self.df