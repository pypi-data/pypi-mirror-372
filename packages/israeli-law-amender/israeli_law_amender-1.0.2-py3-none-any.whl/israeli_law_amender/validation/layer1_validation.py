#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for Layer 1 Validation of consolidated law texts.
Compares an LLM-generated law (in JSON format) against a Gold Standard law (JSON format).

Performs:
1. Exact Match
2. Fuzzy Match Score (Levenshtein-based)
3. Semantic Similarity Score
4. Diff Report Generation

Assumes JSON law files have a structure like:
{
  "parsed_law": {
    "law_title_for_version": "Title of the Law",
    "structure": { // This is the root component, typically type "Law"
      "type": "Law", // Or "Section", "Clause" etc. for children
      "header_text": "Optional Header for the component",
      "number_text": "Optional Numbering for the component",
      "body_text": "Text content of this specific component",
      "children": [ // List of nested components with the same structure
        // ...
      ]
    }
    // Potentially other metadata like "law_version_id"
  }
  // Potentially other top-level keys like "schema", "extracted_metadata"
}

Required libraries:
pip install thefuzz[speedup] sentence-transformers
"""

import json
import os
import re
import difflib
from thefuzz import fuzz # Uses Levenshtein Distance for ratio calculations
import pandas as pd
from pathlib import Path


# Prevent a common warning from Hugging Face tokenizers if run in parallel
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Text Extraction from JSON ---

def extract_text_from_law_json_recursive(component):
    """
    Recursively extracts text from a law component (from the new JSON structure)
    and its children. Constructs the text in a hierarchical order.
    """
    parts = []

    # Get component attributes
    number_text = component.get("number_text")
    header_text = component.get("header_text")
    body_text = component.get("body_text")

    # Construct a representation for the current component's header/identifier
    current_component_header = []
    if number_text:
        current_component_header.append(str(number_text).strip()) # Ensure string and strip
    if header_text:
        current_component_header.append(str(header_text).strip())

    if current_component_header:
        parts.append(" ".join(current_component_header))

    # Add the main body text of the component
    if body_text:
        parts.append(str(body_text).strip()) # Ensure string and strip

    # Recursively process children
    children = component.get("children", [])
    for child_component in children:
        child_text = extract_text_from_law_json_recursive(child_component)
        if child_text:  # Only add if the child produced some text
            parts.append(child_text)

    # Join parts with a newline. Filter out empty strings that might result from empty components.
    return "\n".join(filter(None, parts))

def read_law_json_to_flat_text(file_path):
    """
    Reads a JSON law file (structured as per the user's examples) and returns its
    full text as a single continuous string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from file {file_path}. Details: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

    parsed_law_container = data.get("parsed_law")
    if not parsed_law_container or not isinstance(parsed_law_container, dict):
        print(f"Error: Key 'parsed_law' not found or is not a dictionary in JSON structure of {file_path}")
        return None

    law_title_for_version = parsed_law_container.get("law_title_for_version", "כותרת החוק לא צוינה")

    # The main law structure is expected under "parsed_law"]["structure"]
    law_structure_object = parsed_law_container.get("structure")
    if not law_structure_object or not isinstance(law_structure_object, dict):
        print(f"Error: Key 'structure' not found under 'parsed_law' or is not a dictionary in {file_path}")
        return None

    # Extract text from the main law structure
    extracted_body_text = extract_text_from_law_json_recursive(law_structure_object)

    # Combine title and body
    full_text = f"{law_title_for_version}\n\n{extracted_body_text}".strip()

    return full_text

# --- Layer 1 Validation Functions ---

def compare_exact_match(text1, text2):
    """Checks for exact match between two texts."""
    if text1 is None or text2 is None: return False
    # Normalize whitespace and strip before comparison for robustness
    return " ".join(text1.split()) == " ".join(text2.split())

def compare_fuzzy_match(text1, text2):
    """
    Returns Fuzzy Match Score (0-100) between two texts.
    fuzz.ratio uses Levenshtein Distance.
    """
    if text1 is None or text2 is None: return 0
    return fuzz.ratio(text1, text2)


def generate_diff_report(text1, text2, file1_name="GoldStandardFile", file2_name="LLMOutputFile"):
    """Generates a diff report between two texts."""
    if text1 is None or text2 is None:
        return "Error: One or both texts are missing for diff report."

    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile=file1_name,
        tofile=file2_name,
        lineterm='\n'
    )
    return ''.join(diff)

