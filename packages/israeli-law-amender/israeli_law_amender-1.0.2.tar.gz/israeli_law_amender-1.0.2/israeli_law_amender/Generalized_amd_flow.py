import csv
import json
import os
import re
import time
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError, DeadlineExceeded
from pathlib import Path
import argparse
import sys
import io
from .logger import setup_summary_logger, log_amendment_result


# --- Configuration ---
# Default paths (can be overridden by configure_paths function)
CSV_FILE_PATH = Path("Data") / "amd2_sections.csv"
ORIGINAL_JSON_DIR = Path("Data") / "JSON_Laws_v2"
AMENDED_JSON_DIR = Path("Outputs") / "JSON_amd1"
GENERATED_SCRIPTS_DIR = Path("Outputs") / "Generated_Scripts_Generalized" # New directory for generated .py scripts
API_RETRY_LIMIT = 3
API_RETRY_DELAY_SECONDS = 10 # Initial delay, will increase
GEMINI_MODEL_NAME = "models/gemini-2.5-flash-preview-05-20" # Ensure this is the correct and available model

MAX_SCRIPT_GENERATION_ATTEMPTS_PER_EXECUTION = 3 # Max attempts to get a valid script from LLM for a row
MAX_EXECUTION_ATTEMPTS_PER_AMD = 2       # Max attempts to execute a generated script for a row

MAX_OUTPUT_TOKENS = 32768
MODEL_TEMP = 0.1

def configure_training_paths(training_paths):
    """
    Configure the global path variables from training_paths dictionary.
    
    Args:
        training_paths: Dictionary containing configured paths for training mode
    """
    global CSV_FILE_PATH, ORIGINAL_JSON_DIR, AMENDED_JSON_DIR, GENERATED_SCRIPTS_DIR
    
    if training_paths:
        CSV_FILE_PATH = training_paths['amendments_data_dir'] / "amd2_sections.csv"
        ORIGINAL_JSON_DIR = training_paths['original_laws_dir']
        AMENDED_JSON_DIR = training_paths['amended_output_dir'] / "JSON_amd1"
        GENERATED_SCRIPTS_DIR = training_paths['generated_scripts_dir']

# --- Helper Functions ---

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

def find_original_json_file(law_name_csv, original_json_dir):
    """
    Finds the original JSON law file based on the law name from the CSV.
    Assumes filenames in JSON_Laws_v2/ are like:
    [Base Law Name]_original_oldid_[SOME_ID].json
    where [Base Law Name] corresponds to the part of law_name_csv before the first comma.
    """
    if not law_name_csv:
        return None

    # Extract the base name (part before the first comma, which usually contains the year/designation)
    base_name_csv_parts = law_name_csv.split(',', 1)
    base_name_csv_part_raw = base_name_csv_parts[0].strip()

    # Define regex patterns for year removal
    year_pattern_hebrew = r'(?u)(?:התש|תש)[א-ת]{2}(?:["״׳]{1,2}[א-ת])?(?:-\d{4})?$'
    year_pattern_numeric = r'\b(19|20)\d{2}$'

    # Remove year patterns from the end of the base name
    cleaned_base_name_csv_part = re.sub(year_pattern_hebrew, '', base_name_csv_part_raw).strip()
    cleaned_base_name_csv_part = re.sub(year_pattern_numeric, '', cleaned_base_name_csv_part).strip()
    cleaned_base_name_csv_part = cleaned_base_name_csv_part.rstrip(',- ') # Final cleanup of trailing chars

    base_name_csv = sanitize_filename_component(cleaned_base_name_csv_part)

    # print(f"Searching for original JSON. Raw CSV base part: '{base_name_csv_part_raw}', Cleaned then Sanitized: '{base_name_csv}'")

    for f_path in original_json_dir.iterdir():
        if f_path.is_file() and f_path.suffix.lower() == '.json':
            # Extract the base part of the filename in the directory
            # Example: "חוק לצמצום השימוש במזומן_original_oldid_816623.json"
            # We want "חוק לצמצום השימוש במזומן"
            file_name_stem = f_path.stem # Gets "חוק לצמצום השימוש במזומן_original_oldid_816623"
            if "_original_oldid_" in file_name_stem:
                file_base_name_parts = file_name_stem.split("_original_oldid_", 1)
                file_base_name = sanitize_filename_component(file_base_name_parts[0].strip())

                # print(f"  Comparing with file base: '{file_base_name}' from '{f_path.name}'")
                if file_base_name == base_name_csv:
                    # print(f"  Found matching file: {f_path.name}")
                    return f_path
            
            # Fallback: if the "_original_oldid_" part is missing, try a simpler match (less likely)
            elif sanitize_filename_component(file_name_stem) == base_name_csv:
                #  print(f"  Found matching file (simple stem): {f_path.name}")
                 return f_path

    # print(f"  No matching file found for base name: '{base_name_csv}' in {original_json_dir}")
    return None

