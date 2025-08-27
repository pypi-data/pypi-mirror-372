#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Python script for Validating Consolidated Law Texts.
Supports:
- Layer 1: Comparison of LLM output (JSON) against a Gold Standard (JSON).
- Layer 2: Amendment-centric validation using amendment text from a CSV file.

Layer 1 Performs:
1. Exact Match
2. Fuzzy Match Score (Levenshtein-based)
3. Semantic Similarity Score
4. Diff Report Generation

Layer 2 (Skeleton - Requires NLP/LLM for parsing amendment text):
1. Reads amendment text from CSV.
2. Attempts to parse amendment text into structured instructions.
3. Validates if these instructions are correctly applied in the LLM output.

JSON Law File Structure Assumption:
{
  "parsed_law": {
    "law_title_for_version": "Title of the Law",
    "structure": { // Root component (type "Law")
      "type": "Law",
      "header_text": "Optional Header",
      "number_text": "Optional Numbering",
      "body_text": "Text content",
      "children": [ /* Nested components */ ]
    }
  }
}

Required libraries:
pip install thefuzz[speedup] sentence-transformers pandas
"""

import json
import os
import re
# import difflib
import csv # For reading amendment CSV
import pandas as pd # For easier CSV handling, optional but convenient

# from thefuzz import fuzz # Uses Levenshtein Distance

# Attempt to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: sentence-transformers library not found.")
    print("Semantic similarity checks will be disabled.")
    print("To enable, install it: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    util = None

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Text Extraction from JSON (Layer 1 & for base law in Layer 2) ---

def extract_text_from_law_json_recursive(component):
    """
    Recursively extracts text from a law component and its children.
    """
    parts = []
    number_text = component.get("number_text")
    header_text = component.get("header_text")
    body_text = component.get("body_text")

    current_component_header = []
    if number_text:
        current_component_header.append(str(number_text).strip())
    if header_text:
        current_component_header.append(str(header_text).strip())

    if current_component_header:
        parts.append(" ".join(current_component_header))

    if body_text:
        parts.append(str(body_text).strip())

    children = component.get("children", [])
    for child_component in children:
        child_text = extract_text_from_law_json_recursive(child_component)
        if child_text:
            parts.append(child_text)

    return "\n".join(filter(None, parts))

def read_law_json_to_flat_text(file_path):
    """
    Reads a JSON law file and returns its full text as a single string.
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
        print(f"Error: Key 'parsed_law' not found or is not a dictionary in {file_path}")
        return None

    law_title_for_version = parsed_law_container.get("law_title_for_version", "כותרת החוק לא צוינה")
    law_structure_object = parsed_law_container.get("structure")

    if not law_structure_object or not isinstance(law_structure_object, dict):
        if parsed_law_container.get("type", "").lower() == "law": # Check if parsed_law itself is the root
            law_structure_object = parsed_law_container
        else:
            print(f"Error: 'structure' key missing or invalid under 'parsed_law' in {file_path}")
            return None

    extracted_body_text = extract_text_from_law_json_recursive(law_structure_object)
    full_text = f"{law_title_for_version}\n\n{extracted_body_text}".strip()
    return full_text

# # --- Layer 1 Validation Functions ---

# def compare_exact_match(text1, text2):
#     if text1 is None or text2 is None: return False
#     return " ".join(text1.split()) == " ".join(text2.split())

# def compare_fuzzy_match(text1, text2):
#     if text1 is None or text2 is None: return 0
#     return fuzz.ratio(text1, text2)

# def compare_semantic_similarity(text1, text2, model):
#     if not SENTENCE_TRANSFORMERS_AVAILABLE or model is None or text1 is None or text2 is None:
#         # print("Skipping semantic similarity: library/model/text missing.")
#         return 0.0
#     try:
#         embeddings = model.encode([text1, text2], convert_to_tensor=True, show_progress_bar=False)
#         cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
#         return cosine_scores.item()
#     except Exception as e:
#         print(f"Error calculating semantic similarity: {e}")
#         return 0.0

# def generate_diff_report(text1, text2, file1_name="File1", file2_name="File2"):
#     if text1 is None or text2 is None:
#         return "Error: One or both texts are missing for diff report."
#     lines1 = text1.splitlines(keepends=True)
#     lines2 = text2.splitlines(keepends=True)
#     diff = difflib.unified_diff(lines1, lines2, fromfile=file1_name, tofile=file2_name, lineterm='\n')
#     return ''.join(diff)

