"""
Single-word image generation script using GlyphScribe.
Generates clean single-word images using all available fonts.
Extracts words from dataset sentences.
"""
import os
import shutil
import random
import re
from pathlib import Path
from tqdm import tqdm
from glyphscribe import GlyphScribe
from datasets import load_dataset
from PIL import Image


def get_all_fonts(fonts_dir):
    """Get all font paths from the fonts directory."""
    font_paths = []
    for ext in ['*.ttf', '*.otf']:
        font_paths.extend(Path(fonts_dir).rglob(ext))
    return [str(p) for p in font_paths]


def extract_words_from_text(text, min_length=2):
    """
    Extract individual words from text.

    Args:
        text: Input text string
        min_length: Minimum word length to include

    Returns:
        List of words filtered by minimum length
    """
    # Split by whitespace and filter out empty strings
    words = re.findall(r'\S+', text)
    # Filter by minimum length
    words = [w for w in words if len(w) >= min_length]
    return words


def shift_text_position(image_path, position='center', dummy_word='প্রথম', font_size=48, font_path=''):
    """
    Shift the text position relative to an invisible dummy word at center.

    Concept: Imagine a dummy word (e.g., 'প্রথম') positioned at the center (invisible).
    The actual text is positioned left or right relative to this invisible dummy word.

    Args:
        image_path: Path to the image file
        position: Text position - 'left', 'center', or 'right'
        dummy_word: Reference word to use as center anchor (default: 'প্রথম')
        font_size: Font size for measuring dummy word width
        font_path: Font path for measuring dummy word width

    Returns:
        None (modifies image in-place)
    """
    if position == 'center':
        return  # No shift needed for center position

    from PIL import ImageDraw, ImageFont

    # Load the image (actual text is currently centered)
    img = Image.open(image_path)
    width, height = img.size

    # Calculate the width of the dummy word
    # Use a temporary draw context to measure text
    temp_img = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(temp_img)

    # Use the font if provided, otherwise estimate
    if font_path:
        try:
            font = ImageFont.truetype(font_path, size=font_size)
            dummy_width, _ = draw.textsize(dummy_word, font=font)
        except:
            # Fallback: estimate based on percentage
            dummy_width = int(width * 0.25)
    else:
        # Fallback: estimate dummy word width as 25% of image width
        dummy_width = int(width * 0.25)

    # Add padding/spacing around the dummy word
    # Shift by half the dummy word width for more subtle positioning
    shift_amount = int(dummy_width * 0.6)  # 60% of dummy word width

    # Create a new white canvas
    new_img = Image.new("RGB", (width, height), "white")

    if position == 'left':
        # Position actual text to the LEFT of the invisible dummy word
        # Shift the content left
        new_img.paste(img.crop((shift_amount, 0, width, height)), (0, 0))

    elif position == 'right':
        # Position actual text to the RIGHT of the invisible dummy word
        # Shift the content right
        new_img.paste(img.crop((0, 0, width - shift_amount, height)), (shift_amount, 0))

    # Save the modified image
    new_img.save(image_path)


