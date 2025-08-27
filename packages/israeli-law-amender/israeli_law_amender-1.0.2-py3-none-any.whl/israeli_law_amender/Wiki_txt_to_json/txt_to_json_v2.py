import os
import re
import json
import argparse

THE_LAW_SCHEMA_DEFINITION = {
  "schema": {
    "title": "Law Component Structure",
    "description": "Schema for representing hierarchical law components.",
    "type": "object",
    "properties": {
      "id": {
        "type": "integer",
        "description": "Unique identifier for the component (Corresponds to CSV column ID)."
      },
      "number": {
        "type": "string",
        "Noneable": True,
        "description": "Numbering of the component (e.g., '1', '(א)', '-1'). Corresponds to CSV column NumberText."
      },
      "title": {
        "type": "string",
        "Noneable": True,
        "description": "Header or title of the component. Corresponds to CSV column HeaderText."
      },
      "text": {
        "type": "string",
        "Noneable": True,
        "description": "The textual content of the component. Corresponds to CSV column Content."
      },
      "type": {
        "type": "string",
        "enum": [
          "Law",
          "Chapter",
          "Sign",
          "Section",
          "Paragraph",
          "Item"
        ],
        "description": "The type of the law component. Derived from FK_ComponentTypeID (1=Law, 3=Chapter, 4=Sign, 6=Section, 7=Paragraph, 8=Item)."
      },
      "level": {
        "type": "integer",
        "Noneable": True,
        "description": "Indentation level for items within a paragraph (e.g., 1, 2, 3). Corresponds to CSV column ParagraphLevel."
      },
      "children": {
        "type": "array",
        "items": {
          "$ref": "#/schema"
        },
        "description": "Child components nested under this component. Determined by FK_ParentComponentID."
      }
    },
    "required": [
      "id",
      "type"
    ]
  },
  "example": {
    "id": 1000,
    "number": None,
    "title": "Example Law 2024",
    "text": None,
    "type": "Law",
    "level": None,
    "children": [
      {
        "id": 1001,
        "number": None,
        "title": "Chapter A: Purpose",
        "text": None,
        "type": "Chapter",
        "level": None,
        "children": [
          {
            "id": 1002,
            "number": "1",
            "title": "Purpose",
            "text": None,
            "type": "Section",
            "level": None,
            "children": [
              {
                "id": 1003,
                "number": "(a)",
                "title": None,
                "text": "The purpose of this law is to establish...",
                "type": "Paragraph",
                "level": None,
                "children": [
                  {
                    "id": 1004,
                    "number": "-1",
                    "title": None,
                    "text": "First goal.",
                    "type": "Item",
                    "level": 1,
                    "children": []
                  },
                  {
                    "id": 1005,
                    "number": "-2",
                    "title": None,
                    "text": "Second goal.",
                    "type": "Item",
                    "level": 1,
                    "children": []
                  }
                ]
              },
              {
                "id": 1006,
                "number": "(b)",
                "title": None,
                "text": "This law also aims to...",
                "type": "Paragraph",
                "level": None,
                "children": []
              }
            ]
          }
        ]
      },
      {
        "id": 1007,
        "number": None,
        "title": "Chapter B: Definitions",
        "text": None,
        "type": "Chapter",
        "level": None,
        "children": [
          {
            "id": 1008,
            "number": "2",
            "title": "Definitions",
            "text": "In this law:",
            "type": "Section",
            "level": None,
            "children": [
              {
                "id": 1009,
                "number": None,
                "title": None,
                "text": "\"Term A\" means...",
                "type": "Paragraph",
                "level": None,
                "children": []
              },
              {
                "id": 1010,
                "number": None,
                "title": None,
                "text": "\"Term B\" means...",
                "type": "Paragraph",
                "level": None,
                "children": []
              }
            ]
          }
        ]
      }
    ]
  }
}


