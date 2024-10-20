from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
import tempfile
import requests
import os

# --- Code for Voucher Generator --- 
# Constants
RULER_LENGTH_CM = 5
RULER_HEIGHT_CM = 1
WHITE_SPACE_HEIGHT_CM = RULER_HEIGHT_CM

# Conversion factor from cm to points
CM_TO_POINTS = 28.3464566929
RULER_LENGTH_PT = RULER_LENGTH_CM * CM_TO_POINTS  # Convert cm to points
RULER_HEIGHT_PT = RULER_HEIGHT_CM * CM_TO_POINTS
WHITE_SPACE_HEIGHT_PT = WHITE_SPACE_HEIGHT_CM * CM_TO_POINTS
IMAGE_HEIGHT_PT = RULER_HEIGHT_PT + WHITE_SPACE_HEIGHT_PT
IMAGE_WIDTH_PT = RULER_LENGTH_PT

def create_ruler_image(voucher_number):
    img_width = int(IMAGE_WIDTH_PT)
    img_height = int(IMAGE_HEIGHT_PT)
    
    ruler_image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(ruler_image)
    
    draw.rectangle([0, 0, img_width, int(RULER_HEIGHT_PT)], outline='black', width=2)

    for i in range(RULER_LENGTH_CM + 1):
        x = i * (IMAGE_WIDTH_PT / RULER_LENGTH_CM)
        draw.line([x, 0, x, RULER_HEIGHT_PT], fill='black', width=2)

    for i in range(1, int(RULER_LENGTH_CM * 2)):
        x = i * (IMAGE_WIDTH_PT / (RULER_LENGTH_CM * 2))
        if i % 2 != 0:
            draw.line([x, 0, x, RULER_HEIGHT_PT / 2], fill='black')

    font_size = 14
    font = ImageFont.truetype("arial.ttf", font_size)
    text = voucher_number
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (IMAGE_WIDTH_PT - text_width) / 2
    text_y = RULER_HEIGHT_PT + (WHITE_SPACE_HEIGHT_PT - text_height) / 2
    draw.text((text_x, text_y), text, fill='black', font=font)

    return ruler_image

def save_vouchers_to_pdf(voucher_count, voucher_prefix):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_width, page_height = letter
    slip_width = IMAGE_WIDTH_PT
    slip_height = IMAGE_HEIGHT_PT
    
    x_margin = 5
    y_margin = 8
    x_away = 10 - x_margin
    y_away = 10 - y_margin
    slips_per_row = 4
    slips_per_column = 12 
    
    x_offset = x_margin + x_away
    y_offset = page_height - y_margin - slip_height - y_away

    for i in range(1, voucher_count + 1):
        voucher_number = f"{voucher_prefix}-{i:03d}"
        ruler_image = create_ruler_image(voucher_number)
        
        # Use a temporary file to save the image
        fd, temp_filename = tempfile.mkstemp(suffix=".png")
        try:
            with os.fdopen(fd, 'wb') as temp_file:
                ruler_image.save(temp_file, format='PNG')
            
            # Draw the image on the PDF
            c.drawImage(temp_filename, x_offset, y_offset, width=slip_width, height=slip_height)
        finally:
            # Clean up the temporary file
            os.remove(temp_filename)
        
        x_offset += slip_width + x_margin
        if (i % slips_per_row == 0):
            x_offset = x_margin + x_away
            y_offset -= slip_height + y_margin - y_away
            if (i % (slips_per_row * slips_per_column) == 0):
                c.showPage()
                x_offset = x_margin + x_away
                y_offset = page_height - y_margin - slip_height - y_away

    c.save()
    buffer.seek(0)
    return buffer
