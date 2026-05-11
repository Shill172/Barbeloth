from sklearn.ensemble import RandomForestClassifier
from dataprocessing import (
    read_google_doc_for_rerun_info, 
    parse_banner_history, 
    read_banner_history,
    get_last_regular_rerun)
from apisync import sync_local_data, find_missing_characters
from model import predict_next_patch, prepare_features

GOOGLE_DOC_ID = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
GOOGLE_GID = "551073839"
NEXT_PATCH = 6.6

def main(): 
    print("Fetching Google Sheet...")
    read_google_doc_for_rerun_info(GOOGLE_DOC_ID, GOOGLE_GID)

    print("Syncing API data...")
    sync_local_data()

    print("Filtering data...")
    parse_banner_history()

    get_last_regular_rerun()

    print("Checking if characters are missing...")
    find_missing_characters()

    df = read_banner_history()
    df_original = df.copy()

    X, y = prepare_features(df)
    
    print("Training model on all available history...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(X, y)
    
    print(f"Generating predictions for next patch: {NEXT_PATCH}")
    predict_next_patch(df_original, model, NEXT_PATCH)

    print("NOTE: Patches don't often contain a set amount rerun slots, take predictions with a large grain of salt")

if __name__ == "__main__":
    main()