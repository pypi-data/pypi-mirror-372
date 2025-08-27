import json
import os
import re
import difflib
import csv
import pandas as pd
from pathlib import Path
from thefuzz import fuzz
import time
import logging
from datetime import datetime

# Set up logging configuration
def setup_logging():
    """Set up logging with timestamped log file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"layer3_validation_{timestamp}.log"
    
    # Create logs directory if it doesn't exist
    log_dir = Path("Outputs/l_3_val_outputs/logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_path}")
    return logger

# Initialize logger
logger = setup_logging()

# Attempt to import Google Generative AI for Layer 3
try:
    import google.generativeai as genai
    GOOGLE_GENERATIVEAI_AVAILABLE = True
except ImportError:
    logger.warning("google-generativeai library not found.")
    logger.warning("Layer 3 LLM execution will be disabled.")
    logger.warning("To enable, install it: pip install google-generativeai")
    GOOGLE_GENERATIVEAI_AVAILABLE = False
    genai = None


os.environ["TOKENIZERS_PARALLELISM"] = "false"
API_RETRY_LIMIT = 3
API_RETRY_DELAY_SECONDS = 10 # Initial delay, will increase

# --- Text Extraction from JSON (Helper functions) ---

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
        if not (number_text and str(number_text).strip() == str(header_text).strip()):
             current_component_header.append(str(header_text).strip())

    if current_component_header:
        parts.append(" ".join(filter(None, current_component_header)))

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
        logger.error(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error: Could not decode JSON from file {file_path}. Details: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

    parsed_law_container = data.get("parsed_law")
    if not parsed_law_container or not isinstance(parsed_law_container, dict):
        logger.error(f"Error: Key 'parsed_law' not found or is not a dictionary in {file_path}")
        return None

    law_title_for_version = parsed_law_container.get("law_title_for_version", "כותרת החוק לא צוינה")
    law_structure_object = parsed_law_container.get("structure")

    if not law_structure_object or not isinstance(law_structure_object, dict):
        if parsed_law_container.get("type", "").lower() == "law":
            law_structure_object = parsed_law_container
        else:
            logger.error(f"Error: 'structure' key missing or invalid under 'parsed_law' in {file_path}")
            return None

    extracted_body_text = extract_text_from_law_json_recursive(law_structure_object)
    title_prefix = f"{law_title_for_version}\n\n" if law_title_for_version else ""
    full_text = f"{title_prefix}{extracted_body_text}".strip()
    return full_text

# --- CSV Reading and Name Normalization (for Layer 2 & 3 input) ---
def normalize_law_name(name_str):
    """Normalizes a law name by replacing similar characters and removing extra spaces."""
    if not isinstance(name_str, str): return ""
    name_str = name_str.strip()
    name_str = name_str.replace('״', '"').replace('"״', '"').replace('"״', '"')
    name_str = name_str.replace("׳", "'").replace("'׳", "'").replace("'״", "'")
    name_str = name_str.replace('–', '-').replace('—', '-')
    name_str = re.sub(r'\s+', ' ', name_str)
    return name_str

def read_amendment_text_from_csv(csv_file_path, law_name_target, amd_num=1):
    """Reads amendment text from a CSV file for a specific law, after normalizing the law name."""
    if not law_name_target:
        logger.error("Error (read_amendment_text_from_csv): law_name_target cannot be empty.")
        return None
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        normalized_target_law_name = normalize_law_name(law_name_target)
        logger.debug(f"  Normalized target law name for comparison: \n '{normalized_target_law_name}'")

        if 'Name' not in df.columns:
            logger.error(f"Error: 'Name' column not found in {csv_file_path}. Available columns: {df.columns.tolist()}")
            return None
        df['Name_normalized_for_comparison'] = df['Name'].astype(str).apply(normalize_law_name)

        matching_rows = df[df['Name_normalized_for_comparison'] == normalized_target_law_name]
        amendment_text_dict = {}
        if not matching_rows.empty:
            for amd_i in range(1, amd_num + 1):
                if f'amd{amd_i}_section' not in matching_rows.columns:
                    logger.error(f"Error: 'amd{amd_i}_section' column not found in {csv_file_path}. Available columns: {matching_rows.columns.tolist()}")
                    return None
                amendment_text = matching_rows.iloc[0].get(f'amd{amd_i}_section')
                if pd.isna(amendment_text) or str(amendment_text).strip() == "":
                    logger.warning(f"Warning: 'amd{amd_num}_section' is empty or NaN for law '{law_name_target}' (normalized: '{normalized_target_law_name}') in {csv_file_path}")
                    return None
                amendment_text_dict[f'{amd_i}'] = str(amendment_text).strip()
            return amendment_text_dict
        else:
            logger.warning(f"Warning: Amendment for law '{law_name_target}' (normalized: '{normalized_target_law_name}') not found in {csv_file_path}")
            return None
    except FileNotFoundError:
        logger.error(f"Error: CSV file not found at {csv_file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading or processing CSV file {csv_file_path}: {e}")
        return None

# --- Layer 3: LLM-Based Validation Functions ---
def generate_llm_validation_prompt(original_law_text, amendment_text_raw, llm_consolidated_text, amd_num=1):
    """Generates a detailed prompt for a validator LLM, truncating long texts."""
    def truncate_text(text, label):
        if text is None: return f"[{label} text is missing or could not be loaded]"
        return text

    original_law_processed = truncate_text(original_law_text, "original law")
    amendment_processed = truncate_text(amendment_text_raw, "amendment")
    llm_output_processed = truncate_text(llm_consolidated_text, "LLM consolidated output")
    print(f'amd prmpt is: \n',amendment_processed)
    # Using the full detailed prompt from previous interactions
    full_prompt_text = f"""
