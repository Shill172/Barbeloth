import pandas as pd
from sklearn.ensemble import RandomForestClassifier
 
from config import MODEL_PREDICTIONS_FILE, LONGEST_WAIT_PREDICTIONS_FILE
from dataprocessing import read_banner_history, get_banner_runs, get_num_rerun_slots_per_patch, get_last_regular_rerun
from model import (
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


if __name__ == "__main__":
    
    get_last_regular_rerun()
 
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