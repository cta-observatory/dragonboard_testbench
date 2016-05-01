import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

def func(chunk, name):
    cell, sample = name
    low, med, high = np.percentile(chunk.adc_counts, q=[25, 50, 75])
    return cell, sample, med, high-low

st = pd.HDFStore("timelapse_data/csta1.h5")
outstore = pd.HDFStore("timelapse_data/offset_cell_sample_csta1.h5")
pool = Parallel(5, verbose=5)

for df_name in tqdm(st.keys()):
    df = st[df_name]
    df = df[df.delta_t > 0.05]
    df.drop("delta_t", axis=1, inplace=True)

    grouped = df.groupby(["cell", "sample"])

    result = pd.DataFrame(
        pool(delayed(func)(df, name) for name, df in grouped),
        columns=["cell", "sample", "median", "50%"]
    )

    outstore.append(df_name, result)