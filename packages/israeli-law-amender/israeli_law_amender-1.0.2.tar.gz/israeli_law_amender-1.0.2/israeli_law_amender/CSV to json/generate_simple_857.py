import json

# Create a basic structure for version 857
changes = {
    'law_version_id': "857",
    'law_title_for_version': "חוק שירות נתוני אשראי, התשע\"ו-2016",
    'structure_of_changes': {
        'type': 'Law',
        'children': [
            {
                'type': 'Chapter',
                'header_text': 'פרק ג\': הוראות כלליות',
                'children': [
                    {
                        'type': 'Section',
                        'header_text': 'הוראה שהשתנתה בגרסה 857'
                    }
                ]
            }
        ]
    }
}

# Save to file
output_file = "חוק_שירות_נתוני_אשראי_2016_version_857_changes.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(changes, f, ensure_ascii=False, indent=2)

print(f"Generated changes JSON for version 857") 