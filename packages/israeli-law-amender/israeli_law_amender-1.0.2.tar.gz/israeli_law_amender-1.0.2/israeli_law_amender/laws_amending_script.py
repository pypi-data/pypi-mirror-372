from pathlib import Path
import time, csv, re, sys, io, os, json, shutil, pandas as pd, google.generativeai as genai
from .Generalized_amd_flow import generate_llm_prompt, call_gemini_api, extract_python_code, execute_generated_code
from .logger import setup_summary_logger, log_amendment_result
from .validation.layer1_validation import read_law_json_to_flat_text, compare_fuzzy_match, generate_html_diff_report

AMENDMENTS_SCORES_PATH = Path("Data") / "amendments_scores.csv"
ORIGINAL_JSON_DIR = Path("Data") / "JSON_Laws_v2"
EDA_PATH = Path("Data") / "amendments_scores.csv"
RESULTS_SUMMARY_PATH = Path("Results_Summary.csv")
MODEL_NAME = "models/gemini-2.5-flash-preview-05-20"
MODEL_TEMP = 0.1
MAX_OUTPUT_TOKENS = 32768*2
AMD_COL_RE = re.compile(r"amd(\d+)_section")
GENERATED_SCRIPTS_DIR = Path("Outputs") / "Generated_Scripts_Generalized"
API_RETRY_DELAY_SECONDS = 10
VALIDATION_THRESHOLD = 80


def load_summary_df(results_summary_file_path, exploratory_data_path, max_amds):
    if results_summary_file_path.exists():
        df = pd.read_csv(results_summary_file_path)
        return df
    
    header = ["File", "LawID", "Law Name"]
    for i in range(1, max_amds+1):
        header += [f"amd{i} val1 score", f"amd{i} val3 score"]

    if not exploratory_data_path.exists():
        print(f"Laws names, ids and other data not found at {exploratory_data_path}. Skipping loading scores")
        return
    
    exploratory_df = pd.read_csv(exploratory_data_path)
    rows = []
    for _, row in exploratory_df.iterrows():
        new_row = {col: "-1" for col in header}
        new_row["File"] = ""                           
        new_row["LawID"] = str(row["LawID"])
        new_row["Law Name"] = row["name"]
        rows.append(new_row)

    df = pd.DataFrame(rows, columns=header)
    return df
    
def update_summary_score(df, amd_file, law_id, amd_idx, val1, val3):
    v1_col = f"amd{amd_idx} val1 score"
    v3_col = f"amd{amd_idx} val3 score"

    # Convert both to string for comparison
    mask = df["LawID"].astype(str) == str(law_id)
    
    if not mask.any():
        # Also ensure the new row uses string format
        df.loc[len(df)] = {**{c: -1 for c in df.columns}, "LawID": str(law_id)}
        mask = df["LawID"].astype(str) == str(law_id)

    df.loc[mask, "File"] = amd_file
    if val1 is not None:
        df.loc[mask, v1_col] = val1
    if val3 is not None:
        df.loc[mask, v3_col] = val3

def find_json_by_law_id_and_amd_id(law_id, laws_directory, amendment_idx=None, original_ind=None, gold_ind=None):
    if original_ind:
        for f_path in laws_directory.iterdir():
            if f_path.is_file() and "_original_oldid_" in f_path.stem and f_path.stem.endswith(f"LawID_{law_id}") and f_path.suffix.lower() == '.json':
                return f_path
    elif gold_ind:
        for f_path in laws_directory.iterdir():
            if f_path.is_file() and "_current_" in f_path.stem and f_path.stem.endswith(f"LawID_{law_id}") and f_path.suffix.lower() == '.json':
                return f_path
    else:
        for f_path in laws_directory.iterdir():
            if f_path.is_file() and f_path.suffix.lower() == '.json' and f_path.stem.endswith(f"{law_id}_amd{amendment_idx}"):
                return f_path

