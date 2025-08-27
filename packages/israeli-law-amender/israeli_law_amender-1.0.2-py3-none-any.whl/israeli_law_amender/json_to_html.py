import os
import json
import argparse
import html

# This CSS will be embedded in the generated HTML for a clean, readable output.
EMBEDDED_CSS_STYLE = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 2rem auto;
        padding: 0 1rem;
        direction: rtl; /* Right-to-Left for Hebrew */
        text-align: right;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: "David Libre", "Times New Roman", Times, serif;
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    h1 {
        text-align: center;
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 0.5em;
        font-size: 2.5em;
    }
    h2 { /* Chapter */
        font-size: 2em;
        color: #2980b9;
        border-bottom: 1px solid #ecf0f1;
        padding-bottom: 0.3em;
    }
    h3 { /* SubChapter */
        font-size: 1.75em;
        color: #3498db;
    }
    h4 { /* Section */
        font-size: 1.5em;
        color: #16a085;
    }
    .component {
        margin-bottom: 1em;
        padding-right: 1em;
        border-right: 3px solid transparent;
    }
    .component.section {
        border-right-color: #ecf0f1;
        padding-right: 1.5em;
        margin-top: 2em;
    }
    .component.subsection > p:first-of-type {
        display: inline; /* Allows number to stay on the same line */
    }
    .component.subsection .number, .component.item .number {
        font-weight: bold;
        color: #7f8c8d;
        margin-left: 0.5em;
    }
    ul {
        list-style-type: none;
        padding-right: 20px;
    }
    li.item {
        margin-bottom: 0.5em;
    }
    /* Indentation for nested items based on level */
    .level-2 { margin-right: 2em; }
    .level-3 { margin-right: 4em; }
    .level-4 { margin-right: 6em; }
    .meta-info {
        text-align: center;
        color: #95a5a6;
        font-size: 0.9em;
        margin-bottom: 2em;
    }