def generate_llm_prompt(original_json_file_path_str, amendment_text, output_json_file_path_str):
    """
    Generates the prompt for the LLM.
    """
    # Read the original JSON content
    try:
        with open(original_json_file_path_str, 'r', encoding='utf-8') as f:
            original_json_content = f.read()
    except Exception as e:
        return f"Error reading original JSON: {e}" # This should not happen if find_original_json_file worked

    prompt = f"""
    You are an expert in Israeli Law and Python code.
    Your task is to generate a Python script that will amend an original Israeli law JSON file according to specific amendment instructions.

    **Instructions for the Python Script You Will Generate:**

    1.  The script must define a primary Python function called `apply_amendments_to_data`. This function will perform the core amendment logic.
        *   **Function Signature:** `def apply_amendments_to_data(law_data_dictionary, amendment_text_string):`
        *   **Parameters:**
            *   `law_data_dictionary` (dict): The Python dictionary representing the parsed JSON of the original law.
            *   `amendment_text_string` (str): The string containing the specific amendment instructions.
        *   **Behavior:** The function must apply ONLY the changes specified in the `amendment_text_string` to the `law_data_dictionary`.
            It should modify the dictionary structure or values carefully, preserving the existing schema as much as possible unless an addition/deletion is explicitly part of the amendment.
        *   **Return Value:** The function MUST return the modified Python dictionary.
        *   **Important:** This function should NOT perform any file input/output operations (e.g., reading from files or writing to files).

    2.  The script must also include a standard `if __name__ == "__main__":` block to make it runnable as a standalone script for testing or direct use.
        *   This `__main__` block should use the `argparse` module to accept two command-line arguments:
            *   `original_file_path`: Path to the input JSON law file.
            *   `output_file_path`: Path where the amended JSON law file should be saved.
        *   Inside the `__main__` block, the script should:
            *   Load the JSON data from `original_file_path` into a Python dictionary.
            *   Call the `apply_amendments_to_data` function, passing the loaded dictionary and the specific "AMENDMENT TEXT" (provided below in this prompt) to it.
            *   Take the dictionary returned by `apply_amendments_to_data` and save it as a JSON to the `output_file_path`, ensuring UTF-8 encoding and human-readable indentation.

    3.  The script should include necessary imports (e.g., `json`, `re`, `argparse`).
    4.  The script should be self-contained and runnable.
    5.  The `apply_amendments_to_data` function should handle potential errors gracefully (e.g., if a section mentioned in the amendment is not found in the JSON, comment a warning but try to continue if other amendments are independent).

    **Thinking Process (IMPORTANT):**
    Before generating the Python code, please outline your step-by-step thought process or plan for how you will approach generating the script to apply the specified "Amendment Text" to the "Original Law JSON File Content".
    Enclose this thought process within `<thinking>...</thinking>` tags. This section is for your reasoning and will not be part of the executable code.

    **Python Code Block (CRITICAL):**
    After your thought process, your response MUST then contain ONLY the Python code for the script.
    Do not include any explanations, greetings, or any other text outside the `<thinking>...</thinking>` block and the Python code block.
    Start the Python code block with `--- START OF PYTHON CODE ---` and end it with `--- END OF PYTHON CODE ---`.

    **Original Law JSON File Content:**
    ```json
    {original_json_content}
    ```

    **AMENDMENT TEXT (this is the text your generated `apply_amendments_to_data` function will receive as its second argument, and your generated `__main__` block should use when calling it):**
    ```text
    {amendment_text}
    ```

    The Python script you generate will be used by a calling script (`trial.py`) as follows: The calling script will load the original JSON into a dictionary. It will then dynamically execute your generated script to make the `apply_amendments_to_data` function available. Finally, it will call `your_generated_module.apply_amendments_to_data(loaded_dictionary, amendment_text_string)` and save the returned dictionary.

    Your generated `if __name__ == "__main__":` block is for standalone execution of your script.

    Example of how the `apply_amendments_to_data` function might be structured (adapt this pattern for the *actual* amendment_text and original_json_content):

    ```python
    # --- START OF PYTHON CODE ---
    import json
    import re
    import argparse # Make sure to include this

    def apply_amendments_to_data(law_data_dictionary, amendment_text_string):
        # IMPORTANT: Work with law_data_dictionary and amendment_text_string
        # Apply changes based on amendment_text_string to law_data_dictionary
        # For example, if amendment_text_string was: "In section 1, change X to Y"
        #   section_to_change = find_section_in_dict(law_data_dictionary, "1")
        #   if section_to_change:
        #       section_to_change["text"] = section_to_change["text"].replace("X", "Y")
        #   else:
        #       print("Warning: Section 1 not found in dictionary")
        
        # --- YOUR DETAILED AMENDMENT LOGIC BASED ON THE 'AMENDMENT TEXT' AND THE STRUCTURE OF 'law_data_dictionary' GOES HERE ---
        # Remember to modify law_data_dictionary and then return it.
        
        # Placeholder - replace with your actual logic:
        print(f"apply_amendments_to_data would process the dictionary based on: {{amendment_text_string[:50]}}...")
        # law_data_dictionary["some_key"] = "new_value" # Example modification

        return law_data_dictionary

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Apply specific amendments to a law JSON file.')
        parser.add_argument('original_file_path', type=str, help='Path to the original law JSON file.')
        parser.add_argument('output_file_path', type=str, help='Path to save the amended law JSON file.')
        # The amendment_text is known at generation time from the prompt, so the __main__ block will use that directly.

        args = parser.parse_args()

        # Use repr() to safely embed the amendment_text as a string literal in the generated code
        amendment_details_for_main = {repr(amendment_text)}

        try:
            with open(args.original_file_path, 'r', encoding='utf-8') as f:
                current_law_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Original file not found at {{args.original_file_path}}")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {{args.original_file_path}}")
            exit(1)

        modified_data = apply_amendments_to_data(current_law_data, amendment_details_for_main)

        try:
            with open(args.output_file_path, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=2)
            print(f"Successfully amended law saved to {{args.output_file_path}}")
        except IOError:
            print(f"Error writing amended file to {{args.output_file_path}}")
            exit(1)

    # --- END OF PYTHON CODE ---
    ```
    Now, based on the "Original Law JSON File Content" and the specific "AMENDMENT TEXT" provided above, generate the complete Python script including the `apply_amendments_to_data` function and the `if __name__ == "__main__":` block.
    Remember the `apply_amendments_to_data` function must return the modified dictionary.
    The script will be used with original file path "{original_json_file_path_str}" and save to "{output_json_file_path_str}" when run standalone.
    """
    return prompt

