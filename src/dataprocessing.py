# Going to read from the community updated google doc to get data for:
# Num reruns, avg rerun time,.. 

import json
import requests 
import os
import csv

DATA_FILE = "resources/data.csv"
FILTERED_FILE = "resources/filtered_data.csv"
STANDARD_CHARACTERS = ["Keqing", "Diluc", "Mona", "Qiqi", 
                        "Jean", "Dehya", "Tighnari", "Yumemizuki Mizuki"]

def read_google_doc_for_rerun_info(doc_id, gid):

    resources = "resources"
    if not os.path.exists(resources):
        os.makedirs(resources)

    url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"

    response = requests.get(url) 

    if response.status_code == 200: 

        with open(DATA_FILE, "wb") as f: 
            f.write(response.content)

        print(f"Successfully wrote to {DATA_FILE}")
    else: 
        return "Error: Couldn't fetch document"
    

def create_filtered_data(): 

    # Some names are spelt wrong in the google doc
    CORRECTIONS = {
        "XIanyun": "Xianyun",
        "Emelie": "Emilie",
        "Mauvika": "Mavuika"
    }

    # UTF 8 to parse ★'s
    with open(DATA_FILE, "r", encoding='utf-8') as infile: 
        reader = list(csv.reader(infile))

    with open("resources/characters.json", "r", encoding="utf-8") as f:
        api_data = json.load(f)

    with open(FILTERED_FILE, "w", newline='', encoding='utf-8') as outfile: 
        writer = csv.writer(outfile)

        writer.writerow(["Name", "Appearances", "Element", "Weapon"])

        # Example csv structure: 
        # [Blank, Rarity, Name, Blank, Appearences]
        for row in reader:
            if row[1] == "★★★★★": # Only care about 5-stars
                
                name = row[2]
                appearences = row[4]

                if name in CORRECTIONS:
                    name = CORRECTIONS[name]

                if name and name not in STANDARD_CHARACTERS: # Standard characters don't rerun
                   
                    element = api_data.get(name, {}).get("element", "Unknown")
                    weapon = api_data.get(name, {}).get("weapon", "Unknown")
                   
                    writer.writerow([name, appearences, element, weapon])
                    print(f"Saved: {name} ({element} {weapon}) with {appearences} appearances")

            elif row[1] == "★★★★":
                break; 
            
        print("Data filter complete")
    
doc_id = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
gid = "551073839"

if __name__ == "__main__":
    read_google_doc_for_rerun_info(doc_id, gid)
    create_filtered_data()