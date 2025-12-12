"""Test the dummy word positioning logic"""
from PIL import Image, ImageDraw, ImageFont

def test_shift():
    image_path = "out/single_words/images/image_000006.png"
    dummy_word = 'প্রথম'
    font_path = 'bangla_fonts/hw/Mina-Regular.ttf'
    font_size = 48
    position = 'left'

    # Load the image
    img = Image.open(image_path)
    width, height = img.size
    print(f"Image size: {width}x{height}")

    # Calculate dummy word width
    temp_img = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(temp_img)

    try:
        font = ImageFont.truetype(font_path, size=font_size)
        dummy_width, _ = draw.textsize(dummy_word, font=font)
        print(f"Dummy word '{dummy_word}' width: {dummy_width}px at font size {font_size}")
    except Exception as e:
        print(f"Font loading error: {e}")
        dummy_width = int(width * 0.25)
        print(f"Using fallback dummy width: {dummy_width}px (25% of image width)")

    # Calculate shift
    spacing = int(dummy_width * 0.3)
    shift_amount = dummy_width + spacing
    print(f"Spacing: {spacing}px")
    print(f"Total shift amount: {shift_amount}px ({shift_amount/width*100:.1f}% of image width)")

    # Apply shift
    new_img = Image.new("RGB", (width, height), "white")
    if position == 'left':
        new_img.paste(img.crop((shift_amount, 0, width, height)), (0, 0))

    new_img.save(image_path)
    print(f"Shifted image to {position}")

test_shift()
