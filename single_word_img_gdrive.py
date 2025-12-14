"""
Single-word image generation script with direct Google Drive upload.
Generates clean single-word images and uploads them directly to Google Drive without local storage.
"""
import random
import re
from pathlib import Path
from tqdm import tqdm
from glyphscribe.glyph_scribe_memory import GlyphScribeMemory
from datasets import load_dataset
from PIL import Image, ImageDraw, ImageFont
from gdrive_uploader import GDriveUploader
import io


def get_all_fonts(fonts_dir):
    """Get all font paths from the fonts directory."""
    font_paths = []
    for ext in ['*.ttf', '*.otf']:
        font_paths.extend(Path(fonts_dir).rglob(ext))
    return [str(p) for p in font_paths]


def extract_words_from_text(text, min_length=2):
    """Extract individual words from text."""
    words = re.findall(r'\S+', text)
    words = [w for w in words if len(w) >= min_length]
    return words


def shift_text_position(image, position='center', dummy_word='La', font_size=48, font_path=''):
    """
    Shift the text position relative to an invisible dummy word at center.
    Works with PIL Image objects in memory.

    Args:
        image: PIL Image object
        position: Text position - 'left', 'center', or 'right'
        dummy_word: Reference word to use as center anchor
        font_size: Font size for measuring dummy word width
        font_path: Font path for measuring dummy word width

    Returns:
        PIL Image object (shifted)
    """
    if position == 'center':
        return image

    width, height = image.size

    # Calculate the width of the dummy word
    temp_img = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(temp_img)

    if font_path:
        try:
            font = ImageFont.truetype(font_path, size=font_size)
            dummy_width, _ = draw.textsize(dummy_word, font=font)
        except:
            dummy_width = int(width * 0.25)
    else:
        dummy_width = int(width * 0.25)

    shift_amount = int(dummy_width * 0.6)

    # Create a new white canvas
    new_img = Image.new("RGB", (width, height), "white")

    if position == 'left':
        new_img.paste(image.crop((shift_amount, 0, width, height)), (0, 0))
    elif position == 'right':
        new_img.paste(image.crop((0, 0, width - shift_amount, height)), (shift_amount, 0))

    return new_img


def main():
    # Configuration
    NUM_SAMPLES = 10
    NUM_IMAGES = 10
    FONTS_DIR = "bangla_fonts"
    MIN_WORD_LENGTH = 2
    DUMMY_WORD = 'La'
    GDRIVE_FOLDER = "GlyphScribe_Output"

    print("="*60)
    print("GlyphScribe Single-Word Generator (Google Drive)")
    print("="*60)

    # Initialize Google Drive uploader
    print("\n[1/6] Connecting to Google Drive...")
    try:
        uploader = GDriveUploader(folder_name=GDRIVE_FOLDER)
        print(f"✓ Connected to Google Drive")
        print(f"  Folder URL: {uploader.get_folder_url()}")
    except Exception as e:
        print(f"✗ Failed to connect to Google Drive: {e}")
        print("\nPlease ensure:")
        print("  1. credentials.json file exists in the project directory")
        print("  2. You have authenticated with Google Drive")
        return

    # Load dataset in streaming mode
    print("\n[2/6] Loading dataset (streaming mode)...")
    ds = load_dataset("hishab/titulm-bangla-corpus", "default", streaming=True)
    dataset_stream = ds['train'] if 'train' in ds else ds[list(ds.keys())[0]]

    # Sample texts from dataset
    print(f"✓ Sampling {NUM_SAMPLES} texts from dataset...")
    dataset = list(dataset_stream.shuffle(seed=42, buffer_size=10000).take(NUM_SAMPLES))
    print(f"✓ Loaded {len(dataset)} samples")

    # Extract all words from dataset
    print("\n[3/6] Extracting words from texts...")
    all_words = []
    for sample in dataset:
        text = None
        for col in ['text', 'sentence', 'content', 'line']:
            if col in sample:
                text = sample[col]
                break

        if not text:
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
    print(f"\n[4/6] Finding fonts...")
    fonts = get_all_fonts(FONTS_DIR)
    print(f"✓ Found {len(fonts)} fonts")

    # Initialize GlyphScribe
    print("\n[5/6] Initializing GlyphScribe...")
    scribe = GlyphScribeMemory()
    print("✓ Ready")

    # Generate and upload images
    print(f"\n[6/6] Generating and uploading {len(all_words)} single-word images to Google Drive...\n")

    successful = 0
    failed = 0

    for img_idx, word in enumerate(tqdm(all_words, desc="Progress")):
        try:
            # Cycle through all fonts
            font_path = fonts[img_idx % len(fonts)]

            # Output filenames
            image_filename = f"image_{img_idx:06d}.png"
            json_filename = f"image_{img_idx:06d}.json"

            # Select font size
            selected_font_size = random.choice([36, 40, 44, 48, 52, 56])

            # Parameters for generation
            generation_params = {
                'text': word,
                'font_size': selected_font_size,
                'font_path': font_path,
                'background_path': "",
                'angle': 5,
                'bars': True,
                'add_random_text': True,
                'add_boxes': False,
                'add_curves': True,
                'apply_data_augmentation': True,
                'white_background': True,
            }

            # Generate image in memory
            image, metadata = scribe.generate_to_memory(**generation_params)

            # Randomly select text position
            text_position = random.choice(['left', 'center', 'right'])

            # Apply position shifting in memory
            image = shift_text_position(
                image,
                position=text_position,
                dummy_word=DUMMY_WORD,
                font_size=selected_font_size,
                font_path=font_path
            )

            # Add position info to metadata
            metadata['text_position'] = text_position

            # Upload image to Google Drive
            uploader.upload_image(image, image_filename, folder_path="single_words/images")

            # Upload JSON metadata to Google Drive
            uploader.upload_json(metadata, json_filename, folder_path="single_words/json")

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
    print(f"\nGoogle Drive Folder: {uploader.get_folder_url()}")
    print("  - Images: single_words/images/")
    print("  - JSON:   single_words/json/")
    print("="*60)


if __name__ == '__main__':
    main()
