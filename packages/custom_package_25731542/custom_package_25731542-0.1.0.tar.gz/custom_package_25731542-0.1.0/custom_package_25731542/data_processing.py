
import pandas as pd

def fill_missing_mean(df):
    return df.fillna(df.mean())
