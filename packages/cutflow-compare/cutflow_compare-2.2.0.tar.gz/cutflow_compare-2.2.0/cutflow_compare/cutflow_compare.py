import ROOT
import argparse
import pandas as pd
from uncertainties import ufloat
import prettytable as pt
import sys  # Import the sys module

"""
Usage:
    cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference --separate-selections --relative-error --save my_results --colored

Description:
    This script compares cutflow histograms from multiple ROOT files across specified regions. It displays the results in a table format, optionally with colored columns for better contrast, and can save the results to CSV files.

Arguments:
    --files (-f): List of input ROOT files containing cutflow histograms.
    --regions (-r): List of regions to compare. Region names must match in all files.
    --labels: Optional labels for input files. If not provided, filenames are used.
    --save: Saves the results to CSV files. Optionally specify a custom filename prefix.
    --relative-error: If set, calculates and displays the relative error between files for each selection.
    --comulative-error: It calculates the comulative error for each selection.
    --counts: Compares with counts instead of other ROOT files.
    --colored: Displays the output table with colored columns for better contrast.
    --separate-selections: If set, keeps selections separate for each file instead of merging.
    --version: Shows the version of cutflow_compare.

Example:
    cutflow_compare --files histoOut-compared.root histoOut-reference.root -r region1 region2 region3 --labels Compared Reference --separate-selections --relative-error --save my_results --colored

Notes:
    - Make sure you use the same names for regions in all .root files.
    - To save the table, use the --save option. Optionally, add a custom filename: --save my_filename
"""

def get_file_name(file_path):
    """Extracts the file name without extension from a given file path."""
    try:
        file_name = file_path.split("/")[-1]
        file_name = file_name.replace("histoOut-", "")
        file_name = file_name.replace(".root", "")
        return file_name
    except Exception as e:
        print(f"Error extracting file name from {file_path}: {e}")
        raise

def extract_histogram_data(hist, region):
    """Extracts data (labels, contents, errors) from a ROOT histogram."""
    try:
        if not hist:
            raise ValueError(f"Histogram is None for region: {region}")
        
        nbins = hist.GetXaxis().GetNbins()
        labels_list = []
        contents = []
        contents_errored = []
        
        for i in range(1, nbins + 1):
            label = hist.GetXaxis().GetBinLabel(i)
            content = hist.GetBinContent(i)
            error = hist.GetBinError(i)
            
            labels_list.append(label)
            contents.append(ufloat(content, error))
            contents_errored.append(f"{content} ±{format(error,'.2f')}")
        
        return labels_list, contents, contents_errored
    except Exception as e:
        print(f"Error extracting histogram data for region {region}: {e}")
        raise

def compare_cutflows(args, files, regions, labels, colors, reset):
    """Compares cutflow histograms from multiple ROOT files."""
    for region in regions:
        df = pd.DataFrame()
        cont_dict = {}
        
        print(f"\n*** Processing region: {region} ***")
        
        for file, label in zip(files, labels):
            try:
                f = ROOT.TFile(file)
                if not f or not f.IsOpen():
                    raise FileNotFoundError(f"Could not open file: {file}")

                print(f"*** Starting analysis for file: {file}, region: {region} ***")

                hc = f.Get(region + "/" + "cutflow")
                if not hc:
                    raise ValueError(f"No cutflow histogram found in file {file} for region {region}.")
                
                labels_list, contents, contents_errored = extract_histogram_data(hc, region)

                if args.separate_selections:
                    df[f"{label}_Selection"] = labels_list
                else: 
                    df[f"Selection in region {region}"] = labels_list
                df[f"{label}_Cutflow"] = contents_errored
                cont_dict[f"{label}_Cutflow_ufloat"] = contents
            except Exception as e:
                print(f"Error processing file {file}, region {region}: {e}")
            finally:
                if f:
                    f.Close()

        if args.relative_error and len(cont_dict) > 1:
            print(f"*** Calculating relative error for region: {region} ***")
            error_df = pd.DataFrame.from_dict(cont_dict)
            # Collect all columns for this region
            cols = [f"{label}_Cutflow_ufloat" for label in labels if f"{label}_Cutflow_ufloat" in error_df.columns]
            if len(cols) > 1:
                # Get the nominal values for each file/selection
                values = error_df[cols].apply(lambda row: [x.n for x in row], axis=1)
                # Calculate mean and std for each selection
                means = values.apply(lambda x: sum(x)/len(x))
                stds = values.apply(lambda x: pd.Series(x).std())
                # Relative error: std/mean
                rel_error = stds / means
                df[f"{region}_relative_error_std"] = rel_error

        # Print results (default behavior)
        print(f"\n*** Results for region: {region} ***")
        table = pt.PrettyTable()
        table.field_names = df.columns.tolist()
        
        for _, row in df.iterrows():
            if args.colored:
                colored_row = []
                for i, cell in enumerate(row.tolist()):
                    # Color each file's data with different colors
                    if i == 0:  # Selection column stays uncolored
                        colored_row.append(str(cell))
                    else:
                        # Determine which file this column belongs to
                        file_index = (i - 1) % len(labels)
                        colored_row.append(f"{colors[file_index % len(colors)]}{cell}{reset}")
                table.add_row(colored_row)
            else:
                table.add_row(row.tolist())
        print(table)
        if args.save:
            # Determine filename
            if isinstance(args.save, str):
                # Custom filename prefix provided
                output_filename = f"{args.save}_{region}.csv"
            else:
                # Default filename
                output_filename = f"cutflow_comparison_{region}.csv"
        
            df.to_csv(output_filename, index=False)
            print(f"*** Results for region {region} saved to \033[92m{output_filename}\033[0m ***")

