from dataprocessing import read_google_doc_for_rerun_info, parse_banner_history
from apisync import sync_local_data, find_missing_characters

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

    print("Done!")

if __name__ == "__main__":
    main()