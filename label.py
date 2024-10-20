from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import requests

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
        data = response.json()['results']
        if not data:
            break
        observations.extend(data)
        page += 1
    return observations

def download_image(url):
    large_image_url = url.replace("square", "large")
    response = requests.get(large_image_url)
    return Image.open(BytesIO(response.content))

def create_card(observation, card_size=(600, 800)):
    card = Image.new('RGB', card_size, (255, 255, 255))
    draw = ImageDraw.Draw(card)
    image_url = observation['photos'][-1]['url']
    image = download_image(image_url)
    image = image.resize((card_size[0], int(card_size[1] * 0.775)))
    card.paste(image, (0, 0))
    font = ImageFont.truetype("arial.ttf", size=40)
    font_small = ImageFont.truetype("arial.ttf", size=25)
    text_x = 10
    text_y = image.height + 10
    draw.text((text_x, text_y), f"Name: ", fill="black", font=font)
    draw.text((text_x, text_y + 45), f"iNat ID: {format_number(observation['id'])}", fill="black", font=font)
    draw.text((text_x, text_y + 95), f"Date: {observation['observed_on']}", fill="black", font=font_small)
    draw.text((text_x, text_y + 130), f"Location: {observation['place_guess']}", fill="black", font=font_small)
    return card

def save_as_pdf(cards, output_filename, page_size=(2480, 3508), cards_per_page=(4, 4)):
    page_width, page_height = page_size
    card_width, card_height = cards[0].size
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
    output = BytesIO()
    pages[0].save(output, format='PDF', save_all=True, append_images=pages[1:])
    output.seek(0)
    return output