def main():
    # Configuration
    NUM_SAMPLES = 10000  # Number of text samples to load from dataset
    NUM_IMAGES = 10000  # Total number of word images to generate
    BASE_OUTPUT_DIR = "out/single_words"
    IMAGES_DIR = os.path.join(BASE_OUTPUT_DIR, "images")
    JSON_DIR = os.path.join(BASE_OUTPUT_DIR, "json")
    FONTS_DIR = "bangla_fonts"
    MIN_WORD_LENGTH = 2  # Minimum word length to generate

    # Text position parameters (ADJUSTABLE)
    DUMMY_WORD = 'La'  # Reference word for positioning (invisible, at center) - 1-2 letters
    DUMMY_SPACING_MULTIPLIER = 0.2  # Spacing around dummy word (0.3 = 30% of dummy width)

    print("="*60)
    print("GlyphScribe Single-Word Generator")
    print("="*60)

    # Load dataset in streaming mode
    print("\n[1/5] Loading dataset (streaming mode)...")
    ds = load_dataset("hishab/titulm-bangla-corpus", "default", streaming=True)
    dataset_stream = ds['train'] if 'train' in ds else ds[list(ds.keys())[0]]

    # Sample texts from dataset
    print(f"✓ Sampling {NUM_SAMPLES} texts from dataset...")
    dataset = list(dataset_stream.shuffle(seed=42, buffer_size=10000).take(NUM_SAMPLES))
    print(f"✓ Loaded {len(dataset)} samples")

    # Extract all words from dataset
    print("\n[2/5] Extracting words from texts...")
    all_words = []
    for sample in dataset:
        # Extract text from dataset
        text = None
        for col in ['text', 'sentence', 'content', 'line']:
            if col in sample:
                text = sample[col]
                break

        if not text:
            # Fallback to first string column
            text = next((v for v in sample.values() if isinstance(v, str)), None)

        if text and len(text.strip()) > 0:
            words = extract_words_from_text(text, min_length=MIN_WORD_LENGTH)
            all_words.extend(words)

    print(f"✓ Extracted {len(all_words)} words")

    # Shuffle and limit to NUM_IMAGES
    random.seed(42)
    random.shuffle(all_words)
    all_words = all_words[:NUM_IMAGES]
    print(f"✓ Using {len(all_words)} words for generation")

    # Get all fonts
    print(f"\n[3/5] Finding fonts...")
    fonts = get_all_fonts(FONTS_DIR)
    print(f"✓ Found {len(fonts)} fonts")

    # Create output directories
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    print(f"✓ Output directories created")

    # Initialize GlyphScribe
    print("\n[4/5] Initializing GlyphScribe...")
    scribe = GlyphScribe()
    print("✓ Ready")

    # Generate images
    print(f"\n[5/5] Generating {len(all_words)} single-word images...\n")

    successful = 0
    failed = 0

    for img_idx, word in enumerate(tqdm(all_words, desc="Progress")):
        try:
            # Cycle through all fonts
            font_path = fonts[img_idx % len(fonts)]

            # Output paths
            image_filename = f"image_{img_idx:06d}.png"
            image_path = os.path.join(IMAGES_DIR, image_filename)

            # Select font size
            selected_font_size = random.choice([36, 40, 44, 48, 52, 56])

            # Parameters for GlyphScribe.generate()
            # NO ARTIFACTS: bars=False, add_random_text=False, add_boxes=False,
            # add_curves=False, angle=0
            generation_params = {
                'text': word,
                'font_size': selected_font_size,
                'font_path': font_path,
                'background_path': "",
                'angle': 5,  # No skew
                'bars': True,  # No bars
                'add_random_text': True,  # No random text overlay
                'add_boxes': False,  # No boxes
                'add_curves': True,  # No curves
                'apply_data_augmentation': True,  # Keep augmentation for realism
                'white_background': True,
                'output_path': image_path
            }

            # Generate using GlyphScribe.generate()
            scribe.generate(**generation_params)

            # Randomly select text position for this image
            text_position = random.choice(['left', 'center', 'right'])

            # Apply position shifting to the generated image (using dummy word reference)
            shift_text_position(
                image_path,
                position=text_position,
                dummy_word=DUMMY_WORD,
                font_size=selected_font_size,
                font_path=font_path
            )

            # Move JSON file to json directory
            json_filename = f"image_{img_idx:06d}.json"
            json_source = os.path.join(IMAGES_DIR, json_filename)
            json_dest = os.path.join(JSON_DIR, json_filename)

            if os.path.exists(json_source):
                shutil.move(json_source, json_dest)

            successful += 1

        except Exception as e:
            tqdm.write(f"Error at {img_idx} (word: '{word}'): {e}")
            failed += 1

    # Summary
    print("\n" + "="*60)
    print("✓ Generation Complete!")
    print("="*60)
    print(f"Successful: {successful}/{len(all_words)}")
    if failed > 0:
        print(f"Failed: {failed}")
    print(f"Images: {IMAGES_DIR}/")
    print(f"JSON:   {JSON_DIR}/")
    print("="*60)


if __name__ == '__main__':
    main()
