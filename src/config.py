# Shared constants used across the project.

# File paths
DATA_FILE = "resources/data.csv"
FILTERED_FILE = "resources/filtered_data.csv"
BANNER_HISTORY_FILE = "resources/banner_history_long.csv"
RERUN_SLOT_HISTORY_FILE = "resources/rerun_slot_history.csv"
BANNER_RUNS_FILE = "resources/banner_runs.csv"
MODEL_PREDICTIONS_FILE = "resources/model_predictions.csv"
LAST_REGULAR_RERUN_FILE = "resources/last_regular_rerun.csv"
LONGEST_WAIT_PREDICTIONS_FILE = "resources/longest_waiting_time_will_run_predictions.csv"
CHARACTERS_FILE = "resources/characters.json"

# Character lists
STANDARD_CHARACTERS = [
    "Keqing", "Diluc", "Mona", "Qiqi",
    "Jean", "Dehya", "Tighnari", "Yumemizuki Mizuki", "Aloy"
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
JMP_URL = "https://genshin.jmp.blue/characters/all"

# Characters missing in JMP API
MANUAL_DATA = {
    "Xilonen":   {"element": "Geo",      "weapon": "Sword"},
    "Chasca":    {"element": "Anemo",    "weapon": "Bow"},
    "Mavuika":   {"element": "Pyro",     "weapon": "Claymore"},
    "Citlali":   {"element": "Cryo",     "weapon": "Catalyst"},
    "Varesa":    {"element": "Electro",  "weapon": "Catalyst"},
    "Escoffier": {"element": "Cryo",     "weapon": "Polearm"},
    "Skirk":     {"element": "Cryo",     "weapon": "Sword"},
    "Ineffa":    {"element": "Electro",  "weapon": "Polearm"},
    "Lauma":     {"element": "Dendro",   "weapon": "Catalyst"},
    "Flins":     {"element": "Electro",  "weapon": "Polearm"},
    "Nefer":     {"element": "Dendro",   "weapon": "Catalyst"},
    "Durin":     {"element": "Pyro",     "weapon": "Sword"},
    "Columbina": {"element": "Hydro",    "weapon": "Catalyst"},
    "Zibai":     {"element": "Geo",      "weapon": "Sword"},
    "Varka":     {"element": "Anemo",    "weapon": "Claymore"},
    "Linnea":    {"element": "Geo",      "weapon": "Bow"},
}