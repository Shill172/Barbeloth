import requests 
import json
import os 
import csv
from config import (
    JMP_URL, CHARACTERS_FILE,
    STANDARD_CHARACTERS, MANUAL_DATA, FILTERED_FILE
)

def sync_local_data():
    """
    Pulls 5 stars from JMP Blue API and then merges in any manual data
    from config.py. Writes the results to resources.characters.json. 
    """

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
    with open (CHARACTERS_FILE, "r", encoding="utf-8") as f: 
        api_data = json.load(f)

    missing = []

    with open(FILTERED_FILE, "r", encoding="utf-8") as f: 
        reader = csv.DictReader(f)

        for row in reader:
            name = row["Name"]

            if name not in api_data:
                missing.append(name)
        
    if missing: 
        print("Following characters are in filtered_data.csv but not in api")
        for name in missing:
            print(f"{name}")
    else: 
        print("All characters are accounted for")