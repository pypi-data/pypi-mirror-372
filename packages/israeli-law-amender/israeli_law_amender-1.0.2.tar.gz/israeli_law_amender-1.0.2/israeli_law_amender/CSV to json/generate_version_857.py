import csv
import json
import copy

def main():
    """Generate changes JSON specifically for version 857"""
    csv_file_path = "2002363 - חוק שירות נתוני אשראי 2016.csv"
    target_version = "857"
    
    # Read CSV data
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        all_rows = list(csv_reader)
    
    # Get rows specifically for version 857
    version_857_rows = [row for row in all_rows if row.get('FK_LawVersionID') == target_version]
    
    print(f"Found {len(version_857_rows)} rows for version 857")
    
    # Display information about the rows
    for idx, row in enumerate(version_857_rows):
        component_id = row.get('\ufeffID') or row.get('ID')
        action_type = row.get('FK_ActionTypeID')
        status = row.get('FK_StatusID')
        is_delete = row.get('IsDelete')
        header = row.get('HeaderText', "")
        parent_id = row.get('FK_ParentComponentID')
        
        print(f"Row {idx+1}: ComponentID={component_id}, ActionType={action_type}, Status={status}, IsDelete={is_delete}")
        print(f"       Header={header}, ParentID={parent_id}")
    
    # Create a basic structure for this version
    changes = {
        'law_version_id': target_version,
        'law_title_for_version': "חוק שירות נתוני אשראי, התשע\"ו-2016",
        'structure_of_changes': {
            'type': 'Law',
            'children': []
        }
    }
    
    # Add each component from this version as a direct child of the root
    for row in version_857_rows:
        component_id = row.get('\ufeffID') or row.get('ID')
        header = row.get('HeaderText', "No Header")
        content = row.get('Content', "")
        component_type = row.get('FK_ComponentTypeID')
        
        # Map component type to a readable name
        type_mapping = {
            '1': 'Law',
            '3': 'Chapter',
            '4': 'SubChapter',
            '6': 'Section',
            '7': 'SubSection',
            '8': 'Clause'
        }
        type_name = type_mapping.get(component_type, f"Unknown-{component_type}")
        
        # Create a node for this component
        node = {
            'type': type_name,
            'header_text': header if header and header != "NULL" else None,
            'body_text': content if content and content != "NULL" else None
        }
        
        # Remove None values
        node = {k: v for k, v in node.items() if v is not None}
        
        # Add to children
        changes['structure_of_changes']['children'].append(node)
    
    # Save to file
    output_file = f"חוק_שירות_נתוני_אשראי_2016_version_{target_version}_changes.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)
    
    print(f"Generated changes JSON for version {target_version}")

if __name__ == "__main__":
    main() 