def compare_with_countflow(args, regions, labels, colors, reset):
    """Compares cutflow histograms with countflow histograms within the same file."""
    file = args.files[0]
    try:
        f = ROOT.TFile(file)
        if not f or not f.IsOpen():
            raise FileNotFoundError(f"Could not open file: {file}")
        
        for region in regions:
            df = pd.DataFrame()
            cont_dict = {}
            
            print(f"\n*** Processing region: {region} ***")
            
            hc = f.Get(region + "/" + "cutflow")
            if not hc:
                raise ValueError(f"No cutflow histogram found in file {file} for region {region}.")
            
            cutflow_labels, cutflow_contents, cutflow_contents_errored = extract_histogram_data(hc, region)

            # Pop the first item only if in --counts mode
            if args.counts:
                if cutflow_labels:
                    cutflow_labels.pop(0)
                if cutflow_contents:
                    cutflow_contents.pop(0)
                if cutflow_contents_errored:
                    cutflow_contents_errored.pop(0)

            if args.separate_selections:
                df[f"Selection"] = cutflow_labels
            else:
                df[f"Selection in region {region}"] = cutflow_labels
            df[f"{labels[0]}_Cutflow"] = cutflow_contents_errored
            cont_dict[f"{labels[0]}_Cutflow_ufloat"] = cutflow_contents
            
            for countflow_name in args.counts:
                hp = f.Get(region + "/" + countflow_name)
                if not hp:
                    print(f"Warning: No countflow histogram '{countflow_name}' found in file {file} for region {region}.")
                    continue
                
                countflow_labels, countflow_contents, countflow_contents_errored = extract_histogram_data(hp, region)
                
                df[f"{labels[0]}_{countflow_name}_Countflow"] = countflow_contents_errored
                cont_dict[f"{labels[0]}_{countflow_name}_Countflow_ufloat"] = countflow_contents
            
            # Relative error calculation (only if multiple countflows or cutflows are present)
            if args.relative_error and len(cont_dict) > 1:
                print(f"*** Calculating relative error for region: {region} ***")
                error_df = pd.DataFrame.from_dict(cont_dict)
                
                # Select relevant columns for relative error calculation
                cols = [col for col in error_df.columns if '_ufloat' in col]
                
                if len(cols) > 1:
                    values = error_df[cols].apply(lambda row: [x.n for x in row], axis=1)
                    means = values.apply(lambda x: sum(x)/len(x))
                    stds = values.apply(lambda x: pd.Series(x).std())
                    rel_error = stds / means
                    df[f"{region}_relative_error_std"] = rel_error

            # Comulative error calculation (only if multiple countflows or cutflows are present)
            if args.comulative_error and len(cont_dict) > 1:
                print(f"*** Calculating comulative error for region: {region} ***")
                error_df = pd.DataFrame.from_dict(cont_dict)
                
                # Select relevant columns for comulative error calculation
                cols = [col for col in error_df.columns if '_ufloat' in col]
                
                if len(cols) == 2:
                    values = error_df[cols].apply(lambda row: [x.n for x in row], axis=1)
                    
                    comu_error = values.apply(lambda x: (x[0]-x[1])/x[1] if x[0] != 0 else 0 if x[1] == 0 else 99999999999 )
                    df[f"{region}_comulative_error"] = comu_error
            
            # Print results (default behavior)
            print(f"\n*** Results for region: {region} ***")
            table = pt.PrettyTable()
            table.field_names = df.columns.tolist()
            
            for _, row in df.iterrows():
                if args.colored:
                    colored_row = []
                    for i, cell in enumerate(row.tolist()):
                        # Color each file's data with different colors
                        if i == 0:  # Selection column stays uncolored
                            colored_row.append(str(cell))
                        else:
                            # Determine which file this column belongs to
                            file_index = (i - 1) % (len(args.counts)+1)
                            colored_row.append(f"{colors[file_index % len(colors)]}{cell}{reset}")
                    table.add_row(colored_row)
                else:
                    table.add_row(row.tolist())
            print(table)
            
            if args.save:
                # Determine filename
                if isinstance(args.save, str):
                    # Custom filename prefix provided
                    output_filename = f"{args.save}_{region}.csv"
                else:
                    # Default filename
                    output_filename = f"cutflow_comparison_{region}.csv"
            
                df.to_csv(output_filename, index=False)
                print(f"*** Results for region {region} saved to \033[92m{output_filename}\033[0m ***")
    except Exception as e:
        print(f"Error processing file {file}: {e}")
    finally:
        if f:
            f.Close()

