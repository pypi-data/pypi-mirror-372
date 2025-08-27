import os
import re
from wikiload_v2 import law_names_no_dates_input, sanitize_filename

OUTPUT_DIR = "Data/wikitext_laws"

# Regex for Hebrew and numbers (for date detection)
hebrew_and_number_pattern = re.compile(r"[\u0590-\u05FF]+.*\d+|\d+.*[\u0590-\u05FF]+")

def find_matching_file(base_filename, suffix_pattern):
    # Find any file that starts with base_filename and ends with the given suffix pattern (regex)
    for fname in os.listdir(OUTPUT_DIR):
        if re.match(rf"^{re.escape(base_filename)}.*{suffix_pattern}$", fname):
            return fname
    return None

def file_bigger_than_1kb(filepath):
    return os.path.exists(filepath) and os.path.getsize(filepath) > 1024

def main():
    missing = []
    too_small = []
    for law in law_names_no_dates_input:
        base_filename = sanitize_filename(law)
        # Accept any file that starts with base_filename and ends with _current.txt or _original_oldid_*.txt
        current_file = find_matching_file(base_filename, r'_current\.txt')
        original_file = find_matching_file(base_filename, r'_original_oldid_.*\.txt')
        current_exists = current_file is not None
        original_exists = original_file is not None
        current_path = os.path.join(OUTPUT_DIR, current_file) if current_file else None
        original_path = os.path.join(OUTPUT_DIR, original_file) if original_file else None
        # Check existence
        if not current_exists or not original_exists:
            missing.append({
                'law': law,
                'current_exists': current_exists,
                'original_exists': original_exists,
                'expected_current': current_file or f"{base_filename}*_current.txt",
                'expected_original': original_file or f"{base_filename}*_original_oldid_*.txt"
            })
        else:
            # Check file size
            if not file_bigger_than_1kb(current_path):
                too_small.append({'law': law, 'file': current_file, 'size': os.path.getsize(current_path)})
            if not file_bigger_than_1kb(original_path):
                too_small.append({'law': law, 'file': original_file, 'size': os.path.getsize(original_path)})

    if not missing:
        print("All laws have both current and original files.")
    else:
        print(f"Missing files for {len(missing)} laws:")
        for entry in missing:
            print(f"- {entry['law']}")
            if not entry['current_exists']:
                print(f"    Missing: {entry['expected_current']}")
            if not entry['original_exists']:
                print(f"    Missing: {entry['expected_original']}")

    if too_small:
        print(f"\nFiles smaller than 1 KB:")
        for entry in too_small:
            print(f"- {entry['law']} : {entry['file']} ({entry['size']} bytes)")
    else:
        print("\nNo files smaller than 1 KB.")


if __name__ == "__main__":
    main() 