import csv
import json
import copy
from collections import defaultdict

# Component type mapping
COMPONENT_TYPE_MAP = {
    '1': 'Law',
    '3': 'Chapter',
    '4': 'SubChapter',
    '6': 'Section',
    '7': 'SubSection',
    '8': 'Clause'
}

def get_component_type_name(type_id_str):
    """Map a component type ID to its name"""
    return COMPONENT_TYPE_MAP.get(type_id_str, f"Unknown-{type_id_str}")

def clean_text(text):
    """Clean up text fields by stripping whitespace and handling None"""
    if text is None or text == "NULL":
        return None
    text = text.strip()
    return text if text else None

def create_node_from_row(row_data):
    """Extract relevant fields from a CSV row and create a node dictionary"""
    # Handle BOM character in ID column
    component_id_key = next((k for k in row_data.keys() if k.endswith('ID') and k.startswith('\ufeff')), None)
    if component_id_key:
        component_id = row_data[component_id_key]
    else:
        component_id = row_data.get('ID')
        
    # Get the second ID which is the record ID
    record_id = row_data.get('ID.1') if 'ID.1' in row_data else row_data.get('ID', '')
    if record_id == component_id:  # If they're the same, use a different field
        for key in row_data.keys():
            if key != component_id_key and key.endswith('ID') and key != 'FK_LawVersionID' and key != 'FK_ComponentTypeID':
                record_id = row_data.get(key, '')
                break
    
    node = {
        'component_version_id': component_id,
        'record_id': record_id,
        'type_id': row_data.get('FK_ComponentTypeID'),
        'type': get_component_type_name(row_data.get('FK_ComponentTypeID')),
        'header_text': clean_text(row_data.get('HeaderText')),
        'body_text': clean_text(row_data.get('Content')),
        'parent_id': clean_text(row_data.get('FK_ParentComponentID')),
        'order_num': int(row_data.get('ComponentOrdinal', 0)) if row_data.get('ComponentOrdinal') and row_data.get('ComponentOrdinal') != 'NULL' else 0,
        'law_version_id': row_data.get('FK_LawVersionID'),
        'action_type_id': clean_text(row_data.get('FK_ActionTypeID')),
        'status': int(row_data.get('FK_StatusID')) if row_data.get('FK_StatusID') and row_data.get('FK_StatusID') != 'NULL' else None,
        'is_delete': True if row_data.get('IsDelete') and row_data.get('IsDelete') not in ('0', 'NULL', '') else False,
        'number_text': clean_text(row_data.get('NumberText')),
        'children': []
    }
    return node

def build_tree_for_version(nodes_for_version_dict):
    """Build a hierarchical tree for a specific law version state"""
    if not nodes_for_version_dict:
        # Create a default minimal root node for empty versions
        return {
            'component_version_id': 'root',
            'record_id': 'root',
            'type_id': '1',
            'type': 'Law',
            'header_text': None,
            'body_text': None,
            'order_num': 0,
            'parent_id': None,
            'children': []
        }

    # Create a copy to avoid modifying the original
    local_nodes = copy.deepcopy(nodes_for_version_dict)
    
    # Reset children for all nodes
    for node_id, node in local_nodes.items():
        node['children'] = []
    
    # Build parent-child relationships
    root_candidates = []
    for node_id, node in local_nodes.items():
        parent_id = node.get('parent_id')
        if parent_id and parent_id in local_nodes:
            local_nodes[parent_id]['children'].append(node)
        else:
            root_candidates.append(node)
    
    # Find the root node (typically TypeID = 1, which is Law)
    law_root = None
    for node in root_candidates:
        if node['type'] == 'Law':
            law_root = node
            break
    
    # If there's no specific Law node, use the first root candidate or create a default root
    if not law_root:
        if root_candidates:
            law_root = sorted(root_candidates, key=lambda x: x.get('order_num', 0))[0]
        else:
            # Create a default root node if no root candidates found
            law_root = {
                'component_version_id': 'root',
                'record_id': 'root',
                'type_id': '1',
                'type': 'Law',
                'header_text': None,
                'body_text': None,
                'order_num': 0,
                'parent_id': None,
                'children': []
            }
            
            # Add all orphaned nodes to this root
            for node_id, node in local_nodes.items():
                law_root['children'].append(node)
    
    # Sort children by order_num at each level
    sort_children_recursive(law_root)
    
    return law_root

def sort_children_recursive(node):
    """Sort children by order_num recursively"""
    if node['children']:
        node['children'] = sorted(node['children'], key=lambda x: x.get('order_num', 0))
        for child in node['children']:
            sort_children_recursive(child)

