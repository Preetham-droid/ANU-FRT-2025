# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 23:36:01 2025

@author: 91748
"""
import numpy as np
import pandas as pd
import argparse
import os

def inferNsamp(fname):
    hdrdt = np.dtype([
        ('Number', '<u4'), ('Time', '<u8'),
        ('No_samples', '<u4'), ('Sample length', '<u8')
    ] + [(f'Sample{N+1}', 'float32') for N in range(10)])
    with open(fname, 'rb') as f:
        b = f.read(hdrdt.itemsize)
    np_data = np.frombuffer(b, hdrdt)
    return np_data['No_samples'][0]

def get_dtype(nsamp):
    return np.dtype([
        ('Number', '<u4'), ('Time', '<u8'),
        ('No_samples', '<u4'), ('Sample length', '<u8')
    ] + [(f'Sample{N+1}', 'float32') for N in range(nsamp)])

def ReadDataChunk(f, nrows, dtype):
    row_size = dtype.itemsize
    b = f.read(row_size * nrows)
    if not b:
        return None
    return pd.DataFrame(np.frombuffer(b, dtype=dtype))

def find_median_data(data, median_range):
    lower, upper = median_range
    return data.iloc[:, lower:upper].median(axis=1)

def process_chunk(data_chunk, median_range):
    median_data = find_median_data(data_chunk, median_range)
    centered = data_chunk.iloc[:, 4:].subtract(median_data, axis=0)
    
    max_values = []
    max_indices = []

    for i in range(centered.shape[0]):
        row = centered.iloc[i]
        max_val = row.max()
        col_name = row.idxmax()
        col_index = data_chunk.columns.get_loc(col_name)
        max_values.append(max_val)
        max_indices.append(col_index)

    return pd.DataFrame({'max_value': max_values, 'col_index': max_indices})

def Stats_chunked(fname, chunk_size=1000, median_range=(4, 104), threshold=0):
    nsamp = inferNsamp(fname)
    dtype = get_dtype(nsamp)
    filesize = os.path.getsize(fname)
    row_size = dtype.itemsize
    total_rows = filesize // row_size

    all_results = []

    with open(fname, 'rb') as f:
        for start in range(0, total_rows, chunk_size):
            nrows = min(chunk_size, total_rows - start)
            df = ReadDataChunk(f, nrows, dtype)
            if df is None or df.empty:
                break
            result_chunk = process_chunk(df, median_range)
            all_results.append(result_chunk)

    return pd.concat(all_results, ignore_index=True)

def main():
    parser = argparse.ArgumentParser(description="Process .bin file and return max value locations above threshold.")
    parser.add_argument("filename", help="Path to .bin file")
    parser.add_argument("--median_range", type=int, nargs=2, default=(4, 104),
                        help="Median range as two column indices (default: 4 104)")
    parser.add_argument("--output", type=str, help="Path to save the output CSV file")

    args = parser.parse_args()
    median_range = tuple(args.median_range)

    print(f"Processing file: {args.filename}")
    print(f"Using median range: {median_range}")
    
    result = Stats_chunked(args.filename, median_range=median_range)

    if args.output:
        result.to_csv(args.output, index=False)
        print(f"Saved result to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
