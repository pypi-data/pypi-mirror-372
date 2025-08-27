# Israeli Law Amender

## Project Overview

The Israeli Law Amender is a Python-based tool that automates the complex process of amending Israeli legislation. It leverages the power of Large Language Models (LLMs) to interpret amendment instructions and apply them to existing law documents, which are structured in JSON format. This project aims to significantly reduce the manual effort required to keep legal documents up-to-date, ensuring accuracy and consistency.

The tool is designed with two primary modes of operation: a `training` mode for batch processing and evaluation of the AI's performance, and a `product` mode for on-demand, interactive amendment of individual laws.

## Features

-   **AI-Powered Amendments**: Uses Google's Gemini models (default: `gemini-2.5-flash`) to generate Python scripts that perform the amendments.
-   **Dual-Mode Operation**:
    -   **Training Mode**: Processes large batches of amendments from CSV files, designed for model evaluation and fine-tuning.
    -   **Product Mode**: Interactive command-line interface for amending single laws with user-provided text.
-   **Comprehensive Validation**:
    -   In training mode, it performs a fuzzy matching score (Layer 1) and a more sophisticated LLM-based validation (Layer 3) to check the accuracy of the amendments.
    -   In product mode, it generates detailed HTML diff reports to visualize changes and runs Layer 3 validation.
-   **Configurable Settings**: Uses a `config.yaml` file to manage API keys, model parameters, default paths, and user preferences.
-   **Structured Output**: All generated files, including amended laws, scripts, and validation reports, are organized into a clear directory structure for easy review.
-   **Packaged for Convenience**: The tool is set up as a Python package, allowing for easy installation and command-line access.

## Workflow

### Training Mode

1.  **Input**: The training mode is initiated with the command `amend-law training` and reads predefined CSV files from the `Data/` directory. Each CSV contains a list of laws and the corresponding amendment texts.
2.  **Processing**: For each law, the script iterates through its amendments.
3.  **Generation**: For each amendment, it generates a prompt for the Gemini LLM, which returns a Python script designed to apply the amendment.
4.  **Execution**: The generated script is executed, applying the changes to the law's JSON structure.
5.  **Validation**: The amended law is validated against a "gold standard" version. The results, including fuzzy scores and Layer 3 validation scores, are logged.
6.  **Output**: All artifacts, including the amended JSONs, generated scripts, and validation summaries, are saved to their respective directories.

### Product Mode

1.  **Input**: The product mode is initiated with the `amend-law product` command. It then interactively prompts the user for:
    -   The location of the original law JSON files.
    -   A main directory for all outputs.
    -   An API key if not already set as an environment variable or in the configuration.
    -   The law to be amended (by ID or name) or a CSV file with a list of laws.
    -   The amendment text (pasted directly, from a `.txt` file, or from the CSV).
2.  **Processing**: Based on the user's input, the tool prepares the data for the amendment process.
3.  **Generation & Execution**: Similar to the training mode, it generates and executes a Python script for each amendment.
4.  **Reporting**: After each amendment is applied, it generates:
    -   An **HTML diff report** showing the exact changes between the previous and the newly amended version.
    -   A **Layer 3 validation report** (in JSON format) that provides an AI-based assessment of the amendment's accuracy.
5.  **Output**: The amended law, the diff report, and the validation report are saved in the user-specified output directory.

## Directory Structure

The project is organized as follows:

```
.
├── Data/                          # Contains CSV files with amendment data and original law JSONs
│   ├── JSON_Laws_v2/             # Location of the original, unamended law JSONs
│   ├── CSV/                      # CSV files with law data
│   ├── HTML/                     # HTML format law files
│   └── wikitext_laws/            # Text format law files from Wikipedia
├── israeli_law_amender/          # Main source code package
│   ├── __init__.py
│   ├── core.py                   # Main entry point and mode handlers
│   ├── config.py                 # Configuration management
│   ├── config.yaml               # Configuration file
│   ├── Generalized_amd_flow.py   # Core amendment processing logic
│   ├── laws_amending_script.py   # Training mode implementation
│   ├── product_flow_helpers.py   # Product mode helper functions
│   ├── validation/               # Validation scripts and tools
│   ├── CSV to json/              # Utilities for CSV to JSON conversion
│   ├── Wiki to txt/              # Wikipedia to text conversion tools
│   └── Wiki_txt_to_json/         # Text to JSON conversion utilities
├── Outputs/                      # Generated outputs from training mode
│   ├── Generated_Scripts_Generalized/ # AI-generated Python scripts
│   ├── JSON_amd*/               # Directories for amended JSONs, grouped by amendment number
│   ├── diff_reports/            # HTML difference reports
│   └── LLM_Responses/           # LLM responses and error logs
├── laws_to_review/              # Materials for low-scoring amendments collected for manual review
├── Logs/                        # Validation logs and reports
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup and configuration
└── README.md                    # This file
```

## Installation and Dependencies

