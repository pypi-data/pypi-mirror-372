import numpy as np
import pandas as pd

def permutation(df,columns=None,permute_levels=None):
    """Randomly permute rows of df[columns] at permute_levels.
    """

    df = pd.DataFrame(df) # Make sure we have a DataFrame.

    if columns is None: columns = df.columns

    if permute_levels is None:
        P = pd.DataFrame(np.random.permutation(df.loc[:,columns]),index=df.index,columns=columns)
    else:
       fixed = df.index.names.difference(permute_levels)
       P = pd.DataFrame(df.loc[:,columns].unstack(fixed).sample(frac=1).stack(fixed).values,index=df.index,columns=columns)

    return P
