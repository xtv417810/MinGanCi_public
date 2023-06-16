import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.rand(10,2),columns=['A','B'])
df_train = df.sample(frac=0.8,random_state=0)
df_valid = df.drop(df_train.index, axis=0)
print(df_train)