def call_gemini_api(parts: list[str], model) -> dict:
    """
    Calls Gemini API with retries on rate limits (429) and other transient errors.
    Always returns a dict:
      { "text": <str or None>,
        "input_tokens": <int>,
        "output_tokens": <int>,
        "error": <str or None> }
    """

    response = None
    input_tokens = 0
    output_tokens = 0
    current_delay = API_RETRY_DELAY_SECONDS

    # Build the model handle once per call

    for attempt in range(1, API_RETRY_LIMIT + 1):
        try:
            response = model.generate_content(contents=parts)
            # Pull out usage_metadata if present
            if hasattr(response, "usage_metadata"):
                input_tokens  = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            # Check finish_reason on the first (and usually only) candidate
            if response.candidates:
                fr = response.candidates[0].finish_reason.name
                # print(f"Gemini finish reason: {fr}")
                if fr == "SAFETY":
                    return {
                        "text": None,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "error": "SAFETY_BLOCK"
                    }
                elif fr not in ("STOP", "UNSPECIFIED"):
                    return {
                        "text": None,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "error": f"UNEXPECTED_FINISH_REASON: {fr}"
                    }

            # If we reach here, we have a good response
            return {
                "text": response.text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "error": None
            }

        except ResourceExhausted as re_err:
            # print(f"▶️ ResourceExhausted: {re_err}")
            # Rate limit (429). Look for server‐suggested retry_delay
            retry_delay_secs = re_err.retry_delay.seconds if hasattr(re_err, "retry_delay") and hasattr(re_err.retry_delay, "seconds") else current_delay
            if attempt < API_RETRY_LIMIT:
                time.sleep(retry_delay_secs)
                continue
            else:
                return {
                    "text": None,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "error": "QUOTA_EXHAUSTED"
                }

        except (DeadlineExceeded, GoogleAPIError) as err:
            label = "DEADLINE_EXCEEDED" if isinstance(err, DeadlineExceeded) else f"GAPI_ERROR: {err}"
            # print(f"▶️ {err.__class__.__name__}: {err}")
            if attempt < API_RETRY_LIMIT:
                # print(f"  Retrying in {current_delay} sec…")
                time.sleep(current_delay)
                current_delay *= 2
                continue
            return {"text": None, "input_tokens": input_tokens,
                    "output_tokens": output_tokens, "error": label}


        except Exception as ex:
            if attempt < API_RETRY_LIMIT:
                # print(f"  Retrying in {current_delay} sec…")
                time.sleep(current_delay)
                current_delay *= 2
                continue
            # print(f"▶️ Unexpected exception: {ex}")
            return {
                "text": None,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "error": f"UNEXPECTED: {ex}"
            }
    # print("▶️ Error: Gemini API call failed after retries.")
    # If we somehow exit the loop without returning, treat as a total failure
    # print("Error: Gemini API call failed after retries.")
    return {
        "text": None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "error": "API_RETRIES_EXHAUSTED"
    }

