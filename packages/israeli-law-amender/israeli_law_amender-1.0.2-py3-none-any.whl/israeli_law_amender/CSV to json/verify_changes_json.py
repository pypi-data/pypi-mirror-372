import json
import os

def verify_changes_json_file(file_path, output_file):
    """Verify the structure of a changes JSON file"""
    output_file.write(f"Verifying: {file_path}\n")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check basic structure
        if not isinstance(data, dict):
            output_file.write(f"  ERROR: Root is not a dictionary\n")
            return False
        
        # Check required keys
        required_keys = ['law_version_id', 'law_title_for_version', 'structure_of_changes']
        for key in required_keys:
            if key not in data:
                output_file.write(f"  ERROR: Missing required key '{key}'\n")
                return False
        
        # Check structure
        structure = data['structure_of_changes']
        if not isinstance(structure, dict):
            output_file.write(f"  ERROR: structure_of_changes is not a dictionary\n")
            return False
        
        # Check if structure has type
        if 'type' not in structure:
            output_file.write(f"  ERROR: Structure missing 'type' field\n")
            return False
        
        # Count children if they exist
        children_count = len(structure.get('children', []))
        output_file.write(f"  Structure type: {structure['type']}\n")
        output_file.write(f"  Children count: {children_count}\n")
        
        # Count total number of changed nodes in the tree
        total_changed_nodes = count_nodes_in_tree(structure)
        output_file.write(f"  Total nodes in changes tree: {total_changed_nodes}\n")
        
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

def count_nodes_in_tree(node):
    """Count the total number of nodes in a tree"""
    if not node:
        return 0
    
    count = 1  # Count this node
    
    # Count all children recursively
    if 'children' in node and node['children']:
        for child in node['children']:
            count += count_nodes_in_tree(child)
    
    return count

def main():
    """Verify all changes JSON files"""
    # Write results to a file to avoid terminal encoding issues
    with open("verification_changes_results.txt", 'w', encoding='utf-8') as output_file:
        # Find all JSON files with the matching pattern
        pattern = "_changes.json"
        json_files = [f for f in os.listdir('.') if f.endswith(pattern)]
        
        if not json_files:
            output_file.write("No changes JSON files found.\n")
            return
        
        output_file.write(f"Found {len(json_files)} changes JSON files to verify.\n\n")
        
        # Verify each file
        all_valid = True
        for json_file in sorted(json_files):
            file_valid = verify_changes_json_file(json_file, output_file)
            all_valid = all_valid and file_valid
            output_file.write("\n")  # Empty line for readability
        
        # Print final status
        if all_valid:
            output_file.write("\nAll changes JSON files are valid!\n")
        else:
            output_file.write("\nSome changes JSON files have issues. Check the log above.\n")
    
    print(f"Verification completed. Results saved to verification_changes_results.txt")

if __name__ == "__main__":
    main() 