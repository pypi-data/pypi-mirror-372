import pandas as pd
from datarun import dfcleanse
df = pd.DataFrame({
    'numeric_str': ['10', '20', '30','40'],
    'mixed_str': ['100', 'abc', '200', 'xyz'],
    'pure_text': ['cat', 'dog', 'mouse', 'elephant'],
    'actual_numbers': [1, 2, 3, 4],
    'mostly_numbers': ['1', '2', '3', 'apple'],  # 75% numeric
    'dates_like': ['2020', '2021', '2022', '2023'],  # should be converted
})

cleaner = dfcleanse(
    df,
    handle_nulls="drop",  # try "median", "mode", "drop", or a dict
    #handle_nulls={"A": "drop"},
    drop_constant_columns=True,
    convert_types=True
)
cleaned_df = cleaner.df
print(cleaned_df.dtypes)