def validate_single_amendment(val_threshold, law_id, amd_idx, amd_text, gold_standard_text, model, amended_law_path, prev_law_version_path, api_retry_limit, val3=False):
    result_dict = {"success": None, "val1_score": None, "val3_score": None, "val3_feedback": None, "input_tokens": 0, "output_tokens": 0}

    # VALIDATION LAYER 1 (uses result and gold standard)
    if not amended_law_path.exists():
        print(f"     → Result json for law ID {law_id} and amendment #{amd_idx} not found. Skipping validation.")
        return result_dict
    
    result_text = read_law_json_to_flat_text(amended_law_path)    
    if result_text is None:
        print("Critical Error: Could not extract text from one or both JSON files. Aborting Layer 1 validation.")
        return result_dict
    
    val1_score = compare_fuzzy_match(result_text, gold_standard_text)
    result_dict["val1_score"] = val1_score

    if not val3:
        # If we are not doing validation layer 3, we can return the score directly
        if val1_score < val_threshold:
            print(f"     → 🔄 Amendment #{amd_idx} validation score {val1_score} is below the threshold {val_threshold}. Retrying generation")
            result_dict["success"] = False
            return result_dict
        else:
            print(f"     → ⏩ Amendment #{amd_idx} already satisfied with fuzzy_score of {val1_score}. Skipping generation")
            result_dict["success"] = True
            return result_dict
    else:
        # VALIDATION LAYER 3 (uses original law text, amendment text, and result law text)
        
        prev_law_text = read_law_json_to_flat_text(prev_law_version_path)

        val3_prompt = generate_validation3_prompt(
            original_law_text = prev_law_text,
            amendment_text=amd_text,
            amended_law_text=read_law_json_to_flat_text(amended_law_path)
        )
        #### the prompt validation also has tokens count. its up to us whether to count it or not.
    
        for retry in range(api_retry_limit):
            try:
                response = model.generate_content(val3_prompt)
                if not (response.candidates and len(response.candidates) > 0):
                    continue

                candidate = response.candidates[0]
                if candidate.finish_reason and candidate.finish_reason.name in ["STOP", "UNSPECIFIED"]:
                    result_dict["input_tokens"] += response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0
                    result_dict["output_tokens"] += response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0
                    
                    raw_response = getattr(response, 'text', None) or candidate.text
                    result_dict["val3_feedback"] = raw_response
                    match = re.search(r'"overall_score"\s*:\s*(\d+)', raw_response)
                    val3_score = int(match.group(1)) if match else None

                    if val3_score is None:
                        # print(f"Validation3 FAILURE - score not found in response on retry {retry+1}")
                        continue
                    else:
                        # print(f"Validation3 SUCCESSFUL - score for amendment #{amd_idx} is {val3_score}")
                        result_dict["val3_score"] = val3_score

                        if (val1_score + val3_score)/2 < val_threshold:
                            print(f"     → 🔄 Amendment #{amd_idx} validation score {(val1_score + val3_score)/2} is below the threshold {val_threshold}. Retrying generation")
                            result_dict["success"] = False # only upon score lower than threshold we set success to False (on generation failures it is None)
                            return result_dict
                        else:
                            print(f"     → ⏩ Amendment #{amd_idx} already satisfied with fuzzy_score of {val1_score} and validation3 score of {val3_score} (average score {(val1_score+val3_score)/2} >= validation threshold {val_threshold}). Skipping generation")
                            result_dict["success"] = True
                            return result_dict
            except Exception as e:
                print(f"Validation3 FAILURE - API call #{retry+1} failed: {e}")
                continue
        return result_dict