class OlawToTargetJsonParser:
    def __init__(self, filename_for_id):
        self.law_version_id = self._extract_id_from_filename(filename_for_id)
        self.law_title_for_version = "חוק לא ידוע"
        self.law_component_root = None
        self.parent_stack = []
        self.text_buffer = []
        self.current_section_context = {}

    def _extract_id_from_filename(self, filename):
        match = re.search(r'_oldid_(\d+)\.txt$', filename)
        return match.group(1) if match else "unknown_version"

    def _clean_text_content(self, text, is_header_or_title=False):
        if text is None: return None
        
        # 1. Preserve Vikisource links' display text, remove template wrapper
        # {{ח:חיצוני|DISPLAY_TEXT|...}} or {{ח:חיצוני|LINK_AS_DISPLAY_TEXT}}
        text = re.sub(r"\{\{ח:חיצוני\|([^}|]+?)(?:\|[^}|]+?)?(?:\|[^}]+?)?\}\}", r"\1", text)
        # {{ח:פנימי|DISPLAY_TEXT|...}} or {{ח:פנימי|LINK_AS_DISPLAY_TEXT}}
        text = re.sub(r"\{\{ח:פנימי\|([^}|]+?)(?:\|[^}]+?)?\}\}", r"\1", text)
        
        # 2. Remove {{ח:הגדרה|...}} wrapper, keeping only the content
        text = re.sub(r"\{\{ח:הגדרה\|(.*?)\}\}", r"\1", text)

        # 3. Remove {{ח:הערה|...}} template and its content entirely
        text = re.sub(r"\{\{ח:הערה\|.*?\}\}", "", text)
        text = re.sub(r"\{\{ח:הערה\}\}", "", text) # No content version

        # 4. Remove bold/italic markers (''')
        text = text.replace("'''", "")
        
        # 5. Basic HTML tag stripping (simple tags like <br>)
        text = re.sub(r"<br\s*/?>", "\n", text) # Convert <br> to newline for potential paragraph breaks
        text = re.sub(r"<[^>]+>", "", text) # Strip other tags

        # 6. Strip leading/trailing whitespace and condense multiple newlines
        text = text.strip()
        text = re.sub(r'\n\s*\n', '\n', text) # Condense multiple newlines to one

        # 7. Clean trailing punctuation often found in Vikisource definitions,
        #    but only if it's not a header/title (titles might legitimately end with these).
        if not is_header_or_title:
            if text.endswith(';'): text = text[:-1].strip()
            # Avoid removing period if it's the only char or part of an abbreviation
            if text.endswith('.') and len(text) > 1 and text[-2] != '.':
                 pass # text = text[:-1].strip() # Decided against removing general periods

        return text if text else None

    def _create_component(self, comp_type, header_text=None, number_text=None, body_text=None):
        component = {"type": comp_type}
        # Clean header_text as it might contain Vikisource templates
        cleaned_header = self._clean_text_content(header_text, is_header_or_title=True)
        cleaned_body = self._clean_text_content(body_text) # Body text cleaning is more aggressive

        if cleaned_header: component["header_text"] = cleaned_header
        if number_text: component["number_text"] = number_text
        if cleaned_body: component["body_text"] = cleaned_body
        component["children"] = []
        return component

    def _flush_text_buffer(self):
        if self.text_buffer and self.parent_stack:
            parent_component = self.parent_stack[-1]
            current_text_raw = "\n".join(self.text_buffer).strip()
            current_text_cleaned = self._clean_text_content(current_text_raw)

            if current_text_cleaned:
                if parent_component['type'] in ["Law", "Chapter", "SubChapter"] and \
                   not parent_component.get('body_text') and \
                   not parent_component['children']:
                    pass 
                elif parent_component['type'] == "SubSection" and self.current_section_context.get("is_definitions_section_item"):
                     pass
                else:
                    if parent_component.get('body_text'):
                        parent_component['body_text'] += "\n" + current_text_cleaned
                    else:
                        parent_component['body_text'] = current_text_cleaned
        self.text_buffer = []

    def _add_component(self, component_to_add):
        self._flush_text_buffer()
        target_parent = None

        while self.parent_stack:
            current_potential_parent = self.parent_stack[-1]
            parent_type = current_potential_parent['type']
            new_type = component_to_add['type']
            
            can_be_child = False
            if new_type == "Chapter":
                if parent_type == "Law": can_be_child = True
            elif new_type == "SubChapter":
                if parent_type in ["Chapter", "Law"]: can_be_child = True
            elif new_type == "Section":
                if parent_type in ["SubChapter", "Chapter", "Law"]: can_be_child = True
            elif new_type == "SubSection":
                if parent_type == "Section": can_be_child = True
                elif parent_type == "SubSection": 
                    self.parent_stack.pop(); continue
                elif parent_type == "Clause":
                    self.parent_stack.pop() 
                    if self.parent_stack and self.parent_stack[-1]['type'] == "SubSection":
                        self.parent_stack.pop()
                    continue
            elif new_type == "Clause":
                if parent_type == "SubSection": can_be_child = True
                elif parent_type == "Clause":
                     self.parent_stack.pop(); continue
            
            if can_be_child:
                target_parent = current_potential_parent; break
            else:
                if len(self.parent_stack) > 1: self.parent_stack.pop()
                else: target_parent = self.law_component_root; break
        
        if not target_parent: target_parent = self.law_component_root

        target_parent['children'].append(component_to_add)
        
        if component_to_add['type'] in ["Chapter", "SubChapter", "Section", "SubSection"]:
            self.parent_stack.append(component_to_add)


    def _preprocess_lines(self, raw_lines_input):
        processed_lines = []
        in_toc_block = False
        
        re_law_title_meta = re.compile(r"\{\{ח:כותרת\|(.*?)\}\}")
        skip_templates_exact = {"{{ח:התחלה}}", "{{ח:סוגר}}", "{{ח:מפריד}}", "{{ח:סוף}}"}
        
        in_fatih_or_box_block = False

        for line_content in raw_lines_input:
            stripped_line = line_content.strip()

            if in_fatih_or_box_block:
                if "{{ח:סוגר}}" in stripped_line: in_fatih_or_box_block = False
                continue
            if stripped_line == "{{ח:פתיח-התחלה}}":
                in_fatih_or_box_block = True; continue
            if "{{ח:תיבה|" in stripped_line and not in_fatih_or_box_block:
                if "{{ח:סוגר}}" not in stripped_line: in_fatih_or_box_block = True 
                continue

            title_match = re_law_title_meta.search(stripped_line)
            if title_match:
                self.law_title_for_version = self._clean_text_content(title_match.group(1), is_header_or_title=True)
                continue

            if stripped_line in skip_templates_exact or stripped_line.startswith("[[קטגוריה:"):
                continue
            
            if "{{ח:סעיף*||}}" in stripped_line:
                in_toc_block = True; continue
            if in_toc_block:
                if stripped_line.startswith("{{ח:קטע2") or \
                   (stripped_line.startswith("{{ח:סעיף") and "{{ח:סעיף*||}}" not in stripped_line) :
                    in_toc_block = False
                else: continue 
            
            processed_lines.append(line_content)
        return processed_lines

    def parse(self, text_content):
        lines = self._preprocess_lines(text_content.splitlines())

        self.law_component_root = self._create_component(comp_type="Law")
        self.parent_stack = [self.law_component_root] # Start with Law as parent

        # Regexes
        re_chapter = re.compile(r"\{\{ח:קטע2\|[^|]*?\|(.*?)\}\}")
        re_subchapter = re.compile(r"\{\{ח:קטע3\|[^|]*?\|(.*?)\}\}")
        re_section = re.compile(r"\{\{ח:סעיף\|([0-9א-ת]+(?:[\s.a-zA-Z'()\[\]א-ת0-9-]|תיקון:|מס׳)*?)(?:\|(.*?))?(?:\|(תיקון:\s*.*?))?\}\}")
        re_subsection_clause_base = r"\{\{ח:(ת{2,})\|([()א-ת0-9א-ת.-]*?)\}\}(.*)"
        re_subsection_clause = re.compile(re_subsection_clause_base)
        re_text_line = re.compile(r"\{\{ח:ת\}\}(.*)")
        re_definition_header_marker = re.compile(r"^(ב(?:חוק|פקודה|תקנות) זה|כהגדרתם ב.*?)\s*[:–\-]?$")
        re_definition_item_wrapper = re.compile(r"\{\{ח:הגדרה\|(.*?)\}\}")

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                if self.text_buffer and self.text_buffer[-1]: self.text_buffer.append("")
                continue

            match_chapter = re_chapter.match(line)
            match_subchapter = re_subchapter.match(line)
            match_section = re_section.match(line)
            match_subsection_clause = re_subsection_clause.match(line)
            match_text = re_text_line.match(line)

            if match_chapter:
                self.current_section_context = {}
                comp = self._create_component("Chapter", header_text=match_chapter.group(1))
                self._add_component(comp)
            elif match_subchapter:
                self.current_section_context = {}
                comp = self._create_component("SubChapter", header_text=match_subchapter.group(1))
                self._add_component(comp)
            elif match_section:
                self.current_section_context = {}
                num = match_section.group(1).strip()
                title = match_section.group(2).strip() if match_section.group(2) else None
                
                comp = self._create_component("Section", header_text=title, number_text=num)
                self._add_component(comp)
                
                cleaned_title_for_check = self._clean_text_content(title, is_header_or_title=True) or ""
                self.current_section_context["is_definitions_section_header"] = (cleaned_title_for_check == "הגדרות" or (not cleaned_title_for_check and num == "2"))
                self.current_section_context["definitions_header_processed"] = False
                self.current_section_context["is_definitions_section_item"] = False
                self.current_section_context["is_intro_plus_definition_section"] = False
                self.current_section_context["intro_subsection_created"] = False

            elif match_subsection_clause: # {{ח:תת...}}
                t_count = len(match_subsection_clause.group(1))
                num_raw = match_subsection_clause.group(2).strip()
                text_on_line = match_subsection_clause.group(3).strip()
                
                comp_type = "SubSection" if t_count == 2 else "Clause"
                num_text = f"({num_raw})" if comp_type == "SubSection" and num_raw else \
                           (f"-{num_raw}" if comp_type == "Clause" and num_raw else (num_raw if num_raw else None))

                comp = self._create_component(comp_type, number_text=num_text, body_text=text_on_line)
                self._add_component(comp)
                self.current_section_context["is_definitions_section_item"] = False # Reset after adding item
                self.current_section_context["awaiting_definition_item_content"] = False


            elif match_text: # {{ח:ת}}
                content_on_line = match_text.group(1) # Keep raw for now, clean later
                parent_type = self.parent_stack[-1]['type'] if self.parent_stack else None

                if self.current_section_context.get("is_definitions_section_header") and \
                   not self.current_section_context.get("definitions_header_processed") and \
                   parent_type == "Section":
                    
                    cleaned_content = self._clean_text_content(content_on_line)
                    if re_definition_header_marker.match(cleaned_content or ""):
                        self._flush_text_buffer()
                        self.parent_stack[-1]['body_text'] = cleaned_content
                        self.current_section_context["definitions_header_processed"] = True
                        self.current_section_context["is_definitions_section_item"] = True # Now expect definition items
                        continue # Skip adding to buffer

                if self.current_section_context.get("is_definitions_section_item") and parent_type == "Section":
                    def_item_content_match = re_definition_item_wrapper.search(content_on_line)
                    if def_item_content_match:
                        def_text_raw = def_item_content_match.group(1)
                        # Definitions can be multi-line, so they might have {{ח:תתת inside them
                        # Create SubSection for the definition
                        def_item_comp = self._create_component("SubSection", body_text=def_text_raw) # Cleaned in _create_component
                        self._add_component(def_item_comp)
                        # The SubSection is now on stack, subsequent {{ח:תתת}} will be its children
                        continue 

                # Generic intro + definition pattern (like Sec 126)
                # If current parent is Section, and this {{ח:ת}} is the first child, and next line suggests a def item
                is_potential_intro = (parent_type == "Section" and not self.parent_stack[-1]['children'] and
                                      not self.current_section_context.get("intro_subsection_created"))
                
                if is_potential_intro:
                    current_index = lines.index(raw_line) if raw_line in lines else -1
                    if current_index != -1 and current_index + 1 < len(lines):
                        next_line_stripped = lines[current_index+1].strip()
                        if next_line_stripped.startswith("{{ח:ת}}") and "{{ח:הגדרה|" in next_line_stripped:
                            self.current_section_context["is_intro_plus_definition_section"] = True
                            
                    if self.current_section_context.get("is_intro_plus_definition_section"):
                        intro_comp = self._create_component("SubSection", body_text=content_on_line)
                        self._add_component(intro_comp)
                        self.current_section_context["intro_subsection_created"] = True
                        continue
                
                # If it's the definition part of an intro_plus_definition section
                if self.current_section_context.get("is_intro_plus_definition_section") and \
                   parent_type == "SubSection" and \
                   self.current_section_context.get("intro_subsection_created"):
                    def_item_match = re_definition_item_wrapper.search(content_on_line)
                    if def_item_match:
                        def_text_raw = def_item_match.group(1)
                        clause_comp = self._create_component("Clause", body_text=def_text_raw)
                        self.parent_stack[-1]['children'].append(clause_comp) # Add directly
                        # Reset flags for this specific pattern
                        self.current_section_context["is_intro_plus_definition_section"] = False
                        self.current_section_context["intro_subsection_created"] = False
                        continue
                
                # Default: add to text buffer
                if content_on_line: self.text_buffer.append(content_on_line)
            
            elif line and not (line.startswith("{{ח:") and not re_text_line.match(line)): 
                self.text_buffer.append(line) # Append unstripped line for later cleaning

        self._flush_text_buffer()

        # Final JSON structure for the parsed law
        parsed_law_data = {
            "law_version_id": self.law_version_id,
            "law_title_for_version": self.law_title_for_version,
            "structure": self.law_component_root
        }
        
        # Combine with the schema
        final_output_with_schema = {
            "schema": THE_LAW_SCHEMA_DEFINITION,
            "parsed_law": parsed_law_data
        }
        return final_output_with_schema


