import requests 
import json
import os 
import csv
from config import (
    JMP_URL, CHARACTERS_FILE,
    STANDARD_CHARACTERS, MANUAL_DATA, FILTERED_FILE,
    FIRST_APPEARANCE_FILE
)

def sync_local_data():
    print("Fetching data from JMP Blue API")
    response = requests.get(JMP_URL)

    if response.status_code == 200: 
        raw_data = response.json()
        clean_data = {}

        for character in raw_data:
            if character.get("rarity") == 5 and character.get("name") not in STANDARD_CHARACTERS:
                name = character.get("name")
                clean_data[name] = {
                    "element": character.get("vision"),
                    "weapon": character.get("weapon")
                }

        clean_data.update(MANUAL_DATA)

        os.makedirs("resources", exist_ok=True)
        with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4)

        print(f"Saved {len(clean_data)} characters to {CHARACTERS_FILE}")
    else:
        print(f"Failed to sync. API returned: {response.status_code}")


def find_missing_characters():
    """
    Compares characters.json against filtered_data.csv to find any charactes
    found in csv but not in json. Indicates whether a character needs to be 
    added to MANUAL_DATA in config.py. 
    """
    with open(CHARACTERS_FILE, "r", encoding="utf-8") as f: 
        api_data = json.load(f)

    missing_from_csv = []
    missing_from_json = []

    with open(FILTERED_FILE, "r", encoding="utf-8") as f: 
        reader = csv.DictReader(f)
        csv_names = set()
        for row in reader:
            name = row["Name"]
            csv_names.add(name)
            if name not in api_data:
                missing_from_csv.append(name)

    for name in api_data:
        if name not in csv_names:
            missing_from_json.append(name)

    if missing_from_csv:
        print("In filtered_data.csv but not in characters.json:")
        for name in missing_from_csv:
            print(f"  {name}")

    if missing_from_json:
        print("In characters.json but not in filtered_data.csv (won't show in banner history!):")
        for name in missing_from_json:
            print(f"  {name}")

    if not missing_from_csv and not missing_from_json:
        print("All characters are accounted for")