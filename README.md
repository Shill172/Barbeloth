# Barbeloth

A machine learning model that predicts which Genshin Impact characters are likely to appear on upcoming banner reruns.

Genshin Impact characters return to "banners" (their in-game shop rotation) at irregular intervals, based on a mix of time since their last run, popularity, and release patterns. Barbeloth trains a classifier on historical banner data to predict which characters are most likely to run in a given patch, and compares its predictions against a simple baseline heuristic.

## How It Works

1. **Data collection** — Pulls historical banner appearance data from a community-maintained [Google Sheet](https://docs.google.com/spreadsheets/d/1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy), and syncs character metadata (name, element, weapon type) from [Enka.Network](https://enka.network/)'s public reference data.
2. **Data processing** — Cleans and reshapes the raw data into a long-format table of `(character, patch)` pairs, computing features such as time since last run, total run count, and run frequency.
3. **Feature engineering** — Shifts time-based features forward by one patch per character to prevent data leakage, ensuring the model only ever sees information that would have been available *before* the patch it's predicting.
4. **Model training** — Trains a `RandomForestClassifier` (scikit-learn) on the processed dataset to predict the probability a character runs in a given patch.
5. **Evaluation** — Compares model predictions against a "longest wait wins" (LWW) baseline heuristic, which simply predicts that characters who have waited longest are most likely to return.

## Results

Tested on 41 rerun slots across patches 5.0–6.5:

| Metric | Prediction Model | LWW Heuristic |
|---|---|---|
| Total Accuracy (5.0+) | 43.9% | 26.8% |
| Recent Accuracy (6.0+) | 50.0% | 18.75% |

The model shows a numerical lead over LWW (43.9% vs. 26.8%), but this
difference is not statistically significant at the current sample size
(McNemar's p = 0.23). The testing
set is limited to 41 slots; a few lucky guesses or curveballs by Hoyo
could meaningfully shift these results either way.

See [`Results.md`](Results.md) for the full patch-by-patch breakdown and discussion of limitations.

## Project Structure

```
Barbeloth/
├── src/
│   └── barbeloth/
│       ├── __init__.py       
│       ├── main.py           # Entry point — orchestrates the application workflow
│       ├── apisync.py        # Syncs character metadata from Enka's reference data
│       ├── config.py         # Shared file paths and configuration constants
│       ├── dataprocessing.py # Cleans and transforms raw banner history into model-ready features
│       ├── evaluate.py       # Evaluates the model against the LWW heuristic and random accuracy
│       ├── model.py          # Feature preparation, predictions. 
│       └── stats_utils.py    # Statistical utilities: Wilson CIs, McNemar's test,
│                             # and random-baseline calculations
│
├── resources/                # Cached data, banner history, metadata, and predictions
├── pyproject.toml            # Project metadata and dependency configuration
├── README.md
└── CHANGELOG.md
```

## Installation

Clone the repository:
```bash
git clone https://github.com/Shill172/Barbeloth.git
cd Barbeloth
```
Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Install Barbeloth and its dependencies:
```bash
python -m pip install . (or python -m pip install -e . for your own development)
```

## Usage
Run Barbeloth from the project directory:
```bash
python src\barbeloth\main.py
```

Barbeloth will:
1. Fetch the latest banner data from the configured Google Sheet.
2. Synchronise character data from Enka.Network.
3. Generate the required data files in the ```resources/``` directory.
4. Train the prediction model.
5. Generate predictions for the next patch.

Important: Barbeloth must be run from the project directory containing the ```resources/``` folder. This folder stores downloaded data and generated prediction files.


## Credits

- [Genshin Banner History Spreadsheet](https://docs.google.com/spreadsheets/d/1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy) — maintained by Reddit user Serato-S
- [Enka.Network](https://enka.network/) — character reference data ([API-docs](https://github.com/EnkaNetwork/API-docs))

This project is not affiliated with HoYoverse.