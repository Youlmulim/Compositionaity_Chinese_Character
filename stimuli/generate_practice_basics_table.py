import csv
from pathlib import Path

# Path Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_PATH = BASE_DIR / 'practice_basic_trial.csv'


def generate() -> None:
    char_list = ["火", "口", "山", "己", "工", "手", "生", "田"]

    # Define CSV Fieldnames with separated ID columns for efficiency
    fieldnames = [
        'char_id',
        'character',
        'image_file'
    ]

    rows = [
    ]
    
    # Generate all possible pairs
    for index, char in enumerate(char_list, start=1):
        
        rows.append({
            'char_id': index,
            'character': char,
            'image_file': f"{char}.png"
        })

    # Write data to practice_basic_trial.csv
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Success: Generated {len(rows)} rows with separated ID columns.")
    print(f"File saved at: {OUTPUT_PATH}")

if __name__ == '__main__':
    generate()