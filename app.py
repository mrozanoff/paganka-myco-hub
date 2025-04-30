from flask import Flask, render_template, request, send_file, Blueprint
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import requests
from datetime import datetime
import pandas as pd
import time
import traceback

from label import *
from fasta import *
from voucher import save_vouchers_to_pdf
from dkey import *

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
        username = request.form.get('username')
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        image_place = request.form.get('image_place', -1)  # Default to -1 if not provided
        csv_file = request.files.get('csv_file')

        print("what is csv file equal to", csv_file, username)
        # if not username and not csv_file:
        #     print("First empty request detected, skipping...")
        #     return render_template('voucher_generator.html')  # Skip processing the first request

        observations = []
        print("Run once?", csv_file)
        print("HELLO?")

        if csv_file and csv_file.filename:  # Ensure a file is actually uploaded
            csv_data = csv_file.read().decode('utf-8-sig')
            observation_ids = [line.strip() for line in csv_data.splitlines() if line.strip()]
            print(observation_ids)
            observations = get_observations_by_ids(observation_ids)

        elif username and date_start and date_end:
            observations = get_observations(username, date_start, date_end)

        cards = [create_card(obs) for obs in observations]
        print("THESE ARE THE CARDS", cards)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Labels_{timestamp}.pdf"

        pdf_data = save_as_pdf(cards, output_filename)
        print("PDFDATA", pdf_data)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            print("creating file??")
            temp_file.write(pdf_data.getvalue())
            temp_file.seek(0)
            return send_file(temp_file.name, as_attachment=True, download_name=output_filename, mimetype='application/pdf')

    return render_template('voucher_generator.html')

@app.route('/fasta_generator', methods=['GET', 'POST'])
def fasta_generator():
    try:
        if request.method == 'POST':
            entire_genus = request.form.get('entire_genus') == 'on'
            rows = []

            # Expecting a taxon_id input instead of genus name
            taxon_id = request.form['genus']
            # date_start = request.form['date_start']
            # date_end = request.form['date_end']
            observations = get_observations_with_dna(taxon_id) #, date_start, date_end)

            for obs in observations:
                ofvs = obs.get("ofvs", [])
                dna = next((field["value"] for field in ofvs if field["name"] == 'DNA Barcode ITS'), "")
                if not dna:
                    continue

                place_guess = obs.get("place_guess", "")
                provisional_name = next((field["value"] for field in ofvs if 'provisional' in field["name"].lower()), None)
                taxon_name = obs.get("taxon", {}).get("name", "")
                fallback_name = taxon_name or "Unknown"

                final_name = provisional_name if provisional_name else fallback_name
                inat_id = obs.get("id")

                rows.append({"name": final_name, "inat_id": inat_id, "DNA": dna, "Location": place_guess})

            # Write to FASTA
            fasta_data = BytesIO()
            for row in rows:
                fasta_data.write(f'>{row["inat_id"]} - {row["name"]} - {row["Location"]}\n{row["DNA"]}\n'.encode('utf-8'))
            fasta_data.seek(0)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
                temp_file.write(fasta_data.getvalue())
                temp_file.seek(0)
                return send_file(temp_file.name, as_attachment=True, download_name='out.fasta', mimetype='text/plain')

        return render_template('fasta_generator.html')
    except Exception as e:
        print(e)

@app.route('/dkey_builder', methods=['GET', 'POST'])
def dkey_builder():
    if request.method == 'POST':
        file = request.files['file']

        # Read the uploaded file 
        df = pd.read_csv(file)

        # Preprocess data
        X, y, feature_cols = preprocess_data(df)

        # Build tree
        tree = build_tree(X, y)
        
        # Assuming `tree` and `X` are created earlier in the function or elsewhere in the app
        key = format_dichotomous_key(tree, X.columns)

        # print(key)

        # Save to a temporary file and send it as a response
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding="utf-8") as temp_file:
            temp_file.write(key)  # Write the string to the temporary file
            temp_file.flush()  # Ensure all data is written
            return send_file(temp_file.name, as_attachment=True, download_name='dichotomous_key.txt', mimetype='text/plain')


    return render_template('dkey.html')

@app.route('/purple_russulas')
def purple_russulas():
    return render_template('purple_russulas.html')

@app.route('/key_to_stalked_gilled_mushrooms')
def key_to_stalked_gilled_mushrooms():
    return render_template('key_to_stalked_gilled_mushrooms.html')



@app.route('/fungi_finding_prediction')
def fungi_finding_prediction():
    return render_template('fungi_finding_prediction.html')

# @app.route('/pyrenomycetes_key')
# def pyrenomycetes_key():
#     return render_template('vis.html')


if __name__ == '__main__':
    app.run(debug=True)