def process_directory_or_file(input_path, output_path_or_dir):
    if os.path.isdir(input_path):
        if not os.path.exists(output_path_or_dir):
            os.makedirs(output_path_or_dir, exist_ok=True)
        elif not os.path.isdir(output_path_or_dir):
            print(f"Error: Output path '{output_path_or_dir}' exists and is not a directory.")
            return

        for filename in os.listdir(input_path):
            if filename.endswith(".txt"):
                input_filepath = os.path.join(input_path, filename)
                output_filename = filename.replace(".txt", ".json")
                output_filepath = os.path.join(output_path_or_dir, output_filename)
                
                print(f"Processing: {input_filepath} -> {output_filepath}")
                parse_single_file(input_filepath, output_filepath, filename)
    elif os.path.isfile(input_path):
        # If output is a directory, form the output filename
        if os.path.isdir(output_path_or_dir):
            output_filename = os.path.basename(input_path).replace(".txt", ".json")
            final_output_path = os.path.join(output_path_or_dir, output_filename)
            if not os.path.exists(output_path_or_dir):
                 os.makedirs(output_path_or_dir, exist_ok=True)
        else: # Output is a specific file path
            final_output_path = output_path_or_dir
            output_dir_check = os.path.dirname(final_output_path)
            if output_dir_check and not os.path.exists(output_dir_check):
                os.makedirs(output_dir_check, exist_ok=True)

        print(f"Processing: {input_path} -> {final_output_path}")
        parse_single_file(input_path, final_output_path, os.path.basename(input_path))
    else:
        print(f"Error: Input path '{input_path}' is not a valid file or directory.")

def parse_single_file(input_filepath, output_filepath, filename_for_id):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        parser = OlawToTargetJsonParser(filename_for_id) # Pass filename for ID extraction
        parsed_json_output = parser.parse(file_content)
        
        with open(output_filepath, "w", encoding="utf-8") as f_out:
            json.dump(parsed_json_output, f_out, indent=2, ensure_ascii=False)
        print(f"Successfully parsed '{input_filepath}' and saved to '{output_filepath}'")

    except Exception as e:
        print(f"Error processing file {input_filepath}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    cmd_parser = argparse.ArgumentParser(description="Convert Olaw Vikisource TXT files to specific JSON format.")
    cmd_parser.add_argument("--input_path", "-i", help="Path to the input .txt law file or directory of .txt files.")
    cmd_parser.add_argument("--output_path", "-o", help="Path to save the output .json file or directory for .json files.")
    
    args = cmd_parser.parse_args()
    
    # If arguments are missing, prompt the user
    if not args.input_path:
        args.input_path = str(input("Please enter the input path: "))
    if not args.output_path:
        args.output_path = str(input("Please enter the output path: "))
    process_directory_or_file(args.input_path, args.output_path)