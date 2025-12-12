"""
Batch image generation script using existing GlyphScribe implementation.
Generates single-word images using all available fonts.
Uses streaming mode to avoid loading the entire 128GB dataset into memory.
"""
import os
import shutil
import random
from pathlib import Path
from tqdm import tqdm
from glyphscribe import GlyphScribe
from datasets import load_dataset


#ds = load_dataset("hishab/titulm-bangla-corpus", "default", streaming=True)


def get_all_fonts(fonts_dir):
    """Get all font paths from the fonts directory."""
    font_paths = []
    for ext in ['*.ttf', '*.otf']:
        font_paths.extend(Path(fonts_dir).rglob(ext))
    return [str(p) for p in font_paths]


def main():
    # Configuration
    NUM_IMAGES = 100
    BASE_OUTPUT_DIR = "out/batch"
    IMAGES_DIR = os.path.join(BASE_OUTPUT_DIR, "images")
    JSON_DIR = os.path.join(BASE_OUTPUT_DIR, "json")
    FONTS_DIR = "bangla_fonts"
    MAX_TEXT_LENGTH = 150

    print("="*60)
    print("GlyphScribe Batch Generator")
    print("="*60)

    # Load dataset in streaming mode (avoids loading 128GB into memory)
    print("\n[1/4] Loading dataset (streaming mode)...")
    ds = load_dataset("hishab/titulm-bangla-corpus", "default", streaming=True)
    dataset_stream = ds['train'] if 'train' in ds else ds[list(ds.keys())[0]]

    # Take random 1000 samples from stream
    print(f"✓ Sampling {NUM_IMAGES} random texts from dataset...")
    dataset = list(dataset_stream.shuffle(seed=42, buffer_size=10000).take(NUM_IMAGES))
    print(f"✓ Loaded {len(dataset)} samples")

    # Get all fonts
    print(f"\n[2/4] Finding fonts...")
    fonts = get_all_fonts(FONTS_DIR)
    print(f"✓ Found {len(fonts)} fonts")

    # Create output directories
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    print(f"✓ Output directories created")

    # Initialize GlyphScribe (uses existing augmentation pipeline)
    print("\n[3/4] Initializing GlyphScribe...")
    scribe = GlyphScribe()
    print("✓ Ready")

    # Generate images
    print(f"\n[4/4] Generating {NUM_IMAGES} images...\n")

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
                # Fallback to first string column
                text = next((v for v in sample.values() if isinstance(v, str)), None)

            if not text or len(text.strip()) == 0:
                failed += 1
                continue

            # Truncate long texts
            if len(text) > MAX_TEXT_LENGTH:
                text = text[:MAX_TEXT_LENGTH]

            # Cycle through all fonts
            font_path = fonts[img_idx % len(fonts)]

            # Random parameters for variety
            image_filename = f"image_{img_idx:06d}.png"
            image_path = os.path.join(IMAGES_DIR, image_filename)

            params = {
                'text': text,
                'font_size': random.choice([36, 40, 44, 48, 52, 56]),
                'font_path': font_path,
                'background_path': "",
                'angle': random.choice([0, 0, 5, -5, 8, -8, 10]),
                'bars': random.choice([True, False]),
                'add_random_text': random.choice([True, False]),
                'add_boxes': random.choice([True, False, False, False]),
                'add_curves': random.choice([True, False, False, False]),
                'apply_data_augmentation': True,  # Always use augmentation
                'white_background': random.choice([True, True, True, False]),
                'output_path': image_path
            }

            # Generate using existing GlyphScribe.generate()
            scribe.generate(**params)

            # Move JSON file to json directory
            json_filename = f"image_{img_idx:06d}.json"
            json_source = os.path.join(IMAGES_DIR, json_filename)
            json_dest = os.path.join(JSON_DIR, json_filename)

            if os.path.exists(json_source):
                shutil.move(json_source, json_dest)

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
    print(f"Images: {IMAGES_DIR}/")
    print(f"JSON:   {JSON_DIR}/")
    print("="*60)


if __name__ == '__main__':
    main()
