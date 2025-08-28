# cutflow_compare

## Overview
`cutflow_compare` is a Python package designed to simplify the comparison of cutflow histograms from ROOT files. It provides an intuitive command-line interface for analyzing and visualizing differences in cutflow data across multiple regions and files. Whether you're working with high-energy physics datasets or other ROOT-based analyses, `cutflow_compare` helps you streamline your workflow by automating comparisons and generating detailed reports.

## Features
- Compare cutflow histograms from multiple ROOT files.
- Compare cutflow histograms with countflow histograms within the same file.
- Custom labels for each file using the `--labels` argument.
- Generate separate CSV reports for each region.
- Calculate relative errors and standard deviations across all files for each selection.
- Calculate cumulative error between cutflow and countflow histograms.
- Easy to use with command-line arguments for file input and region selection.

## Installation
You can install the package using pip:

```sh
pip install cutflow_compare
```

Alternatively, you can clone the repository and install it manually:

```sh
git clone https://github.com/ibeuler/cutflow_compare.git
cd cutflow_compare
```

Or, if running from source:

```sh
python cutflow_compare.py --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference
```

## Usage

After installation, you can use the command-line tool directly:

```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference
```

Or, if running from source:

```sh
python cutflow_compare.py --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference
```

### Note: 
Make sure the same regions are present in all files with the same name.

### Arguments
- `--files`: List of input ROOT files to compare. **Required.**
- `--regions`: List of regions to compare within the cutflow histograms. **Required.**
- `--labels`: Custom labels for each file, used in the output CSV and terminal display. **Optional.**
- `--separate-selections`: Keep selections separate instead of merging them. **Optional.**
- `--relative-error`: Include relative error calculations in the output. **Optional.**
- `--save`: Save the results to CSV files. Optionally, specify a custom filename prefix. **Optional.**
- `--colored`: Display table with colored columns for better contrast in the terminal. **Optional.**
- `--counts`: Compare cutflow output with specified countflow histograms (names provided). **Optional.**
- `--comulative-error`: Calculate cumulative error between cutflow and countflow (only valid with `--counts`). **Optional.**
- `--version`: Check the current version of cutflow_compare. **Optional.**

### Output
The tool generates **separate CSV files for each region** when the `--save` option is used. Each CSV file contains:
- Columns for each file's event counts after cuts.
- Calculated relative errors and standard deviations for each selection (if multiple files are compared).
- Calculated cumulative error between cutflow and countflow (if `--counts` and `--comulative-error` are used).

### Example Output
For a region `WZ` and files `histoOut-compared.root`, `histoOut-reference.root`, and `histoOut-third.root`, the output CSV might look like this:

| Selection       | Compared_Event_After_Cut | Reference_Event_After_Cut | Third_Event_After_Cut | RelativeError_AllFiles |
|------------------|--------------------------|---------------------------|-----------------------|-------------------------|
| Selection 1      | 100 ± 5                 | 105 ± 6                   | 102 ± 4              | 0.03                   |
| Selection 2      | 200 ± 10                | 195 ± 9                   | 198 ± 8              | 0.02                   |


When comparing with countflow, the output might look like this:

| Selection       | Cutflow_Event_After_Cut | countflow1_countflow | countflow2_countflow |
|------------------|--------------------------|----------------------|----------------------|
| Selection 1      | 100 ± 5                 | 98 ± 3               | 101 ± 4              |
| Selection 2      | 200 ± 10                | 195 ± 8              | 202 ± 9              |


---

## Examples

### Basic Comparison
```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2
```
This compares `region1` and `region2` in the two ROOT files and prints the results to the terminal.

### Save Results to CSV
```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 --save
```
This saves the results for each region to separate CSV files, e.g., `cutflow_comparison_region1.csv` and `cutflow_comparison_region2.csv`.

### Custom Filename for Saved Results
```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 --save my_results
```
This saves the results to `my_results_region1.csv` and `my_results_region2.csv`.

### Colored Output
```sh
cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 --colored
```
This displays the results in the terminal with contrasting colors for each file's data.

#### Compare with Countflow
```sh
cutflow_compare --files histoOut-compared.root -r region1 region2 --counts countflow
```
This compares the cutflow histogram with `countflow` in `histoOut-compared.root` for `region1` and `region2`.

#### Calculate Cumulative Error
```sh
cutflow_compare --files histoOut-compared.root -r region1 --counts countflow --comulative-error
```
This compares the cutflow histogram with `countflow` in `histoOut-compared.root` for `region1` and calculates the cumulative error.

---

## Requirements

- Python 3.6+
- [ROOT](https://root.cern/) (must be installed separately, e.g., via conda: `conda install -c conda-forge root`)
- pandas (automatically installed with the package)
- uncertainties (automatically installed with the package)
- prettytable (automatically installed with the package)

---

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

## Contributing
Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/ibeuler/cutflow_compare).

---

## Acknowledgments
This package leverages the ROOT framework for data analysis and visualization. Special thanks to the open-source community for providing the tools and libraries that make this project possible.