# --- Layer 2: Amendment-Centric Validation Functions ---

def read_amendment_text_from_csv(csv_file_path, law_name_target):
    """
    Reads amendment text from a CSV file for a specific law.
    Args:
        csv_file_path (str): Path to the CSV file.
        law_name_target (str): The name of the law (from 'Name' column in CSV)
                               to find the amendment for.
    Returns:
        str: The amendment text from 'amd1_section' column, or None if not found.
    """
    if not law_name_target:
        print("Error: law_name_target cannot be empty for CSV lookup.")
        return None
    try:
        # Using pandas for robust CSV reading, especially with Excel-generated CSVs
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        # Normalize names for comparison (optional, but good practice)
        df['Name_normalized'] = df['Name'].astype(str).str.strip()
        law_name_target_normalized = str(law_name_target).strip()

        # Find the row matching the law name
        # Ensure case-insensitivity if needed, or other normalization
        matching_rows = df[df['Name_normalized'] == law_name_target_normalized]

        if not matching_rows.empty:
            # Assuming the first match is the desired one if multiple exist
            amendment_text = matching_rows.iloc[0].get('amd1_section')
            if pd.isna(amendment_text): # Handle empty cell
                 print(f"Warning: 'amd1_section' is empty for law '{law_name_target}' in {csv_file_path}")
                 return None
            return str(amendment_text) # Ensure it's a string
        else:
            print(f"Warning: Amendment for law '{law_name_target}' not found in {csv_file_path}")
            return None
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error reading or processing CSV file {csv_file_path}: {e}")
        return None

def parse_amendment_text_to_instructions(amendment_text_str):
    """
    !!! CRITICAL PLACEHOLDER - Requires significant NLP/LLM development !!!
    Parses free-form amendment text into a list of structured instructions.
    Each instruction should be a dictionary, e.g.:
    {
        'type': 'replace' | 'add' | 'delete',
        'location_descriptor': "סעיף 2(א)(1)", // Text describing where the change occurs
        'old_text_pattern': "text to find and replace/delete", // Optional
        'new_text': "text to insert/replace with" // Optional
        'raw_instruction': "The original line from amendment text" // For reference
    }
    """
    if not amendment_text_str or not isinstance(amendment_text_str, str):
        print("Warning: No valid amendment text string provided to parse.")
        return []

    print(f"--- Attempting to parse amendment text (first 500 chars): ---\n{amendment_text_str[:500]}...\n---")
    parsed_instructions = []

    # EXAMPLE: Very basic regex for "בסעיף X(Y) במקום 'ישן' יבוא 'חדש'"
    # This is highly simplistic and will miss most real-world cases.
    # It's here for illustrative purposes ONLY.
    # A robust solution would likely involve an LLM or advanced NLP techniques.

    # Split by lines, as amendments might have multiple instructions
    for line in amendment_text_str.splitlines():
        line = line.strip()
        if not line:
            continue

        # Example 1: Simple replacement "בסעיף...במקום...יבוא..."
        # (This regex is very basic and needs to be much more robust for real use)
        replace_pattern = r"בסעיף\s+([0-9א-ת\(\)\-\"\.'\s]+?)\s+(?:קטן\s+)?([0-9א-ת\(\)\-\"\.']+)?\s*במקום\s+['\"](.*?)['\"]\s+יבוא\s+['\"](.*?)['\"]"
        replace_match = re.search(replace_pattern, line)
        if replace_match:
            location_main = replace_match.group(1).strip()
            location_sub = replace_match.group(2).strip() if replace_match.group(2) else ""
            full_location = f"סעיף {location_main} {location_sub}".strip()

            parsed_instructions.append({
                'type': 'replace',
                'location_descriptor': full_location,
                'old_text_pattern': replace_match.group(3).strip(),
                'new_text': replace_match.group(4).strip(),
                'raw_instruction': line
            })
            continue # Move to next line

        # Example 2: Simple addition "בסעיף...אחרי...יתווסף..."
        # (Also very basic)
        add_pattern = r"בסעיף\s+([0-9א-ת\(\)\-\"\.'\s]+?)\s+אחרי\s+(['\"].*?['\"]|הקטע הפותח|הרישה|ההגדרה)\s+יתווסף\s+['\"](.*?)['\"]"
        add_match = re.search(add_pattern, line)
        if add_match:
            location_main = add_match.group(1).strip()
            # 'after_what' can be used to refine insertion point if needed
            # after_what = add_match.group(2).strip()
            parsed_instructions.append({
                'type': 'add',
                'location_descriptor': f"סעיף {location_main} אחרי {add_match.group(2).strip()}",
                'new_text': add_match.group(3).strip(),
                'raw_instruction': line
            })
            continue

        # Example 3: Simple deletion "סעיף X – יימחק" or "סעיף X – בטל"
        delete_pattern = r"סעיף\s+([0-9א-ת\(\)\-\"\.'\s]+?)\s*–\s*(?:יימחק|יבוטל|בטל)"
        delete_match = re.search(delete_pattern, line)
        if delete_match:
            parsed_instructions.append({
                'type': 'delete',
                'location_descriptor': f"סעיף {delete_match.group(1).strip()}",
                'old_text_pattern': None, # Deletion might be of the whole section
                'raw_instruction': line
            })
            continue

        # If no pattern matched, add as a raw, unparsed instruction for now
        if line: # ensure it's not an empty line from split
            print(f"  INFO: Could not parse line with basic regex: '{line}'")
            # parsed_instructions.append({'type': 'unknown', 'raw_instruction': line})


    if not parsed_instructions and amendment_text_str:
        print(f"Warning: No structured instructions could be parsed from the provided amendment text using basic regex.")
    elif parsed_instructions:
        print(f"  Successfully parsed {len(parsed_instructions)} potential instruction(s) using basic regex.")

    return parsed_instructions

