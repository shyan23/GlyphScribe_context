import click
from glyphscribe import GlyphScribe

@click.command()
@click.option('--text', help='Text to be generated in the image')
@click.option('--font_size', default=48, help='Font size for the text')
@click.option('--font_path', default="", help='Path to the font file (empty for random font)')
@click.option('--background_path', default="", help='Path to the background image file (empty for random background image)')
@click.option('--angle', default=0, help='Skew angle in degrees')
@click.option('--bars', default=True, type=click.BOOL, help='List of bars to be added to the image')
@click.option('--add_random_text', default=True, type=click.BOOL, help='Add random text to the image')
@click.option('--add_boxes', default=True, type=click.BOOL, help='Add boxes to the image')
@click.option('--add_curves', default=False, type=click.BOOL, help='Apply curves to the text')
@click.option('--apply_data_augmentation', default=True, type=click.BOOL, help='Apply data augmentation to the image')
@click.option('--white_background', default=True, type=click.BOOL, help='Use white background instead of background image')
@click.option('--output_path', default="generated_image.png", help='Output path of the generated image')
def generate_text_image(text, font_size, font_path, background_path, angle, bars, add_random_text, add_boxes, add_curves, apply_data_augmentation, white_background, output_path):
    print(f"Provided text: {text}")
    scribe = GlyphScribe()
    return scribe.generate(text, font_size, font_path, background_path, angle, bars,
                          add_random_text, add_boxes, add_curves, apply_data_augmentation, white_background, output_path)

if __name__ == '__main__':
    generate_text_image()