def generate_html_diff_report(text1, text2, file1_name="Gold Standard", file2_name="LLM Output"):
    """
    Generates a visually appealing HTML diff report between two texts.
    Uses difflib.HtmlDiff for side-by-side comparison with inline differences highlighted.
    """
    if text1 is None or text2 is None:
        return "<html><body><p>Error: One or both texts are missing for HTML diff report.</p></body></html>"

    lines1 = text1.splitlines() # HtmlDiff expects lists of lines without newlines
    lines2 = text2.splitlines()

    # Create an HtmlDiff object
    # charade=True enables character-by-character comparison within lines
    # wrapcolumn=70 can wrap long lines, adjust as needed or remove
    differ = difflib.HtmlDiff(wrapcolumn=70)

    # make_file generates a complete HTML document
    # context=True means it shows context lines around changes
    html_diff = differ.make_file(lines1, lines2, fromdesc=file1_name, todesc=file2_name, context=True)

    return html_diff

# --- Layer 1 Validation Script ---
def layer_1_execute_validation(LAW_NAME, number_of_amd=1):
    json_laws_v2_path = Path("Data") / "JSON_Laws_v2"    
    GOLD_STANDARD_JSON_FILE = find_gold_standard_json_file(LAW_NAME, current_json_dir=json_laws_v2_path)
    print(f"Gold Standard JSON File: {GOLD_STANDARD_JSON_FILE}")
    LLM_OUTPUT_JSON_FILE = f"Outputs/JSON_amd1/{LAW_NAME}_amd1.json"

    print("Starting Layer 1 Validation Script (JSON input)...")
    print(f"LLM Output JSON: {LLM_OUTPUT_JSON_FILE}")
    print(f"Gold Standard JSON: {GOLD_STANDARD_JSON_FILE}")

    # --- Read and Extract Text from JSON Law Files ---
    # print("\nReading and extracting text from JSON files...")
    llm_output_flat_text = read_law_json_to_flat_text(LLM_OUTPUT_JSON_FILE)
    gold_standard_flat_text = read_law_json_to_flat_text(GOLD_STANDARD_JSON_FILE)

    if llm_output_flat_text is None or gold_standard_flat_text is None:
        print("Critical Error: Could not extract text from one or both JSON files. Aborting Layer 1 validation.")
    else:
        # print(f"Successfully extracted text. LLM output length: {len(llm_output_flat_text)} chars, Gold standard length: {len(gold_standard_flat_text)} chars.")

        # --- Perform Layer 1 Validations ---
        # print("\n--- Running Layer 1 Validation Metrics ---")

        # 1. Exact Match
        exact_match_result = compare_exact_match(llm_output_flat_text, gold_standard_flat_text)
        # print(f"  Exact Match: {exact_match_result}")

        # 2. Fuzzy Match Score (Levenshtein-based)
        fuzzy_score = compare_fuzzy_match(llm_output_flat_text, gold_standard_flat_text)
        # print(f"  Fuzzy Match Score (Levenshtein-based): {fuzzy_score:.2f}/100")

        # 3. Generate Diff Report
        # print("\n  Generating Diff Report...")
        # Using actual filenames in the diff header for clarity
        diff_report_output = generate_diff_report(gold_standard_flat_text, llm_output_flat_text,
                                                  str(GOLD_STANDARD_JSON_FILE), LLM_OUTPUT_JSON_FILE)
        
        # Define the directory and filename
        formated_law_name = LAW_NAME.replace(" ", "_")  # Replace spaces with underscores for filename
        output_directory_amd = f"diff_reports/amd{number_of_amd}"
        output_directory_amd_folder_path = os.path.join(os.path.dirname(__file__), "..", "..", "Outputs", output_directory_amd)
        if not os.path.exists(output_directory_amd_folder_path):
            print(f"Creating output directory: {output_directory_amd_folder_path}")

        # Ensure the output directory exists
        # output_directory = os.path.join(output_directory_amd, formated_law_name)
        diff_report_filename = f"layer1_validation_diff_report_{formated_law_name}.txt"
        diff_report_file_path = os.path.join(output_directory_amd_folder_path, diff_report_filename)
        
        # Create the directory if it doesn't exist
        os.makedirs(output_directory_amd_folder_path, exist_ok=True)

        html_diff_report_filename = f"layer1_validation_html_diff_report_{formated_law_name}.html"
        html_diff_report_file_path = os.path.join(output_directory_amd_folder_path, html_diff_report_filename)
        # HTML diff report
        html_diff_output = generate_html_diff_report(
            gold_standard_flat_text, llm_output_flat_text,
            f"Gold Standard: {os.path.basename(GOLD_STANDARD_JSON_FILE)}",
            f"LLM Output: {os.path.basename(LLM_OUTPUT_JSON_FILE)}"
        )

        try:
            with open(html_diff_report_file_path, "w", encoding="utf-8") as f:
                f.write(html_diff_output)
            print(f"HTML diff report saved to: {html_diff_report_file_path}")
        except Exception as e:
            print(f"Error saving HTML diff report: {e}")


        # print("\n  Generating Diff Report...")

        try:
            with open(diff_report_file_path, "w", encoding="utf-8") as f:
                f.write(diff_report_output)
            # print(f"  Diff report saved to: {diff_report_file_path}")

        except Exception as e:
            print(f"  Error saving diff report: {e}")
        
        finally:
            return {
                "exact_match": exact_match_result, "fuzzy_score": fuzzy_score,
                "diff_report_file": diff_report_file_path, "html_diff_report_file": html_diff_report_file_path}



