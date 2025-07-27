import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import pandas as pd

SHOW_PLOTS = False

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

def find_median_data(data, median_range=None):
    if median_range is None:
        median_data = data.iloc[:, 4:104].median(axis=1)
    else:
        lower, upper = median_range
        median_data = data.iloc[:, lower:upper].median(axis=1)
    return median_data

def process_chunk(data_chunk, median_range, threshhold):
    data = data_chunk.iloc[:, 1500:2200]
    median_data = find_median_data(data, median_range)
    centered = data.iloc[:, 4:-1].subtract(median_data, axis=0)
    qthr = centered.T.apply(lambda x: -np.sum(np.where(x > threshhold, 0, x)))
    return qthr

def Stats_chunked(fname, chunk_size=1000, median_range=None, threshhold=-1):
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

def plot_qthr(qthr, save_plot=None, save_data=None):
    plt.figure()
    plt.hist(qthr, bins=100, density=True, histtype='step')
    if save_plot:
        plt.savefig(save_plot)
    if save_data:
        pd.Series(qthr).to_csv(save_data, index=False)
    if SHOW_PLOTS:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Chunked qthr computation from .bin file")
    parser.add_argument("filename", type=str, help="Path to the .bin file")
    parser.add_argument("--median_lower", type=int, default=4, help="Lower bound of median range (default 4)")
    parser.add_argument("--median_upper", type=int, default=104, help="Upper bound of median range (default 104)")
    parser.add_argument("--save_plot", nargs="?", const="output/size_plot.png", help="File to save plot")
    parser.add_argument("--save_data", nargs="?", const="output/qthr_data.csv", help="File to save qthr values")
    args = parser.parse_args()

    global SHOW_PLOTS
    SHOW_PLOTS = True

    median_range = (args.median_lower, args.median_upper)
    qthr = Stats_chunked(args.filename, chunk_size=1000, median_range=median_range, threshhold=-1)
    plot_qthr(qthr, save_plot=args.save_plot, save_data=args.save_data)

if __name__ == "__main__":
    main()
