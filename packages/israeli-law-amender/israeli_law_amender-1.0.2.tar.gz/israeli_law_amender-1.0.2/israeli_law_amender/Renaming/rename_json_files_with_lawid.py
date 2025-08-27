#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import re
import logging
from difflib import SequenceMatcher
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rename_operations.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def normalize_law_name(name):
    """
    Normalize law name for comparison by removing punctuation and normalizing space.
    Years and other distinguishing text are preserved.
    """
    if not name:
        return ""
    
    # Remove extra punctuation and normalize spaces, but keep years.
    name = re.sub(r'[,\(\)\[\]\"\':-]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    return name

def similarity_score(a, b):
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def find_best_match(json_filename, csv_names):
    """
    Find the best matching CSV name for a JSON filename
    Returns (best_match_name, similarity_score, law_id)
    """
    # Extract law name from JSON filename
    json_name = json_filename.replace('_current.json', '').replace('.json', '')
    json_name = re.sub(r'(_original)?_oldid_\d+', '', json_name)
    json_name = json_name.replace('_', ' ')
    
    json_normalized = normalize_law_name(json_name)

    if not json_normalized:
        return None, 0, None
    
    best_match = None
    best_score = 0
    best_law_id = None
    
    for csv_name, law_id in csv_names:
        csv_normalized = normalize_law_name(csv_name)
        
        if not csv_normalized:
            continue

        # Give a bonus if the CSV name is a substring of the JSON name.
        # This helps with truncated CSV entries.
        substring_bonus = 0.5 if csv_normalized in json_normalized else 0

        # SequenceMatcher score
        seq_score = similarity_score(json_normalized, csv_normalized)
        
        # Word-based score. We use the length of the CSV name's words in the
        # denominator to avoid penalizing matches with truncated CSV names.
        json_words = set(json_normalized.split())
        csv_words = set(csv_normalized.split())
        
        if not csv_words:
            word_score = 0
        else:
            word_score = len(json_words.intersection(csv_words)) / len(csv_words)

        # Combine scores. Word score is weighted more heavily, and the
        # substring bonus gives a large advantage to likely matches.
        combined_score = (seq_score * 0.4) + (word_score * 0.6) + substring_bonus
        
        if combined_score > best_score:
            best_score = combined_score
            best_match = csv_name
            best_law_id = law_id
    
    return best_match, best_score, best_law_id

def load_csv_data(csv_file_path):
    """Load CSV data and return list of (name, law_id) tuples"""
    csv_names = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            # Manually read and clean headers
            header = [h.strip() for h in next(csv.reader(file))]
            
            reader = csv.DictReader(file, fieldnames=header)
            
            # Log header to debug
            if not reader.fieldnames:
                logging.error("Could not read CSV headers. File might be empty or corrupt.")
                return []

            logging.info(f"CSV headers: {reader.fieldnames}")
            
            # Check if required headers are present
            required_headers = ['Name', 'LawID']
            if not all(h in reader.fieldnames for h in required_headers):
                logging.error(f"CSV file must contain 'Name' and 'LawID' columns. Found: {reader.fieldnames}")
                return []

            for i, row in enumerate(reader):
                name = row.get('Name', '').strip()
                law_id = row.get('LawID', '').strip()
                
                if name and law_id:
                    # Remove quotes from name if present
                    name = name.strip('"')
                    csv_names.append((name, law_id))
                else:
                    logging.warning(f"Skipping row {i+2} due to missing Name or LawID. Row: {row}")
    except FileNotFoundError:
        logging.error(f"CSV file not found at path: {csv_file_path}")
        return []
    except Exception as e:
        logging.error(f"Error loading CSV file {csv_file_path}: {e}")
        return []
        
    return csv_names

def main():
    # Paths
    csv_file_path = 'Data/amd_database_flow.csv'
    json_directory = 'Data/JSON_Laws_v2'
    
    # Check if paths exist
    if not os.path.exists(csv_file_path):
        logging.error(f"CSV file not found: {csv_file_path}")
        return
    
    if not os.path.exists(json_directory):
        logging.error(f"JSON directory not found: {json_directory}")
        return
    
    # Load CSV data
    logging.info("Loading CSV data...")
    csv_names = load_csv_data(csv_file_path)
    logging.info(f"Loaded {len(csv_names)} entries from CSV")
    
    # Get all JSON files
    json_files = [f for f in os.listdir(json_directory) if f.endswith('.json')]
    logging.info(f"Found {len(json_files)} JSON files")
    
    # Track operations
    successful_renames = []
    failed_matches = []
    csv_entries_used = set()
    
    # Process each JSON file
    for json_file in json_files:
        logging.info(f"Processing: {json_file}")
        
        # Skip if already has LawID suffix
        if re.search(r'_LawID_\d+\.json$', json_file):
            logging.info(f"Skipping {json_file} - already has LawID suffix")
            continue
        
        # Find best match
        best_match_name, score, law_id = find_best_match(json_file, csv_names)
        
        if score < 0.9:  # Stricter threshold with the new scoring logic
            logging.warning(f"No good match found for {json_file} (best score: {score:.2f})")
            failed_matches.append({
                'file': json_file,
                'best_match': best_match_name,
                'score': score,
                'reason': 'Low similarity score'
            })
            continue
        
        # Generate new filename
        base_name = json_file.replace('.json', '')
        new_filename = f"{base_name}_LawID_{law_id}.json"
        
        old_path = os.path.join(json_directory, json_file)
        new_path = os.path.join(json_directory, new_filename)
        
        # Check if target file already exists
        if os.path.exists(new_path):
            logging.warning(f"Target file already exists: {new_filename}")
            failed_matches.append({
                'file': json_file,
                'best_match': best_match_name,
                'score': score,
                'reason': 'Target file already exists'
            })
            continue
        
        # Rename file
        try:
            os.rename(old_path, new_path)
            logging.info(f"Renamed: {json_file} -> {new_filename} (LawID: {law_id}, Score: {score:.2f})")
            successful_renames.append({
                'old_name': json_file,
                'new_name': new_filename,
                'law_id': law_id,
                'matched_csv_name': best_match_name,
                'similarity_score': score
            })
            csv_entries_used.add(best_match_name)
        except Exception as e:
            logging.error(f"Failed to rename {json_file}: {e}")
            failed_matches.append({
                'file': json_file,
                'best_match': best_match_name,
                'score': score,
                'reason': f'Rename error: {e}'
            })
    
    # Find unused CSV entries
    all_csv_names = {name for name, _ in csv_names}
    unused_csv_entries = all_csv_names - csv_entries_used
    
    # Log summary
    logging.info("=== OPERATION SUMMARY ===")
    logging.info(f"Total JSON files processed: {len(json_files)}")
    logging.info(f"Successful renames: {len(successful_renames)}")
    logging.info(f"Failed matches: {len(failed_matches)}")
    logging.info(f"CSV entries used: {len(csv_entries_used)}")
    logging.info(f"Unused CSV entries: {len(unused_csv_entries)}")
    
    # Detailed logs
    logging.info("\n=== SUCCESSFUL RENAMES ===")
    for rename in successful_renames:
        logging.info(f"✓ {rename['old_name']} -> {rename['new_name']} (LawID: {rename['law_id']}, Score: {rename['similarity_score']:.2f})")
    
    logging.info("\n=== FAILED MATCHES ===")
    for failed in failed_matches:
        logging.info(f"✗ {failed['file']} - {failed['reason']} (Best match: {failed['best_match']}, Score: {failed.get('score', 'N/A')})")
    
    logging.info("\n=== UNUSED CSV ENTRIES (Laws not found in JSON directory) ===")
    for unused in sorted(unused_csv_entries):
        logging.info(f"○ {unused}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"rename_report_{timestamp}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as report:
        report.write("JSON FILES RENAME OPERATION REPORT\n")
        report.write("=" * 50 + "\n\n")
        
        report.write(f"Operation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Total JSON files: {len(json_files)}\n")
        report.write(f"Successful renames: {len(successful_renames)}\n")
        report.write(f"Failed matches: {len(failed_matches)}\n")
        report.write(f"CSV entries used: {len(csv_entries_used)}\n")
        report.write(f"Unused CSV entries: {len(unused_csv_entries)}\n\n")
        
        report.write("SUCCESSFUL RENAMES:\n")
        report.write("-" * 20 + "\n")
        for rename in successful_renames:
            report.write(f"✓ {rename['old_name']}\n")
            report.write(f"  -> {rename['new_name']}\n")
            report.write(f"  LawID: {rename['law_id']}\n")
            report.write(f"  Matched CSV: {rename['matched_csv_name']}\n")
            report.write(f"  Similarity: {rename['similarity_score']:.2f}\n\n")
        
        report.write("FAILED MATCHES:\n")
        report.write("-" * 15 + "\n")
        for failed in failed_matches:
            report.write(f"✗ {failed['file']}\n")
            report.write(f"  Reason: {failed['reason']}\n")
            report.write(f"  Best match: {failed['best_match']}\n")
            report.write(f"  Score: {failed.get('score', 'N/A')}\n\n")
        
        report.write("UNUSED CSV ENTRIES:\n")
        report.write("-" * 18 + "\n")
        for unused in sorted(unused_csv_entries):
            report.write(f"○ {unused}\n")
    
    logging.info(f"\nDetailed report saved to: {report_filename}")

if __name__ == "__main__":
    main() 