To set up the project, it is recommended to use a virtual environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Double-N-A/israeli-law-amender.git
    cd israeli-law-amender
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the package:**
    The project is configured as a Python package. Installing it will also handle all required dependencies.
    ```bash
    pip install israeli-law-amender
    ```

### Dependencies

The main dependencies are:
-   `google-generativeai>=0.3.0` - Google's Generative AI library for Gemini models
-   `google-api-core>=2.0.0` - Core Google API functionality
-   `pandas>=1.3.0` - Data manipulation and analysis
-   `PyYAML>=6.0` - YAML configuration file processing
-   `thefuzz[speedup]>=0.19.0` - Fuzzy string matching for validation
-   `sentence-transformers>=2.2.0` - Sentence embedding models for validation

These are installed automatically when you run `pip install .`.

## Configuration

The tool uses a `config.yaml` file for configuration management. The configuration file is created automatically and includes:

-   **API Settings**: Google API key configuration
-   **Default Paths**: Default directories for input and output files
-   **Model Configuration**: Gemini model parameters (name, temperature, token limits, retry settings)
-   **User Preferences**: Saved default mode and other preferences

### Example config.yaml:
```yaml
api:
  google_api_key: 'your-api-key-here'
defaults:
  mode: product
model:
  name: gemini-2.5-flash
  temperature: 0.2
  max_output_tokens: 8192
  api_retry_limit: 3
  api_retry_delay_seconds: 10
  max_script_generation_attempts: 3
  max_execution_attempts: 2
paths:
  originals_path: Data/JSON_Laws_v2
  output_path: Outputs
```

## Usage

Before running the tool, make sure to set your Google API key either as an environment variable or in the configuration file:

### Option 1: Environment Variable
```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

### Option 2: Configuration File
The tool will prompt you for the API key on first run and save it to `config.yaml`.

After installation, you can use the command-line tool `amend-law`.

### Interactive Mode (Default)

To run the tool with interactive mode selection:
```bash
amend-law
```
The tool will guide you through:
1. Mode selection (Training or Product)
2. Path configuration
3. API key setup
4. Amendment processing

### Training Mode

To run the training mode directly:
```bash
amend-law training
```
The script will use the configured paths to find the input data and save the results.

### Product Mode

To run the interactive product mode directly:
```bash
amend-law product
```
The script will then guide you through the process of:
1. Selecting input type (single law or CSV file)
2. Providing law identifier or file path
3. Entering amendment text
4. Processing and generating reports

## Output Files

The tool generates several types of output files:

-   **Amended JSON Files**: Updated law documents with applied amendments
-   **Python Scripts**: Generated amendment scripts for transparency and debugging
-   **HTML Diff Reports**: Visual comparison between original and amended versions
-   **Validation Reports**: AI-based assessment of amendment accuracy
-   **Log Files**: Processing logs, errors, and validation summaries

## Convert Law and Validation Report JSONs to HTML

You can convert **any version of a law** (in the standard law JSON format) or **Layer 3 validation report JSONs** (e.g., `val3_report_*.json`) into clean, readable HTML files for easy review and sharing.

### Supported Input Types

- **Law JSONs:**  
  Converts the full structure of a law (with sections, chapters, etc.) into a styled, human-readable HTML document.
- **Validation Report JSONs:**  
  Converts Layer 3 validation reports into a summary HTML with tables for summary, validation, discrepancies, and assessment.

### Modes of Operation

You can use the script in several ways:

- **Non-interactive (CLI) mode:**  
  Specify input and output paths directly for batch or single-file conversion.
  ```bash
  python -m israeli_law_amender.json_to_html --input_path <input_json_or_directory> --output_path <output_html_or_directory>
  ```
  - **Single file:**  
    ```bash
    python -m israeli_law_amender.json_to_html --input_path Outputs/JSON_amd1/2003234_amd1.json --output_path Outputs/HTML/2003234_amd1.html
    ```
  - **Batch convert a directory:**  
    ```bash
    python -m israeli_law_amender.json_to_html --input_path Outputs/JSON_amd1/ --output_path Outputs/HTML/
    ```

- **Interactive mode:**  
  Run the script with no arguments and follow the prompts. You can:
  - Convert a single file or directory
  - Convert multiple directories
  - Convert all subdirectories within a parent directory

  The script will ask where to save the output files and guide you through the process.

### Output

- **Law JSONs:**  
  The output HTML preserves the law’s structure, sections, and formatting for easy reading and navigation.
- **Validation Report JSONs:**  
  The output HTML summarizes the validation results, including tables for instructions, validation accuracy, discrepancies, and a final assessment.

**Tip:**  
The script automatically detects the input type and applies the appropriate conversion logic.

## Authors

-   Hila Peled (hila.peled@mail.huji.ac.il)
-   Nitzan Naimi (nitzan.naimi@mail.huji.ac.il)  
-   Ohad Nahari (ohad.nahar@mail.huji.ac.il)
-   Ran Cohen (ran.cohen@mail.huji.ac.il)

## License

This project is licensed under the MIT License.

## Requirements

-   Python 3.8 or higher
-   Google API key with access to Gemini models
-   Internet connection for API calls