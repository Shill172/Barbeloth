# Going to read from the community updated google doc to get data for:
# Num reruns, avg rerun time,.. 

import requests 
import os
import csv
import pandas as pd
from config import (
    DATA_FILE, FILTERED_FILE, BANNER_HISTORY_FILE,
    RERUN_SLOT_HISTORY_FILE, BANNER_RUNS_FILE,
    ARCHONS, LUNA_VERSION_MAP
)

# Some names are spelt wrong in the google doc
NAME_CORRECTIONS = {
    "XIanyun": "Xianyun",
    "Emelie": "Emilie",
    "Mauvika": "Mavuika"
}


def read_banner_history():
    """
    Reads banner_history_long.csv and converts patch names to floats
    """

    df = pd.read_csv(BANNER_HISTORY_FILE)
    df["Patch"] = df["Patch"].map(LUNA_VERSION_MAP).fillna(df["Patch"])
    df["Patch"] = df["Patch"].astype(float)
    return df


def read_google_doc_for_rerun_info(doc_id, gid):
    """
    Fetches the community maintained Google Sheet as a CSV and saves it to
    resources/data.csv. The sheet is only for visual purposes, so
    it's quite messy in raw csv format 
    """

    url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"

    response = requests.get(url) 

    if response.status_code == 200: 

        with open(DATA_FILE, "wb") as f: 
            f.write(response.content)

        print(f"Successfully wrote to {DATA_FILE}")
    else: 
        return "Error: Couldn't fetch document"
    

def parse_banner_history():
    """
    Transforms raw data.csv to banner_history_long.csv

    Each row is a (character, patch) pair with: 
        Ran                 - 1 if the character ran that patch, 0 otherwise
        Time_since_ran      - patches since thier last banner 
        Total_runs          - total banner appearences
        Patches_since_debut - patches since thier first banner
        Run_frequency       - Total_runs / Patches_since_debut
        Is_archon           - 1 if character is an archon, 0 otherwise
        Is_chronicle        - 1 if the banner appearence is chronicle
        Element             - character element
        Weapon              - character weapon
    """
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

        if name1 in NAME_CORRECTIONS:
            name1 = NAME_CORRECTIONS[name1]
        if name2 in NAME_CORRECTIONS:
            name2 = NAME_CORRECTIONS[name2]

        if name1 != "":
            col_to_characters[col_idx].append(name1)
        if name2 != "":
            col_to_characters[col_idx].append(name2)

    # (character, patch) -> run type 
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
        if name in NAME_CORRECTIONS:
            name = NAME_CORRECTIONS[name]

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

            

    with open(BANNER_HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Patch", "Ran", "Time_since_ran", "Total_runs", "Patches_since_debut", "Run_frequency", "Is_archon", "Is_chronicle", "Element", "Weapon"])
        writer.writerows(rows)

    print(f"Written {len(rows)} rows to {BANNER_HISTORY_FILE}")


def get_num_rerun_slots_per_patch():
    """
    Returns a DataFrame (Patch, Rerun_slots) of how many non-chronicle rerun slots
    a patch had. Writes to rerun_slot_history.csv
    """
    df = read_banner_history() 
    all_patches = df["Patch"].copy().unique()

    df = df[df["Is_chronicle"] == 0]
    df = df[(df["Total_runs"] > 1) & (df["Ran"] == 1)] 
    runs_per_patch = df.groupby("Patch")["Ran"].sum().reset_index()
    runs_per_patch.columns = ["Patch", "Rerun_slots"]
    
    full_df = pd.DataFrame({"Patch": all_patches})

    final = pd.merge(full_df, runs_per_patch, on="Patch", how="left")
    final["Rerun_slots"] = final["Rerun_slots"].fillna(0).astype(int)

    final = final.sort_values("Patch").reset_index(drop=True)

    final.to_csv(RERUN_SLOT_HISTORY_FILE, index=False)
    return final

def get_banner_runs():
    """
    Returns a DataFrame (Patch, Name) for all non chronicle reruns. 
    Need this to calculate model and heuristic accuaracy. Also writes to file
    banner_runs.csv.
    """
    df = read_banner_history()

    df = df[df["Is_chronicle"] == 0]
    df = df[(df["Total_runs"] > 1) & (df["Ran"] == 1)]

    df = df[["Patch", "Name"]]

    df = df.sort_values(by="Patch", ascending=True)

    df.to_csv("resources/banner_runs.csv", index=False)

    return df
    

if __name__ == "__main__":
    parse_banner_history()
    get_num_rerun_slots_per_patch()
    get_banner_runs()
    print("Done.")