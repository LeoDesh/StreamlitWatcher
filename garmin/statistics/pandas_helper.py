import pandas as pd
from typing import List,Any
def get_overview_table(df: pd.DataFrame,column:str) -> pd.DataFrame:
    df = (
        df[column]
        .agg(["mean", "median", "min", "max"])
        .T
    )
    df.index = df.index.map(
        {
        
            "mean": "Average",
            "median": "Median",
            "min": "Min",
            "max": "Max",
        }
    )
    return pd.DataFrame(df)

def get_grouped_table(df:pd.DataFrame,group_columns:List[str],agg_columns:List[str]):
    sum_df =  df.groupby(group_columns)[agg_columns].sum()
    count_df = df.groupby(group_columns).size().to_frame('Count')
    return count_df.join(sum_df).reset_index()


def get_unique_values_per_column(df:pd.DataFrame,columns:list[str]) -> dict[str,list[Any]]:
    return {column:df[column].unique().tolist() for column in columns}


def filter_dataframe(df:pd.DataFrame,filter_kwargs:dict[str,Any]) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for col, val in filter_kwargs.items():
        if isinstance(val, (list, tuple, set)):
            mask &= df[col].isin(val)
        else:
            mask &= df[col] == val
    return df[mask]