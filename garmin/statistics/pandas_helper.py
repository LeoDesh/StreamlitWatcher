import pandas as pd
from typing import List
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