</style>
"""

class JsonToHtmlConverter:
    """
    Converts a law JSON structure back into a readable HTML file.
    """
    def __init__(self, law_json_data):
        # The actual law data is inside the 'parsed_law' key
        self.data = law_json_data.get("parsed_law", {})
        if not self.data:
            raise ValueError("JSON does not contain a 'parsed_law' key.")

    def convert_to_html(self):
        """
        Generates the full HTML document as a string.
        """
        title = html.escape(self.data.get("law_title_for_version", "Law Document"))
        version_id = self.data.get("law_version_id", "N/A")
        root_component = self.data.get("structure")

        if not root_component:
            return "<html><head><title>Error</title></head><body>No structure found in JSON.</body></html>"

        # Start building the HTML document
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="he">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"  <title>{title}</title>",
            '  <link rel="preconnect" href="https://fonts.googleapis.com">',
            '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '  <link href="https://fonts.googleapis.com/css2?family=David+Libre:wght@400;700&display=swap" rel="stylesheet">',
            EMBEDDED_CSS_STYLE,
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            f'<div class="meta-info">Law Version ID: {version_id}</div>'
        ]

        # Recursively render the main structure
        body_content = self._render_component(root_component)
        html_parts.append(body_content)

        # Close the document
        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)


    def _render_component(self, component):
        """
        Recursively renders a single law component and its children into HTML.
        """
        if not component:
            return ""

        comp_type = component.get("type")
        comp_id = component.get("id")
        # Support both old and new field names
        number = component.get("number") or component.get("number_text")
        title = component.get("title") or component.get("header_text")
        text = component.get("text") or component.get("body_text")
        level = component.get("level", 1) # Default level for items
        children = component.get("children", [])

        # Using a list to build the string is more efficient
        parts = []
        
        # --- 1. Generate Opening Tag and Main Content ---
        # Note: The original JSON parser uses a mix of schema types and its own types.
        # We handle the types produced by OlawToTargetJsonParser: Law, Chapter, SubChapter, Section, SubSection, Clause.
        # We also handle types from the schema example for compatibility: Paragraph, Item.
        
        css_class = f"component {comp_type.lower()}"
        div_id = f'id="comp-{comp_id}"' if comp_id else ""

        if comp_type == "Law":
            # The Law component is the root, its title is already the H1.
            # We just process its children.
            pass
        elif comp_type in ["Chapter", "Sign"]:
            parts.append(f'<div {div_id} class="{css_class}">')
            if title: parts.append(f'<h2>{html.escape(title)}</h2>')
        elif comp_type == "SubChapter":
            parts.append(f'<div {div_id} class="{css_class}">')
            if title: parts.append(f'<h3>{html.escape(title)}</h3>')
        elif comp_type == "Section":
            parts.append(f'<div {div_id} class="{css_class}">')
            title_part = f': {html.escape(title)}' if title else ''
            number_part = f'סעיף {html.escape(number)}' if number else ''
            parts.append(f'<h4>{number_part}{title_part}</h4>')
        elif comp_type in ["Paragraph", "SubSection"]:
            parts.append(f'<div {div_id} class="{css_class}">')
            if number: parts.append(f'<span class="number">{html.escape(number)}</span>')
        elif comp_type in ["Item", "Clause"]:
            # List items are handled specially with <li>
            css_class += f" level-{level}"
            parts.append(f'<li {div_id} class="{css_class}">')
            if number: parts.append(f'<span class="number">{html.escape(number)}</span> ')
        
        # --- 2. Add Text Content ---
        if text:
            # Escape text and replace newlines with <br> to preserve formatting
            formatted_text = html.escape(text).replace('\n', '<br>\n')
            # For block-level components, wrap text in a paragraph. For list items, just append.
            if comp_type in ["Section", "Paragraph", "SubSection"]:
                 parts.append(f'<p>{formatted_text}</p>')
            else:
                 parts.append(formatted_text)

        # --- 3. Render Children Recursively ---
        if children:
            # If the children are list items, wrap them in a <ul> tag
            is_list = children[0].get("type") in ["Item", "Clause"]
            if is_list:
                parts.append("<ul>")
            
            for child in children:
                parts.append(self._render_component(child))

            if is_list:
                parts.append("</ul>")

        # --- 4. Generate Closing Tag ---
        if comp_type in ["Item", "Clause"]:
            parts.append("</li>")
        elif comp_type != "Law":
            # The Law component is not wrapped in a div
            parts.append("</div>")

        return "\n".join(parts)


def process_directory_or_file(input_path, output_path_or_dir):
    """Processes a single JSON file or a directory of JSON files."""
    if os.path.isdir(input_path):
        os.makedirs(output_path_or_dir, exist_ok=True)
        if not os.path.isdir(output_path_or_dir):
            print(f"Error: Output path '{output_path_or_dir}' exists and is not a directory.")
            return

        for filename in os.listdir(input_path):
            if filename.endswith(".json"):
                input_filepath = os.path.join(input_path, filename)
                output_filename = filename.replace(".json", ".html")
                output_filepath = os.path.join(output_path_or_dir, output_filename)
                
                print(f"Converting: {input_filepath} -> {output_filepath}")
                convert_single_file(input_filepath, output_filepath)
    elif os.path.isfile(input_path):
        if os.path.isdir(output_path_or_dir):
            output_filename = os.path.basename(input_path).replace(".json", ".html")
            final_output_path = os.path.join(output_path_or_dir, output_filename)
            os.makedirs(output_path_or_dir, exist_ok=True)
        else: # Output is a specific file path
            final_output_path = output_path_or_dir
            output_dir_check = os.path.dirname(final_output_path)
            if output_dir_check:
                os.makedirs(output_dir_check, exist_ok=True)

        print(f"Converting: {input_path} -> {final_output_path}")
        convert_single_file(input_path, final_output_path)
    else:
        print(f"Error: Input path '{input_path}' is not a valid file or directory.")

def convert_single_file(input_filepath, output_filepath):
    """Loads a single JSON file, converts it, and saves it as HTML."""
    try:
        if 'val3_report' in os.path.basename(input_filepath):
            # Special handler for val3_report files - using exact logic from p.py
            with open(input_filepath, encoding="utf-8") as f:
                raw = f.read()
            
            # Remove outer quotes if the entire content is wrapped in quotes
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            
            # Replace escaped newlines and other escape sequences
            raw = raw.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            
            # Clean up any markdown-style JSON blocks
            def clean_json_string(json_str):
                # Remove triple backticks and "json" if present
                import re
                json_str = re.sub(r'^```json\s*', '', json_str)
                json_str = re.sub(r'```$', '', json_str)
                json_str = json_str.strip()
                return json_str
            
            json_str = clean_json_string(raw)
            
            # Parse the JSON with multiple attempts to handle malformed JSON
            data = None
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"First JSON decode attempt failed: {e}")
                # Debug: print the problematic area
                error_pos = getattr(e, 'pos', 0)
                start = max(0, error_pos - 50)
                end = min(len(json_str), error_pos + 50)
                print(f"Error area: ...{json_str[start:end]}...")
                
                # Try to fix the specific issue with double quotes in new_text fields
                try:
                    import re
                    # This specific pattern handles the malformed quotes in new_text fields
                    # Pattern: "new_text": ""content""  -> "new_text": "content"
                    fixed_json = re.sub(r'"new_text":\s*""([^"]*(?:[^"\\]|\\.)*)""', r'"new_text": "\1"', json_str)
                    data = json.loads(fixed_json)
                    print("Successfully parsed JSON after fixing new_text quotes")
                except json.JSONDecodeError as e2:
                    print(f"Second attempt failed: {e2}")
                    try:
                        # More aggressive quote fixing
                        # Fix any \" patterns that aren't properly escaped
                        lines = json_str.split('\n')
                        fixed_lines = []
                        for line in lines:
                            # Fix lines with malformed quotes in string values
                            if '"new_text":' in line and '""' in line:
                                # Extract the problematic value and fix it
                                import re
                                match = re.search(r'"new_text":\s*""([^"]*)"([^"]*)"', line)
                                if match:
                                    # Reconstruct the line with proper escaping
                                    content = match.group(1) + '"' + match.group(2)
                                    content = content.replace('"', '\\"')  # Properly escape quotes
                                    line = re.sub(r'"new_text":\s*""[^"]*"[^"]*""', f'"new_text": "{content}"', line)
                            fixed_lines.append(line)
                        fixed_json = '\n'.join(fixed_lines)
                        data = json.loads(fixed_json)
                        print("Successfully parsed JSON after line-by-line quote fixing")
                    except (json.JSONDecodeError, Exception) as e3:
                        print(f"All attempts failed: {e3}")
                        # Final fallback: create a minimal valid structure
                        print("Creating fallback data structure")
                        data = {
                            "overall_score": "N/A",
                            "summary": [],
                            "validation": [],
                            "discrepancies": {"missing_changes": [], "incorrect_changes": [], "unexpected_changes": []},
                            "assessment": {"text": "Failed to parse original JSON data"}
                        }
            
            if data is None:
                print("Failed to parse JSON data")
                return

            def json_to_html(data):
                import re
                html_parts = [
                    '<!DOCTYPE html>',
                    '<html lang="en">',
                    '<head>',
                    '<meta charset="UTF-8">',
                    '<title>Validation Report</title>',
                    '<style>',
                    'body { font-family: Arial, sans-serif; margin: 2em; }',
                    'h1, h2 { color: #2c3e50; }',
                    'table { border-collapse: collapse; width: 100%; margin-bottom: 2em; }',
                    'th, td { border: 1px solid #ccc; padding: 8px; }',
                    'th { background: #f4f4f4; }',
                    '.rtl { direction: rtl; unicode-bidi: embed; }',
                    '</style>',
                    '</head>',
                    '<body>',
                    '<h1>Validation Report</h1>'
                ]

                html_parts.append(f"<h2>Overall Score: {data.get('overall_score', 'N/A')}</h2>")

                # Summary
                html_parts.append("<h2>Summary</h2>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Instruction</th><th>Type</th><th>Location</th><th>Old Text</th><th>New Text</th></tr>")
                for item in data.get("summary", []):
                    new_text = item.get("new_text", "") or ""
                    # If new_text contains Hebrew, add RTL class
                    rtl_class = ' class="rtl"' if re.search(r'[\u0590-\u05FF]', new_text) else ''
                    html_parts.append(
                        f"<tr>"
                        f"<td>{html.escape(str(item.get('instruction', '')))}</td>"
                        f"<td>{html.escape(str(item.get('type', '')))}</td>"
                        f"<td>{html.escape(str(item.get('location', '')))}</td>"
                        f"<td>{html.escape(str(item.get('old_text', '')))}</td>"
                        f"<td{rtl_class}>{html.escape(new_text)}</td>"
                        f"</tr>"
                    )
                html_parts.append("</table>")

                # Validation
                html_parts.append("<h2>Validation</h2>")
                html_parts.append("<table>")
                html_parts.append("<tr><th>Instruction</th><th>Implemented</th><th>Accuracy</th><th>Location</th></tr>")
                for item in data.get("validation", []):
                    html_parts.append(
                        f"<tr>"
                        f"<td>{html.escape(str(item.get('instruction', '')))}</td>"
                        f"<td>{html.escape(str(item.get('implemented', '')))}</td>"
                        f"<td>{html.escape(str(item.get('accuracy', '')))}</td>"
                        f"<td>{html.escape(str(item.get('location', '')))}</td>"
                        f"</tr>"
                    )
                html_parts.append("</table>")

                # Discrepancies
                html_parts.append("<h2>Discrepancies</h2>")
                discrepancies = data.get("discrepancies", {})
                html_parts.append("<ul>")
                for key in ["missing_changes", "incorrect_changes", "unexpected_changes"]:
                    values = discrepancies.get(key, [])
                    html_parts.append(f"<li><strong>{key.replace('_', ' ').title()}:</strong> {', '.join(map(str, values)) if values else 'None'}</li>")
                html_parts.append("</ul>")

                # Assessment
                html_parts.append("<h2>Assessment</h2>")
                assessment = data.get("assessment", {}).get("text", "") or ""
                rtl_class = ' class="rtl"' if re.search(r'[\u0590-\u05FF]', assessment) else ''
                html_parts.append(f"<p{rtl_class}>{html.escape(assessment)}</p>")

                html_parts.append("</body></html>")
                return "\n".join(html_parts)

            html_output = json_to_html(data)
        else:
            with open(input_filepath, 'r', encoding='utf-8-sig') as f:
                raw_content = f.read()
                # Handle code-block-wrapped JSON (e.g., starts with ```json or ```)
                stripped = raw_content.strip()
                if (stripped.startswith('```json') or stripped.startswith('```')) and stripped.endswith('```'):
                    # Remove the first line (```json or ```) and the last line (```)
                    lines = stripped.splitlines()
                    # Remove the first and last line
                    json_str = '\n'.join(lines[1:-1])
                else:
                    json_str = raw_content
                json_data = json.loads(json_str)
                # Handle double-encoded JSON (JSON string containing JSON)
                if isinstance(json_data, str):
                    # Check if it's a markdown code block within the string
                    if json_data.startswith('```json\n') and json_data.endswith('\n```'):
                        json_content = json_data[8:-4]  # Remove ```json\n and \n```
                        json_data = json.loads(json_content)
                    else:
                        json_data = json.loads(json_data)
            converter = JsonToHtmlConverter(json_data)
            html_output = converter.convert_to_html()
        
        with open(output_filepath, "w", encoding="utf-8-sig") as f_out:
            f_out.write(html_output)
        print(f"Successfully converted '{input_filepath}' to '{output_filepath}'")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {input_filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {input_filepath}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cmd_parser = argparse.ArgumentParser(description="Convert law JSON files (from txt_to_json_v2.py) to readable HTML.")
    cmd_parser.add_argument("--input_path", "-i", required=False, help="Path to the input .json law file or directory of .json files.")
    cmd_parser.add_argument("--output_path", "-o", required=False, help="Path to save the output .html file or directory for .html files.")
    args = cmd_parser.parse_args()

    # --- NON-INTERACTIVE MODE: If both input_path and output_path are provided, process directly and exit ---
    if args.input_path and args.output_path:
        process_directory_or_file(args.input_path, args.output_path)
        exit(0)

    def ask_yes_no(prompt):
        while True:
            ans = input(prompt + " (y/n): ").strip().lower()
            if ans in ("y", "yes"): return True
            if ans in ("n", "no"): return False
            print("Please enter 'y' or 'n'.")

    def process_multiple_dirs(input_dirs, output_to_same_dir, output_dir=None):
        for input_dir in input_dirs:
            input_dir = input_dir.strip()
            if not input_dir:
                continue
            if not os.path.isdir(input_dir):
                print(f"Warning: '{input_dir}' is not a directory. Skipping.")
                continue
            if output_to_same_dir:
                out_dir = input_dir
            else:
                out_dir = output_dir
            print(f"Processing directory: {input_dir} -> {out_dir}")
            process_directory_or_file(input_dir, out_dir)

    # --- INTERACTIVE MODE (fallback) ---
    print("Choose processing mode:")
    print("1. Single file or directory")
    print("2. Multiple directories")
    print("3. All subdirectories in a directory")
    mode = input("Enter 1, 2 or 3: ").strip()

    if mode == "3":
        # All subdirectories in a directory
        parent_dir = input("Enter the parent directory containing subdirectories: ").strip()
        if not os.path.isdir(parent_dir):
            print(f"'{parent_dir}' is not a valid directory. Exiting.")
            exit(1)
        # Find all immediate subdirectories
        input_dirs = [os.path.join(parent_dir, d) for d in os.listdir(parent_dir)
                     if os.path.isdir(os.path.join(parent_dir, d))]
        if not input_dirs:
            print(f"No subdirectories found in '{parent_dir}'. Exiting.")
            exit(1)
        output_to_same_dir = ask_yes_no("Do you want to output the HTML files to the same directory as the input files?")
        output_dir = None
        if not output_to_same_dir:
            output_dir = input("Enter the path to save the output .html files (directory): ").strip()
        process_multiple_dirs(input_dirs, output_to_same_dir, output_dir)
    elif mode == "2":
        # Multiple directories
        input_dirs = []
        print("Enter the paths to the input directories (one per line). Leave blank and press Enter when done:")
        while True:
            dir_path = input("Input directory: ").strip()
            if not dir_path:
                break
            input_dirs.append(dir_path)
        if not input_dirs:
            print("No input directories provided. Exiting.")
            exit(1)
        output_to_same_dir = ask_yes_no("Do you want to output the HTML files to the same directory as the input files?")
        output_dir = None
        if not output_to_same_dir:
            output_dir = input("Enter the path to save the output .html files (directory): ").strip()
        process_multiple_dirs(input_dirs, output_to_same_dir, output_dir)
    else:
        # Single file or directory (default)
        input_path = args.input_path
        output_path = args.output_path
        if not input_path:
            input_path = input("Enter the path to the input .json law file or directory: ").strip()
        output_to_same_dir = ask_yes_no("Do you want to output the HTML file(s) to the same directory as the input file(s)?")
        if output_to_same_dir:
            if os.path.isdir(input_path):
                output_path = input_path
            else:
                output_path = os.path.dirname(input_path) or "."
        else:
            if not output_path:
                output_path = input("Enter the path to save the output .html file or directory: ").strip()
        process_directory_or_file(input_path, output_path)