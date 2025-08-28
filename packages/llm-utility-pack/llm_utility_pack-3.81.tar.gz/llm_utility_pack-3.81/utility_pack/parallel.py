from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from tqdm import tqdm
import pandas as pd
import numpy as np
import cloudpickle

def _worker(serialized_func, idx, chunk):
    """Worker function that deserializes the function, applies it, and returns index + result."""
    func = cloudpickle.loads(serialized_func)
    return idx, func(chunk)

def process_chunk(args):
    serialized_func, idx, chunk = args
    return _worker(serialized_func, idx, chunk)

def parallelize_apply(df, func, n_jobs=-1):
    if n_jobs == -1:
        n_jobs = cpu_count()

    # Split the dataframe
    chunks = np.array_split(df, n_jobs)
    
    # Serialize function
    serialized_func = cloudpickle.dumps(func)
    
    # Prepare arguments for the process_chunk function
    args_list = [(serialized_func, i, chunk) for i, chunk in enumerate(chunks)]
    
    with ProcessPoolExecutor(n_jobs) as executor:
        results = list(tqdm(executor.map(process_chunk, args_list), total=n_jobs))

    # Sort results by original index and concatenate
    results.sort(key=lambda x: x[0])  # Sort by index
    ordered_dfs = [df for _, df in results]  # Extract sorted DataFrames
    return pd.concat(ordered_dfs, ignore_index=True)  # Concatenate properly
