import os
import pandas as pd
import numpy as np

df = pd.read_csv('DataCollection/clean_data/to_be_cleaned.csv')
df['follower_following_ratio'] = df['Followers'] / np.where(df['Following'] == 0, 1, df['Following'])
df.to_csv('to_be_cleaned.csv', index=False)

