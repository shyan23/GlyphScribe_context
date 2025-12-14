# GlyphScribe Google Drive Integration

Generate Bangla handwritten text images and upload them directly to Google Drive - saving local disk space!

## Features

✅ **Space-saving**: Images upload directly to Google Drive without local storage
✅ **Organized folders**: Automatic folder structure in Google Drive
✅ **Multi-line & single-word**: Two generation modes
✅ **Clean images**: Random mix of single-line and multi-line text
✅ **JSON metadata**: Complete generation parameters saved

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. First-Time Authentication

When you run the script for the first time, a browser window will open:

```bash
python generate_batch.py
```

1. Sign in with your Google account
2. Click "Allow" to grant access to Google Drive
3. The authentication token will be saved for future runs

**Note**: You only need to do this once!

### 3. Run the Generators

#### Batch Generator (Multi-line images)
```bash
python generate_batch.py
```

This creates images with:
- 50% single-line text (short sentences)
- 50% multi-line text (longer paragraphs)
- Random fonts, angles, and augmentations

#### Single-Word Generator
```bash
python single_word_img.py
```

This creates images with:
- Individual words extracted from dataset
- Random positioning (left, center, right)
- Clean single-word appearance

## Google Drive Folder Structure

After running, your Google Drive will contain:

```
Google Drive/
└── GlyphScribe_Output/
    ├── batch/
    │   ├── images/
    │   │   ├── image_000000.png
    │   │   ├── image_000001.png
    │   │   └── ...
    │   └── json/
    │       ├── image_000000.json
    │       ├── image_000001.json
    │       └── ...
    └── single_words/
        ├── images/
        │   └── ...
        └── json/
            └── ...
```

## Configuration

### Change Number of Images

Edit `generate_batch.py`:
```python
NUM_IMAGES = 10  # Change to any number
```

Edit `single_word_img.py`:
```python
NUM_IMAGES = 10  # Change to any number
```

### Change Google Drive Folder Name

Edit either script:
```python
GDRIVE_FOLDER = "GlyphScribe_Output"  # Change to your preference
```

### Adjust Text Length

In `generate_batch.py`:
```python
MAX_TEXT_LENGTH = 300  # For multi-line
# Single-line is automatically limited to 80 characters
```

## How It Works

1. **No Local Storage**: Images are generated in memory (RAM)
2. **Direct Upload**: Each image uploads immediately to Google Drive
3. **Auto-cleanup**: Temporary data is cleared after upload
4. **Metadata**: JSON files contain all generation parameters

## Files

- `credentials.json` - Your Google Drive OAuth credentials (required, in gitignore)
- `gdrive_token.json` - Saved authentication token (auto-generated, in gitignore)
- `gdrive_uploader.py` - Google Drive upload handler
- `generate_batch.py` - Multi-line image generator
- `single_word_img.py` - Single-word image generator
- `glyphscribe/glyph_scribe_memory.py` - Memory-based image generation

## Troubleshooting

### "Failed to connect to Google Drive"

1. Make sure `credentials.json` exists in the project directory
2. Check your internet connection
3. Try deleting `gdrive_token.json` and re-authenticating

### "Authentication failed"

Delete the token file and try again:
```bash
rm gdrive_token.json
python generate_batch.py
```

### Upload is slow

- Google Drive upload speed depends on your internet connection
- Reduce `NUM_IMAGES` for testing
- Images are uploaded one-by-one to ensure reliability

### Need more storage

With Google One (free 1-year subscription):
- You get 100GB of storage
- Perfect for thousands of images!

## Comparing to Local Storage

| Feature | Google Drive | Local Storage |
|---------|-------------|---------------|
| Disk space used | **0 MB** | 10,000+ MB |
| Backup | **Automatic** | Manual |
| Access from anywhere | **Yes** | No |
| Organized folders | **Automatic** | Manual |

## Security

- `credentials.json` is in `.gitignore` (never committed to git)
- `gdrive_token.json` is in `.gitignore` (never committed to git)
- Only you can access your Google Drive files
- Revoke access anytime from Google Account settings

## Get Your Google Drive URL

After running, the script will print:
```
Google Drive Folder: https://drive.google.com/drive/folders/xxxxx
```

Click this link to view your generated images!

## Support

Having issues? Check:
1. credentials.json is in the project root
2. PyDrive2 is installed: `pip install PyDrive2`
3. You have internet connection
4. You have space in Google Drive

Happy generating! 🎨
