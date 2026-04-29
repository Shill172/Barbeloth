from sklearn.ensemble import RandomForestClassifier
from dataprocessing import read_google_doc_for_rerun_info, parse_banner_history
from apisync import sync_local_data, find_missing_characters
from model import predict_next_patch, prepare_features, read_banner_history

def main(): 
    doc_id = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
    gid = "551073839"

    print("Fetching Google Sheet...")
    read_google_doc_for_rerun_info(doc_id, gid)

    print("Syncing API data...")
    sync_local_data()

    print("Filtering data...")
    parse_banner_history()

    print("Checking if characters are missing...")
    find_missing_characters()

    df = read_banner_history()
    df_original = df.copy()

    X, y, chronicle_names = prepare_features(df)
    
    print("Training model on all available history...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(X, y)

    last_patch = df["Patch"].max()
    next_patch = round(last_patch + 0.1, 1) 
    
    print(f"Generating predictions for next patch: {next_patch}")
    predict_next_patch(df_original, model, chronicle_names, next_patch)

    print("NOTE: Patches don't often contain 4 rerun slots, take predictions with a large grain of salt")

if __name__ == "__main__":
    main()