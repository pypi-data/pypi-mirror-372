import json
import os

def verify_json_file(file_path, output_file):
    """Verify the structure of a single JSON file"""
    output_file.write(f"Verifying: {file_path}\n")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check basic structure
        if not isinstance(data, dict):
            output_file.write(f"  ERROR: Root is not a dictionary\n")
            return False
        
        # Check required keys
        required_keys = ['law_version_id', 'law_title_for_version', 'structure']
        for key in required_keys:
            if key not in data:
                output_file.write(f"  ERROR: Missing required key '{key}'\n")
                return False
        
        # Check structure
        structure = data['structure']
        if not isinstance(structure, dict):
            output_file.write(f"  ERROR: Structure is not a dictionary\n")
            return False
        
        # Check if structure has type
        if 'type' not in structure:
            output_file.write(f"  ERROR: Structure missing 'type' field\n")
            return False
        
        # Count children if they exist
        children_count = len(structure.get('children', []))
        output_file.write(f"  Structure type: {structure['type']}\n")
        output_file.write(f"  Children count: {children_count}\n")
        
        # Get first few child types if they exist
        if children_count > 0:
            output_file.write("  First few children:\n")
            for i, child in enumerate(structure.get('children', [])[:3]):
                child_header = child.get('header_text', 'No header')
                child_type = child.get('type', 'Unknown type')
                output_file.write(f"    {i+1}. {child_type} - {child_header}\n")
        
        return True
    except Exception as e:
        output_file.write(f"  ERROR: Exception while verifying file: {str(e)}\n")
        return False

def main():
    """Verify all JSON files corresponding to law versions"""
    # Write results to a file to avoid terminal encoding issues
    with open("verification_results.txt", 'w', encoding='utf-8') as output_file:
        # Find all JSON files with the matching pattern
        pattern = "חוק_שירות_נתוני_אשראי_2016_version_"
        json_files = [f for f in os.listdir('.') if f.endswith('.json') and pattern in f]
        
        if not json_files:
            output_file.write("No JSON files found matching the pattern.\n")
            return
        
        output_file.write(f"Found {len(json_files)} JSON files to verify.\n\n")
        
        # Verify each file
        all_valid = True
        for json_file in sorted(json_files):
            file_valid = verify_json_file(json_file, output_file)
            all_valid = all_valid and file_valid
            output_file.write("\n")  # Empty line for readability
        
        # Also verify the combined file
        combined_file = "חוק_שירות_נתוני_אשראי_2016_all_versions.json"
        if os.path.exists(combined_file):
            output_file.write(f"Verifying combined file: {combined_file}\n")
            try:
                with open(combined_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                versions_count = len(data.get('versions', []))
                output_file.write(f"  Contains {versions_count} versions\n")
                if versions_count != len(json_files):
                    output_file.write(f"  WARNING: Number of versions in combined file ({versions_count}) doesn't match number of individual files ({len(json_files)})\n")
            except Exception as e:
                output_file.write(f"  ERROR: Exception while verifying combined file: {str(e)}\n")
                all_valid = False
        else:
            output_file.write(f"Combined file not found: {combined_file}\n")
            all_valid = False
        
        # Print final status
        if all_valid:
            output_file.write("\nAll JSON files are valid!\n")
        else:
            output_file.write("\nSome JSON files have issues. Check the log above.\n")
    
    print(f"Verification completed. Results saved to verification_results.txt")

if __name__ == "__main__":
    main() 