def generate_validation3_prompt(original_law_text, amendment_text, amended_law_text):
    if not original_law_text or not amendment_text or not amended_law_text:
        return
    full_prompt_text = f"""You are an expert legal assistant specializing in Israeli legislation. Your task is to validate if legislative amendments have been correctly incorporated into a base law text by another AI model. 
    Provided Texts:
    1.  **Original Law Text (A):**
        ```text
        {original_law_text}
        ```

    2.  **Amendment Text (B) (raw text of the amending instructions):**
        ```text
        {amendment_text}
        ```

    3.  **Consolidated Law Text (C) (Output from the AI model being validated):**
        ```text
        {amended_law_text}
        ```

    Your Validation Task:

    1.  **Analyze Amendment (B):** Carefully analyze the Amendment Text (B) to understand all the specific changes it mandates for the Original Law Text (A). For each distinct instruction in the amendment:
        * Identify the type of change (addition, deletion, replacement, renumbering).
        * Pinpoint the exact location in Original Law (A).
        * Note the old text (if any) and the new text (if any).

    2.  **Validate Consolidated Text (C):** Compare those required changes against Text (C). For each instruction:
        * **implemented**: (Yes/No/Partially)
        * **accuracy**: (Accurate / Minor Discrepancies / Major Discrepancies)
        * **location**: (Correct / Incorrect)

    3.  **Identify Other Discrepancies:**
        * **missing_changes**: amendments from B not found in C.
        * **incorrect_changes**: applied inaccurately.
        * **unexpected_changes**: differences in C not mandated by B.

    4.  **Overall Assessment:**
        * **text**: brief human-readable summary (e.g., "Highly accurate...", etc.)
        * **overall_score**: integer 0–100 for compliance accuracy.

    **Output & Parsing Requirements:**
    Your response **must** be a single JSON object with these fields **in this order**:

    1. **overall_score** (integer)
    2. **summary** (array of objects):
    - Each object:  
        `{{ "instruction": <number>, "type": <string>, "location": <string>, "old_text": <string|null>, "new_text": <string|null> }}`
    3. **validation** (array of objects):
    - Each object:  
        `{{ "instruction": <number>, "implemented": <"Yes"|"No"|"Partially">, "accuracy": <string>, "location": <string> }}`
    4. **discrepancies** (object with arrays):
    - `missing_changes`: [<instruction numbers>]
    - `incorrect_changes`: [<instruction numbers>]
    - `unexpected_changes`: [<descriptions>]
    5. **assessment** (object):
    - `{{ "text": <string> }}`

    All other text **must** be omitted so that the JSON can be parsed automatically.
    The code I will run on the prompt to parse the score is as follows:
    ```python
    response = model.generate_content(prompt=val3_prompt)
    candidate = response.candidates[0]
    raw_response = getattr(response, 'text', None) or candidate.text
    val3_score = response_data.get("overall_score", 0)
    ```
    """

    return full_prompt_text