You are an expert legal assistant specializing in Israeli legislation. Your task is to validate if legislative amendments have been correctly incorporated into a base law text by another AI model.

Provided Texts:
1.  **Original Law Text (A):**
    ```text
    {original_law_processed}
    ```

2.  **Amendment Text (B) (raw text of the amending instructions):**
    ```text
    {amendment_processed}
    ```

3.  **Consolidated Law Text (C) (Output from the AI model being validated):**
    ```text
    {llm_output_processed}
    ```

**Your Validation Task:**

1.  **Analyze Amendment (B):** Carefully analyze the Amendment Text (B) to understand all the specific changes it mandates for the Original Law Text (A). For each distinct instruction in the amendment:
    * Identify the type of change (e.g., addition, deletion, replacement/substitution, renumbering of sections, change of title).
    * Pinpoint the exact location in the Original Law Text (A) where the change should occur (e.g., specific section, sub-section, clause number, or descriptive location like "after the definition of X", "at the end of section Y").
    * Note the old text (if any) to be replaced/deleted and the new text (if any) to be added/substituted.

2.  **Validate Consolidated Text (C):** Compare the required changes (from your analysis of B) against the Consolidated Law Text (C). For each mandated change:
    * **Implementation:** Was the change implemented? (Yes/No/Partially)
    * **Accuracy:** If implemented, was it accurate? (Does the new text in C match what was specified in B? Was the correct old text removed/replaced without unintended alterations to surrounding unchanged text?)
    * **Location:** Was the change implemented at the correct location in C (corresponding to its intended location in A)?

**Output Requirements:**

Please provide a structured report with the following sections:

* **A. Summary of Identified Amendment Instructions from Text (B):**
    * List each distinct amendment instruction you identified. For each, detail:
        * Instruction Number (e.g., 1, 2, 3...)
        * Type of Change: (e.g., Replacement, Addition, Deletion)
        * Target Location in Original Law (A): (Be as specific as possible)
        * Old Text (if applicable): (Quote or summarize)
        * New Text (if applicable): (Quote or summarize)

* **B. Validation of Consolidated Text (C) against Amendment Instructions:**
    * For each Instruction Number from section A:
        * Implemented in (C)?: (Yes / No / Partially)
        * Accuracy of Implementation: (e.g., Accurate / Minor Discrepancies / Major Discrepancies - explain briefly)
        * Correctness of Location: (e.g., Correct / Incorrect - explain briefly if incorrect)

