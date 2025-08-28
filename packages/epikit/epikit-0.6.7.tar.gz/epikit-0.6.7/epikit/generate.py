import csv
import argparse
import glob
import os
import sys

DATA_VERSION_CHECKED = "1.2"

def unique_first_column(csv_file):
    """
    Find unique strings in the first column of a CSV file, ignoring the header.
    
    Parameters:
        csv_file (str): Path to the CSV file.
    
    Returns:
        set: A set of unique values from the first column.
    """
    unique_values = set()

    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        
        # Skip header
        next(reader, None)

        for row in reader:
            if row:  # avoid empty lines
                unique_values.add(row[0])  # first column

    return unique_values




def main():
    parser = argparse.ArgumentParser(
        description="tool that generates metadata for ensemble."
    )
    
    # Add required argument
    parser.add_argument( "ensemble", help="Name of the ensemble to use.")
    parser.add_argument( "--verbose", action="store_true",   help="Enable verbose output.")
    parser.add_argument( "-v", "--version", action="store_true", help="Print script version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"data version checked: {DATA_VERSION_CHECKED}")
        sys.exit(0)
    
    if not args.ensemble:
        parser.error("the following argument is required: --ensemble")

    # experiment meta.yaml
    expmeta = os.path.join(args.ensemble, "experiments/meta.yaml")
    print(f"Creating {expmeta} file")
    if not os.path.exists(expmeta):
        # find structure files
        structure_files = glob.glob(os.path.join(args.ensemble, 'experiments/*/*/structure.csv'), recursive=True)
        csv_path = structure_files[0] 
        unique_strings = unique_first_column(csv_path)
        sorted_unique_strings = sorted(unique_strings)

        with open(expmeta, 'w') as outfile:
            outfile.write("structure:\n")
            outfile.write("  chromosomes:\n")
            for s in sorted_unique_strings:
                outfile.write("    - " + s + "\n")
    else:
        print(f"  {expmeta} exists, not writing a new one ...")
