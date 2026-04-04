# Going to read from the community updated google doc to get data for:
# Num reruns, avg rerun time,.. 

import requests 
import os

#TODO filter read in so new csv is neat and contains needed data
def read_google_doc(doc_id, gid):

    resources = "resources"
    if not os.path.exists(resources):
        os.makedirs(resources)

    url = f"https://docs.google.com/spreadsheets/d/{doc_id}/export?format=csv&gid={gid}"

    response = requests.get(url) 

    if response.status_code == 200: 
        file_path = os.path.join(resources, "data.csv")

        with open(file_path, "wb") as f: 
            f.write(response.content)

        print(f"Successfully wrote to {file_path}")
    else: 
        return "Error: Couldn't fetch document"
    
doc_id = "1QLE2W3Suz-UgJCLKWL7FuffZlP5a7QUy"
gid = "551073839"

raw_data = read_google_doc(doc_id, gid)
print(raw_data)