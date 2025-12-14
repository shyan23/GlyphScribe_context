"""
Modified GlyphScribe that returns images in memory instead of saving to disk.
Used for direct Google Drive upload without local storage.
"""
from .glyph_scribe import GlyphScribe as BaseGlyphScribe
from PIL import Image
import json


class GlyphScribeMemory(BaseGlyphScribe):
    """Extended GlyphScribe that returns images and metadata instead of saving"""

    def generate_to_memory(self, text, font_size=48, font_path="", background_path="", angle=0,
                          bars=True, add_random_text=True, add_boxes=True, add_curves=False,
                          apply_data_augmentation=True, white_background=True,
                          multiline=False, max_line_width=1200):
        """
        Generate a distorted text image and return it with metadata (no disk save).

        Returns:
            tuple: (PIL.Image, dict) - Image object and metadata dictionary
        """
        # Import required modules
        import random
        from PIL import ImageDraw, ImageFont, ImageOps
        import numpy as np
        import math
        from bidi.algorithm import get_display
        from .augmentation import data_transformer

        # Store original input values for context
        original_text = text
        original_font_path = font_path
        original_background_path = background_path

        image = Image.new("RGB", (2000, 2000), "white")
        draw = ImageDraw.Draw(image)

        text = get_display(text)

        if font_path == "":
            font_path = self.get_random_font_path(font_type="hw")

        font = ImageFont.truetype(font_path, size=font_size)

        # Handle multi-line text wrapping
        if multiline:
            lines = self.wrap_text(text, font, max_line_width)
        else:
            lines = [text]

        words = self.extract_words(text)

        # Calculate dimensions for single line
        text_width, text_height = draw.textsize(text, font=font)

        total_word_width = 0
        for word in words:
            word_width, _ = draw.textsize(word, font=font)
            total_word_width += word_width

        if add_boxes:
            tol = random.randint(10, 15) / 10
            character_width, character_height = np.mean([draw.textsize(c, font) for c in text], axis=0).astype(int)
            image = Image.new("RGB", (int(tol * character_width * len(text)), character_height), "white")
        else:
            if multiline:
                # Calculate dimensions for multi-line text
                max_width = 0
                total_height = 0
                line_height = text_height
                line_spacing = int(line_height * 0.3)

                for line in lines:
                    line_width, _ = draw.textsize(line, font=font)
                    max_width = max(max_width, line_width)
                    total_height += line_height + line_spacing

                total_height -= line_spacing

                new_w = max_width
                new_h = total_height
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
            if multiline:
                # Draw multi-line text
                y_offset = padding[1]
                line_height = text_height
                line_spacing = int(line_height * 0.3)

                for line in lines:
                    draw.text(
                        (padding[0], y_offset),
                        line,
                        font=font,
                        fill=tuple([np.random.randint(0, 100)] * 3),
                    )
                    y_offset += line_height + line_spacing
            elif add_curves:
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

        # Create metadata dictionary
        metadata = {
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
            "multiline": multiline,
            "max_line_width": max_line_width
        }

        return image, metadata