def implement_amendments_per_file(laws_jsons_dir,amendments_file_path,model,val_threshold,generated_code_paths,max_execution_attempts,max_generation_attempts,api_retry_delay_seconds, max_amds, sum_df):
    """
    receives a file of amendments\n
    iterates on file rows (laws)\n
    per row implements amendments (given by specific column names)\n
    logs the results into a csv file
    """
    implementation_start_time = time.time()
    implementation_input_tokens = 0
    implementation_output_tokens = 0
    val3_input_tokens = 0
    val3_output_tokens = 0

    rows_totally_succeeded = 0
    rows_totally_failed = 0
    rows_partially_succeeded = 0
    rows_skipped = 0

    amendments_succeeded = 0
    amendments_failed = 0
    amendments_skipped = 0
    total_amendments = 0

    csv_path_str = str(amendments_file_path)

    if not amendments_file_path.exists():
        print(f"⚠️ MAIN ERROR: Amendments Data CSV file not found at {amendments_file_path}")
        return
    
    if not laws_jsons_dir.exists():
        print(f"⚠️ MAIN ERROR: Laws JSON directory not found at {laws_jsons_dir}")
        return
    
    try:
        summary_logger = setup_summary_logger()
    except Exception as e:
        print(f"⚠️ MAIN ERROR: logger initialization failure:\n{e}")
        return
    
    with open(amendments_file_path, newline="", encoding="utf-8") as f:
        amendments_data = list(csv.DictReader(f))

    total_rows = len(amendments_data)
    if total_rows == 0:
        print(f"⚠️ MAIN ERROR: No data found in the amendments CSV file at {amendments_file_path}.")
        return
    
    # =================================================================
    # First loop - iterate on rows
    # =================================================================
    for row_idx, row in enumerate(amendments_data, start=1):
        row_start_time = time.time()
        row_input_tokens = 0
        row_output_tokens = 0

        row_amendments_failed = 0
        row_amendments_succeeded = 0
        row_amendments_skipped = 0
        row_total_amendments = 0

        law_id = row.get("LawID", "").strip()
        print(f"\n=== Row {row_idx}/{total_rows} • Law ID {law_id} ===")

        if not law_id:
            print("⚠️ LAW ERROR (id not found) - SKIPPING ROW")
            failure_reason = "failure in main() - missing law_id"
            log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=0, success=False,reason=failure_reason)
            rows_skipped += 1
            continue

        original_json_path = find_json_by_law_id_and_amd_id(law_id, laws_jsons_dir, original_ind=True)
        if not original_json_path:
            print("⚠️ LAW ERROR (original law json not found) - SKIPPING ROW")
            failure_reason = f"failure in main() - original JSON not found in {laws_jsons_dir}"
            log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=0, success=False,reason=failure_reason)
            rows_skipped += 1
            continue

        amendment_cols = sorted([c for c in row if AMD_COL_RE.fullmatch(c) and row[c].strip()],key=lambda c: int(AMD_COL_RE.fullmatch(c).group(1)))
        if not amendment_cols:
            print("⚠️ LAW ERROR (no amendments found) - SKIPPING LAW")
            failure_reason = f"failure in main() - no amendments found in CSV"
            log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=0, success=False,reason=failure_reason)
            rows_skipped += 1
            continue

        max_amendments = len(amendment_cols)
        prev_version_path = original_json_path
        gold_standard_file = find_json_by_law_id_and_amd_id(law_id, laws_jsons_dir, gold_ind=True) # initializing this each time is not efficient. this can be done once per law_id
        gold_standard_text = read_law_json_to_flat_text(gold_standard_file)
        # =================================================================
        # Second loop - iterate on amendments per row
        # =================================================================
        for amd_idx, col in enumerate(amendment_cols, start=1):
            # --------------------------------
            # ---- assign amendment parameters
            amendment_text = row[col].strip()
            print(f"  → Amendment {amd_idx}/{max_amendments}")
            out_dir  = Path("Outputs") / f"JSON_amd{max_amds}"
            out_dir.mkdir(exist_ok=True)
            amended_json_path = out_dir / f"{law_id}_amd{amd_idx}.json"
            row_total_amendments += 1

            validation_dict = validate_single_amendment(val_threshold=val_threshold, law_id=law_id, amd_idx=amd_idx, amd_text=amendment_text, gold_standard_text=gold_standard_text, model=model, amended_law_path=amended_json_path, prev_law_version_path=prev_version_path, api_retry_limit=max_generation_attempts, val3=True)
            val3_input_tokens += validation_dict["input_tokens"]
            val3_output_tokens += validation_dict["output_tokens"]
            update_summary_score(
                sum_df,             # df
                csv_path_str,       # amd_file
                law_id,             # law_id
                amd_idx,            # amendment index (see note below)
                validation_dict["val1_score"],
                validation_dict["val3_score"],
            )


            if validation_dict["success"]:
                log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=amd_idx, success=True,reason ="amendment already satisfied")
                row_amendments_skipped += 1
                continue

            # ----------------------------------
            # ---- GENERATE PROMPT PER AMENDMENT
            prompt = generate_llm_prompt(str(prev_version_path),amendment_text,str(amended_json_path)) # this also has tokens count, if we want to count it

            if "Error reading original JSON" in prompt:
                print(f"  → ⚠️ AMENDMENT #{amd_idx} ERROR - SKIPPING AMENDMENT")
                failure_reason = f"failure in generate_llm_prompt() - error with opening original json file: {str(prev_version_path)}"
                log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=amd_idx, success=False,reason=failure_reason)
                row_amendments_skipped += 1
                continue

            # build a list of parts in the order you want to consume them
            feedback = validation_dict["val3_feedback"]
            gen_code_path = generated_code_paths / f"{law_id}_amd{amd_idx}_amending_script.py"
            extend_prompt_condition = feedback and gen_code_path.is_file() and amended_json_path.is_file() 
            if extend_prompt_condition:
                feedback_path = generated_code_paths / f"{law_id}_amd{amd_idx}_feedback.json"
                with open(feedback_path, "w", encoding="utf-8") as f:
                    json.dump(feedback, f, ensure_ascii=False, indent=2)
                
                feedback_file = genai.upload_file(
                    path=str(feedback_path),
                    display_name=feedback_path.name,
                    mime_type="text/plain" 
                )
                script_file = genai.upload_file(
                    path=str(gen_code_path),
                    display_name=gen_code_path.name
                )
                result_file = genai.upload_file(
                    path=str(amended_json_path),
                    display_name=amended_json_path.name,
                    mime_type="text/plain" 
                )

                prompt += f"\n\nYou will be provided with multiple files from a previous attempt to amend this law:\n1. Feedback file with validation results as judged by the validation unit.\n2. The script file with the code that was generated in the previous attempt.\n3. The result file with the law as it was amended by the previous attempt.\n\nUse these files to improve your generation of the amending script."
            
                parts = [prompt, feedback_file, script_file, result_file]

                print(f"     → using feedback file {feedback_path.name} and script file {gen_code_path.name} to improve generation.")
            else:
                parts = [prompt]
                print("     → no feedback file or script file found, using only the prompt for generation.")
                # if not feedback:
                #     print("     → no feedback provided, generation will not be extended with previous results.")
                # if not gen_code_path.is_file():
                #     print(f"     → no script file found at {gen_code_path}, generation will not be extended with previous results.")
                # if not amended_json_path.is_file():
                #     print(f"     → no result file found at {amended_json_path}, generation will not be extended with previous results.")
            # =================================================================
            # Third loop - Iterate on execution attempts per amendment
            # =================================================================
            generated_code              = None
            code_executed_successfully  = False

            for amendment_execution_attempt in range(max_execution_attempts):
                # =================================================================
                # Fourth loop - Iterate on generation attempts per execution
                # =================================================================
                print(f"     → beginning execution attempt {amendment_execution_attempt+1}/{max_execution_attempts}.")
                
                for script_generation_attempt in range(max_generation_attempts):
                    # --------------------------------------------------
                    # ---- ATTEMPT TO CALL API, RECORD GEN TIME & TOKENS
                    t0 = time.time()
                    formatted_time = time.strftime("%H:%M", time.localtime(t0))
                    print(f"        → attempting generation {script_generation_attempt+1}/{max_generation_attempts} at: {formatted_time}")
                    llm_resp = call_gemini_api(parts, model)
                    row_input_tokens  += llm_resp.get("input_tokens", 0)
                    row_output_tokens += llm_resp.get("output_tokens", 0)

                    # --------------------------------------
                    # ---- API CALLING FAILED - LOG & REPEAT
                    if llm_resp["error"]:
                        failure_reason = f"failure in call_gemini_api() - {llm_resp['error']} [AMD #{amd_idx}, EXEC #{amendment_execution_attempt+1}, GEN #{script_generation_attempt+1}]"
                        log_amendment_result(summary_logger, amd_file=csv_path_str,row_idx=row_idx, law_id=law_id, amendment=amd_idx, success=False,reason=failure_reason)
                        if script_generation_attempt < max_generation_attempts-1:
                            time.sleep(api_retry_delay_seconds / 2)
                        continue
                    
                    # -----------------------------------------
                    # ---- API CALLING SUCCEEDED - EXTRACT CODE
                    generated_code = extract_python_code(llm_resp["text"])
                    if generated_code:
                        with open(gen_code_path, 'w', encoding='utf-8') as f:
                            f.write(generated_code)
                        break  # exit code generation loop

                # if all code generation attempts weren't fruitful - proceed to next execution attempt
                if not generated_code:
                    print(f"     → execution attempt {amendment_execution_attempt+1}/{max_execution_attempts} did not succeed.")
                    continue

                # if code generation was successful at any of the execution attempts - try to execute the generated code
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

                if code_executed_successfully:       
                    # success and failure updates are further down
                    prev_version_path = amended_json_path   # next amendment builds on this
                    log_amendment_result(summary_logger, amd_file=csv_path_str, row_idx=row_idx, law_id=law_id, amendment=amd_idx, success=True,reason="amendment applied successfully")
                    break

                # if the code wasn't executed successfully, proceed to the next amendment_execution_attempt
                else:
                    print(f"     → execution attempt {amendment_execution_attempt+1}/{max_execution_attempts} did not succeed.\n")
                    failure_reason = f"failure in execute_generated_code() - returned False"
                    log_amendment_result(summary_logger, amd_file=csv_path_str, row_idx=row_idx, law_id=law_id, amendment=amd_idx, success=False,reason=failure_reason)
            
            if not code_executed_successfully:
                row_amendments_failed += 1
                print(f"  → ❌ AMENDMENT #{amd_idx} FAILURE - AMENDMENT FAILED")
            else:
                row_amendments_succeeded += 1
                print(f"  → ✅ AMENDMENT #{amd_idx} APPLIED SUCCESSFULLY")

        
        # ========== row summary
        implementation_input_tokens += row_input_tokens
        implementation_output_tokens += row_output_tokens

        amendments_failed += row_amendments_failed
        amendments_succeeded += row_amendments_succeeded
        amendments_skipped += row_amendments_skipped
        total_amendments += row_total_amendments

        if row_amendments_succeeded == total_amendments:
            rows_totally_succeeded += 1
        elif row_amendments_succeeded > 0:
            rows_partially_succeeded += 1
        else:
            if not row_amendments_skipped:
                rows_totally_failed += 1
            elif row_amendments_skipped == row_total_amendments:
                rows_skipped += 1

        row_end_time = time.time()
        row_time_taken = row_end_time - row_start_time
        print(f"Row time elapsed: {row_time_taken/60:.1f} min")
    
    sum_df.to_csv(RESULTS_SUMMARY_PATH, index=False, encoding='utf-8')
    # ========== final summary
    elapsed = time.time() - implementation_start_time
    print("\n\n======= SUMMARY =======")
    print(f"Amendments Implementation Time                                               : {elapsed/60:.1f} min")
    print(f"Input tokens | output tokens | Val3 input tokens | Val3 output tokens        : {implementation_input_tokens} | {implementation_output_tokens} | {val3_input_tokens} | {val3_output_tokens}")
    print(f"Rows succeeded | partially succeeded | totally failed | skipped ||| TOTAL    : {rows_totally_succeeded} | {rows_partially_succeeded} | {rows_totally_failed} | {rows_skipped} ||| {total_rows}")
    print(f"Amendments succeeded | failed | skipped ||| TOTAL                            : {amendments_succeeded} | {amendments_failed} | {amendments_skipped} ||| {total_amendments}")

