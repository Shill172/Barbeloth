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

The model consistently outperforms the baseline, particularly for characters on their second or third rerun — a pattern the "longest wait" heuristic misses, since newer characters haven't accumulated enough time off-banner to be favoured by it.

See [`Results.md`](Results.md) for the full patch-by-patch breakdown and discussion of limitations.

## Project Structure

```
src/
  main.py            # Entry point — orchestrates data sync, processing, training, and prediction
  apisync.py         # Syncs character metadata from Enka's reference data
  dataprocessing.py  # Cleans and transforms raw banner history into model-ready features
  model.py           # Feature preparation, prediction, and leakage-prevention logic
  evaluate.py        # Baseline heuristic and model comparison
  config.py          # Shared file paths and constants
resources/           # Cached data files (banner history, character metadata, predictions)
```

## Usage

```bash
git clone https://github.com/Shill172/Barbeloth.git
cd Barbeloth
pip install -r requirements.txt
python src/main.py
```

This will fetch the latest data, retrain the model on full history, and print predictions for the next patch.

## Limitations

- The test set is limited to 41 rerun slots, so results can shift significantly with a small number of surprising picks.
- Character reruns are influenced by unpredictable factors (popularity, story relevance, events) that aren't captured in the model's features.

## Credits

- [Genshin Banner History Spreadsheet](https://docs.google.com/spreadsheets/d/1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy) — maintained by Reddit user Serato-S
- [Enka.Network](https://enka.network/) — character reference data ([API-docs](https://github.com/EnkaNetwork/API-docs))

This project is not affiliated with HoYoverse.