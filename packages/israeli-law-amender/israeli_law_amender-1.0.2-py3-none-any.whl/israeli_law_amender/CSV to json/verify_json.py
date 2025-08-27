import json
import os
import sys

def verify_individual_json_file(file_path):
    print(f"Verifying individual file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Basic structure verification
        if 'law_version_id' not in data:
            print(f"  ERROR: Missing 'law_version_id' in {file_path}")
            return False
        
        if 'law_title_for_version' not in data:
            print(f"  ERROR: Missing 'law_title_for_version' in {file_path}")
            return False
        
        if 'structure' not in data:
            print(f"  ERROR: Missing 'structure' in {file_path}")
            return False
        
        # Check structure content
        if data['structure'] is None:
            print(f"  WARNING: 'structure' is null in {file_path}")
            return True
        
        # Check hierarchy
        if 'type' not in data['structure']:
            print(f"  ERROR: Root node missing 'type' in {file_path}")
            return False
        
        # Check children
        children_count = len(data['structure'].get('children', []))
        print(f"  Law version: {data['law_version_id']}")
        print(f"  Law title: {data['law_title_for_version']}")
        print(f"  Root node type: {data['structure'].get('type')}")
        print(f"  First-level children count: {children_count}")
        
        # Check first few children
        if children_count > 0:
            for i, child in enumerate(data['structure'].get('children', [])[:3]):
                print(f"    Child {i+1} type: {child.get('type', 'Unknown')}")
                print(f"    Child {i+1} header: {child.get('header_text', 'No header')}")
                print(f"    Child {i+1} has {len(child.get('children', []))} sub-children")
                
        return True
    
    except json.JSONDecodeError:
        print(f"  ERROR: Invalid JSON format in {file_path}")
        return False
    except Exception as e:
        print(f"  ERROR: {str(e)} in {file_path}")
        return False

def verify_combined_json_file(file_path):
    print(f"Verifying combined file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Check the top-level structure
        if 'law_name' not in data:
            print(f"  ERROR: Missing 'law_name' in {file_path}")
            return False
        
        if 'versions_count' not in data:
            print(f"  ERROR: Missing 'versions_count' in {file_path}")
            return False
        
        if 'versions' not in data:
            print(f"  ERROR: Missing 'versions' in {file_path}")
            return False
        
        versions = data['versions']
        if not isinstance(versions, list):
            print(f"  ERROR: 'versions' is not a list in {file_path}")
            return False
        
        # Print basic info
        print(f"  Law name: {data['law_name']}")
        print(f"  Versions count: {data['versions_count']}")
        print(f"  Actual versions in file: {len(versions)}")
        
        # Check some versions
        sample_count = min(3, len(versions))
        if sample_count > 0:
            print(f"  Checking {sample_count} sample versions:")
            for i, version in enumerate(versions[:sample_count]):
                if 'law_version_id' not in version:
                    print(f"    ERROR: Version {i} missing 'law_version_id'")
                    continue
                    
                if 'structure' not in version:
                    print(f"    ERROR: Version {i} (ID: {version['law_version_id']}) missing 'structure'")
                    continue
                
                print(f"    Version {i}: ID {version['law_version_id']}, Title: {version.get('law_title_for_version', 'No title')}")
                if version['structure'] is not None:
                    print(f"    Has {len(version['structure'].get('children', []))} first-level nodes")
                else:
                    print(f"    Structure is null")
                    
        return True
    
    except json.JSONDecodeError:
        print(f"  ERROR: Invalid JSON format in {file_path}")
        return False
    except Exception as e:
        print(f"  ERROR: {str(e)} in {file_path}")
        return False

def main():
    # Get all JSON files
    individual_files = [f for f in os.listdir('.') if f.endswith('.json') and 'version_' in f]
    combined_file = "חוק_שירות_נתוני_אשראי_2016_all_versions.json"
    
    all_files = []
    all_files.extend(individual_files)
    if os.path.exists(combined_file):
        all_files.append(combined_file)
    
    if not all_files:
        print("No JSON files found!")
        return
    
    print(f"Found {len(all_files)} JSON files to verify")
    
    successful = 0
    for file_path in all_files:
        if file_path == combined_file:
            if verify_combined_json_file(file_path):
                successful += 1
        else:
            if verify_individual_json_file(file_path):
                successful += 1
        print("-" * 50)
    
    print(f"Verification complete: {successful}/{len(all_files)} files are valid")

if __name__ == "__main__":
    main() 