# APICURON Integration Trendline Chart

## Overview

This project contains a Python script that generates a publication-quality trendline chart, visualizing the cumulative growth of APICURON integrations over time. It reads data from a CSV file, plots the trend, and adds clear, non-overlapping annotations for each newly integrated resource.

## Prerequisites

*   Python 3.x
*   pip (Python package installer)

## Installation

1.  Clone the repository to your local machine:
    ```bash
    git clone https://github.com/gavinf97/APICURON_pub_figures_20260225.git
    cd APICURON_pub_figures_20260225
    ```

2.  Install the required Python packages using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To generate or update the chart, simply run the script from the root directory of the project:
```bash
python3 create_chart.py
```
This command reads the `APICURON_paper_figure_trend_data.csv` file and generates (or overwrites) the chart image named `apicuron_trendline.png`.

## Data Format

The script requires the input data to be in a CSV file named `APICURON_paper_figure_trend_data.csv`. This file must contain two columns:
*   `Resource Name`: The name of the integrated resource (string).
*   `Year Added`: The year the resource was integrated (integer).

The script is designed to be robust to new data; you can add more rows to the CSV file and rerun the script to automatically update the chart.

## Code Explanation (`create_chart.py`)

The script is structured within a single function, `create_trendline_chart`, which handles all aspects of the chart generation.

1.  **Import Libraries**: The script begins by importing `pandas` for data manipulation and `matplotlib.pyplot` for creating the plot.

2.  **Data Loading and Processing**:
    *   The CSV data is loaded into a pandas DataFrame and sorted by `Year Added`.
    *   To calculate the trendline, the script groups the resources by year, counts the number of new additions in each year, and then computes a cumulative sum (`cumsum()`) to track the growth.

3.  **Plotting and Styling**:
    *   The script sets a clean, professional plot style using `plt.style.use('seaborn-v0_8-whitegrid')`.
    *   It then plots the years on the x-axis against the cumulative resource counts on the y-axis to create the main trendline. Markers (`marker='o'`) are used to indicate the data points for each year.

4.  **Annotation Logic**:
    *   To ensure annotations are clear and do not overlap with the trendline, a `placements` dictionary pre-defines whether a resource's label should appear 'above' or 'below' the line.
    *   The script iterates through each year's new resources and performs the following for each label:
        *   It looks up the desired placement ('above' or 'below') from the `placements` dictionary, defaulting to 'below' if not specified.
        *   It calculates a vertical `offset` to stack multiple labels neatly and prevent them from overlapping each other.
        *   The `ax.text()` function places the text. The horizontal alignment is set to `ha='left'`, so each label starts directly at its corresponding data point on the trendline.

5.  **Final Touches and Saving**:
    *   Axis labels (`xlabel`, `ylabel`) and tick parameters are set for clarity.
    *   Finally, the chart is saved as a high-resolution (300 DPI) PNG file named `apicuron_trendline.png`. `bbox_inches='tight'` is used to ensure that all elements of the chart, including labels, are saved without being cut off.

6.  **Execution Block**: The `if __name__ == "__main__":` block at the end ensures that the `create_trendline_chart` function is called only when the script is executed directly from the command line.