def remove_suffix_from_filenames(directory_path, suffix):
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return

    # print(f"Searching for files with suffix '{suffix}' in '{directory_path}'...")
    file_names = []
    for filename in os.listdir(directory_path):
        if filename.endswith(suffix):
            new_filename = filename[:-len(suffix)]
            file_names.append(new_filename)
           
    return file_names


def sanitize_filename_component(name_part):
    """Sanitizes a string component to be part of a filename."""
    # Replace problematic characters with underscores or remove them
    name_part = name_part.replace('"', '_') # Handle double quotes from CSV
    name_part = name_part.replace("'", '_')
    name_part = name_part.replace('/', '_')
    name_part = name_part.replace('\\', '_')
    name_part = name_part.replace(':', '_')
    name_part = name_part.replace('*', '_')
    name_part = name_part.replace('?', '_')
    name_part = name_part.replace('<', '_')
    name_part = name_part.replace('>', '_')
    name_part = name_part.replace('|', '_')
    # Replace multiple underscores with a single one
    name_part = re.sub(r'_+', '_', name_part)
    # Remove leading/trailing underscores
    name_part = name_part.strip('_')
    return name_part


def find_gold_standard_json_file(law_name_csv, current_json_dir):
    """
    Finds the gol standard JSON law file based on the law name from the CSV.
    Assumes filenames in JSON_Laws_v2/ are like:
    [Base Law Name]_current_LawID_[SOME_ID].json
    where [Base Law Name] corresponds to the part of law_name_csv before the first comma.
    """
    if not law_name_csv:
        print("Error: law_name_csv is empty or None.")
        return None

    print(f"Searching for Gold Standard JSON file for law name: {law_name_csv} in directory: {current_json_dir}")
    for f_path in current_json_dir.iterdir():
        if f_path.is_file() and f_path.suffix.lower() == '.json':

            file_name_stem = f_path.stem # Gets "חוק לצמצום השימוש במזומן_current_LawID_816623"
            if "_current_LawID_" in file_name_stem:
                file_base_name_parts = file_name_stem.split("_current_LawID_", 1)
                file_base_name = sanitize_filename_component(file_base_name_parts[0].strip())
  
                if file_base_name == law_name_csv:
                    return f_path
            # Fallback: if the "_current_LawID_" part is missing, try a simpler match (less likely)
            elif sanitize_filename_component(file_name_stem) == law_name_csv:
                 return f_path

    print(f"Error: No matching Gold Standard JSON file found for law name '{law_name_csv}' in directory '{current_json_dir}'.")
    return None


# --- Main Execution Block ---
def main():
    for i in range(1, 5):
        # --- Define File Paths (UPDATE THESE TO YOUR ACTUAL FILE PATHS) ---

        # Using the filenames you uploaded as placeholders.
        # Ensure these files are in the same directory as the script, or provide full paths.
        target_directory = f"Outputs/JSON_amd{i}"
        suffix_to_remove = f"_amd{i}.json"
    
        # # Ensure the target directory exists
        if not os.path.exists(target_directory):
            print(f"stop runing the code for layer 1 validation, we do not have laws with {i} amd. If we do, please check the following path: {target_directory}")
            print(f"Error: Target directory '{target_directory}' does not exist.")
            print("Stopping Layer 1 validation script execution.")
            break
        print(f"Target directory: {target_directory}")
        print(f"\n--- Starting Layer 1 Validation for laws with {i} amendments ---")


        # Run the function to remove the suffix
        law_names_list = remove_suffix_from_filenames(target_directory, suffix_to_remove)

        layer_1_validation_dict = {}
        for law_name in law_names_list:
            print(f"\nStarting validation for law: {law_name}")
            law_layer_1_validation = layer_1_execute_validation(law_name, number_of_amd=i)
            if law_layer_1_validation:
                layer_1_validation_dict[law_name] = law_layer_1_validation
                print(f"Validation for {law_name} completed successfully.")
            else:
                print(f"Validation for {law_name} failed or was skipped due to errors.")

        print(layer_1_validation_dict)
        laws_layer_1_validation_df = pd.DataFrame.from_dict(layer_1_validation_dict, orient='index')
        folder_path = os.path.join(os.path.dirname(__file__), "layer1_validation_summary")
        os.makedirs(folder_path, exist_ok=True)  
        csv_file_path = os.path.join(folder_path, f"layer1_validation_results_amd{i}.csv")
        laws_layer_1_validation_df.to_csv(csv_file_path, encoding='utf-8-sig')
        print(laws_layer_1_validation_df)
        print(f"\nLayer 1 Validation Script Finished for amd {i}.")
    print("\nLayer 1 Validation Script Finished.")

if __name__ == "__main__":
    main()

