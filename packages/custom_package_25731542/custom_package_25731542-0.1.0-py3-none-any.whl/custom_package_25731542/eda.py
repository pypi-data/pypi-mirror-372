
import pandas as pd

def print_eda(df):
    print('===== SHAPE =====')
    print(df.shape)
    print('\n===== INFO =====')
    print(df.info())
    print('\n===== DESCRIBE =====')
    print(df.describe())
    print('\n===== HEAD =====')
    print(df.head())
