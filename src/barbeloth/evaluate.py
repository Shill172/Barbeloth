import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from barbeloth.config import (
    MODEL_PREDICTIONS_FILE, LONGEST_WAIT_PREDICTIONS_FILE, 
    ACTUAL_BANNER_RUNS_FILE, RERUN_SLOT_HISTORY_FILE
)
from barbeloth.stats_utils import accuracy_with_ci, mcnemar_test, random_baseline_accuracy
from barbeloth.dataprocessing import read_banner_history, get_banner_runs, get_num_rerun_slots_per_patch, get_last_regular_rerun
from barbeloth.model import (
    show_predictions_for_patch,
    prepare_features,
    load_last_regular_rerun_map
)

def longest_time_is_rerun():
    """
    Picks the n characters who have waited the longest for a rerun, where n is the 
    number of rerun slots for that patch. Using this to compare models to a baseline
    heuristic.
    """
    df = read_banner_history() 
    
    last_regular_map = load_last_regular_rerun_map()

    # Exclude entries where a character's next appearance is chronicle
    # E.g. Lyney is chronicle in 6.5, meaning from his latest regular rerun (5.2)
    # He will not be counted
    df["Cutoff_Patch"] = df["Name"].map(last_regular_map).fillna(float("inf"))
    df = df[df["Patch"] <= df["Cutoff_Patch"]].copy()

    rerun_slots = get_num_rerun_slots_per_patch()
    
    all_patches = sorted(df["Patch"].unique())
    
    results = []

    for _, row in rerun_slots.iterrows(): 
        current_patch = row["Patch"]
        n = int(row["Rerun_slots"])

        if n == 0:
            continue

        # Find the index of the current patch so we can tell how long they have waited
        # When they actually run
        try:
            current_idx = all_patches.index(current_patch)
            if current_idx == 0: 
                continue 
            previous_patch = all_patches[current_idx - 1]
        except ValueError:
            continue

        prediction_pool = df[df["Patch"] == previous_patch].copy()

        # Don't want debuts 
        prediction_pool = prediction_pool[prediction_pool["Total_runs"] >= 1]

        # Pick n (num of rerun slots for that patch) top wait times
        top = prediction_pool.nlargest(n, "Time_since_ran").copy()
        top["Patch"] = current_patch 
      
        results.append(top[["Patch", "Name", "Time_since_ran"]])

    if not results:
        return pd.DataFrame()

    final = pd.concat(results).reset_index(drop=True)
    
    final.to_csv(LONGEST_WAIT_PREDICTIONS_FILE, index=False)
    
    return final


def predict_n_patches(df_original, X, y, start_patch):
    """
    Each patch trains on all previous patches, then predicts that patch. 
    Writes model_predictions.csv and returns the combined predictions DataFrame.
    """
    all_patches = sorted(X["Patch"].unique())

    patches_to_predict = []

    for p in all_patches:
        if p >= start_patch:
            patches_to_predict.append(p)

    results = []

    for patch in patches_to_predict: 
        train_mask = X["Patch"] < patch 
        test_mask = X["Patch"] == patch

        if train_mask.sum() == 0 or test_mask.sum() == 0:
            continue

        X_train = X[train_mask].drop(columns=["Patch"])
        y_train = y[train_mask]

        X_patch = X[test_mask]
        y_patch = y[test_mask]

        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")

        model.fit(X_train, y_train)

        predicted = show_predictions_for_patch(
            df_original,
            model, 
            X_patch, 
            y_patch,
            patch
        )

        results.append(predicted)

    final = pd.concat(results).reset_index(drop=True)

    final.to_csv(MODEL_PREDICTIONS_FILE, index=False)

    return final


