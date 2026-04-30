# Going to read from the community updated google doc to get data for:
# Num reruns, avg rerun time,.. 

import requests 
import os
import csv

DATA_FILE = "resources/data.csv"
FILTERED_FILE = "resources/filtered_data.csv"
STANDARD_CHARACTERS = ["Keqing", "Diluc", "Mona", "Qiqi", 
                        "Jean", "Dehya", "Tighnari", "Yumemizuki Mizuki"]
ARCHONS = ["Venti", "Zhongli", "Raiden Shogun", "Nahida", "Furina", "Mavuika", "Columbina"]

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
    
# Transforms the raw banner history into a long format CSV. 
# Each row represents one patch where a character: 
# 0: didn't run
# 1: run
# 2: run on chronicle banner
def parse_banner_history():

    # Some names are spelt wrong in the google doc
    CORRECTIONS = {
        "XIanyun": "Xianyun",
        "Emelie": "Emilie",
        "Mauvika": "Mavuika"
    }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    patch_row = reader[3]
    BANNER_COL_START = 5

    # patch_columns will look like:
    # { "1.0": [5, 6], "1.1": [7, 8], "1.2": [9, 10], ... }
    patch_columns = {}

    for col_idx in range(BANNER_COL_START, len(patch_row)):
        patch = patch_row[col_idx].strip()

        if patch == "":
            continue  # skip empty columns

        if patch not in patch_columns:
            patch_columns[patch] = []

        patch_columns[patch].append(col_idx)
    
    # Row 8 and 10 are the patch header rows containing the character name     
    slot1_row = reader[8]
    slot2_row = reader[10]

    # List of character names running in that column.
    # Columns can have 2 characters, one from each banner slot 
    # e.g. Nahida & Lauma in Luna I 1st half
    col_to_characters = {}

    for col_idx in range(BANNER_COL_START, len(slot1_row)):
        col_to_characters[col_idx] = []

        name1 = slot1_row[col_idx].strip() if col_idx < len(slot1_row) else ""
        name2 = slot2_row[col_idx].strip() if col_idx < len(slot2_row) else ""

        if name1 in CORRECTIONS:
            name1 = CORRECTIONS[name1]
        if name2 in CORRECTIONS:
            name2 = CORRECTIONS[name2]

        if name1 != "":
            col_to_characters[col_idx].append(name1)
        if name2 != "":
            col_to_characters[col_idx].append(name2)

    # (character, patch) -> run type 
    # Stores either 0, 1, C 
    ran_in_patch = {}

    # Read from banner header rows 
    for col_idx in range(BANNER_COL_START, len(slot1_row)):
        for name in col_to_characters.get(col_idx, []):

            # Find what patch name owns the column index 
            patch = None
            for patch_name, col_indices in patch_columns.items():
                if col_idx in col_indices:
                    patch = patch_name
                    break
            if patch:
                ran_in_patch[(name, patch)] = 1

    # Check for chronicle runs

    chronicles = set()
    for row in reader:
        if row[1] != "★★★★★":
            continue

        name = row[2].strip()
        if name in CORRECTIONS:
            name = CORRECTIONS[name]

        for col_idx in range(BANNER_COL_START, len(row)):
            if row[col_idx].strip() == "C":
                patch = None
                for patch_name, col_indices in patch_columns.items():
                    if col_idx in col_indices:
                        patch = patch_name
                        break
                if patch:
                    ran_in_patch[(name, patch)] = 1
                    chronicles.add((name, patch))

    all_patches = list(patch_columns.keys())    


    # Pull from filtered_data.csv to get all the characters we care about
    # (non standard 5 stars)
    characters = []
    with open(FILTERED_FILE, "r", encoding="utf-8") as f:
        reader_filtered = csv.DictReader(f)
        for row in reader_filtered:
            characters.append(row)

    rows = []

    for char in characters:
        name = char["Name"]
        element = char["Element"]
        weapon = char["Weapon"]

        seen_first_run = False
        time_since_ran = 0
        total_runs = 0 
        is_archon = 0 
        patches_since_debut = 0 
        run_frequency = 0 

        # All characters get a row for every patch
        for patch in all_patches:

            if name in ARCHONS:
                is_archon = 1 

            is_chronicle = 1 if (name, patch) in chronicles else 0 

            if (name, patch) in ran_in_patch:
                ran = ran_in_patch[(name, patch)]
                time_since_ran = 0
                seen_first_run = True
                total_runs = total_runs + 1 
                patches_since_debut = patches_since_debut + 1 
                
                
                rows.append([name, patch, ran, time_since_ran, total_runs, patches_since_debut, run_frequency, is_archon, is_chronicle, element, weapon])
                
                run_frequency = total_runs / patches_since_debut 
            else:
                ran = 0
                if seen_first_run:
                    time_since_ran += 1 
                    patches_since_debut += 1 
                    rows.append([name, patch, ran, time_since_ran, total_runs,  patches_since_debut, run_frequency, is_archon, is_chronicle, element, weapon,])
                else:
                    time_since_ran = 0  

            

    with open("resources/banner_history_long.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Patch", "Ran", "Time_since_ran", "Total_runs", "Patches_since_debut", "Run_frequency", "Is_archon", "Is_chronicle", "Element", "Weapon"])
        writer.writerows(rows)

    print(f"Written {len(rows)} rows to banner_history_long.csv")

#read_google_doc_for_rerun_info("1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy", "551073839") 

#parse_banner_history() 

#     doc_id = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
#     gid = "551073839"