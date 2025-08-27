import pandas as pd
import os
import re

def extract_law_names_from_csv(csv_file_path, law_name_column='Name'):
    """
    Extracts a list of unique law names from a specified column in a CSV file.

    Args:
        csv_file_path (str): The path to the CSV file.
        law_name_column (str): The name of the column containing the law names.
                               Defaults to 'Name'.

    Returns:
        list: A list of unique law names, or an empty list if an error occurs
              or the column is not found.
    """
    law_names = []
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        if law_name_column in df.columns:
            # Get unique, non-null law names and convert to list
            law_names = df[law_name_column].dropna().unique().tolist()
            print(f"Successfully extracted {len(law_names)} unique law names from column '{law_name_column}' in '{csv_file_path}'.")
        else:
            print(f"Error: Column '{law_name_column}' not found in CSV file: {csv_file_path}")
            print(f"Available columns are: {df.columns.tolist()}")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
    except Exception as e:
        print(f"An error occurred while reading or processing the CSV file: {e}")
    return law_names

def extract_law_names_from_directory(directory_path, file_extension=".json"):
    """
    Extracts law names from filenames in a specified directory.
    It tries to remove common suffixes and the file extension.

    Args:
        directory_path (str): The path to the directory containing the law files.
        file_extension (str): The file extension to filter by and remove (e.g., ".json").

    Returns:
        list: A list of unique, processed law names.
    """
    law_names = set() # Use a set to store unique names
    try:
        if not os.path.isdir(directory_path):
            print(f"Error: Directory not found at {directory_path}")
            return []

        for filename in os.listdir(directory_path):
            if filename.endswith(file_extension):
                # Remove the file extension
                name_part = filename[:-len(file_extension)]

                # Remove common suffixes or patterns
                # Order matters here if suffixes can be substrings of others
                name_part = re.sub(r'_original_oldid_\d+$', '', name_part) # e.g., _original_oldid_852368
                name_part = re.sub(r'_amd\d+$', '', name_part)             # e.g., _amd1
                name_part = re.sub(r'_current$', '', name_part)           # e.g., _current
                name_part = re.sub(r'_לחוק$', '', name_part) # Example: if there's a common suffix like this

                # Replace underscores with spaces for a more readable name (optional)
                # name_part = name_part.replace("_", " ")

                law_names.add(name_part.strip())

        unique_law_names = list(law_names)
        print(f"Successfully extracted {len(unique_law_names)} unique potential law names from directory '{directory_path}'.")
        return unique_law_names

    except Exception as e:
        print(f"An error occurred while processing the directory: {e}")
    return []



def remove_suffix_from_filenames(directory_path, suffix):
    """
    Removes a specified suffix from the end of filenames in a directory.

    Args:
        directory_path (str): The path to the directory.
        suffix (str): The suffix to remove (e.g., "_amd1.json").
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return

    print(f"Searching for files with suffix '{suffix}' in '{directory_path}'...")
    file_names = []
    for filename in os.listdir(directory_path):
        if filename.endswith(suffix):
            # old_filepath = os.path.join(directory_path, filename)
            # Construct the new filename by removing the suffix
            new_filename = filename[:-len(suffix)]
            # new_filepath = os.path.join(directory_path, new_filename)
            file_names.append(new_filename)
            # try:
            #     # Check if the target filename already exists to avoid overwriting
            #     if os.path.exists(new_filepath):
            #         print(f"Warning: Target file '{new_filename}' already exists. Skipping renaming of '{filename}'.")
            #     else:
            #         os.rename(old_filepath, new_filepath)
            #         print(f"Renamed '{filename}' to '{new_filename}'")
            # except OSError as e:
            #     print(f"Error renaming file '{filename}': {e}")
    return file_names



if __name__ == "__main__":
    # --- Scenario 1: Extract from CSV ---
    # Replace with the actual path to your CSV file
    # csv_path = "1amd.xlsx - Sheet1.csv"
    # print(f"\n--- Extracting from CSV: {csv_path} ---")
    # csv_law_names = extract_law_names_from_csv(csv_path, law_name_column='Name')
    # if csv_law_names:
    #     print("First 5 law names from CSV:")
    #     for i, name in enumerate(csv_law_names):
    #         if i < 5:
    #             print(f"  {i+1}. {name}")
    #         else:
    #             print(f"  ... and {len(csv_law_names) - 5} more.")
    #             break
    # else:
    #     print("No law names extracted from CSV or an error occurred.")

    
    # --- Usage Example ---
    # Define the directory where your JSON files are located
    # Assuming the files are in the current directory or a specific path
    target_directory = "Outputs/JSON_amd1" # Replace with the actual path if needed (e.g., "/content/your_files")
    suffix_to_remove = "_amd1.json"

    # Run the function to remove the suffix
    file_names_list = remove_suffix_from_filenames(target_directory, suffix_to_remove)
    print(file_names_list)
    # --- Scenario 2: Extract from Directory Filenames ---
    # Replace with the actual path to your directory containing JSON law files
    # For example, if your script is in the same directory as the JSON files, use "."
    # json_directory_path = "."
    # print(f"\n--- Extracting from filenames in directory: {os.path.abspath(json_directory_path)} ---")
    # dir_law_names = extract_law_names_from_directory(json_directory_path, file_extension=".json")
    # if dir_law_names:
    #     print("First 5 law names from directory filenames:")
    #     for i, name in enumerate(dir_law_names):
    #         if i < 5:
    #             print(f"  {i+1}. {name}")
    #         else:
    #             print(f"  ... and {len(dir_law_names) - 5} more.")
    #             break
    # else:
    #     print("No law names extracted from directory or an error occurred.")