def find_text_in_flat_law(flat_law_text, text_to_find, is_regex=False):
    """
    Checks if a specific text (or regex pattern) exists in the flattened law text.
    Returns True if found, False otherwise.
    """
    if not flat_law_text or not text_to_find:
        return False
    if is_regex:
        return bool(re.search(text_to_find, flat_law_text))
    else:
        # Simple substring search, might need to be more sophisticated
        # (e.g., normalize whitespace, case-insensitivity)
        return text_to_find in flat_law_text

def validate_amendment_centric(original_law_flat_text, llm_output_flat_text, parsed_instructions):
    """
    Validates if parsed amendment instructions are reflected in the LLM output
    compared to the original law.
    This is a SKELETON and needs robust implementation, especially for location finding.
    """
    issues = []
    if not parsed_instructions:
        print("  Layer 2: No parsed amendment instructions to validate.")
        return issues
    if original_law_flat_text is None or llm_output_flat_text is None:
        print("  Layer 2 Error: Missing original law or LLM output text.")
        return [{"error": "Missing base law or LLM output for Layer 2."}]

    print(f"\n--- Running Layer 2 Validation ({len(parsed_instructions)} parsed instructions) ---")
    for i, instruction in enumerate(parsed_instructions):
        idx = i + 1
        instr_type = instruction.get('type', 'unknown')
        location = instruction.get('location_descriptor', 'מיקום לא ידוע')
        old_text = instruction.get('old_text_pattern')
        new_text = instruction.get('new_text')
        raw = instruction.get('raw_instruction', '')

        print(f"  Validating Instruction {idx}: [{instr_type}] at [{location}] (Raw: '{raw[:70]}...')")

        if instr_type == 'replace':
            if not old_text or not new_text:
                issues.append(f"Instruction {idx} (Replace @ {location}): Missing old_text or new_text in parsed data. Raw: {raw}")
                continue
            # Check if old text existed in original (it should)
            if not find_text_in_flat_law(original_law_flat_text, old_text):
                issues.append(f"Instruction {idx} (Replace @ {location}): Old text pattern '{old_text[:50]}...' NOT found in ORIGINAL law. Raw: {raw}")
            # Check if old text is GONE from LLM output
            if find_text_in_flat_law(llm_output_flat_text, old_text):
                issues.append(f"Instruction {idx} (Replace @ {location}): Old text pattern '{old_text[:50]}...' STILL FOUND in LLM output. Raw: {raw}")
            # Check if new text is PRESENT in LLM output
            if not find_text_in_flat_law(llm_output_flat_text, new_text):
                issues.append(f"Instruction {idx} (Replace @ {location}): New text '{new_text[:50]}...' NOT FOUND in LLM output. Raw: {raw}")

        elif instr_type == 'add':
            if not new_text:
                issues.append(f"Instruction {idx} (Add @ {location}): Missing new_text in parsed data. Raw: {raw}")
                continue
            # Check if new text is PRESENT in LLM output
            # A more robust check would verify it wasn't in the original (unless it's an addition to existing text)
            if not find_text_in_flat_law(llm_output_flat_text, new_text):
                issues.append(f"Instruction {idx} (Add @ {location}): New text '{new_text[:50]}...' NOT FOUND in LLM output. Raw: {raw}")

        elif instr_type == 'delete':
            # For deletion, old_text_pattern might be the text of the entire section to be deleted,
            # or a pattern within it. The location_descriptor is key.
            # This check is very basic: if old_text is provided, check it's gone.
            if old_text: # If specific text to delete was identified
                if not find_text_in_flat_law(original_law_flat_text, old_text):
                     issues.append(f"Instruction {idx} (Delete @ {location}): Target text pattern '{old_text[:50]}...' for deletion NOT found in ORIGINAL law. Raw: {raw}")
                if find_text_in_flat_law(llm_output_flat_text, old_text):
                    issues.append(f"Instruction {idx} (Delete @ {location}): Text pattern '{old_text[:50]}...' intended for deletion STILL FOUND in LLM output. Raw: {raw}")
            else: # If no specific old_text, this implies deleting a section by its descriptor. Harder to verify with flat text.
                # A more advanced `find_section` working on JSON would be needed here to confirm the section is gone.
                # For now, we can only check if the location descriptor itself (e.g. "סעיף 5") is still present with content.
                # This is a very weak check.
                # if find_text_in_flat_law(llm_output_flat_text, location):
                #     issues.append(f"Instruction {idx} (Delete @ {location}): Location descriptor still seems present; section might not be fully deleted. Raw: {raw}")
                print(f"  INFO: Delete instruction for '{location}' without specific old_text is hard to verify accurately with flat text. Raw: {raw}")


        elif instr_type == 'unknown':
            issues.append(f"Instruction {idx}: Could not determine action type for instruction at [{location}]. Raw: {raw}")

        # TODO: Implement more sophisticated location finding within the flat text.
        # Ideally, this layer would work with the JSON structures directly for precise location.
        # TODO: Check for unintended changes around the modification area.

    if not issues:
        print("  Layer 2: No specific issues detected based on current checks and parsed instructions.")
    return issues


