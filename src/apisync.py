"""Syncs character metadata (name, element, weapon) from Enka's reference data."""

import requests
import json
import os
import csv
from config import (
    ENKA_AVATARS_URL, ENKA_LOC_URL, USER_AGENT, LANG,
    AVATARS_FILE, LOC_FILE, CHARACTERS_FILE,
    ELEMENT_MAP, WEAPON_MAP, FIVE_STAR_QUALITY,
    STANDARD_CHARACTERS, FILTERED_FILE,
)


def load_etag(etag_path):
    if os.path.exists(etag_path):
        with open(etag_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def save_etag(etag_path, etag):
    with open(etag_path, "w", encoding="utf-8") as f:
        f.write(etag)


def fetch_cached_json(url, path):
    """
    Fetch JSON, reusing the local copy when the server says nothing changed.
    Enka's reference files are several hundred KB and rarely change, so we
    send the stored ETag and fall back to disk on a 304.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    etag_path = path + ".etag"

    cached_etag = load_etag(etag_path)
    headers = {"User-Agent": USER_AGENT}

    if cached_etag and os.path.exists(path):
        headers["If-None-Match"] = cached_etag

    response = requests.get(url, headers=headers)

    if response.status_code == 304:  # Nothing changed
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} for {url}")

    data = response.json()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    new_etag = response.headers.get("ETag")
    if new_etag:
        save_etag(etag_path, new_etag)

    return data


def get_localized_name(name_hash, loc, lang=LANG):
    """Resolve a TextMap hash to a readable localized name."""
    return loc.get(lang, {}).get(str(name_hash))


def sync_local_data():
    """
    Build characters.json from Enka's avatars.json + locs.json.

    Keeps only 5-star characters that aren't on the standard banner, mapping
    Enka's internal codenames onto the names used in the banner history sheet.
    """
    print("Fetching character data from Enka")
    avatars = fetch_cached_json(ENKA_AVATARS_URL, AVATARS_FILE)
    loc = fetch_cached_json(ENKA_LOC_URL, LOC_FILE)

    if LANG not in loc:
        raise Exception(f"Language '{LANG}' not present in Enka localization data")

    clean_data = {}
    unresolved = []

    for avatar_id, character in avatars.items():
        if character.get("QualityType") != FIVE_STAR_QUALITY:
            continue

        name = get_localized_name(character.get("NameTextMapHash"), loc)

        if not name:
            unresolved.append(avatar_id)
            continue

        if name in STANDARD_CHARACTERS:
            continue

        # Traveler elements and costumes share a name across several avatar IDs.
        if name in clean_data:
            continue

        element = ELEMENT_MAP.get(character.get("Element"))
        weapon = WEAPON_MAP.get(character.get("WeaponType"))

        if element is None or weapon is None:
            unresolved.append(name)
            continue

        clean_data[name] = {"element": element, "weapon": weapon}

    if not clean_data:
        raise Exception("Enka sync produced no characters, aborting rather than overwriting")

    os.makedirs("resources", exist_ok=True)
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=4)

    print(f"Saved {len(clean_data)} characters to {CHARACTERS_FILE}")

    if unresolved:
        print(f"Skipped {len(unresolved)} entries with incomplete data: {', '.join(map(str, unresolved))}")


def find_missing_characters():
    """
    Compares characters.json against filtered_data.csv to find any characters
    found in one but not the other. Characters present in the JSON but absent
    from the sheet are usually upcoming ones Enka has added ahead of release.
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