def calculate_prediction_accuracy(predicted_df, actual_df, min_patch):
    """
    Scores predictions against actual reruns from min_patch onwards. 
    Prints a breakdown and returns accuracy as a percentage. 
    """

    # Data types must match
    predicted_df["Patch"] = predicted_df["Patch"].astype(float)
    actual_df["Patch"] = actual_df["Patch"].astype(float)

    filtered_predictions = predicted_df[predicted_df["Patch"] >= min_patch].copy()

    if filtered_predictions.empty:
        print(f"No predictions found after patch {min_patch}.")
        return 0.0

    # Intersection to find where columns match (correct prediction)
    correct_predictions = pd.merge(
        filtered_predictions, 
        actual_df[["Name", "Patch"]], 
        on=["Name", "Patch"], 
        how="inner"
    )

    if not correct_predictions.empty:
        print(f"Correct predictions for patch: {min_patch}+:")
        print(correct_predictions.sort_values("Patch").to_string(index=False))
    else:
        print(f"No correct predictions found after patch {min_patch}")

    accuracy = (len(correct_predictions) / len(filtered_predictions)) * 100

    print(f"\nTotal Predicted: {len(filtered_predictions)}")
    print(f"Correct Hits: {len(correct_predictions)}")
    print(f"Accuracy: {accuracy:.2f}%")

    return accuracy


model_df = pd.read_csv(MODEL_PREDICTIONS_FILE)
lww_df = pd.read_csv(LONGEST_WAIT_PREDICTIONS_FILE)
actual_df = pd.read_csv(ACTUAL_BANNER_RUNS_FILE)
slot_history_df = pd.read_csv(RERUN_SLOT_HISTORY_FILE)


def patches_in_range(df, start, end):
    return sorted(p for p in df["Patch"].unique() if start <= p <= end)


def get_names_for_patch(df, patch):
    rows = df[df["Patch"] == patch]
    return set(rows["Name"])


def backtest_and_collect_records(start_patch, end_patch):
    records = []
    for patch in patches_in_range(actual_df, start_patch, end_patch):
        actual_reruns = get_names_for_patch(actual_df, patch)
        model_guesses = get_names_for_patch(model_df, patch, score_col="Predicted_prob")
        baseline_guesses = get_names_for_patch(lww_df, patch, score_col="Time_since_ran")

        for character in actual_reruns:
            records.append({
                "patch": patch,
                "character": character,
                "model_correct": character in model_guesses,
                "baseline_correct": character in baseline_guesses,
            })
    return records


def get_random_acc(start_patch=5.0, end_patch=6.5):
    pool_sizes, slot_counts = [], []
    for patch in patches_in_range(slot_history_df, start_patch, end_patch):
        prior_appearances = actual_df[actual_df["Patch"] < patch]
        pool_sizes.append(prior_appearances["Name"].nunique())
        n_slots = slot_history_df.loc[slot_history_df["Patch"] == patch, "Rerun_slots"].iloc[0]
        slot_counts.append(n_slots)

    return random_baseline_accuracy(pool_sizes, slot_counts)


if __name__ == "__main__":

    acc, lo, hi = accuracy_with_ci(18, 41)
    print(f"{acc:.1%} (95% CI: {lo:.1%}-{hi:.1%})")

    records = backtest_and_collect_records(5.0, 6.5)
    model_correct = [r["model_correct"] for r in records]
    baseline_correct = [r["baseline_correct"] for r in records]
    b, c, p = mcnemar_test(model_correct, baseline_correct)
    print(f"ML-only wins: {b}")
    print(f"Baseline-only wins: {c}")
    print(f"McNemar's p-value: {p:.4f}")

    print(get_random_acc())

    
    """     get_last_regular_rerun()

        actual_df = get_banner_runs()

        print("\nBaseline: longest wait time")
        baseline_predictions = longest_time_is_rerun()
        calculate_prediction_accuracy(baseline_predictions, actual_df, min_patch=6.0)

        print("\nML model backtest")
        df = read_banner_history()
        df_original = df.copy()
        df_original = df_original.sort_values(["Name", "Patch"]).reset_index(drop=True)

        X, y = prepare_features(df)

        ml_predictions = predict_n_patches(df_original, X, y, start_patch=5.0)
        calculate_prediction_accuracy(ml_predictions, actual_df, min_patch=5.0) 
    """