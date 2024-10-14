import pandas as pd

def read_df_csv(path):
    df = pd.read_csv(path,  encoding='cp1251')
    return df