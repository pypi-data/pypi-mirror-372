import argparse
import os
import re
import sys
import time
import csv
import io
import json
import shutil
import datetime
import pandas as pd
import google.generativeai as genai
from pathlib import Path
from . import config


def training_mode():
    """
    Runs the training mode, which is equivalent to the main function of
    Src/laws_amending_script.py.
    """
    print("Running in Training Mode...")
    
    # Load configuration and get training paths
    conf = config.load_config()
    training_paths = config.get_training_paths(conf)
    
    try:
        # Configure paths in helper modules
        from .Generalized_amd_flow import configure_training_paths as configure_gen_paths
        from .product_flow_helpers import configure_training_paths as configure_prod_paths
        
        configure_gen_paths(training_paths)
        configure_prod_paths(training_paths)
        
        from .laws_amending_script import main as training_main
        # Pass the configured paths to training main
        training_main(training_paths)
    except ImportError:
        print("Error: Could not import required modules from 'laws_amending_script.py'.")
        print("Please ensure the file exists and is in the correct directory.")
    except Exception as e:
        print(f"An error occurred during training mode: {e}")


def get_paths(conf):
    """Gets original JSONs path and output path from the config."""
    originals_path = config.get_or_prompt_path(conf, 'originals_path', "Enter path to original JSONs directory")
    output_path = config.get_or_prompt_path(conf, 'output_path', "Enter path for the main output directory")
    return originals_path, output_path

def get_api_key(conf):
    """Gets Gemini API key from the config."""
    return config.get_api_key(conf)


