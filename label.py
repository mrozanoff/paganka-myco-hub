from io import BytesIO
from flask import jsonify
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import requests
import time

def format_number(number):
    number_str = str(number)
    if len(number_str) == 9:
        return ' '.join(number_str[i:i+3] for i in range(0, len(number_str), 3))
    else:
        raise ValueError("The number must be a 9-digit integer.")

def get_observations(username, date_start, date_end):
    observations = []
    page = 1
    per_page = 30
    while True:
        url = f"https://api.inaturalist.org/v1/observations?user_id={username}&d1={date_start}&d2={date_end}&page={page}&per_page={per_page}" # add location and taxon id here to filter
        response = requests.get(url)

        if response.status_code == 422:
            print("response 422, mispelled username")

        # print(response)
        # return
        data = response.json()['results']

        if not data:
            break
        observations.extend(data)
        page += 1
    return observations

def get_observations_by_ids(observation_ids):
    """
    Fetch observations by their IDs and return them in the same format as get_observations.
    """
    observations = []
    base_url = "https://api.inaturalist.org/v1/observations/"
    
    for obs_id in observation_ids:
        time.sleep(1.5)  # Respect API rate limits
        url = f"{base_url}{obs_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                obs = data['results'][0]  # Single observation
                # Ensure the response structure matches get_observations()
                observation = {
                    "id": obs.get("id"),
                    "observed_on": obs.get("observed_on"),
                    "place_guess": obs.get("place_guess", "Unknown Location"),
                    "photos": obs.get("photos", []),  # Ensure it's always a list
                }
                observations.append(observation)
        else:
            print(f"Failed to fetch observation {obs_id}: {response.status_code}")

    return observations



from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def download_image(url):
    large_image_url = url.replace("square", "large")
    response = requests.get(large_image_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    return None  # Return None if the image can't be downloaded

def create_card(observation, card_size=(600, 800)):
    card = Image.new('RGB', card_size, (255, 255, 255))
    draw = ImageDraw.Draw(card)
    # print("beg of create card", card)
    # Handle missing images
    image_url = observation['photos'][-1]['url'] if observation['photos'] else None
    if image_url:
        image = download_image(image_url)
        if image:
            image = image.resize((card_size[0], int(card_size[1] * 0.775)))
            card.paste(image, (0, 0))
        else:
            draw.text((10, 10), "No Image Available", fill="black")
    else:
        draw.text((10, 10), "No Image Available", fill="black")
    # print("mid of create card", card)
    font = ImageFont.truetype("./static/fonts/arial.ttf", size=40)
    font_small = ImageFont.truetype("./static/fonts/arial.ttf", size=25)
    text_x = 10
    text_y = image.height + 10 # text_y = int(card_size[1] * 0.775) + 10

    draw.text((text_x, text_y), f"Name: ", fill="black", font=font)
    draw.text((text_x, text_y + 45), f"iNat ID: {format_number(observation.get('id', 'Unknown'))}", fill="black", font=font)
    draw.text((text_x, text_y + 95), f"Date: {observation.get('observed_on', 'Unknown')}", fill="black", font=font_small)
    draw.text((text_x, text_y + 130), f"Location: {observation.get('place_guess', 'Unknown')}", fill="black", font=font_small)
    # print("end of create card", card)
    return card


def save_as_pdf(cards, output_filename, page_size=(2480, 3508), cards_per_page=(4, 4)):
    print("card beg of pdf creation", cards)
    page_width, page_height = page_size
    try:
        card_width, card_height = cards[0].size
    except IndexError:
        print("No Observations on this date range!")
        return
    cols, rows = cards_per_page
    x_margin = (page_width - (cols * card_width)) // (cols + 1)
    y_margin = (page_height - (rows * card_height)) // (rows + 1) - 25
    pages = []
    page = Image.new('RGB', page_size, (255, 255, 255))
    x_offset = x_margin + 5
    y_offset = y_margin
    for i, card in enumerate(cards):
        page.paste(card, (x_offset, y_offset))
        x_offset += card_width + x_margin
        if (i + 1) % cols == 0:
            x_offset = x_margin + 5
            y_offset += card_height + y_margin
        if (i + 1) % (cols * rows) == 0:
            pages.append(page)
            page = Image.new('RGB', page_size, (255, 255, 255))
            x_offset = x_margin + 5
            y_offset = y_margin
    if len(cards) % (cols * rows) != 0:
        pages.append(page)
    print("page", page)
    page.show()
    output = BytesIO()
    pages[0].save(output, format='PDF', save_all=True, append_images=pages[1:])
    print("output1", output)
    output.seek(0)
    print("output2 seek", output.seek(0))
    # pages.show()
    print("outputcheck", output.getvalue()[:100])
    return output