def read_utf8(path):
    return path.read_text(encoding='utf-8')

def collect_low_score_materials(
        summary_excel_path: Path,
        original_json_dir: Path,
        amendments_csv_dir: Path,
        generated_scripts_dir: Path,
        threshold: float = 80.0
):
    """
    Walk through Results_Summary.xlsx and copy all artefacts for any amendment
    whose average(val1, val3) < threshold into a folder  '<LawID>_materials/'.
    The folder will contain:
        ├─ original_{LawID}.json
        ├─ amendment_{i}.txt
        ├─ gemini_script_{i}.py
        ├─ val3_report_{i}.json
        ├─ diff_{i}.html
        ├─ amended_{i}.json
        └─ val3_prompt_{i}.txt
    """
    df = pd.read_excel(summary_excel_path)

    mother_dir = Path("laws_to_review")
    mother_dir.mkdir(exist_ok=True)

    for _, row in df.iterrows():
        law_id = row["LawID"]
        max_i = int(row['File']) if pd.notna(row['File']) else 0
        if max_i == 0:
            continue

        # 1. original JSON ----------------------------------------------------------
        original_json_path = find_json_by_law_id_and_amd_id(law_id, original_json_dir, original_ind=True)

        csv_path = amendments_csv_dir / f"{max_i}amd.csv"
        csv_df = pd.read_csv(csv_path)

        for i in range(1, max_i + 1):
            v1 = row.get(f"amd{i} val1 score", -1)
            v3 = row.get(f"amd{i} val3 score", -1)
            
            if v1 == -1 and v3 == -1:
                # print(f"Skipping Law ID {law_id} amendment {i} due to missing scores.")
                continue
            if (v1 + v3) / 2 >= threshold:
                # print(f"Skipping Law ID {law_id} amendment {i} due to average score {(v1 + v3) / 2:.2f} >= threshold {threshold}.")
                continue
            print(f"Collecting materials for Law ID {law_id} amendment {i} with average score {(v1 + v3) / 2:.2f} < threshold {threshold}.")
            # --- create / reuse folder -------------------------------------------------
            mat_dir = mother_dir / Path(f"{law_id}_materials")
            mat_dir.mkdir(exist_ok=True)
            shutil.copy(original_json_path, mat_dir / f"original_{law_id}.json")

            # 2. amendment text ---------------------------------------------------------
            filtered_df = csv_df[csv_df["LawID"] == law_id]
            amd_col = f"amd{i}_section"
            try:
                amd_text = filtered_df[amd_col].iloc[0]
            except IndexError:
                print(f"amendment text for law ID {law_id} and amendment {i} not found in CSV file {csv_path}. Skipping.")
            (mat_dir / f"{law_id}_amendment_{i}.txt").write_text(str(amd_text), encoding="utf-8")

            # 3. gemini script ----------------------------------------------------------
            gen_code_path = generated_scripts_dir / f"{law_id}_amd{i}_amending_script.py"
            shutil.copy(gen_code_path, mat_dir / f"gemini_script_{i}.py")
            
            # 4. val-3 report -----------------------------------------------------------
            feedback_path = generated_scripts_dir / f"{law_id}_amd{i}_feedback.json"
            shutil.copy(feedback_path, mat_dir / f"val3_report_{i}.json")

            # 5. HTML diff --------------------------------------------------------------
            llm_path  = (Path("Outputs") / f"JSON_amd{max_i}" / f"{law_id}_amd{i}.json")
            llm_text = read_utf8(llm_path)
            try:
                gold_path = (mat_dir / f"original_{law_id}.json") if i==1 else (Path("Outputs") / f"JSON_amd{max_i}" / f"{law_id}_amd{i-1}.json")
                gold_text = read_utf8(gold_path)
                diff_html = generate_html_diff_report(gold_text, llm_text)
                (mat_dir / f"diff_amd{i}.html").write_text(diff_html, encoding="utf-8")
            except FileNotFoundError as e:
                print(f"Error generating HTML diff for Law ID {law_id} amendment {i}: {e}")
                continue

            # 6. amended JSON -----------------------------------------------------------
            shutil.copy(Path("Outputs") / f"JSON_amd{max_i}" / f"{law_id}_amd{i}.json", mat_dir / f"amended_{i}.json")

            # 7. val-3 prompt -----------------------------------------------------------
            val3_prompt = generate_validation3_prompt(original_law_text = gold_text,amendment_text=amd_text,amended_law_text=read_law_json_to_flat_text(Path("Outputs") / f"JSON_amd{max_i}" / f"{law_id}_amd{i}.json"))
            (mat_dir / f"val3_prompt_{i}.txt").write_text(val3_prompt, encoding="utf-8")

            # 8. generation prompt ------------------------------------------------------
            prev_version_path = find_json_by_law_id_and_amd_id(law_id, original_json_dir, amendment_idx=i-1) if i > 1 else original_json_path
            amended_json_path = Path("Outputs") / f"JSON_amd{max_i}" / f"{law_id}_amd{i}.json"
            prompt = generate_llm_prompt(str(prev_version_path),amd_text,str(amended_json_path))
            prompt += f"\n\nYou will be provided with multiple files from a previous attempt to amend this law:\n1. Feedback file with validation results as judged by the validation unit.\n2. The script file with the code that was generated in the previous attempt.\n3. The result file with the law as it was amended by the previous attempt.\n\nUse these files to improve your generation of the amending script."
            (mat_dir / f"generation_prompt.txt").write_text(prompt, encoding="utf-8")









