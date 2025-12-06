# GlyphScribe

GlyphScribe is a tool for generating synthetic Bengali handwriting images, designed to support research and development in handwriting recognition and related machine learning tasks.

This tool has been used in the paper:

**GraDeT-HTR: A Resource-Efficient Bengali Handwritten Text Recognition System utilizing Grapheme-based Tokenizer and Decoder-only Transformer**

*Accepted in the System Demonstrations Track of EMNLP 2025*

Paper: https://aclanthology.org/2025.emnlp-demos.52/

The code has been adapted from: https://github.com/v-laurent/VRD-image-text-generator

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python3 generate_distorted_image.py \
    --text "কোচবিহারের প্রথম রেলপথ ছিল যখন কোচবিহার রাজ্য রেলপথ ১৯০১ সালে" \
    --font_size 48 \
    --font_path "" \
    --background_path "" \
    --angle 5 \
    --bars True \
    --add_random_text False \
    --add_boxes False \
    --add_curves False \
    --apply_data_augmentation True \
    --output_path "out/generated_image.png"
```

## Arguments

- `--text`: The Bengali text to render
- `--font_size`: Size of the font in points
- `--font_path`: Path to custom font file (leave empty for default)
- `--background_path`: Path to background image (leave empty for default)
- `--angle`: Rotation angle in degrees for the text
- `--bars`: Add horizontal bars to the image
- `--add_random_text`: Add random text elements to the image
- `--add_boxes`: Add rectangular boxes to the image
- `--add_curves`: Add curved distortions to the image (takes precedence over `--angle`)
- `--apply_data_augmentation`: Apply data augmentation transformations
- `--output_path`: Path where the generated image will be saved

**Note:** When `--add_curves` is enabled, the `--angle` parameter will have no effect as curve distortions take precedence over rotation.

## Troubleshooting

If any rendering issue occurs, please follow the discussion at: https://github.com/python-pillow/Pillow/issues/3593

**Note:** This code has been heavily refactored before being pushed to GitHub. While we've tested it thoroughly, bugs may have snuck in during the refactoring process (they're sneaky like that). If you encounter any issues, please open an issue on GitHub or send an email to tahsinbd247@gmail.com.

## Acknowledgements

If this work is useful in your research, please cite it as follows:

```bibtex
@inproceedings{hasan-etal-2025-gradet,
    title = "{G}ra{D}e{T}-{HTR}: A Resource-Efficient {B}engali Handwritten Text Recognition System utilizing Grapheme-based Tokenizer and Decoder-only Transformer",
    author = "Hasan, Md. Mahmudul  and
      Choudhury, Ahmed Nesar Tahsin  and
      Hasan, Mahmudul  and
      Khan, Md Mosaddek",
    editor = {Habernal, Ivan  and
      Schulam, Peter  and
      Tiedemann, J{\"o}rg},
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-demos.52/",
    doi = "10.18653/v1/2025.emnlp-demos.52",
    pages = "696--706",
    ISBN = "979-8-89176-334-0",
    abstract = "Despite Bengali being the sixth most spoken language in the world, handwritten text recognition (HTR) systems for Bengali remain severely underdeveloped. The complexity of Bengali script{---}featuring conjuncts, diacritics, and highly variable handwriting styles{---}combined with a scarcity of annotated datasets makes this task particularly challenging. We present **GraDeT-HTR**, a resource-efficient Bengali handwritten text recognition system based on a **Gra**pheme-aware **De**coder-only **T**ransformer architecture. To address the unique challenges of Bengali script, we augment the performance of a decoder-only transformer by integrating a grapheme-based tokenizer and demonstrate that it significantly improves recognition accuracy compared to conventional subword tokenizers. Our model is pretrained on large-scale synthetic data and fine-tuned on real human-annotated samples, achieving state-of-the-art performance on multiple benchmark datasets."
}
```