def extract_python_code(llm_response_text):
    """Extracts the Python code block from the LLM's response."""
    if not llm_response_text:
        return None

    match = re.search(r"--- START OF PYTHON CODE ---(.*)--- END OF PYTHON CODE ---", llm_response_text, re.DOTALL)
    if match:
        code = match.group(1).strip()
        # Basic check to ensure it's not just whitespace or placeholder comments
        if len(code.splitlines()) > 5: # Arbitrary threshold for "real" code
            return code
        else:
            # print("Warning: Extracted code block seems too short or empty.")
            return None
    else:
        # print("Error: Could not find Python code markers in LLM response.")
        # print("LLM Response was:\n", llm_response_text[:1000] + "..." if len(llm_response_text) > 1000 else llm_response_text)
        return None

def execute_generated_code(code_string, original_json_path, output_json_path, amendment_text_for_script):
    """
    Executes the generated Python code string.
    The generated code is expected to define a function `apply_amendments_to_data`.
    """
    try:
        # Create a single scope for exec, acting as both globals and locals for the script
        execution_scope = {}
        execution_scope["__name__"] = "__generated_script__" # Prevent generated __main__ from running
        # Add modules/functions the generated script might need
        execution_scope["json"] = json
        execution_scope["re"] = re
        execution_scope["os"] = os
        execution_scope["Path"] = Path
        execution_scope["argparse"] = argparse
        # Add any other necessary built-ins or custom helper functions if they are
        # expected to be globally available to the executed script (not the case here yet)
        # Execute the generated code string.
        # Functions defined in code_string will be added to execution_scope.
        exec(code_string, execution_scope, execution_scope) 

        amendment_function_name = "apply_amendments_to_data"
        
        if amendment_function_name in execution_scope and callable(execution_scope[amendment_function_name]):
            # print(f"Attempting to use generated function: {amendment_function_name}")
            
            original_data_dict = None
            try:
                with open(original_json_path, 'r', encoding='utf-8') as f:
                    original_data_dict = json.load(f)
            except Exception as e_load:
                useless_var_here_only_to_avoid_printing = True
                # print(f"Error loading original JSON {original_json_path} into dictionary for function call: {e_load}")
                # Don't return False yet, allow fallback to __main__ check

            if original_data_dict is not None:
                try:
                    # print(f"Calling {amendment_function_name} with data dictionary and amendment text.")
                    modified_data_dict = execution_scope[amendment_function_name](original_data_dict, amendment_text_for_script)
                    
                    if isinstance(modified_data_dict, dict):
                        with open(output_json_path, 'w', encoding='utf-8') as f_out:
                            json.dump(modified_data_dict, f_out, ensure_ascii=False, indent=2)
                        # print(f"Generated function {amendment_function_name} executed and output saved to {output_json_path.name}.")
                        return True # Success via function call
                    else:
                        # print(f"Error: Generated function {amendment_function_name} did not return a dictionary.")
                        # Fall through to __main__ check if function didn't behave as expected
                        useless_var_here_only_to_avoid_printing = True
                except Exception as e_call_func:
                    # print(f"Error during call to or processing result from {amendment_function_name}: {e_call_func}")
                    # traceback.print_exc()
                    useless_var_here_only_to_avoid_printing = True

        # If we reached here, the preferred function call path either failed or was skipped.
        # Now, check if the generated script's __main__ block might have created the file.
        # print(f"Preferred function call path for '{amendment_function_name}' did not complete successfully. Checking for file creation by generated script's __main__.")
        if output_json_path.exists() and output_json_path.stat().st_size > 0:
            # print(f"Output file {output_json_path.name} was created and is not empty. Assuming direct execution by generated script's __main__ was successful.")
            return True
        else:
            # print(f"Output file {output_json_path.name} does not exist or is empty after attempting function call and checking for __main__ execution.")
            return False

    except Exception as e_exec_outer:
        # print(f"Outer error during execution of generated code for {original_json_path.name}: {e_exec_outer}")
        # traceback.print_exc()
        return False