def handle_law_input(originals_path, output_path, law_identifier):
    """Handles amending a single law based on user-provided text."""
    from .laws_amending_script import find_json_by_law_id_and_amd_id

    # Try to find law by ID.
    original_law_path = find_json_by_law_id_and_amd_id(law_identifier, originals_path, original_ind=True)
    if not original_law_path:
        # Fallback to a less strict search
        found_files = list(originals_path.glob(f"*{law_identifier}*.json"))
        if not found_files:
            print(f"Error: No JSON file found for law identifier '{law_identifier}' in '{originals_path}'.")
            return
        original_law_path = found_files[0]
        print(f"Found law file: {original_law_path.name}")

    # Extract law_id from the original law path
    law_id = law_identifier
    if not law_id.isdigit():
        match = re.search(r'LawID_(\d+)', original_law_path.name)
        law_id = match.group(1) if match else law_identifier

    amendments = []
    amd_count = 1
    while True:
        print(f"\n--- Amendment {amd_count} ---")
        amd_choice = input("Add amendment from (1) .txt file, (2) paste text, (3) CSV with all amendments, or (4) finish: ").strip()
        if amd_choice == '1':
            amd_path_str = input("Enter path to amendment .txt file: ").strip()
            amd_path = Path(amd_path_str)
            if amd_path.is_file():
                amendments.append(amd_path.read_text(encoding='utf-8'))
                print(f"✓ Amendment from {amd_path.name} added.")
                amd_count += 1
            else:
                print(f"Error: File not found at '{amd_path_str}'")
        elif amd_choice == '2':
            print("Enter amendment text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == "" and lines:  # Empty line after content
                    break
                lines.append(line)
            amendment_text = "\n".join(lines).strip()
            if amendment_text:
                amendments.append(amendment_text)
                print("✓ Amendment text added.")
                amd_count += 1
            else:
                print("No text entered. Amendment not added.")
        elif amd_choice == '3':
            csv_path_str = input("Enter path to CSV file with all amendments: ").strip()
            csv_path = Path(csv_path_str)
            if csv_path.is_file():
                try:
                    df = pd.read_csv(csv_path)
                    amd_cols = [c for c in df.columns if c.startswith('amd') and c.endswith('_section')]
                    if amd_cols:
                        # Find the row for this law
                        law_rows = df[df['LawID'] == law_id]
                        if not law_rows.empty:
                            for col in amd_cols:
                                amd_text = law_rows[col].iloc[0]
                                if pd.notna(amd_text) and str(amd_text).strip():
                                    amendments.append(str(amd_text).strip())
                            print(f"✓ Added {len(amendments)} amendments from CSV.")
                            break
                        else:
                            print(f"Error: No amendments found for LawID {law_id} in the CSV.")
                    else:
                        print("Error: No amendment columns found in CSV (expected format: amd1_section, amd2_section, etc.)")
                except Exception as e:
                    print(f"Error reading CSV file: {e}")
            else:
                print(f"Error: CSV file not found at '{csv_path_str}'")
        elif amd_choice == '4':
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    if not amendments:
        print("No amendments provided. Exiting.")
        return
    
    data = {'LawID': [law_id]}
    data.update({f'amd{i+1}_section': [text] for i, text in enumerate(amendments)})
    
    df = pd.DataFrame(data)
    temp_csv_path = output_path / f"temp_amendments_{law_id}.csv"
    df.to_csv(temp_csv_path, index=False, encoding='utf-8')
    
    return temp_csv_path


def handle_csv_input(csv_path_str, output_path):
    """Handles amending laws    a user-provided CSV file."""
    csv_path = Path(csv_path_str)
    if not csv_path.is_file():
        print(f"Error: CSV file not found at '{csv_path_str}'.")
        return None
    
    df = pd.read_csv(csv_path)
    amd_cols = [c for c in df.columns if c.startswith('amd') and c.endswith('_section')]
    
    rows_to_update = []
    for index, row in df.iterrows():
        if not any(pd.notna(row.get(col)) and str(row.get(col)).strip() for col in amd_cols):
            rows_to_update.append(row)
            
    if rows_to_update:
        print("\nThe following laws in the CSV are missing amendment text:")
        for row in rows_to_update:
            print(f"- LawID: {row['LawID']}")
        if len(rows_to_update) > 1:
            print("\nRecommendation: It's best to prepare a complete CSV with all amendment texts.")

        for row in rows_to_update:
            law_id = row['LawID']
            print(f"\n--- Adding amendment for LawID {law_id} ---")
            amd_choice = input("Enter (1) path to .txt file or (2) paste text directly: ").strip()
            if amd_choice == '1':
                amd_path = input("Enter path to .txt file: ").strip()
                if Path(amd_path).is_file():
                    amd_text = Path(amd_path).read_text(encoding='utf-8')
                else:
                    print(f"Error: File not found at '{amd_path}'")
                    continue
            elif amd_choice == '2':
                print("Enter amendment text (press Enter twice to finish):")
                lines = []
                while True:
                    line = input()
                    if line.strip() == "" and lines:  # Empty line after content
                        break
                    lines.append(line)
                amd_text = "\n".join(lines).strip()
                if not amd_text:
                    print("No text entered. Skipping this amendment.")
                    continue
            else:
                print("Invalid choice. Skipping this amendment.")
                continue
            
            # Find the first empty amdX_section for this law_id
            target_col = None
            i = 1
            while True:
                col_name = f'amd{i}_section'
                if col_name not in df.columns:
                    df[col_name] = pd.NA # Create column if it doesn't exist
                
                # Check if the value for the specific row is missing
                # Assuming LawID is unique in the context of this loop
                current_val = df.loc[df['LawID'] == law_id, col_name].iloc[0]
                if pd.isna(current_val) or str(current_val).strip() == '':
                    target_col = col_name
                    break
                i += 1
            
            if target_col:
                df.loc[df['LawID'] == law_id, target_col] = amd_text
            else:
                # This case is unlikely to be reached with the while True logic
                print(f"Warning: Could not find an empty amendment column for LawID {law_id}")

        updated_csv_path = output_path / f"updated_{csv_path.name}"
        df.to_csv(updated_csv_path, index=False, encoding='utf-8')
        print(f"\nUpdated CSV with new amendments saved to: {updated_csv_path}")
        return updated_csv_path
        
    return csv_path


def run_product_flow(originals_path, amendments_csv_path, output_path, model, model_config):
    """
    A modified version of the amendment implementation flow for product mode.
    This version does not use a gold standard. Instead, it generates an HTML
    diff report and runs Layer 3 validation after each amendment.
    It also includes a self-correction loop that retries failed amendments
    by providing feedback from the previous attempt to the model.
    """
    from .product_flow_helpers import (
        generate_llm_prompt, call_gemini_api, extract_python_code,
        execute_generated_code, format_json_for_human_reading
    )
    from .laws_amending_script import (
        find_json_by_law_id_and_amd_id, generate_validation3_prompt
    )
    from .validation.layer1_validation import (
        generate_html_diff_report, read_law_json_to_flat_text
    )
    import datetime

    # Ask user about diff report behavior at the start
    review_choice = input("\nHow to handle HTML diff reports?\n1. Open automatically after each amendment (default)\n2. Do not open automatically\nEnter choice (1 or 2): ").strip()
    auto_open_diffs = (review_choice != '2')

    # Setup output directories
    diff_dir = output_path / "diff_reports"
    scripts_dir = output_path / "generated_scripts"
    amended_dir = output_path / "amended_laws"
    val_reports_dir = output_path / "validation_reports"
    logs_dir = output_path / "logs"
    [d.mkdir(exist_ok=True) for d in [diff_dir, scripts_dir, amended_dir, val_reports_dir, logs_dir]]

    # Create comprehensive log file for this run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_path = logs_dir / f"product_run_{timestamp}.log"
    
    def log_to_file(message, echo=True):
        """Helper function to log messages to both console and file"""
        if echo:
            print(message)
        with open(run_log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    
    log_to_file("=== PRODUCT MODE RUN STARTED ===")
    log_to_file(f"Originals path: {originals_path}")
    log_to_file(f"Amendments CSV: {amendments_csv_path}")
    log_to_file(f"Output path: {output_path}")
    log_to_file(f"Run log: {run_log_path}")

    # Token counters
    total_gen_input_tokens = 0
    total_gen_output_tokens = 0
    total_val3_input_tokens = 0
    total_val3_output_tokens = 0

    with open(amendments_csv_path, newline="", encoding="utf-8") as f:
        amendments_data = list(csv.DictReader(f))

    AMD_COL_RE = re.compile(r"amd(\d+)_section")

    for row in amendments_data:
        law_id = row.get("LawID", "").strip()
        if not law_id:
            log_to_file("Skipping a row due to missing LawID.")
            continue

        log_to_file(f"\n{'='*10} Processing Law ID: {law_id} {'='*10}")

        original_json_path = find_json_by_law_id_and_amd_id(law_id, originals_path, original_ind=True)
        if not original_json_path:
            found_files = list(originals_path.glob(f"*{law_id}*.json"))
            if not found_files:
                log_to_file(f"Error: Could not find original law JSON for LawID {law_id} in {originals_path}. Skipping.")
                continue
            original_json_path = found_files[0]

        log_to_file(f"Found original law file: {original_json_path.name}")

        amendment_cols = sorted(
            [c for c in row if AMD_COL_RE.fullmatch(c) and str(row.get(c, '')).strip()],
            key=lambda c: int(AMD_COL_RE.fullmatch(c).group(1))
        )

        if not amendment_cols:
            log_to_file(f"No amendments found for Law ID {law_id}. Skipping.")
            continue

        log_to_file(f"Found {len(amendment_cols)} amendments to apply: {amendment_cols}")
        prev_version_path = original_json_path

        for col in amendment_cols:
            amd_idx = int(AMD_COL_RE.fullmatch(col).group(1))
            amendment_text = str(row[col]).strip()
            log_to_file(f"\n--- Applying Amendment #{amd_idx} ---")
            log_to_file(f"Amendment text: {amendment_text}")

            amended_json_path = amended_dir / f"{law_id}_amd{amd_idx}.json"
            
            # --- Self-Correction Loop ---
            max_retries = model_config.get("self_correction_retries", 2)
            threshold = model_config.get("self_correction_threshold", 85)
            
            amendment_successful = False
            val3_feedback = None # To store feedback from a failed attempt
            
            for attempt in range(max_retries + 1): # Initial attempt + retries
                log_to_file(f"\n--- Attempt {attempt + 1}/{max_retries + 1} for Amendment #{amd_idx} ---")
                
                # --- Prompt Generation (with potential feedback) ---
                prompt = generate_llm_prompt(str(prev_version_path), amendment_text, str(amended_json_path))
                if prompt.startswith("Error"):
                    log_to_file(f"Error generating prompt: {prompt}")
                    break # Break from retry loop, will fail this amendment
                
                parts = [prompt]
                script_path = scripts_dir / f"{law_id}_amd{amd_idx}_attempt{attempt+1}_script.py"

                # If this is a retry, use feedback from the previous failed attempt
                if attempt > 0 and val3_feedback and script_path.with_name(script_path.name.replace(f"attempt{attempt+1}", f"attempt{attempt}")).exists() and amended_json_path.exists():
                    log_to_file("Previous attempt failed. Using feedback to generate a better script.")
                    
                    feedback_path = logs_dir / f"val3_feedback_law_{law_id}_amd_{amd_idx}_attempt{attempt}.json"
                    with open(feedback_path, "w", encoding="utf-8") as f:
                        f.write(val3_feedback)
                    
                    prev_script_path = script_path.with_name(script_path.name.replace(f"attempt{attempt+1}", f"attempt{attempt}"))

                    try:
                        feedback_file = genai.upload_file(path=str(feedback_path), display_name=feedback_path.name)
                        script_file = genai.upload_file(path=str(prev_script_path), display_name=prev_script_path.name)
                        result_file = genai.upload_file(path=str(amended_json_path), display_name=amended_json_path.name)
                        
                        prompt += (
                            "\n\nA previous attempt to apply this amendment resulted in a low validation score. "
                            "You are being provided with three files to help you correct the mistake:\n"
                            "1. The validation feedback file, explaining what was wrong.\n"
                            "2. The incorrect Python script that was generated previously.\n"
                            "3. The incorrect JSON output produced by that script.\n\n"
                            "Please analyze these files carefully to generate a corrected Python script."
                        )
                        parts = [prompt, feedback_file, script_file, result_file]
                    except Exception as e:
                        log_to_file(f"Warning: Could not upload feedback files. Retrying with basic prompt. Error: {e}")
                        parts = [prompt]

                # --- API Call and Code Generation ---
                log_to_file("Calling Gemini API for code generation...")
                llm_resp = call_gemini_api(
                    parts, model,
                    api_retry_limit=model_config.get("api_retry_limit", 3),
                    api_retry_delay_seconds=model_config.get("api_retry_delay_seconds", 10)
                )
                gen_input = llm_resp.get("input_tokens", 0)
                gen_output = llm_resp.get("output_tokens", 0)
                log_to_file(f"Generation API Tokens (Attempt {attempt+1}) - Input: {gen_input}, Output: {gen_output}")
                total_gen_input_tokens += gen_input
                total_gen_output_tokens += gen_output
                if llm_resp["error"]:
                    log_to_file(f"Error from Gemini API: {llm_resp['error']}")
                    continue # Go to next retry attempt

                generated_code = extract_python_code(llm_resp["text"])
                if not generated_code:
                    log_to_file("Error: Could not extract Python code from the model's response.")
                    continue # Go to next retry attempt

                script_path.write_text(generated_code, encoding='utf-8')
                log_to_file(f"Generated script for attempt {attempt+1} saved to: {script_path}")

                # --- Code Execution ---
                log_to_file("Executing generated script...")
                executed = execute_generated_code(generated_code, prev_version_path, amended_json_path, amendment_text)
                
                if not executed or not amended_json_path.exists():
                    log_to_file(f"Error: Execution of generated script for attempt {attempt+1} failed.")
                    continue # Go to next retry attempt

                log_to_file(f"Script executed. Output saved to: {amended_json_path}")

                # --- Validation and Diff Report ---
                log_to_file("Generating diff report and performing validation...")
                prev_text = read_law_json_to_flat_text(prev_version_path)
                new_text = read_law_json_to_flat_text(amended_json_path)

                if not (prev_text and new_text):
                    log_to_file("Could not read text from JSON files, skipping validation for this attempt.")
                    continue

                # Layer 3 Validation
                val3_prompt = generate_validation3_prompt(
                    original_law_text=prev_text,
                    amendment_text=amendment_text,
                    amended_law_text=new_text
                )
                # Log the full prompt only to file, not console
                log_to_file("Layer 3 validation prompt written to run log.", echo=True)
                log_to_file(val3_prompt, echo=False)
                
                val3_resp = call_gemini_api(
                    [val3_prompt],
                    model,
                    api_retry_limit=model_config.get("api_retry_limit", 3),
                    api_retry_delay_seconds=model_config.get("api_retry_delay_seconds", 10),
                    json_mode=True
                )
                val_input = val3_resp.get('input_tokens', 0)
                val_output = val3_resp.get('output_tokens', 0)
                log_to_file(f"Validation API Tokens (Attempt {attempt+1}) - Input: {val_input}, Output: {val_output}")
                total_val3_input_tokens += val_input
                total_val3_output_tokens += val_output
                
                val3_score = "N/A"
                if val3_resp["error"]:
                    log_to_file(f"Layer 3 validation API call failed: {val3_resp['error']}")
                else:
                    val3_feedback = val3_resp["text"] # Store for potential next attempt
                    val3_report_path = val_reports_dir / f"val3_report_law_{law_id}_amd_{amd_idx}_attempt{attempt+1}.json"
                    val3_txt_report_path = val3_report_path.with_suffix('.txt')
                    try:
                        val3_raw = val3_feedback.strip()
                        if val3_raw.startswith("```"):
                            val3_raw = re.sub(r'^```[a-zA-Z]*\s*', '', val3_raw)
                            val3_raw = re.sub(r'\s*```$', '', val3_raw)
                        m = re.search(r'\{[\s\S]*\}', val3_raw)
                        if m:
                            val3_raw = m.group(0)
                        json_response = json.loads(val3_raw)
                        val3_score = json_response.get("overall_score", 0)
                        with open(val3_report_path, 'w', encoding='utf-8') as f:
                            json.dump(json_response, f, ensure_ascii=False, indent=2)
                        human_readable_text = format_json_for_human_reading(json_response)
                        val3_txt_report_path.write_text(human_readable_text, encoding='utf-8')
                        log_to_file(f"Layer 3 validation report saved to: {val3_report_path} and {val3_txt_report_path}")
                    except json.JSONDecodeError:
                        match = re.search(r'"overall_score"\s*:\s*(\d+)', val3_feedback)
                        val3_score = int(match.group(1)) if match else 0
                        val3_report_path.write_text(val3_feedback, encoding='utf-8')
                        log_to_file(f"Layer 3 validation report JSON decode error, saving only raw text to {val3_report_path}")
                    
                    log_to_file(f"Layer 3 Validation Score for attempt {attempt+1}: {val3_score}/100")


                # --- Decision Point ---
                if isinstance(val3_score, int) and val3_score >= threshold:
                    log_to_file(f"✅ Amendment #{amd_idx} SUCCEEDED with score {val3_score} (>= threshold {threshold}).")
                    amendment_successful = True
                    
                    # Generate final diff report on success
                    diff_report_path = diff_dir / f"diff_law_{law_id}_amd_{amd_idx}.html"
                    html_diff = generate_html_diff_report(prev_text, new_text, file1_name=prev_version_path.name, file2_name=amended_json_path.name)
                    diff_report_path.write_text(html_diff, encoding='utf-8')
                    log_to_file(f"Final HTML diff report generated: {diff_report_path}")
                    if auto_open_diffs:
                        try:
                            import webbrowser
                            webbrowser.open(f'file://{diff_report_path.resolve()}')
                            log_to_file(f"Opened HTML diff report in browser: {diff_report_path}")
                        except Exception as e:
                            log_to_file(f"Could not open HTML diff report in browser: {e}")
                            print(f"Could not open browser. Please manually open: {diff_report_path}")

                    break # Exit the retry loop
                else:
                    log_to_file(f"🔄 Amendment #{amd_idx} attempt {attempt+1} failed with score {val3_score} (< threshold {threshold}).")
                    if attempt == max_retries:
                        log_to_file(f"❌ Amendment #{amd_idx} FAILED after all {max_retries+1} attempts.")
            
            # --- After the retry loop ---
            if amendment_successful:
                prev_version_path = amended_json_path # Set up for the next amendment
            else:
                log_to_file(f"Stopping processing for Law ID {law_id} because amendment #{amd_idx} could not be applied successfully.")
                break # Stop processing other amendments for this law
    
    log_to_file("\n--- Product Mode Run Summary ---")
    log_to_file(f"Generation Tokens: {total_gen_input_tokens} (input), {total_gen_output_tokens} (output)")
    log_to_file(f"Validation Tokens: {total_val3_input_tokens} (input), {total_val3_output_tokens} (output)")
    log_to_file(f"Total Tokens Used: {total_gen_input_tokens + total_val3_input_tokens} (input), {total_gen_output_tokens + total_val3_output_tokens} (output)")
    log_to_file("=== PRODUCT MODE RUN COMPLETED ===")
    
    print(f"\n✓ Product mode run finished. Comprehensive log saved to: {run_log_path}")

def setup_product_model(api_key, model_config):
    """Initializes and configures the Gemini model."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_config.get("name", "gemini-2.5-flash"),
        safety_settings=[
            {"category": c, "threshold": "BLOCK_NONE"} for c in 
            ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", 
             "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]
        ],
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=model_config.get("max_output_tokens", 8192),
            temperature=model_config.get("temperature", 0.2)
        )
    )
    return model

def product_mode():
    """
    Runs the product mode, an interactive process for amending laws.
    """
    print("Running in Product Mode...")
    
    conf = config.load_config()
    api_key = get_api_key(conf)
    originals_path, output_path = get_paths(conf)
    if not originals_path:
        return

    model_conf = config.get_model_config(conf)
    model = setup_product_model(api_key, model_conf)

    print("\nC. Choose input type:")
    choice = input("1. Law Name or LawID\n2. CSV file with multiple laws\nEnter your choice (1 or 2): ").strip()

    csv_to_process = None
    if choice == '1':
        print("\nD. Law input:")
        law_identifier = input("Enter the Law Name or LawID: ").strip()
        csv_to_process = handle_law_input(originals_path, output_path, law_identifier)
    elif choice == '2':
        print("\nE. CSV file input:")
        csv_path_str = input("Enter path to your CSV file: ").strip()
        csv_to_process = handle_csv_input(csv_path_str, output_path)
    else:
        print("Invalid choice. Exiting.")
        return

    if csv_to_process:
        run_product_flow(originals_path, csv_to_process, output_path, model, model_conf)

def main():
    parser = argparse.ArgumentParser(description="A script to amend laws using AI, with two operational modes.")
    parser.add_argument("mode", nargs='?', choices=["training", "product"], help="'training' to run on existing data, 'product' for interactive use.")
    args = parser.parse_args()

    # If no mode was provided, check for saved preference or ask user
    if args.mode is None:
        conf = config.load_config()
        saved_mode = conf.get("defaults", {}).get("mode")
        
        print("Israeli Law Amender")
        print("=" * 50)
        
        if saved_mode:
            print(f"✓ Found saved default mode: {saved_mode.title()} Mode")
            use_saved = input("Use saved mode? (Y/n): ").strip().lower()
            if use_saved not in ['n', 'no']:
                args.mode = saved_mode
            else:
                # Ask for new choice and save it
                args.mode = config.get_default_mode(conf)
        
        if not args.mode:
            print("Choose a mode:")
            print("1. Training Mode - Process batch amendments from CSV files")
            print("2. Product Mode - Interactive amendment of individual laws (default)")
            
            choice = input("\nEnter your choice (1 or 2, press Enter for Product Mode): ").strip()
            if choice == '1':
                args.mode = "training"
            else:
                args.mode = "product"  # Default to product mode
            
            # Ask if user wants to save this preference
            save_mode = input(f"Save '{args.mode.title()} Mode' as default for future runs? (Y/n): ").strip().lower()
            if save_mode not in ['n', 'no']:
                if "defaults" not in conf:
                    conf["defaults"] = {}
                conf["defaults"]["mode"] = args.mode
                config.save_config(conf)
                print("✓ Default mode saved to config.yaml.")

    if args.mode == "training":
        training_mode()
    elif args.mode == "product":
        product_mode()

if __name__ == "__main__":
    main() 