def main(training_paths=None):
    """
    Main training function that can accept configurable paths.
    
    Args:
        training_paths: Dictionary containing configured paths for training mode.
                       If None, uses hardcoded defaults for backward compatibility.
    """
    # Use configured paths or fall back to hardcoded defaults
    if training_paths:
        data_dir = training_paths['amendments_data_dir']
        original_json_dir = training_paths['original_laws_dir'] 
        generated_scripts_dir = training_paths['generated_scripts_dir']
        amended_output_dir = training_paths['amended_output_dir']
    else:
        # Backward compatibility with hardcoded paths
        data_dir = Path("Data")
        original_json_dir = ORIGINAL_JSON_DIR
        generated_scripts_dir = GENERATED_SCRIPTS_DIR
        amended_output_dir = Path("Outputs")
    
    amd_files = [(int(re.search(r'(\d+)amd', f.name).group(1)), f) for f in data_dir.glob("*amd.csv") if re.search(r'(\d+)amd', f.name)]
    amd_files.sort(key=lambda x: x[0])
    
    # Use configured paths for summary files
    results_summary_path = amended_output_dir / "Results_Summary.csv"
    eda_path = data_dir / "amendments_scores.csv"
    
    summary_df = load_summary_df(results_summary_path, eda_path, max_amds=len(amd_files))
    
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    ai_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",  # Updated to a current model name
         safety_settings=[
             {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
             {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
             {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
             {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
         ],
         generation_config=genai.types.GenerationConfig(
             max_output_tokens=MAX_OUTPUT_TOKENS,
             temperature=MODEL_TEMP
         )
    )
    
    for amd_number, csv_file_path in amd_files:
        print(amd_number, csv_file_path)
        if amd_number == 12:
            implement_amendments_per_file(original_json_dir, csv_file_path, ai_model, VALIDATION_THRESHOLD, generated_scripts_dir, 2, 3, API_RETRY_DELAY_SECONDS, amd_number, summary_df)

    # collect_low_score_materials(
    #     summary_excel_path=results_summary_path,
    #     original_json_dir=original_json_dir,
    #     amendments_csv_dir=data_dir,
    #     generated_scripts_dir=generated_scripts_dir,
    #     threshold=80
    # )

if __name__ == "__main__":
    # When run directly, use hardcoded defaults for backward compatibility
    main()