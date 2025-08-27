import json
import re

def apply_amendments(law_data_orig):
    """
    Applies the amendments to the law data.
    Modifies the law_data_orig in place, preserving the original structure.
    """
    law_data = law_data_orig # Work on the original data structure

    # --- Amendment 1: Add item to "גוף פיננסי מפוקח" in Section 1 ---
    # Navigate to the definitions SubSection in Section 1
    definitions_subsection = None
    try:
        chapter_alef = None
        for ch_idx, ch_val in enumerate(law_data['parsed_law']['structure']['children']):
            if ch_val.get('type') == 'Chapter' and ch_val.get('header_text') == "פרק א׳: הגדרות":
                chapter_alef = ch_val
                break
        
        if chapter_alef:
            section_1 = chapter_alef['children'][0] # Assuming Section "1" is the first child
            if section_1.get('type') == 'Section' and section_1.get('number_text') == '1':
                if section_1['children'] and section_1['children'][0].get('type') == 'SubSection':
                    definitions_subsection = section_1['children'][0]
    except (IndexError, KeyError, AttributeError, TypeError) as e:
        print(f"Error navigating to definitions SubSection for Amendment 1: {e}")
        definitions_subsection = None

    if definitions_subsection:
        insertion_index = -1
        clauses = definitions_subsection.get('children', [])
        # Find the 4th item related to "גוף פיננסי מפוקח"
        # These are the first few clauses in this specific SubSection's children.
        # Item (1) is index 0, (2) is index 1, (3) is index 2, (4) is index 3.
        # We need to insert after index 3.
        if len(clauses) > 3 and \
           clauses[0].get("number_text") == "-1" and "תאגיד בנקאי" in clauses[0].get("body_text", "") and \
           clauses[1].get("number_text") == "-2" and "בנק הדואר" in clauses[1].get("body_text", "") and \
           clauses[2].get("number_text") == "-3" and "בעל רישיון למתן אשראי" in clauses[2].get("body_text", "") and \
           clauses[3].get("number_text") == "-4" and "בעל רישיון למתן שירות בנכס פיננסי" in clauses[3].get("body_text", ""):
            insertion_index = 4 # Insert at index 4, which is after current index 3
        
        if insertion_index != -1:
            new_clause_item_5 = {
              "type": "Clause",
              "number_text": "-(5)", # Matching target format style
              "body_text": 'מוסד לגמילות חסדים כהגדרתו בחוק להסדרת מתן שירותי פיקדון ואשראי בלא ריבית על ידי מוסדות לגמילות חסדים, התשע"ט-2019;',
              "children": []
            }
            clauses.insert(insertion_index, new_clause_item_5)
            # No need to reassign definitions_subsection['children'] as list.insert modifies in place
            print("Amendment 1 applied: Added item (5) to 'גוף פיננסי מפוקח'.")
        else:
            print("Warning: Could not find the precise insertion point for Amendment 1 (item (4) of 'גוף פיננסי מפוקח'). Items might not match expected content or order.")
    else:
        print("Warning: Could not find definitions SubSection for Amendment 1.")

    # --- Amendment 2: Modify Section 41 ---
    section_41 = None
    try:
        chapter_het = None
        for ch in law_data['parsed_law']['structure']['children']:
            if ch.get('type') == 'Chapter' and ch.get('header_text', '').startswith("פרק ח"):
                chapter_het = ch
                break
        
        if chapter_het:
            for sec in chapter_het.get('children', []):
                if sec.get('type') == 'Section' and sec.get('number_text') == '41':
                    section_41 = sec
                    break
    except (IndexError, KeyError, AttributeError, TypeError) as e:
        print(f"Error navigating to Section 41: {e}")
        section_41 = None

    if section_41:
        # Section 41's body_text is in its first child, which is a SubSection
        section_41_subsection = None
        if section_41.get('children') and isinstance(section_41['children'], list) and len(section_41['children']) > 0:
            # Assuming the first child is the target SubSection
            if section_41['children'][0].get('type') == 'SubSection':
                 section_41_subsection = section_41['children'][0]

        if section_41_subsection and 'body_text' in section_41_subsection and section_41_subsection['body_text']:
            original_text_s41 = section_41_subsection['body_text']
            
            pattern_s41_start = r"עד תום שנתיים מיום התחילה או עד יום תחילתו של החוק המסדיר, לפי המוקדם,"
            replacement_s41_start = r'עד יום תחילתו של החוק להסדרת מתן שירותי פיקדון ואשראי בלא ריבית על ידי מוסדות לגמילות חסדים, התשע"ט–2019, ואם תידחה תחילתו בהתאם לסעיף 109(ג) לאותו החוק, תידחה התקופה בהתאמה,'

            modified_text_s41, count_2_1 = re.subn(pattern_s41_start, replacement_s41_start, original_text_s41, count=1)
            
            if count_2_1 > 0:
                print("Amendment 2.1 applied to Section 41 (רישה).")
            else:
                print("Warning: Pattern for Amendment 2.1 (רישה Section 41) not found in SubSection.")

            # Amendment 2.2: Delete definition "החוק המסדיר"
            # This pattern targets the definition part specifically, preserving the leading "בסעיף זה –"
            pattern_s41_def = r'(;\s*בסעיף זה\s*–)\s*\n?\s*”החוק המסדיר“\s*–\s*חוק שמסדיר את עיסוקו של מי שעיסוקו במתן אשראי שאינו נושא ריבית ליחיד או לאחר שעיסוקו במתן אשראי כאמור\.?'
            replacement_s41_def = r'\1' 
            
            final_text_s41, count_2_2 = re.subn(pattern_s41_def, replacement_s41_def, modified_text_s41, count=1)

            if count_2_2 > 0:
                section_41_subsection['body_text'] = final_text_s41.strip()
                print("Amendment 2.2 applied to Section 41 (delete החוק המסדיר).")
            else:
                # Fallback if the specific pattern for definition removal fails (e.g., if newline or spacing is different)
                # This simpler pattern just removes the definition string if found.
                simpler_pattern_s41_def = r'\s*\n?\s*”החוק המסדיר“\s*–\s*חוק שמסדיר את עיסוקו של מי שעיסוקו במתן אשראי שאינו נושא ריבית ליחיד או לאחר שעיסוקו במתן אשראי כאמור\.?'
                final_text_s41_alt, count_2_2_alt = re.subn(simpler_pattern_s41_def, '', modified_text_s41, count=1)
                if count_2_2_alt > 0:
                     section_41_subsection['body_text'] = final_text_s41_alt.strip()
                     print("Amendment 2.2 (alternative pattern) applied to Section 41 (delete החוק המסדיר).")
                else:
                    print("Warning: Pattern for Amendment 2.2 (delete החוק המסדיר in Section 41) not found.")
                    # If no change was made for 2.2, ensure the text from 2.1 is set (if 2.1 was successful)
                    if count_2_1 > 0 :
                         section_41_subsection['body_text'] = modified_text_s41.strip()
                    else: # If neither 2.1 nor 2.2 applied, no change to body_text
                        pass


        elif section_41_subsection and (not 'body_text' in section_41_subsection or not section_41_subsection['body_text']):
            print("Warning: Section 41's SubSection found, but its body_text is missing or empty. Cannot apply Amendments 2.1, 2.2.")
        else:
            print("Warning: SubSection containing body_text for Section 41 not found as expected. Cannot apply Amendments 2.1, 2.2.")
            
    elif not section_41:
        print("Warning: Section 41 not found. Cannot apply Amendments 2.1, 2.2.")

    return law_data

# --- Main execution ---
original_file_path = 'Data/JSON_Laws_v2/חוק לצמצום השימוש במזומן_original_oldid_816623.json'
output_file_path = 'חוק לצמצום השימוש במזומן_amended.json'

try:
    with open(original_file_path, 'r', encoding='utf-8') as f:
        law_data_original = json.load(f)
except FileNotFoundError:
    print(f"Error: Original law file not found at {original_file_path}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {original_file_path}")
    exit()

# Deep copy if you want to ensure original_data is untouched,
# but for this script, modifying in place is fine as per current structure.
# import copy
# law_to_amend = copy.deepcopy(law_data_original)
# amended_law_data = apply_amendments(law_to_amend)

amended_law_data = apply_amendments(law_data_original) # Modifies in place

try:
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(amended_law_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully amended law saved to {output_file_path}")
except IOError:
    print(f"Error: Could not write amended law to {output_file_path}")