import requests 
import json
import os 
import csv

JMP_URL = "https://genshin.jmp.blue/characters/all"
MY_API = "resources/characters.json"
STANDARD_CHARACTERS = ["Keqing", "Diluc", "Mona", "Qiqi", 
                        "Jean", "Dehya", "Tighnari", "Yumemizuki Mizuki", 
                        "Aloy"]
MANUAL_DATA = {
    "Xilonen": {"element": "Geo", "weapon": "Sword"},
    "Chasca": {"element": "Anemo", "weapon": "Bow"},
    "Mavuika": {"element": "Pyro", "weapon": "Claymore"},
    "Citlali": {"element": "Cryo", "weapon": "Catalyst"},
    "Varesa": {"element": "Electro", "weapon": "Catalyst"},
    "Escoffier": {"element": "Cryo", "weapon": "Polearm"},
    "Skirk": {"element": "Cryo", "weapon": "Sword"},
    "Ineffa": {"element": "Electro", "weapon": "Polearm"},
    "Lauma": {"element": "Dendro", "weapon": "Catalyst"},
    "Flins": {"element": "Electro", "weapon": "Polearm"},
    "Nefer": {"element": "Dendro", "weapon": "Catalyst"},
    "Durin": {"element": "Pyro", "weapon": "Sword"},
    "Columbina": {"element": "Hydro", "weapon": "Catalyst"},
    "Zibai": {"element": "Geo", "weapon": "Sword"},
    "Varka": {"element": "Anemo", "weapon": "Claymore"}
}

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
        with open(MY_API, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4)

        print(f"Saved {len(clean_data)} characters to {MY_API}")
    else:
        print(f"Failed to sync. API returned: {response.status_code}")

# Need this as JMP API isn't updated. 
def find_missing_characters():
    with open (MY_API, "r", encoding="utf-8") as f: 
        api_data = json.load(f)

    missing = []

    with open("resources/filtered_data.csv", "r", encoding="utf-8") as f: 
        reader = csv.DictReader(f)

        for row in reader:
            name = row["Name"]

            if name not in api_data:
                missing.append(name)
        
        if missing: 
            print("Following characters are in filtered data but not in api")
            for name in missing:
                print(f"{name}")
        else: 
            print("All characters are accounted for")

if __name__ == "__main__":
    sync_local_data()
    find_missing_characters()