import requests
import time

# Define constants
RATE_LIMIT = 100  # requests per minute
WAIT_TIME = 60 / RATE_LIMIT + 0.1 # time to wait between requests

#------------ Code for FASTA Generator --

def get_observations_with_dna(taxon_id): #, date_start, date_end):
    observations = []
    page = 1
    per_page = 30
    while True:
        url = f"https://api.inaturalist.org/v1/observations?taxon_id={taxon_id}&verifiable=any&field:DNA%20Barcode%20ITS=&page={page}&per_page={per_page}"
        response = requests.get(url)

        if response.status_code == 422:
            print("422 Error: Possibly bad taxon_id or dates")
            break

        data = response.json().get('results', [])
        if not data:
            break

        observations.extend(data)
        page += 1
        time.sleep(WAIT_TIME)  # if needed to avoid rate limit
    return observations