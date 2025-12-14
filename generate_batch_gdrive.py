"""
Batch image generation script with direct Google Drive upload.
Generates multi-line images and uploads them directly to Google Drive without local storage.
"""
import random
from pathlib import Path
from tqdm import tqdm
from glyphscribe.glyph_scribe_memory import GlyphScribeMemory
from datasets import load_dataset
from gdrive_uploader import GDriveUploader


def get_all_fonts(fonts_dir):
    """Get all font paths from the fonts directory."""
    font_paths = []
    for ext in ['*.ttf', '*.otf']:
        font_paths.extend(Path(fonts_dir).rglob(ext))
    return [str(p) for p in font_paths]


def main():
    # Configuration
    NUM_IMAGES = 10
    FONTS_DIR = "bangla_fonts"
    MAX_TEXT_LENGTH = 300  # Increased for multi-line support
    MAX_LINE_WIDTH = 1400  # Maximum width per line in pixels
    GDRIVE_FOLDER = "GlyphScribe_Output"  # Root folder in Google Drive

    print("="*60)
    print("GlyphScribe Batch Generator (Google Drive)")
    print("="*60)

    # Initialize Google Drive uploader
    print("\n[1/5] Connecting to Google Drive...")
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
    print("\n[2/5] Loading dataset (streaming mode)...")
    ds = load_dataset("hishab/titulm-bangla-corpus", "default", streaming=True)
    dataset_stream = ds['train'] if 'train' in ds else ds[list(ds.keys())[0]]

    # Sample texts from dataset
    print(f"✓ Sampling {NUM_IMAGES} random texts from dataset...")
    dataset = list(dataset_stream.shuffle(seed=42, buffer_size=10000).take(NUM_IMAGES))
    print(f"✓ Loaded {len(dataset)} samples")

    # Get all fonts
    print(f"\n[3/5] Finding fonts...")
    fonts = get_all_fonts(FONTS_DIR)
    print(f"✓ Found {len(fonts)} fonts")

    # Initialize GlyphScribe (memory mode)
    print("\n[4/5] Initializing GlyphScribe...")
    scribe = GlyphScribeMemory()
    print("✓ Ready")

    # Generate and upload images
    print(f"\n[5/5] Generating and uploading {NUM_IMAGES} images to Google Drive...\n")

    successful = 0
    failed = 0

    for img_idx in tqdm(range(NUM_IMAGES), desc="Progress"):
        try:
            # Get text from dataset
            sample = dataset[img_idx]

            # Extract text from dataset
            text = None
            for col in ['text', 'sentence', 'content', 'line']:
                if col in sample:
                    text = sample[col]
                    break

            if not text:
                text = next((v for v in sample.values() if isinstance(v, str)), None)

            if not text or len(text.strip()) == 0:
                failed += 1
                continue

            # Randomly decide if this should be single-line or multi-line
            is_multiline = random.choice([True, False])

            # Adjust text length based on line type
            max_length = MAX_TEXT_LENGTH if is_multiline else 80
            if len(text) > max_length:
                text = text[:max_length]

            # Cycle through all fonts
            font_path = fonts[img_idx % len(fonts)]

            # Random parameters for variety
            image_filename = f"image_{img_idx:06d}.png"
            json_filename = f"image_{img_idx:06d}.json"

            params = {
                'text': text,
                'font_size': random.choice([40, 44, 48, 52]),
                'font_path': font_path,
                'background_path': "",
                'angle': random.choice([0, 0, 0, 0, 5, -5]),
                'bars': random.choice([False, False, False, True]),
                'add_random_text': False,
                'add_curves': False,
                'add_boxes': False,
                'apply_data_augmentation': random.choice([True, True, False]),
                'white_background': random.choice([True, True, True, True, False]),
                'multiline': is_multiline,
                'max_line_width': MAX_LINE_WIDTH,
            }

            # Generate image in memory
            image, metadata = scribe.generate_to_memory(**params)

            # Upload image to Google Drive
            uploader.upload_image(image, image_filename, folder_path="batch/images")

            # Upload JSON metadata to Google Drive
            uploader.upload_json(metadata, json_filename, folder_path="batch/json")

            successful += 1

        except Exception as e:
            tqdm.write(f"Error at {img_idx}: {e}")
            failed += 1

    # Summary
    print("\n" + "="*60)
    print("✓ Generation Complete!")
    print("="*60)
    print(f"Successful: {successful}/{NUM_IMAGES}")
    if failed > 0:
        print(f"Failed: {failed}")
    print(f"\nGoogle Drive Folder: {uploader.get_folder_url()}")
    print("  - Images: batch/images/")
    print("  - JSON:   batch/json/")
    print("="*60)


if __name__ == '__main__':
    main()
