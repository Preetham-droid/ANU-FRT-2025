# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 22:54:12 2025

@author: 91748
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import pandas as pd

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

def process_chunk(data_chunk, median_range, threshhold):
    data = data_chunk.iloc[:, 1500:2200]
    median_data = find_median_data(data, median_range)
    centered = data.iloc[:, 4:-1].subtract(median_data, axis=0)
    qthr = centered.T.apply(lambda x: -np.sum(np.where(x > threshhold, 0, x)))
    return qthr

def Stats_chunked(fname, chunk_size=1000, median_range=(4, 104), threshhold=-1):
    nsamp = inferNsamp(fname)
    dtype = get_dtype(nsamp)
    filesize = os.path.getsize(fname)
    row_size = dtype.itemsize
    total_rows = filesize // row_size

    qthr_all = []

    with open(fname, 'rb') as f:
        for start in range(0, total_rows, chunk_size):
            nrows = min(chunk_size, total_rows - start)
            df = ReadDataChunk(f, nrows, dtype)
            if df is None or df.empty:
                break
            qthr_chunk = process_chunk(df, median_range, threshhold)
            qthr_all.append(qthr_chunk)

    return pd.concat(qthr_all, ignore_index=True)

def main():
    parser = argparse.ArgumentParser(description="Compare multiple .bin files overlaid in one histogram")
    parser.add_argument("filenames", nargs="+", help="Paths to .bin files")
    args = parser.parse_args()

    plt.figure(figsize=(10, 6))

    for fname in args.filenames:
        print(f"Processing {fname}...")
        qthr = Stats_chunked(fname)
        lower = np.percentile(qthr, 1)
        upper = np.percentile(qthr, 99)
        plt.hist(qthr, bins=100, density=True, histtype='step', label=os.path.basename(fname), range=(lower, upper))

    plt.xlabel("Qthr")
    plt.ylabel("Density")
    plt.title("Overlayed Qthr Histograms")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    import os
    main()
