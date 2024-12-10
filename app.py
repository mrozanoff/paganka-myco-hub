from flask import Flask, render_template, request, send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import requests
from datetime import datetime
# import pandas as pd
import time
import traceback

from label import *
from fasta import *
from voucher import save_vouchers_to_pdf

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voucher_generator', methods=['GET', 'POST'])
def voucher_generator():
    if request.method == 'POST':
        voucher_prefix = request.form['voucher_prefix']
        total_vouchers = int(request.form['total_vouchers'])

        # Generate a unique filename with a datetime stamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Vouchers_{timestamp}"

        pdf_data = save_vouchers_to_pdf(total_vouchers, voucher_prefix)
        return send_file(pdf_data, as_attachment=True, download_name=f"{output_filename}.pdf", mimetype='application/pdf')
    return render_template('voucher_generator.html')

@app.route('/label_generator', methods=['GET', 'POST'])
def label_generator():
    if request.method == 'POST':
        username = request.form['username']
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        image_place = request.form.get('image_place', -1)  # Default to -1 if not provided
        
        observations = get_observations(username, date_start, date_end)
        cards = [create_card(obs) for obs in observations]
        
        # Generate a unique filename with a datetime stamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Labels_{timestamp}.pdf"
        
        pdf_data = save_as_pdf(cards, output_filename)
        
        # Use tempfile.mkstemp to create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_data.getvalue())
            temp_file.seek(0)
            return send_file(temp_file.name, as_attachment=True, download_name=output_filename, mimetype='application/pdf')
    
    return render_template('label_generator.html')

@app.route('/fasta_generator', methods=['GET', 'POST'])
def fasta_generator():
    if request.method == 'POST':

        # Get the checkbox value
        entire_genus = request.form.get('entire_genus') == 'on'

        # Get uploaded file and genus
        genus = request.form['genus']

        rows = []
        if entire_genus:
            file = None  # Handle accordingly if entire_genus is checked

            name = f"{genus}"
            observation_ids = get_observation_ids(name, 'all')
            for obs_id in observation_ids:
                rows.append({"name": name, "inat_id": obs_id})
        else:
            file = request.files['file']

            # Read the uploaded file 
            df = pd.read_excel(file)

            # Generate the FASTA content
            prov_names = df['prov_names'].dropna().values.tolist()
            normal_names_list = df['names'].dropna().values.tolist()

            for name in prov_names:
                search_name = f"{genus} {name}"
                observation_ids = get_observation_ids(search_name, 'prov')
                for obs_id in observation_ids:
                    rows.append({"name": search_name, "inat_id": obs_id})

            for name in normal_names_list:
                search_name = f"{genus} {name}"
                observation_ids = get_observation_ids(search_name, 'normal')
                for obs_id in observation_ids:
                    rows.append({"name": search_name, "inat_id": obs_id})

        df = pd.DataFrame(rows).drop_duplicates(subset='inat_id')

        # Fetch DNA sequences
        id_list = df['inat_id'].values.tolist()
        clean_df = df[['name', 'inat_id']].copy()
        dna_sequences = {}
        state_country = {}  # To store state and country

        for id_ in id_list:
            while True:
                try:
                    obs = get_observations_fasta(id_)
                    # pprint.pp(obs)
                    observational_fields = obs.get("results", [{}])[0].get("ofvs", [])
                    dna = next((field["value"] for field in observational_fields if field["name"] == 'DNA Barcode ITS'), "")
                    if dna:
                        dna_sequences[id_] = dna
                    # Extract state and country
                    place_guess = obs.get("results", [{}])[0].get("place_guess", [])
                    state_country[id_] = f"{place_guess}"
                    break
                except Exception as e:
                    print(f"Exception: {e}")
                    traceback.print_exc()
                    time.sleep(30)
                time.sleep(WAIT_TIME)

        # Update DataFrame with DNA sequences
        clean_df['DNA'] = clean_df['inat_id'].map(dna_sequences)
        clean_df['Location'] = clean_df['inat_id'].map(state_country)
        clean_df = clean_df.dropna(subset=['DNA'])

        # Writing FASTA content to a file in memory
        fasta_data = BytesIO()
        for index, row in clean_df.iterrows():
            name = row['name']
            inat_id = row['inat_id']
            DNA = row['DNA']
            location = row['Location']
            fasta_data.write(f'>{inat_id} - {name} - {location}\n{DNA}\n'.encode('utf-8'))
        
        fasta_data.seek(0)

        # Save to a temporary file and send it as a response
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
            temp_file.write(fasta_data.getvalue())
            temp_file.seek(0)
            return send_file(temp_file.name, as_attachment=True, download_name='out.fasta', mimetype='text/plain')
    return render_template('fasta_generator.html')


@app.route('/purple_russulas')
def purple_russulas():
    return render_template('purple_russulas.html')

@app.route('/key_to_stalked_gilled_mushrooms')
def key_to_stalked_gilled_mushrooms():
    return render_template('key_to_stalked_gilled_mushrooms.html')

@app.route('/fungi_finding_prediction')
def fungi_finding_prediction():
    return render_template('fungi_finding_prediction.html')


# Temporary list of images (you can load this from a database or JSON file in the future)
images = [
    {
        'filename': 'helvella.jpg',
        'species': 'Helvella cf. cupuliformis',
        'inat_link': 'https://www.inaturalist.org/observations/224769178',
        'date': 'Jun 22, 2024',
        'location': 'Perry County, US-PA, US'
    },
    {
        'filename': 'unknown1.jpg',
        'species': 'Unknown',
        'inat_link': 'https://www.inaturalist.org/observations/237669128',
        'date': 'Aug 24, 2024',
        'location': 'Pike County, US-PA, US'
    },
    {
        'filename': 'unknown2.jpg',
        'species': 'Unknown',
        'inat_link': '',
        'date': 'June 2024',
        'location': 'PA, USA'
    },
]


@app.route('/gallery')
def gallery():
    return render_template('gallery.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)

