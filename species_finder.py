import requests

def get_observations_with_dna_coords(lat, lng, radius, taxon_id, with_provisional=True):
    observations = []
    page = 1
    per_page = 100
    base_url = "https://api.inaturalist.org/v1/observations"

    while True:
        url = (
            f"{base_url}?lat={lat}&lng={lng}&radius={radius}"
            f"&taxon_id={taxon_id}&verifiable=any&per_page={per_page}&page={page}"
        )

        # Add field filters
        if with_provisional:
            url += "&field:Provisional%20Species%20Name=&field:DNA%20Barcode%20ITS="
        else:
            url += "&without_field=Provisional%20Species%20Name&field:DNA%20Barcode%20ITS="

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error {response.status_code}: Could not fetch observations.")
            break

        data = response.json().get('results', [])
        if not data:
            break

        observations.extend(data)
        page += 1

    return observations

def get_provisional_names(observations):
    provisional_names = set()

    for obs in observations:
        ofvs = obs.get('ofvs', [])
        
        for field in ofvs:
            if field.get('name') == 'Provisional Species Name' and field.get('value'):
                provisional_names.add(field['value'])
    return provisional_names

def get_binomial_names(observations):
    binomial_names = set()

    for obs in observations:
        taxon = obs.get('taxon')
        if taxon and 'name' in taxon:
            binomial_names.add(taxon['name'])

    return binomial_names