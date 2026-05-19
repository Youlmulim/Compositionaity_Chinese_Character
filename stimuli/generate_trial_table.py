import csv
from itertools import product
from pathlib import Path

# Path Configuration
BASE_DIR = Path(__file__).parent
CHARS_CSV_PATH = BASE_DIR / 'basic_characters.csv'
OUTPUT_PATH = BASE_DIR / 'trial_table.csv'

def load_character_mappings():
    """
    Reads basic_characters.csv and returns a dictionary 
    mapping the character to its integer ID {char: id}.
    """
    char_to_id = {}
    try:
        with open(CHARS_CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Mapping character (e.g., '月') to its integer ID (e.g., 1)
                char_to_id[row['character']] = int(row['char_id'])
    except FileNotFoundError:
        print(f"Error: {CHARS_CSV_PATH} not found. Please ensure the file exists.")
        return None
    return char_to_id

def generate() -> None:
    # 1. Load mapping data from the CSV
    char_mapping = load_character_mappings()
    if not char_mapping:
        return

    char_list = list(char_mapping.keys())

    # 2. Define CSV Fieldnames with separated ID columns for efficiency
    fieldnames = [
        'stim_pair_id',
        'char1',
        'char2',
        'char1_id',      # Separated ID for character 1
        'char2_id',      # Separated ID for character 2
        'canonical_pair',
        'meaning',
        'meaning_opt1',
        'meaning_opt2',
        'meaning_opt3',
        'meaning_opt4',
    ]

    rows = []
    
    # 3. Generate all possible pairs (13 * 13 = 169 rows)
    # Using product() ensures we get permutations and self-pairs (e.g., 1-1, 1-2, 2-1)
    for index, (c1, c2) in enumerate(product(char_list, repeat=2), start=1):
        pair_id = f"pair_{index:03d}"
        
        rows.append({
            'stim_pair_id':   pair_id,
            'char1':          c1,
            'char2':          c2,
            'char1_id':       char_mapping[c1],
            'char2_id':       char_mapping[c2],
            'canonical_pair': c1 + c2,
            'meaning':       '',
            'meaning_opt1':  '',
            'meaning_opt2':  '',
            'meaning_opt3':  '',
            'meaning_opt4':  '',
        })

    # 4. Write data to trial_table.csv
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Success: Generated {len(rows)} rows with separated ID columns.")
    print(f"File saved at: {OUTPUT_PATH}")

if __name__ == '__main__':
    generate()