import requests
import time

# Define constants
RATE_LIMIT = 100  # requests per minute
WAIT_TIME = 60 / RATE_LIMIT + 0.1 # time to wait between requests

#------------ Code for FASTA Generator --

def get_observation_ids(name, param_type):

    if param_type == 'prov':
        params = {
            "field:Provisional Species Name": name,
            "field:DNA Barcode ITS": "",  # Ensure we get observations with DNA Barcode ITS field
            "per_page": 200,
            "page": 1
        }
    elif param_type == 'normal':
        params = {
        "taxon_name": name,
        "field:DNA Barcode ITS": "",  # Ensure we get observations with DNA Barcode ITS field
        "per_page": 200,
        "page": 1
        }
    elif param_type == 'all':
        params = {
        "taxon_name": name,
        "field:DNA Barcode ITS": "",  # Ensure we get observations with DNA Barcode ITS field
        "per_page": 200,
        "page": 1
        }

    observation_ids = []
    while True:
        response = requests.get("https://api.inaturalist.org/v1/observations", params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                break
            observation_ids.extend(obs["id"] for obs in results)
            params["page"] += 1  # Move to the next page
            time.sleep(WAIT_TIME)
        else:
            print(f"Failed to retrieve data for {provisional_name}: {response.status_code}")
            break
    return observation_ids

def get_observations_fasta(id):
    response = requests.get(f"https://api.inaturalist.org/v1/observations/{id}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve observation {id}: {response.status_code}")
        return {"results": []}