# Analysis of the 2021 Inflation Shock and Structural Vulnerabilities in Europe

**Author:** Hedi SAGAR  
**Date:** November 2025

## Project Overview

This project provides an in-depth analysis of the historic inflation surge that occurred in the European Union (EU27) during the 2021-2022 period. By examining long-term time series and decomposing consumption categories (COICOP), the study demonstrates how countries absorbed these shocks differently.

While the initial trigger was a symmetric exogenous shock (a global spike in energy and commodity prices), its propagation across member states was asymmetric, dictated by pre-existing structural vulnerabilities.

## Key Features

The analysis is performed using a Jupyter Notebook that orchestrates the data processing and visualization pipeline:

* **HICP Evolution Analysis:** Tracking the Harmonised Index of Consumer Prices to pinpoint the structural break in 2021.
* **COICOP Decomposition:** Breaking down inflation contributions by categories (Energy, Food, Services, Industrial Goods).
* **Structural Profiling:**
    * **PCA (Principal Component Analysis):** Identifying clusters of countries with similar inflationary behaviors.
    * **Heatmaps:** Visualizing the intensity of price variations across different economies.
* **East-West Divergence:** Highlighting the contrast between Western European stability and the high volatility in Central/Eastern European (and Baltic) states.

## Project Structure

* `Analysis_of_Inflation_Shocks_in_Europe.ipynb`: The main entry point. This notebook contains all the execution logic, visualizations, and analytical commentary.
* `Preprocessing.py`: A helper module responsible for loading raw Excel data, cleaning it, and transforming it into a format suitable for analysis.
* `Analysis_of_Inflation_Shocks_in_Europe.docx`: The full analytical report containing the executive summary and detailed conclusions.

## Prerequisites

To run this project, you need **Python 3.10** and the following libraries:

* pandas
* numpy
* matplotlib
* scikit-learn

You can install the dependencies using pip:

```bash
pip install pandas numpy matplotlib scikit-learn openpyxl
