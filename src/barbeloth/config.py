# Shared constants used across the project.
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# File paths
DATA_FILE = ROOT / "resources" / "data.csv"
FILTERED_FILE = ROOT / "resources" / "filtered_data.csv"
BANNER_HISTORY_FILE = ROOT / "resources" / "banner_history_long.csv"
RERUN_SLOT_HISTORY_FILE = ROOT / "resources" / "rerun_slot_history.csv"
BANNER_RUNS_FILE = ROOT / "resources" / "banner_runs.csv"
MODEL_PREDICTIONS_FILE = ROOT / "resources" / "model_predictions.csv"
LAST_REGULAR_RERUN_FILE = ROOT / "resources" / "last_regular_rerun.csv"
LONGEST_WAIT_PREDICTIONS_FILE = ROOT / "resources" / "longest_waiting_time_will_run_predictions.csv"
CHARACTERS_FILE = ROOT / "resources" / "characters.json"
FIRST_APPEARANCE_FILE = ROOT / "resources" / "first_appearance.csv"

# Cached Enka reference data
AVATARS_FILE = ROOT / "resources" / "avatars.json"
LOC_FILE = ROOT / "resources" / "loc.json"

CURRENT_PATCH = 7.0

# Standard characters, Archons, Luna version map are manually maintained as no API expose them
STANDARD_CHARACTERS = [
    "Keqing", "Diluc", "Mona", "Qiqi",
    "Jean", "Dehya", "Tighnari", "Yumemizuki Mizuki",
    "Aloy", "Traveler"
]

ARCHONS = [
    "Venti", "Zhongli", "Raiden Shogun",
    "Nahida", "Furina", "Mavuika", "Columbina"
]

LUNA_VERSION_MAP = {
    "Luna I":   6.0,
    "Luna II":  6.1,
    "Luna III": 6.2,
    "Luna IV":  6.3,
    "Luna V":   6.4,
    "Luna VI":  6.5,
    "Luna VII": 6.6,
    "Luna VIII":6.7,
}

# API
# Enka publishes the game's own reference tables. avatars.json holds one entry
# per playable character (element, weapon, rarity, name hash). 
# locs.json maps those name hashes to localized display names.
ENKA_AVATARS_URL = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/refs/heads/master/store/gi/avatars.json"
ENKA_LOC_URL = "https://raw.githubusercontent.com/EnkaNetwork/API-docs/refs/heads/master/store/gi/locs.json"

USER_AGENT = "Barbeloth"
LANG = "en"

# Enka stores internal codenames, not the names players see.
ELEMENT_MAP = {
    "Fire":     "Pyro",
    "Water":    "Hydro",
    "Wind":     "Anemo",
    "Electric": "Electro",
    "Grass":    "Dendro",
    "Ice":      "Cryo",
    "Rock":     "Geo",
}

WEAPON_MAP = {
    "WEAPON_SWORD_ONE_HAND": "Sword",
    "WEAPON_CLAYMORE":       "Claymore",
    "WEAPON_POLE":           "Polearm",
    "WEAPON_BOW":            "Bow",
    "WEAPON_CATALYST":       "Catalyst",
}

# QUALITY_ORANGE is 5-star. QUALITY_ORANGE_SP covers Aloy and the Traveler
# variants, which are excluded as standard characters anyway.
FIVE_STAR_QUALITY = "QUALITY_ORANGE"