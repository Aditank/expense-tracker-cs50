import pandas as pd

def summary_dataframe(rows):
    return pd.DataFrame(rows, columns=["Category", "Amount"])
