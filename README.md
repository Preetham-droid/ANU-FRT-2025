ANU-FRT Summary
Author: Preetham
Date: May–July 2025

Introduction
This is a summary of the work done during the ANU-FRT program 2025. Most of the project focused on writing Python codes to analyze experimental data. Each code is briefly described below, and key results are noted where relevant.

Analyzing the .bin Files
During the experiment, the lab software shows real-time readings from the PMT and other signals. However, assessing these signals quickly was not straightforward.

These scripts aim to simplify that process — they can be called directly from the terminal with specific arguments to analyze and optionally save results.

A key quantity is the "charge", computed as the sum of the area under the histogram in the .bin file.

Scripts:
Height.py – Reports the maximum value in a single row of the .bin file and its index.

Compare.py – Overlays and compares the normalized charge histograms from two .bin files.

round_window.py – Analyzes a given .bin file and returns the normalized charge histogram. Option to save plot and data as .csv.

🛈 Run any of these with the --help flag to see usage instructions.

Analyzing the Ion-Backfire
Goal: Analyze image intensity in three regions:

Track region – where the particle passed.

Non-track region – within the camera viewport.

Outside viewport.

The code used: Can you see the pixels.ipynb (a Jupyter notebook, self-explanatory).

Basic noise reduction was applied by ignoring pixel values < 10.

A key observation: plotting the track-to-dark intensity ratio vs intensifier gate length revealed a peak — possibly evidence of the ion-backfire process, where secondary avalanches are triggered by ion feedback in the GEM.


Techniques to Measure Intensity
Different methods were explored to measure track intensity:

Sum of pixel values in the track.

Count of fired pixels.

Count of small clusters, estimating the number of electrons.

While method (3) is theoretically most accurate, practical limitations (parameter tuning, lack of noise reduction) meant no significant improvement over the summed intensity method.

Code: Track.ipynb

For Katie’s data comparison: Final.ipynb

Miscellaneous
Various images and code files that didn’t fit into the above sections are stored here.
Open at your own risk 😄

📄 For a more detailed explanation, open the full summary: ANU-FRT Summary.tex (or its compiled PDF, if available).

