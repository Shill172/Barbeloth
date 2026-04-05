from dataprocessing import read_google_doc_for_rerun_info, create_filtered_data
from apisync import sync_local_data, find_missing_characters

def main(): 
    doc_id = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
    gid = "551073839"

    print("Fetching Google Sheet...")
    read_google_doc_for_rerun_info(doc_id, gid)

    print("Syncing API data...")
    sync_local_data()

    print("Filtering data...")
    create_filtered_data()

    print("Checking if characters are missing...")
    find_missing_characters()

    print("Done!")

if __name__ == "__main__":
    main()