# --- Main Execution Block ---
if __name__ == "__main__":
    # --- Define File Paths (UPDATE THESE) ---
    # Using the filenames from your upload as placeholders
    ORIGINAL_LAW_JSON_FILE = "חוק הגז הפחמימני המעובה_original_oldid_1010075.json"
    GOLD_STANDARD_JSON_FILE = "חוק עידוד מעורבות סטודנטים בפעילות חברתית וקהילתית_current.json"
    LLM_OUTPUT_JSON_FILE = "חוק הגז הפחמימני המעובה_amd2.json" 
    AMENDMENTS_CSV_FILE = "1amd.csv"

    # print("Starting Full Validation Script (JSON laws, CSV amendments)...")

    # # --- Load Semantic Model (once) ---
    # semantic_model = None
    # if SENTENCE_TRANSFORMERS_AVAILABLE:
    #     SEMANTIC_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
    #     try:
    #         print(f"\nLoading semantic model: {SEMANTIC_MODEL_NAME}...")
    #         semantic_model = SentenceTransformer(SEMANTIC_MODEL_NAME)
    #         print("Semantic model loaded successfully.")
    #     except Exception as e:
    #         print(f"Could not load semantic model '{SEMANTIC_MODEL_NAME}': {e}")
    #         semantic_model = None
    # else:
    #     print("\nSemantic similarity checks are disabled.")

    # --- Read Law Files (Original, LLM Output, Gold Standard) ---
    print("\nReading and extracting text from JSON law files...")
    original_law_flat_text = read_law_json_to_flat_text(ORIGINAL_LAW_JSON_FILE)
    llm_output_flat_text = read_law_json_to_flat_text(LLM_OUTPUT_JSON_FILE)
    gold_standard_flat_text = read_law_json_to_flat_text(GOLD_STANDARD_JSON_FILE)

    # # --- Layer 1 Validation ---
    # print("\n--- Running Layer 1 Validation (LLM Output vs. Gold Standard) ---")
    # if llm_output_flat_text and gold_standard_flat_text:
    #     exact_match_result = compare_exact_match(llm_output_flat_text, gold_standard_flat_text)
    #     print(f"  Exact Match (LLM vs Gold): {exact_match_result}")
    #     fuzzy_score = compare_fuzzy_match(llm_output_flat_text, gold_standard_flat_text)
    #     print(f"  Fuzzy Match Score (LLM vs Gold): {fuzzy_score:.2f}/100")
    #     semantic_score = compare_semantic_similarity(llm_output_flat_text, gold_standard_flat_text, semantic_model)
    #     print(f"  Semantic Similarity Score (LLM vs Gold): {semantic_score:.4f}")

    #     diff_report_l1 = generate_diff_report(gold_standard_flat_text, llm_output_flat_text,
    #                                           GOLD_STANDARD_JSON_FILE, LLM_OUTPUT_JSON_FILE)
    #     diff_report_file_l1 = "layer1_llm_vs_gold_diff.txt"
    #     try:
    #         with open(diff_report_file_l1, "w", encoding="utf-8") as f: f.write(diff_report_l1)
    #         print(f"  Layer 1 Diff report saved to: {diff_report_file_l1}")
    #     except Exception as e: print(f"  Error saving Layer 1 diff report: {e}")
    # else:
    #     print("  Could not perform Layer 1 validation: Missing LLM output or Gold Standard text.")

    # --- Layer 2 Validation ---
    print("\n--- Preparing for Layer 2 Validation (Amendment-Centric) ---")
    # Get the law name from the original law JSON to find it in the CSV
    original_law_title_for_csv_lookup = None
    if os.path.exists(ORIGINAL_LAW_JSON_FILE): # Check if file exists before trying to open
        try:
            with open(ORIGINAL_LAW_JSON_FILE, 'r', encoding='utf-8') as f_orig:
                original_law_data = json.load(f_orig)
                original_law_title_for_csv_lookup = original_law_data.get("parsed_law", {}).get("law_title_for_version")
                print(f"  Original law title for CSV lookup: '{original_law_title_for_csv_lookup}'")
        except Exception as e:
            print(f"Error reading original law title from {ORIGINAL_LAW_JSON_FILE} for CSV lookup: {e}")

    raw_amendment_text = None
    if original_law_title_for_csv_lookup:
        print(f"  Looking for amendment for law: '{original_law_title_for_csv_lookup}' in {AMENDMENTS_CSV_FILE}")
        raw_amendment_text = read_amendment_text_from_csv(AMENDMENTS_CSV_FILE, original_law_title_for_csv_lookup)
    else:
        print("  Skipping amendment reading from CSV: Original law title could not be determined.")

    parsed_instructions = []
    if raw_amendment_text:
        parsed_instructions = parse_amendment_text_to_instructions(raw_amendment_text)
    else:
        print("  No raw amendment text found to parse for Layer 2.")

    if original_law_flat_text and llm_output_flat_text and parsed_instructions:
        layer2_issues = validate_amendment_centric(original_law_flat_text, llm_output_flat_text, parsed_instructions)
        if layer2_issues:
            print("  Layer 2 Issues Found:")
            for issue in layer2_issues:
                print(f"    - {issue}")
        # else: # This message is now inside validate_amendment_centric
        #     print("  Layer 2: No specific issues detected based on current checks.")
    elif not parsed_instructions and raw_amendment_text :
         print("  Layer 2: Amendment text was found but could not be parsed into structured instructions by basic regex.")
    else:
        print("  Skipping Layer 2 validation due to missing data (original law, LLM output, or parsed instructions).")

    # Layers 3 and 4 would follow here, using the flattened texts and parsed instructions
    # For Layer 3 (LLM-based validation prompt):
    # validation_prompt_l3 = generate_llm_validation_prompt(original_law_flat_text, raw_amendment_text, llm_output_flat_text)
    # ... save and instruct user to run with an LLM ...

    print("\nValidation Script Finished.")
