"""Quick test to verify the shift function works"""
from PIL import Image

def shift_text_position(image_path, position='center', shift_percentage=0.25):
    """Shift the text position in the image relative to center."""
    if position == 'center':
        return

    img = Image.open(image_path)
    width, height = img.size
    shift_amount = int(width * shift_percentage)
    new_img = Image.new("RGB", (width, height), "white")

    if position == 'left':
        cropped = img.crop((shift_amount, 0, width, height))
        new_img.paste(cropped, (0, 0))
    elif position == 'right':
        cropped = img.crop((0, 0, width - shift_amount, height))
        new_img.paste(cropped, (shift_amount, 0))

    new_img.save(image_path)

# Test on the image you mentioned
test_image = "out/single_words/images/image_000098.png"
print(f"Testing shift on {test_image}")
shift_text_position(test_image, position='left', shift_percentage=0.25)
print("Done! Check the image now.")