* **C. Other Discrepancies:**
    * **Missing Changes:** List any amendment instructions from (B) that were not found or were incompletely applied in (C).
    * **Incorrect Changes:** List any amendment instructions from (B) that were applied inaccurately in (C) (e.g., wrong text inserted, wrong location).
    * **Unexpected Changes:** List any modifications observed in (C) that were NOT mandated by (B) and differ from the Original Law (A).

* **D. Overall Assessment:**
    * Provide a brief overall assessment of the accuracy and completeness of Text (C) in consolidating Text (A) with Text (B). (e.g., "Highly accurate," "Mostly accurate with minor errors," "Significant errors found requiring revision.")
    * Provide a numerical score from 0 to 100 indicating the overall accuracy of the consolidation, where 100 means perfect compliance with the amendment instructions and 0 means no compliance at all.

Be precise and refer to specific text or section numbers where possible in your analysis.
"""
    return full_prompt_text

def send_prompt_to_gemini_and_count_tokens(prompt_text, api_key=None, model_name="models/gemini-2.5-flash-preview-05-20"):
    """
    Sends a prompt to the specified Gemini model, returns the response text,
    and token counts.
    """
    if not GOOGLE_GENERATIVEAI_AVAILABLE:
        logger.error("Error: google-generativeai library is not available. Cannot send prompt.")
        return None, 0, 0

    if api_key:
        genai.configure(api_key=api_key)
    else:
        try:
            env_api_key = os.getenv("GOOGLE_API_KEY")
            if not env_api_key:
                logger.error("Error: GOOGLE_API_KEY environment variable not set and no API key provided.")
                return None, 0, 0
            genai.configure(api_key=env_api_key)
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            return None, 0, 0

    logger.info(f"\n--- Sending prompt to Gemini model: {model_name} ---")

    generation_config = {
        "temperature": 0.2, # Adjust as needed
        "top_p": 0.9,
        "top_k": 1,
        "max_output_tokens": 30000, # Check model limits
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    current_delay = API_RETRY_DELAY_SECONDS
    for attempt in range(API_RETRY_LIMIT):
        response = None
        try:
            model = genai.GenerativeModel(model_name=model_name,
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

            # Count input tokens before sending
            input_token_count = model.count_tokens(prompt_text).total_tokens
            logger.info(f"  Estimated input tokens for prompt: {input_token_count}")

            response = model.generate_content(prompt_text)

            response_text = None
            output_token_count = 0

            if response.parts:
                # Check for finish reason
                if response.candidates and response.candidates[0].finish_reason:
                    finish_reason = response.candidates[0].finish_reason.name
                    logger.info(f"Gemini finish reason: {finish_reason}")
                    if finish_reason == "MAX_TOKENS":
                        logger.warning("Warning: Gemini stopped due to MAX_TOKENS. Code might be incomplete.")
                    elif finish_reason == "SAFETY":
                        logger.error("Error: Gemini stopped due to SAFETY reasons. Prompt or response might be problematic.")
                        return {"text": None, "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0, "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0, "error": "SAFETY"}
                    elif finish_reason not in ["STOP", "UNSPECIFIED"]: # Other problematic reasons
                        logger.error(f"Error: Gemini stopped due to an unexpected reason: {finish_reason}")
                        return {"text": None, "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0, "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0, "error": f"UNEXPECTED_FINISH_REASON: {finish_reason}"}
                
                # Extract token usage if available
                if hasattr(response, 'usage_metadata'):
                    input_tokens = response.usage_metadata.prompt_token_count
                    output_tokens = response.usage_metadata.candidates_token_count
                    logger.debug(f"Tokens used: Input={input_tokens}, Output={output_tokens}")
                else:
                    logger.warning("Warning: usage_metadata not found in response. Token count will be 0 for this call.")

                return {"text": response.text, "input_tokens": input_tokens, "output_tokens": output_tokens, "error": None}
            else:
                logger.error("Error: Gemini API response has no parts.")
                logger.error(f"Full response object: {response}") # Detailed logging
                error_reason = "NO_PARTS"
                if response.prompt_feedback:
                    logger.info(f"Prompt Feedback when no parts: {response.prompt_feedback}")
                    if response.prompt_feedback.block_reason:
                        block_reason_name = response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason.name
                        logger.info(f"Prompt was blocked (reason in feedback): {block_reason_name}")
                        error_reason = f"PROMPT_BLOCKED: {block_reason_name}"
                # Try to get token count even on error if usage_metadata exists
                if hasattr(response, 'usage_metadata'):
                    input_tokens = response.usage_metadata.prompt_token_count
                    output_tokens = response.usage_metadata.candidates_token_count
                return {"text": "PROMPT_BLOCKED" if "PROMPT_BLOCKED" in error_reason else None, "input_tokens": input_tokens, "output_tokens": output_tokens, "error": error_reason}

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            # Attempt to get usage_metadata if the error object is the response itself and has it (less likely here)
            current_input_tokens = 0
            current_output_tokens = 0 
            if hasattr(e, 'response') and hasattr(e.response, 'usage_metadata'):
                current_input_tokens = e.response.usage_metadata.prompt_token_count
                current_output_tokens = e.response.usage_metadata.candidates_token_count
            elif response and hasattr(response, 'usage_metadata'): # If response object exists from a partial success before exception
                current_input_tokens = response.usage_metadata.prompt_token_count
                current_output_tokens = response.usage_metadata.candidates_token_count

            if "429" in str(e) or "Resource has been exhausted" in str(e): # Rate limit
                logger.info(f"Rate limit likely hit. Retrying in {current_delay} seconds...")
            elif "500" in str(e) or "503" in str(e): # Server error
                logger.info(f"Server error from API. Retrying in {current_delay} seconds...")
            else: # Other errors, may not be worth retrying for token counting, but will for call
                logger.info("Non-retryable API error during this attempt.")
                # For non-retryable errors during an attempt, we return the tokens accumulated so far for this attempt (likely 0)
                # The loop will retry, or eventually fail and return from outside the loop with last known token counts.
                # For the final failure outside the loop, it will be the default 0s unless response was ever populated.
                # This ensures we return the dictionary structure even for errors within an attempt. 
                return {"text": None, "input_tokens": current_input_tokens, "output_tokens": current_output_tokens, "error": str(e)}
        
        time.sleep(current_delay)
        current_delay *= 2 # Exponential backoff


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

    for f_path in original_json_dir.iterdir():
        if f_path.is_file() and f_path.suffix.lower() == '.json':

            file_name_stem = f_path.stem # Gets "חוק לצמצום השימוש במזומן_original_oldid_816623"
            logger.debug(f"  Checking file: {f_path.name} (stem: {file_name_stem})")
            if "_original_oldid_" in file_name_stem:
                file_base_name_parts = file_name_stem.split("_original_oldid_", 1)
                file_base_name = sanitize_filename_component(file_base_name_parts[0].strip())
  
                if file_base_name == law_name_csv:
                    logger.info(f"  Found matching file: {f_path.name}")
                    return f_path
            # Fallback: if the "_original_oldid_" part is missing, try a simpler match (less likely)
            elif sanitize_filename_component(file_name_stem) == law_name_csv:
                 logger.info(f"  Found matching file (simple stem): {f_path.name}")
                 return f_path


    logger.info(f"  No matching file found for base name: '{law_name_csv}' in {original_json_dir}")
    return None


def remove_suffix_from_filenames(directory_path, suffix):
    if not os.path.isdir(directory_path):
        logger.error(f"Error: Directory not found at {directory_path}")
        return

    logger.info(f"Searching for files with suffix '{suffix}' in '{directory_path}'...")
    file_names = []
    for filename in os.listdir(directory_path):
        if filename.endswith(suffix):
            new_filename = filename[:-len(suffix)]
            file_names.append(new_filename)
           
    return file_names


def create_amd_text_prompt_from_amd_dict(amd_dict):
    """
    Creates a formatted text prompt from the amendment dictionary.
    """
    if not amd_dict:
        print("Error: Empty amendment dictionary provided.")
        return None

    prompt_parts = []
    for key, value in amd_dict.items():
        if value:  # Only include non-empty values
            prompt_parts.append(f"amendment number {key}: \n {value.strip()}")
    return "\n\n".join(prompt_parts) if prompt_parts else "No valid amendment text found."


def layer_3_validation_for_law(law_name, amd_csv_file, outputs_folder_path, amd_num=1, gemini_api_key=None):
    """
    Main function to execute Layer 3 validation for a specific law.
    """
    logger.info(f"\n--- Starting Layer 3 Validation for Law: {law_name} ---")
    json_laws_v2_path = os.path.join(os.path.dirname(__file__), "..", "..", "Data", "JSON_Laws_v2")
    original_law_json_file = find_original_json_file(law_name, Path(json_laws_v2_path))
    # gold_standard_json_file = os.path.join(json_laws_v2_path, f"{law_name}_current.json") # Output of your main LLM
    llm_output_json_file = os.path.join(os.path.dirname(__file__), "..", "..", "Outputs", f"JSON_amd{amd_num}", f"{law_name}_amd{amd_num}.json") 

    prompts_outputs_dir = os.path.join(outputs_folder_path, f"l_3_prompts_amd{amd_num}")
    os.makedirs(prompts_outputs_dir, exist_ok=True)  # Creates the directory if it doesn't exist
    gemini_response_output_dir = os.path.join(outputs_folder_path, f"l_3_gemini_res_amd{amd_num}")
    os.makedirs(gemini_response_output_dir, exist_ok=True)  # Creates the directory if it doesn't exist
    law_name_for_file = law_name.replace(" ", "_").replace("/", "_").replace("\\", "_")  # Sanitize for filenames
    LAYER3_PROMPT_OUTPUT_FILE = f"{law_name_for_file}_layer3_validator_llm_prompt.txt"
    LAYER3_RESPONSE_OUTPUT_FILE = f"{law_name_for_file}_layer3_validator_llm_response.txt"

    all_inputs_valid = True

    # --- Read Law Files ---
    logger.info("\nReading and extracting text from JSON law files...")
    original_law_flat_text = read_law_json_to_flat_text(original_law_json_file)
    llm_primary_output_flat_text = read_law_json_to_flat_text(llm_output_json_file) # Renamed for clarity
    # gold_standard_flat_text = read_law_json_to_flat_text(gold_standard_json_file)

    # Basic checks for essential files
    if original_law_flat_text is None: all_inputs_valid = False; logger.critical(f"CRITICAL: Failed to read {original_law_json_file}")
    if llm_primary_output_flat_text is None: all_inputs_valid = False; logger.critical(f"CRITICAL: Failed to read {llm_output_json_file}")
    # Gold standard is for L1, script can proceed for L2/L3 if it's missing, but L1 will be incomplete
    # if gold_standard_flat_text is None: logger.warning(f"WARNING: Failed to read {gold_standard_json_file}. Layer 1 will be affected.")


    # --- Get Original Law Title for CSV Lookup ---
    original_law_title_for_csv = None
    if all_inputs_valid and os.path.exists(original_law_json_file):
        try:
            with open(original_law_json_file, 'r', encoding='utf-8') as f_orig:
                original_law_data = json.load(f_orig)
                original_law_title_for_csv = original_law_data.get("parsed_law", {}).get("law_title_for_version")
                logger.debug(f"  Original law title for CSV lookup:\n '{original_law_title_for_csv}'")
        except Exception as e:
            logger.error(f"Error reading original law title from {original_law_json_file}: {e}")
            all_inputs_valid = False
    elif not os.path.exists(original_law_json_file):
        logger.error(f"Error: Original law file {original_law_json_file} not found.")
        all_inputs_valid = False

    # --- Read Raw Amendment Text from CSV ---
    raw_amendment_text_from_csv = None
    if all_inputs_valid and original_law_title_for_csv:
        logger.info(f"\nReading amendment text for law: '{original_law_title_for_csv}' from CSV: {amd_csv_file}")
        raw_amendment_dict_text_from_csv = read_amendment_text_from_csv(amd_csv_file, original_law_title_for_csv, amd_num=amd_num)
        
        if raw_amendment_dict_text_from_csv:
            raw_amendment_text_from_csv = create_amd_text_prompt_from_amd_dict(raw_amendment_dict_text_from_csv)
        
        if not raw_amendment_text_from_csv:
            logger.warning(f"  Could not find or read amendment text for '{original_law_title_for_csv}'. Layers 2 & 3 will be affected.")
            # For Layer 3, amendment text is critical.
            all_inputs_valid = False # Set to false if amendment text is crucial and not found
    elif not original_law_title_for_csv and all_inputs_valid:
        logger.warning("  Skipping amendment reading from CSV: Original law title could not be determined.")
        all_inputs_valid = False

    # --- Execute Layer 3 ---
    logger.info("\n--- Running Layer 3 Validation (LLM-Based Validation) ---")
    if all_inputs_valid and original_law_flat_text and raw_amendment_text_from_csv and llm_primary_output_flat_text:
        logger.info("  Generating prompt for validator LLM...")
        validator_prompt_l3 = generate_llm_validation_prompt(
            original_law_flat_text,
            raw_amendment_text_from_csv,
            llm_primary_output_flat_text
        )
        try:
            logger.debug("  Saving Layer 3 validation prompt to file...")
            # Define the full path for your file
            layer_3_law_prompt_path = os.path.join(prompts_outputs_dir, LAYER3_PROMPT_OUTPUT_FILE)
            logger.debug(f"  Layer 3: Saving prompt to: \n {layer_3_law_prompt_path}")
            with open(layer_3_law_prompt_path, "w", encoding="utf-8") as f:
                f.write(validator_prompt_l3)
            logger.debug(f"  Layer 3: Validation prompt saved to: {layer_3_law_prompt_path}")
        except Exception as e:
            logger.error(f"  Error saving Layer 3 validation prompt: {e}")

        if GOOGLE_GENERATIVEAI_AVAILABLE and gemini_api_key:
            response_data = send_prompt_to_gemini_and_count_tokens(
                validator_prompt_l3,
                api_key=gemini_api_key,
                model_name="models/gemini-2.5-flash-preview-05-20"
            )
            validator_response_text = response_data.get("text")
            input_tokens = response_data.get("input_tokens", 0)
            output_tokens = response_data.get("output_tokens", 0)
            error = response_data.get("error")

            if error:
                logger.error(f"  Layer 3: Gemini API call failed with error: {error}")

            if validator_response_text:
                logger.info("\n  --- Validator LLM Response Received ---")
                logger.info(validator_response_text[:1000] + "..." if len(validator_response_text) > 1000 else validator_response_text) # Log preview
                logger.info(f"\n  Layer 3 - Token Usage:")
                logger.info(f"    Input Prompt Tokens (to validator LLM): {input_tokens}")
                logger.info(f"    Output Response Tokens (from validator LLM): {output_tokens}")
                logger.info(f"    Total Tokens for this Layer 3 call: {input_tokens + output_tokens}")
                try:
                    # Define the full path for your file
                    layer_3_law_validation_response = os.path.join(gemini_response_output_dir, LAYER3_RESPONSE_OUTPUT_FILE)
                    logger.debug(f"  Layer 3: Saving validator LLM response to: \n {layer_3_law_validation_response}")
                    with open(layer_3_law_validation_response, "w", encoding="utf-8") as f:
                        f.write(validator_response_text)
                    logger.debug(f"  Layer 3: Validator LLM response saved to: {layer_3_law_validation_response}")
                    return input_tokens, output_tokens
                except Exception as e:
                    logger.error(f"  Error saving Layer 3 validator LLM response: {e}")
            else:
                logger.info("  Layer 3: No response received from validator LLM or an error occurred during the API call.")
        elif not GOOGLE_GENERATIVEAI_AVAILABLE:
            logger.info("  Layer 3: LLM execution skipped (google-generativeai library not installed). Prompt saved.")
        else: # API key not provided
            logger.info("  Layer 3: LLM execution skipped (API key not provided). Prompt saved.")
    else:
        logger.info("  Skipping Layer 3: Missing one or more required texts (original law, amendment text, or LLM primary output).")
    
    return None, None



# --- Main Execution Block ---
if __name__ == "__main__":
    # Handle API Key once at the beginning
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key and GOOGLE_GENERATIVEAI_AVAILABLE:
        logger.info("\nGoogle API Key for Gemini not found in GOOGLE_API_KEY environment variable.")
        gemini_api_key = input("Please enter your Google API Key for Gemini and press Enter: ").strip()
        if not gemini_api_key:
            logger.warning("No API Key provided. Layer 3 LLM execution will be skipped.")
    elif not GOOGLE_GENERATIVEAI_AVAILABLE:
        logger.warning("Google Generative AI library not installed. Layer 3 LLM execution will be skipped.")
        gemini_api_key = None

    # # --- Define Output Folder for Layer 3 ---
    LAYER3_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "Outputs", "l_3_val_outputs")
    os.makedirs(LAYER3_OUTPUT_FOLDER, exist_ok=True)  # Ensure output folder exists
    for i in range(1, 5):
         # # --- Define File Paths (UPDATE THESE) ---
        CSV_FILE_PATH = Path("Data") / f"{i}amd.csv"
        # # Ensure these files are in the root directory of the workspace.
        target_directory = f"Outputs/JSON_amd{i}"
        suffix_to_remove = f"_amd{i}.json"
        if not os.path.exists(CSV_FILE_PATH):
            logger.error(f"stop runing the code for layer 3 validation, we do not have laws with {i} amd. If we do, please check the following path: {CSV_FILE_PATH}")
            logger.error("Stopping Layer 3 validation script execution.")
            break

        LAYER3_OUTPUT_AMD_FOLDER = os.path.join(LAYER3_OUTPUT_FOLDER, f"amd{i}")
        os.makedirs(LAYER3_OUTPUT_AMD_FOLDER, exist_ok=True)  # Ensure output folder exists

        logger.info(f"\n--- Starting Layer 3 Validation for laws with {i} amendments ---")
        # # Ensure the target directory exists
        if not os.path.exists(target_directory):
            logger.error(f"Error: Target directory '{target_directory}' does not exist.")
            logger.error("Stopping Layer 3 validation script execution.")
            break
        logger.info(f"Target directory: {target_directory}")
        logger.info(f"CSV file path: {CSV_FILE_PATH}")
        
        # # Run the function to remove the suffix
        law_names_list = remove_suffix_from_filenames(target_directory, suffix_to_remove)

        logger.info(f"Found {len(law_names_list)} law names in {target_directory} after removing suffix '{suffix_to_remove}':")
        logger.debug(f"Law names list: {law_names_list}")
        layer_3_validation_token_usage = {}
        for law in law_names_list:
            law_name = law.replace("_", " ")  # Convert to human-readable format
            try:
                input_tokens, output_tokens = layer_3_validation_for_law(
                    law_name, 
                    CSV_FILE_PATH, 
                    LAYER3_OUTPUT_AMD_FOLDER, 
                    amd_num=i, 
                    gemini_api_key=gemini_api_key  # Pass the API key as parameter
                )
                if input_tokens is not None and output_tokens is not None:
                    layer_3_validation_token_usage[law_name] = {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens_for_law": input_tokens + output_tokens
                    }
            except Exception as e:
                logger.error(f"Error processing law '{law_name}': {e}")
                layer_3_validation_token_usage[law_name] = {
                    "error": str(e),
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens_for_law": 0
                }
            logger.info(f"\nFinished processing layer 3 validation to law: {law_name}\n")
        # Save the token usage to a CSV file
        token_usage_df = pd.DataFrame.from_dict(layer_3_validation_token_usage, orient='index')
        # csv_outputs_folder_path = os.path.join(LAYER3_OUTPUT_AMD_FOLDER, f"layer_3_validation_gemini_token_usage")
        # os.makedirs(csv_outputs_folder_path, exist_ok=True)
        csv_output_path = os.path.join(LAYER3_OUTPUT_AMD_FOLDER, f"l_3_val_gemini_token_usage_amd{i}.csv")
        token_usage_df.to_csv(csv_output_path, encoding='utf-8-sig')
        logger.info(f"\nLayer 3 validation for laws with {i} amendments completed.")
    logger.info("\nFull Validation Script Finished.")