def cleanup_node_for_output(node):
    """Clean up node for output by removing empty fields and internal metadata"""
    cleaned_node = {
        'type': node['type'],
        'header_text': node['header_text'],
        'body_text': node['body_text'],
        'number_text': node.get('number_text')
    }
    
    # Remove None/empty values
    cleaned_node = {k: v for k, v in cleaned_node.items() if v is not None}
    
    # Add children if they exist
    if node['children']:
        cleaned_node['children'] = [cleanup_node_for_output(child) for child in node['children']]
    
    return cleaned_node

def build_all_law_versions(csv_filepath):
    """Process the CSV and build a JSON structure for all versions of the law"""
    # Read CSV data first to see actual column names
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        all_rows_raw = list(csv_reader)
    
    # Print first row keys to see actual column names for debugging
    if all_rows_raw:
        first_row = all_rows_raw[0]
        print(f"CSV Column Names: {list(first_row.keys())}")
    
    # Get all unique law versions and sort them
    law_version_ids = sorted(set(row.get('FK_LawVersionID') for row in all_rows_raw), key=int)
    print(f"Found {len(law_version_ids)} law versions: {', '.join(law_version_ids)}")
    
    # Initialize structure to track the current state of all components
    active_nodes_in_current_law_state = {}
    
    # List to store JSON data for all versions
    all_versions_json_data = []
    
    # Process each law version chronologically
    for law_version_id_str in law_version_ids:
        print(f"\nProcessing law version {law_version_id_str}")
        
        # Get all changes for this specific version
        changes_in_this_version = [
            row for row in all_rows_raw 
            if row.get('FK_LawVersionID') == law_version_id_str
        ]
        
        print(f"  Found {len(changes_in_this_version)} component changes in this version")
        
        # Apply changes from this version to our current state
        for change_row in changes_in_this_version:
            # Get component ID handling BOM character
            component_id_key = next((k for k in change_row.keys() if k.endswith('ID') and k.startswith('\ufeff')), None)
            component_version_id = change_row.get(component_id_key) if component_id_key else change_row.get('ID')
            
            if not component_version_id:
                continue  # Skip rows without component ID
                
            # Check if this change is an active update or a deletion
            is_active = (
                (change_row.get('FK_StatusID') in ('1', '4')) and  # Status is active or superseded
                not (change_row.get('IsDelete') and change_row.get('IsDelete') not in ('0', 'NULL', ''))  # Not deleted
            )
            
            is_deleted = (
                (change_row.get('IsDelete') and change_row.get('IsDelete') not in ('0', 'NULL', '')) or  # IsDelete flag
                (change_row.get('FK_ActionTypeID') == '3' and change_row.get('FK_StatusID') == '4')  # Delete action + superseded
            )
            
            # Update or remove the component in our current state
            if is_active:
                active_nodes_in_current_law_state[component_version_id] = create_node_from_row(change_row)
            elif is_deleted and component_version_id in active_nodes_in_current_law_state:
                del active_nodes_in_current_law_state[component_version_id]
        
        # Make a deep copy of the current state for tree building
        current_version_nodes = copy.deepcopy(active_nodes_in_current_law_state)
        
        # Build the hierarchical tree for this version
        root_node = build_tree_for_version(current_version_nodes)
        
        # For output, clean up the nodes and create a cleaner JSON structure
        cleaned_root = cleanup_node_for_output(root_node)
        
        # Try to get law title from the root node
        law_title = root_node.get('header_text')
        if not law_title:
            law_title = "חוק שירות נתוני אשראי, התשע\"ו-2016"
        
        version_json = {
            'law_version_id': law_version_id_str,
            'law_title_for_version': law_title,
            'structure': cleaned_root
        }
        
        all_versions_json_data.append(version_json)
        
        # Save individual version to file
        output_file = f"חוק_שירות_נתוני_אשראי_2016_version_{law_version_id_str}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(version_json, f, ensure_ascii=False, indent=2)
        
        print(f"  Saved version {law_version_id_str} to: {output_file}")
    
    # Save all versions to a combined file
    combined_data = {
        "law_name": "חוק שירות נתוני אשראי, התשע\"ו-2016",
        "versions": all_versions_json_data
    }
    
    combined_output_file = "חוק_שירות_נתוני_אשראי_2016_all_versions.json"
    with open(combined_output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSuccessfully processed {len(all_versions_json_data)} versions into: {combined_output_file}")
    
    return all_versions_json_data

if __name__ == "__main__":
    csv_file_path = "2002363 - חוק שירות נתוני אשראי 2016.csv"
    build_all_law_versions(csv_file_path)