def main():
    """Implement all amendments of all laws:\n
    Iterate over all rows in amd_descriptions.csv\n
    Per row, attempt to implement every amendment\n
    Every amendment has 2* execution attempts (*MAX_EXECUTION_ATTEMPTS_PER_ROW)\n
    Every execution attempt includes 3* generation attempts (*MAX_SCRIPT_GENERATION_ATTEMPTS_PER_ROW)"""

    # =================================================================
    # Part 1 - Define main measuring parameters 
    # =================================================================
    script_start_time = time.time()
    total_input_tokens  = total_output_tokens = 0
    total_api_time_sec  = successful_api_calls = failed_api_calls = 0
    amds_ok = failed_code_generations = failed_amendment_executions   = 0
    rows_succeeded = 0
    rows_failed = 0
    amendments_succeeded = 0
    amendments_failed = 0
    GENERATED_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    # =================================================================
    # Part 2 - Attempt to open general tools 
    # =================================================================
    if not CSV_FILE_PATH.exists():
        print(f"⚠️ MAIN ERROR: Amendments Data CSV file not found at {CSV_FILE_PATH}")
        return

    if not ORIGINAL_JSON_DIR.exists():
        print(f"⚠️ MAIN ERROR: Laws JSON directory not found at {ORIGINAL_JSON_DIR}")
        return
    
    try:
        summary_logger = setup_summary_logger()
    except Exception as e:
        print(f"⚠️ MAIN ERROR: logger initialization failure:\n{e}")
        return
    
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        rows_data = list(csv.DictReader(f))
    
    # =================================================================
    # Part 3 - First loop - iterate on rows
    # =================================================================

    total_rows = len(rows_data)
    start_row=1
    end_row=total_rows
    rows=rows_data[start_row-1:end_row]

    for row_idx, row in enumerate(rows, start=start_row):
        # --------------------------
        # ---- assign row parameters
        law_name      = row.get("Name", "").strip()
        fixing_law_id = row.get("FixingLawID", "unknown").strip()
        failure_reasons = []
        print(f"\n=== Row {row_idx}/{total_rows} • {law_name or '??'} (FixingLawID: {fixing_law_id}) ===")
        
        # --------------------------------
        # ---- gather this row's JSON file 
        if not law_name:
            print("⚠️ LAW ERROR - SKIPPING LAW")
            failure_reasons.append("failure in main() - missing law_name")
            log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=0, success=False,reasons=failure_reasons)
            rows_failed += 1
            continue
        
        original_json_path = find_original_json_file(law_name, ORIGINAL_JSON_DIR)
        if not original_json_path:
            print("⚠️ LAW ERROR - SKIPPING LAW")
            failure_reasons.append(f"failure in main() - original JSON not found in {ORIGINAL_JSON_DIR}")
            log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=0, success=False,reasons=failure_reasons)
            rows_failed += 1
            continue
        
        # ----------------------------------------
        # ---- gather this row’s amendment columns 
        amendment_cols = sorted([c for c in row if re.fullmatch(r"amd\d+_section", c) and row[c].strip()],key=lambda c: int(re.findall(r"\d+", c)[0]))
        if not amendment_cols:
            print("⚠️ LAW ERROR - SKIPPING LAW")
            failure_reasons.append(f"failure in main() - no amendments found in CSV")
            log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=0, success=False,reasons=failure_reasons)
            rows_failed += 1
            continue
        
        # ----------------------------------------------
        # ---- filename stem for all outputs of this law
        stem = (original_json_path.stem.split("_original_oldid_", 1)[0] if "_original_oldid_" in original_json_path.stem else original_json_path.stem)
        prev_version_path = original_json_path

        # =================================================================
        # Second loop - iterate on amendments per row
        # =================================================================
        for idx, col in enumerate(amendment_cols, start=1):
            # --------------------------------
            # ---- assign amendment parameters
            amendment_text = row[col].strip()
            print(f"  → Amendment #{idx}: {col}")
            out_dir  = Path("Outputs") / f"JSON_amd{idx}"
            out_dir.mkdir(exist_ok=True)
            amended_json_path = out_dir / f"{stem}_amd{idx}.json"

            # ----------------------------------
            # ---- GENERATE PROMPT PER AMENDMENT
            prompt = generate_llm_prompt(str(prev_version_path),amendment_text,str(amended_json_path))

            if "Error reading original JSON" in prompt:
                print(f"  → ⚠️ AMENDMENT #{idx} ERROR - SKIPPING AMENDMENT")
                failure_reasons.append(f"failure in generate_llm_prompt() - error with opening original json file: {str(prev_version_path)}")
                log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=idx, success=False,reasons=failure_reasons)
                amendments_failed += 1
                continue

            # =================================================================
            # Third loop - Iterate on execution attempts per amendment
            # =================================================================
            generated_code              = None
            code_executed_successfully  = False

            for amendment_execution_attempt in range(MAX_EXECUTION_ATTEMPTS_PER_AMD):
                # =================================================================
                # Fourth loop - Iterate on generation attempts per execution
                # =================================================================
                exec_time = time.time()
                formatted_exec_time = time.strftime("%H:%M", time.localtime(exec_time))
                print(f"     → beginning execution attempt {amendment_execution_attempt+1}/{MAX_EXECUTION_ATTEMPTS_PER_AMD}.")
                
                for script_generation_attempt in range(MAX_SCRIPT_GENERATION_ATTEMPTS_PER_EXECUTION):
                    # --------------------------------------------------
                    # ---- ATTEMPT TO CALL API, RECORD GEN TIME & TOKENS
                    t0 = time.time()
                    formatted_time = time.strftime("%H:%M", time.localtime(t0))
                    print(f"        → attempting generation {script_generation_attempt+1}/{MAX_SCRIPT_GENERATION_ATTEMPTS_PER_EXECUTION} at: {formatted_time}")
                    llm_resp = call_gemini_api(prompt)
                    api_dur  = time.time() - t0
                    total_api_time_sec  += api_dur
                    total_input_tokens  += llm_resp.get("input_tokens", 0)
                    total_output_tokens += llm_resp.get("output_tokens", 0)

                    # --------------------------------------
                    # ---- API CALLING FAILED - LOG & REPEAT
                    if llm_resp["error"]:
                        failed_api_calls += 1
                        failure_reasons.append(f"failure in call_gemini_api() - {llm_resp["error"]} [AMD #{idx}, EXEC #{amendment_execution_attempt+1}, GEN #{script_generation_attempt+1}]")
                        log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=idx, success=False,reasons=failure_reasons)
                        if script_generation_attempt < MAX_SCRIPT_GENERATION_ATTEMPTS_PER_EXECUTION-1:
                            time.sleep(API_RETRY_DELAY_SECONDS / 2)
                        continue
                    
                    # -----------------------------------------
                    # ---- API CALLING SUCCEEDED - EXTRACT CODE
                    successful_api_calls += 1
                    generated_code = extract_python_code(llm_resp["text"])
                    if generated_code:
                        gen_code_path     = GENERATED_SCRIPTS_DIR / f"{stem}_amd{idx}_generated_exec{amendment_execution_attempt}.py"
                        with open(gen_code_path, 'w', encoding='utf-8') as f:
                            f.write(generated_code)
                        break  # exit code generation loop

                # if all code generation attempts weren't fruitful - proceed to next execution attempt
                if not generated_code:
                    failed_code_generations += 1
                    print(f"     → execution attempt {amendment_execution_attempt+1}/{MAX_EXECUTION_ATTEMPTS_PER_AMD} did not succeed.")
                    continue

                # if code generation was successful at any of the execution attempts - try to execute the generated code
                # Save the generated code to disk
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
                try:
                    code_executed_successfully = execute_generated_code(
                        generated_code,
                        prev_version_path,
                        amended_json_path,
                        amendment_text
                    )
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                # if code executed successfully - record
                if code_executed_successfully:
                    amendments_succeeded += 1
                    prev_version_path = amended_json_path   # next amendment builds on this
                    print(f"  → ✅ AMENDMENT #{idx} APPLIED SUCCESSFULLY")
                    log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=idx, success=True,reasons=failure_reasons)
                    break

                # if the code wasn't executed successfully, proceed to the next amendment_execution_attempt
                else:
                    failed_amendment_executions += 1
                    print(f"     → execution attempt {amendment_execution_attempt+1}/{MAX_EXECUTION_ATTEMPTS_PER_AMD} did not succeed.\n")
                    if amendment_execution_attempt == MAX_EXECUTION_ATTEMPTS_PER_AMD-1:                  
                        print(f"  → ⚠️ AMENDMENT #{idx} ERROR - SKIPPING AMENDMENT")
                        failure_reasons.append(f"failure in execute_generated_code() - returned False")
                        log_amendment_result(summary_logger, row_idx=row_idx, law_name=law_name, amendment=idx, success=False,reasons=failure_reasons)

            # ========== end attempt loops ===========================

    # ---- summary --------------------------------------------------
    elapsed = time.time() - script_start_time
    print("\n\n======= SUMMARY =======")
    print(f"Elapsed                 : {elapsed/60:.1f} min")
    print(f"Rows succeeded          : {rows_succeeded}")
    print(f"Rows failed             : {rows_failed}")
    print(f"Amendments succeeded    : {amendments_succeeded}")
    print(f"Amendments failed       : {amendments_failed}")
    # print(f"Failures (gen|exec)     : {failed_code_generations} | {failed_amendment_executions}")
    # print(f"LLM calls – ok / error  : {successful_api_calls} / {failed_api_calls}")
    # print(f"Tokens in / out         : {total_input_tokens:,} / {total_output_tokens:,}")

if __name__ == "__main__":
    main()