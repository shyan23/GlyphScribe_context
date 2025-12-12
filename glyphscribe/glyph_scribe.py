import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import string
import numpy as np
import math
import os
import json
from .augmentation import data_transformer
from bidi.algorithm import get_display

# Adding Bangla characters
bangla_characters = ''.join([chr(i) for i in range(0x0980, 0x09FF + 1)])

# Combine with other character sets as needed
all_characters = string.punctuation + " " + bangla_characters


class GlyphScribe:
    """
    GlyphScribe: A class for generating distorted text images with various effects.
    """

    def __init__(self, base_fonts_dir='bangla_fonts', background_base_dir='background'):
        """
        Initialize the GlyphScribe.

        Args:
            base_fonts_dir (str): Base directory for fonts
            background_base_dir (str): Base directory for background images
        """
        self.base_fonts_dir = base_fonts_dir
        self.background_base_dir = background_base_dir
        self.all_characters = string.punctuation + " " + bangla_characters

    @staticmethod
    def calculate_skew_offset(x, x_pivot, angle):
        """
        Calculate the vertical offset for skewing text.

        Args:
            x: current x-coordinate.
            x_pivot: x-coodinate of the pivot based on which the text has to be skewed.
            angle: angle of the skew (in degrees).
        """
        angle = np.radians(angle)
        delta_y = (x_pivot - x) * np.tan(angle)
        return delta_y

    @staticmethod
    def calculate_bent_offset(x, amplitude, frequency):
        """
        Calculate the vertical offset for a bent effect using a sine wave.

        Args:
            x: current x-coordinate.
            amplitude: amplitude of the sine wave.
            frequency: frequency of the sine wave.
        """
        return int(amplitude * np.sin(frequency * x))

    @staticmethod
    def extract_words(sentence):
        """
        Extracts and returns a list of words from a Bangla sentence, retaining spaces between words.

        Args:
            sentence (str): The input Bangla sentence.

        Returns:
            list: A list of words in the sentence, including spaces.
        """
        import re
        words = re.findall(r'\S+\s*', sentence)
        return words

    def get_random_font_path(self, font_type="hw"):
        """
        Get a random font path from the fonts directory.

        Args:
            font_type (str): Type of font ('hw' or 'printed')

        Returns:
            str: Path to a random font file
        """
        font_name = np.random.choice(os.listdir(f"{self.base_fonts_dir}/{font_type}/"))
        return os.path.join(self.base_fonts_dir, font_type, font_name)

    def get_random_background_path(self):
        """
        Get a random background image path.

        Returns:
            str: Path to a random background image
        """
        background_image_name = np.random.choice(os.listdir(f"{self.background_base_dir}/"))
        return os.path.join(self.background_base_dir, background_image_name)

    def add_bars(self, draw, image_size):
        """
        Add random vertical and horizontal bars to the image.

        Args:
            draw: ImageDraw object
            image_size: Tuple of (width, height)
        """
        for _ in range(random.randint(3, 6)):
            bar_x = random.randint(0, image_size[0] - 1)
            draw.line([(bar_x, 0), (bar_x, image_size[1])],
                     fill=tuple([np.random.randint(0, 100)] * 3),
                     width=random.randint(1, 3))

        for _ in range(random.randint(1, 3)):
            bar_y = random.randint(0, image_size[1] - 1)
            draw.line([(0, bar_y), (image_size[0], bar_y)],
                     fill=tuple([np.random.randint(0, 100)] * 3),
                     width=random.randint(1, 3))

    def add_random_text_overlay(self, draw, text, font, padding, image_size):
        """
        Add random text overlay to the image.

        Args:
            draw: ImageDraw object
            text: Original text
            font: Font object
            padding: Padding tuple
            image_size: Tuple of (width, height)
        """
        random_text = ''.join(random.choice(self.all_characters) for _ in range(len(text)))
        # bbox = draw.textbbox((0, 0), text, font=font)
        # text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]
        # Using textsize for compatibility with Pillow < 8.0.0
        text_width, text_height = draw.textsize(text, font=font)
        draw.text(
            (random.randint(-50, 50),
             image_size[1] - random.randint(5, 15) if padding[1] <= padding[3]
             else -text_height + random.randint(5, 15)),
            random_text,
            font=font,
            fill=tuple([np.random.randint(0, 100)] * 3),
        )

    def draw_text_with_boxes(self, draw, text, font, padding, tol, character_width, character_height):
        """
        Draw text with boxes around each character.

        Args:
            draw: ImageDraw object
            text: Text to draw
            font: Font object
            padding: Padding tuple
            tol: Tolerance factor
            character_width: Average character width
            character_height: Average character height
        """
        color = tuple([np.random.randint(0, 100)] * 3)
        text_color = tuple([np.random.randint(0, 100)] * 3)
        width = random.randint(1, 3)

        for i in range(len(text)):
            draw.line([(padding[0] + i*tol * character_width, padding[1]),
                      (padding[0] + i*tol * character_width, padding[1] + tol * character_width)],
                      fill=color, width=width)
            draw.line([(padding[0] + i*tol * character_width, padding[1] + tol * character_width),
                      (padding[0] + (i+1)*tol * character_width, padding[1] + tol * character_width)],
                      fill=color, width=width)
            draw.line([(padding[0] + (i+1)*tol * character_width, padding[1]),
                      (padding[0] + (i+1)*tol * character_width, padding[1] + tol * character_width)],
                      fill=color, width=width)
            draw.text(
                (padding[0] + i*tol * character_width + ((tol-1) * character_width) // 2 + random.randint(-2,2),
                 padding[1] + tol * character_width - character_height + random.randint(-2,2)),
                text[i],
                font=font,
                fill=text_color,
            )

    def draw_text_with_curves(self, draw, words, font, padding):
        """
        Draw text with curved effect.

        Args:
            draw: ImageDraw object
            words: List of words to draw
            font: Font object
            padding: Padding tuple
        """
        x, y = padding[0], padding[1]
        for word in words:
            offset_y = self.calculate_bent_offset(x=x, amplitude=4, frequency=0.02)
            draw.text(
                (x, y + offset_y),
                word,
                font=font,
                fill=tuple([np.random.randint(0, 100)] * 3),
            )

            word_width, _ = draw.textsize(word, font=font)
            x += word_width

    def draw_text_with_skew(self, draw, words, font, padding, text_width, image_height, angle):
        """
        Draw text with skew effect.

        Args:
            draw: ImageDraw object
            words: List of words to draw
            font: Font object
            padding: Padding tuple
            text_width: Width of the text
            image_height: Height of the image
            angle: Skew angle
        """
        x, y = padding[0], (image_height // 2)
        x_mid = x + (text_width // 2)
        for word in words:
            offset_y = self.calculate_skew_offset(x=x, x_pivot=x_mid, angle=angle)
            draw.text(
                (x, y - offset_y),
                word,
                font=font,
                fill=tuple([np.random.randint(0, 100)] * 3),
            )

            word_width, _ = draw.textsize(word, font=font)
            x += word_width

    def generate(self, text, font_size=48, font_path="", background_path="", angle=0,
                bars=True, add_random_text=True, add_boxes=True, add_curves=False,
                apply_data_augmentation=True, white_background=True, output_path="generated_image.png"):
        """
        Generate a distorted text image with various effects.

        Args:
            text (str): Text to be generated in the image
            font_size (int): Font size for the text
            font_path (str): Path to the font file (empty for random font)
            background_path (str): Path to the background image file (empty for random background)
            angle (int): Skew angle in degrees
            bars (bool): Add bars to the image
            add_random_text (bool): Add random text overlay
            add_boxes (bool): Add boxes around characters
            add_curves (bool): Apply curves to the text
            apply_data_augmentation (bool): Apply data augmentation
            white_background (bool): Use white background instead of background image
            output_path (str): Output path of the generated image
        """
        # Store original input values for context
        original_text = text
        original_font_path = font_path
        original_background_path = background_path

        image = Image.new("RGB", (2000, 2000), "white")
        draw = ImageDraw.Draw(image)

        text = get_display(text)
        words = self.extract_words(text)

        if font_path == "":
            font_path = self.get_random_font_path(font_type="hw")

        font = ImageFont.truetype(font_path, size=font_size)
        # bbox = draw.textbbox((0, 0), text, font=font)
        # text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]
        # Using textsize for compatibility with Pillow < 8.0.0
        text_width, text_height = draw.textsize(text, font=font)

        total_word_width = 0
        for word in words:
            # word_bbox = draw.textbbox((0, 0), word, font=font)
            # word_width = word_bbox[2] - word_bbox[0]
            # Using textsize for compatibility with Pillow < 8.0.0
            word_width, _ = draw.textsize(word, font=font)
            total_word_width += word_width

        if add_boxes:
            tol = random.randint(10, 15) / 10
            character_width, character_height = np.mean([draw.textsize(c, font) for c in text], axis=0).astype(int)
            image = Image.new("RGB", (int(tol * character_width * len(text)), character_height), "white")
        else:
            w = text_width
            h = text_height

            if angle != 0 or add_curves == True:
                w = total_word_width

            angle_rad = math.radians(angle)
            new_w = w
            new_h = h
            if add_curves == False:
                new_h = h + int(abs(w * np.tan(angle_rad)))

            image = Image.new("RGB", (new_w, new_h), "white")

        padding = tuple(random.randint(40, 40) for _ in range(4))
        image = ImageOps.expand(image, padding, fill="white")
        image_width, image_height = image.size

        # Track actual background path used
        actual_background_path = None
        if not white_background:
            if background_path == "":
                background_path = self.get_random_background_path()
            actual_background_path = background_path
            background_image = Image.open(background_path)
            background_image = background_image.resize((image_width, image_height))
            image.paste(background_image)

        draw = ImageDraw.Draw(image)

        if bars:
            self.add_bars(draw, image.size)

        if add_random_text:
            self.add_random_text_overlay(draw, text, font, padding, image.size)

        if add_boxes:
            self.draw_text_with_boxes(draw, text, font, padding, tol, character_width, character_height)
        else:
            if add_curves:
                self.draw_text_with_curves(draw, words, font, padding)
            elif angle != 0:
                self.draw_text_with_skew(draw, words, font, padding, text_width, image_height, angle)
            else:
                draw.text(
                    (padding[0], padding[1]),
                    text,
                    font=font,
                    fill=tuple([np.random.randint(0, 100)] * 3),
                )

        if apply_data_augmentation:
            image = data_transformer(image)

        directory = os.path.dirname(output_path)
        os.makedirs(directory, exist_ok=True)

        image.save(output_path)

        # Save generation context as JSON
        context = {
            "text": original_text,
            "font_size": font_size,
            "font_path_input": original_font_path,
            "font_path_used": font_path,
            "background_path_input": original_background_path,
            "background_path_used": actual_background_path,
            "angle": angle,
            "bars": bars,
            "add_random_text": add_random_text,
            "add_boxes": add_boxes,
            "add_curves": add_curves,
            "apply_data_augmentation": apply_data_augmentation,
            "white_background": white_background,
            "output_path": output_path
        }

        # Generate JSON file path by replacing image extension with .json
        json_path = os.path.splitext(output_path)[0] + ".json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)

        print(f"Image saved to: {output_path}")
        print(f"Context saved to: {json_path}")

        return
