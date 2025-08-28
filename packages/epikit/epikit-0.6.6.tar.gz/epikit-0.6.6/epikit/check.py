import os
import glob
import yaml
import argparse
import sys

DATA_VERSION_CHECKED = "1.2"

# Check that all files contain a set of strings 
def check_strings_in_files(strings, files):
    """
    Check if each string in `strings` is present in each file in `files`.

    Parameters:
        strings (list): A list of strings to search for.
        files (list): A list of file paths.

    Returns:
        dict: A nested dictionary mapping {filename: {string: True/False}}.
    """
    results = {}

    for file_path in files:
        if not os.path.isfile(file_path):
            raise ValueError(f"{file_path} is not a valid file.")

        results[file_path] = {}
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            for s in strings:
                results[file_path][s] = s in content

    return results

def check_directories_have_same_contents(directories):
    """
    Check if all given directories contain the same contents 

    Parameters:
        directories (list): A list of directory paths.

    Returns:
        bool: True if all directories have the same files, False otherwise.
        dict: A dictionary mapping each directory to its set of files.
    """
    dir_files = {}
    
    # Collect contents 
    for d in directories:
        if not os.path.isdir(d):
            raise ValueError(f"{d} is not a valid directory.")
        dir_files[d] = set(os.listdir(d))
        if False:
            print(os.listdir(d))
    
    # Compare sets of files
    all_file_sets = list(dir_files.values())
    first_set = all_file_sets[0]
    all_same = all(fs == first_set for fs in all_file_sets)

    return all_same, dir_files

def main():
    parser = argparse.ArgumentParser(
        description="Script that requires an ensemble argument."
    )
    
    # Add required argument
    parser.add_argument( "--ensemble", required=False, help="Name of the ensemble to use.")
    parser.add_argument( "--verbose", action="store_true",   help="Enable verbose output.")
    parser.add_argument( "-v", "--version", action="store_true", help="Print script version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"data version checked: {DATA_VERSION_CHECKED}")
        sys.exit(0)
    
    if not args.ensemble:
        parse.error("the following argument is required: --ensemble")

    # Access the value
    print(f"Checking integrity of ensemble: {args.ensemble}")

    # check directories
    directories = glob.glob(os.path.join(args.ensemble, 'experiments/*/'), recursive=True)

    # Print the found directories
    if args.verbose: 
        print(directories)

    success = True

    # timesteps
    print("Checking experiment directories for timesteps")
    same, files_per_dir = check_directories_have_same_contents(directories)
    if same:
        print("  All experiments have the same timesteps.")
    else:
        print("  All experiments DO NOT have the same timesteps.")
        success = False
        for d, files in files_per_dir.items():
            print(f"{d}: {files}")

    # contents of timesteps
    print("Checking contents of timestep directories")
    timesteps = glob.glob(os.path.join(args.ensemble, 'experiments/*/*/'), recursive=True)
    same, files_per_dir = check_directories_have_same_contents(timesteps)
    if same:
        print("  All experiment/timestep directories contain the same files.")
    else:
        print("  All experiment/timestep directories DO NOT contain the same files.")
        success = False
        for d, files in files_per_dir.items():
            print(f"{d}: {files}")

    # check chromosome list against all relevant files
    print("Checking that all relevant files have required chromosomes")
    files_to_check = glob.glob(os.path.join(args.ensemble, 'experiments/*/*/*'), recursive=True)

    # Load YAML file
    metafile = os.path.join(args.ensemble, "experiments", "meta.yaml") 
    with open(metafile, "r") as f:
        data = yaml.safe_load(f)
    strings_to_check = data["structure"]["chromosomes"] 

    # perform the check
    results = check_strings_in_files(strings_to_check, files_to_check)

    # Print results nicely
    found = True
    for file, checks in results.items():
        # print(f"\nFile: {file}")
        for s, found in checks.items():
            if found:
                status = "found" 
            else:
                found = False
                status = "not found"

    if found:
        print("  All chromosomes found in all files")
    else:
        success = False
        print("  All chromosomes NOT found in all files")

    # final evaluation
    print("")
    print("Result")
    if success:
        print("  PASS")
        exit(0)
    else:
        print("  FAIL")
        exit(1)