def main():
    parser = argparse.ArgumentParser(description='Compare cutflow histograms')
    parser.add_argument('-f', '--files', nargs='+', required=True, help='Input ROOT files')
    parser.add_argument('-r', '--regions', nargs='+', required=True, help='Regions to compare')
    parser.add_argument('--labels', nargs='+', required=False, help='Labels for input files')
    parser.add_argument('--separate-selections', action='store_true', help='Keep selections separate instead of merging')
    parser.add_argument('--relative-error', action='store_true', help='Include std in the output')
    parser.add_argument('--save', nargs='?', const=True, help='Save the results to CSV files. Optionally specify a custom filename prefix.')
    parser.add_argument('--colored', action='store_true', help='Display table with colored columns for better contrast')
    parser.add_argument('--version', action='version', version='cutflow_compare 2.2.0', help='Show the version of cutflow_compare')
    parser.add_argument('--counts', nargs='+', help='Compare with countflow histograms (names provided).')
    parser.add_argument('--comulative-error', action='store_true', help='Include comulative error in the output')
    args = parser.parse_args()    
    
    # Color codes for different files
    colors = ['\033[92m', '\033[94m', '\033[95m', '\033[96m', '\033[93m']  # Green, Blue, Magenta, Cyan, Yellow
    reset = '\033[0m'

    # Parse the input arguments
    files = args.files
    regions = args.regions
    labels = args.labels if args.labels else [get_file_name(file) for file in files]

    if len(labels) != len(files):
        print("Error: Number of labels must match number of files.")
        sys.exit(1)

    if args.counts:
        if len(args.files) != 1:
            print("Error: --counts option is only valid with a single file.")
            sys.exit(1)
        compare_with_countflow(args, regions, labels, colors, reset)
    else:
        compare_cutflows(args, files, regions, labels, colors, reset)
        if args.comulative_error:
            print("\033[91m Note:\033[0m comulative error is only calculated with --counts option!")

    if args.save:
        print("\n" + "*" * 50)
        print("*** All comparison results saved successfully! ***")
        print("*" * 50 + "\n")
    else:
        print("\033[91m The Table is not saved!")
        print("\033[0m*** To save the table, use \033[92m--save\033[0m option. Optionally, add a custom filename: \033[92m--save my_filename\033[0m ***\033[0m")
        
if __name__ == "__main__":
    main()