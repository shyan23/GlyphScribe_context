# ✅ Setup Complete - Google Drive Integration

Your GlyphScribe project is now configured to upload images directly to Google Drive, saving disk space!

## 🎯 What's Been Set Up

### Modified Files
1. **generate_batch.py** - Now uploads multi-line images to Google Drive
2. **single_word_img.py** - Now uploads single-word images to Google Drive
3. **requirements.txt** - Added PyDrive2 and Google Auth packages
4. **.gitignore** - Secured your credentials (they won't be committed to git)

### New Files Created
1. **gdrive_uploader.py** - Handles all Google Drive operations
2. **glyphscribe/glyph_scribe_memory.py** - Memory-based image generation (no disk writes)
3. **README_GDRIVE.md** - Complete usage guide

### Installed Packages
✅ PyDrive2
✅ google-auth
✅ google-auth-oauthlib
✅ google-auth-httplib2

## 🚀 How to Use

### First Time Setup (One-time only)

Run either script:
```bash
python generate_batch.py
```

A browser window will open automatically:
1. **Sign in** with your Google account
2. **Click "Allow"** when asked for permissions
3. Done! The token is saved for future runs

### Regular Usage

After authentication, just run:
```bash
# Multi-line images (mixed single and multi-line)
python generate_batch.py

# Single-word images
python single_word_img.py
```

## 📁 Google Drive Folder Structure

Your Google Drive will automatically create:
```
Google Drive/
└── GlyphScribe_Output/
    ├── batch/
    │   ├── images/          <- Multi-line images
    │   └── json/            <- Metadata
    └── single_words/
        ├── images/          <- Single-word images
        └── json/            <- Metadata
```

## ⚙️ Configuration

### Number of Images
Edit the scripts to change how many images to generate:

**generate_batch.py:**
```python
NUM_IMAGES = 10  # Change this number
```

**single_word_img.py:**
```python
NUM_IMAGES = 10  # Change this number
```

### Google Drive Folder Name
Change the root folder name in either script:
```python
GDRIVE_FOLDER = "GlyphScribe_Output"  # Customize this
```

## 💾 Disk Space Savings

**Before (Local Storage):**
- 10,000 images = ~2-5 GB on your hard drive
- Manual backup required
- Local-only access

**After (Google Drive):**
- 0 MB on your hard drive! ✨
- Automatic cloud backup
- Access from anywhere
- 15GB free (100GB with Google One)

## 📊 What Gets Uploaded

For each image:
1. **PNG file** - The generated image
2. **JSON file** - Complete metadata including:
   - Original text
   - Font used
   - All generation parameters
   - Whether it's single or multi-line
   - Augmentation settings

## 🔒 Security

Your credentials are protected:
- ✅ `credentials.json` - In .gitignore (never committed)
- ✅ `gdrive_token.json` - In .gitignore (never committed)
- ✅ Only you can access your Google Drive
- ✅ Revoke access anytime from Google Account settings

## 🛠️ Troubleshooting

### "credentials.json not found"
Make sure the file is in the project root:
```bash
ls credentials.json
```

### Authentication Issues
Delete the token and re-authenticate:
```bash
rm gdrive_token.json
python generate_batch.py
```

### Check Installation
Verify PyDrive2 is installed:
```bash
pip show PyDrive2
```

## 📝 Example Session

```bash
$ python generate_batch.py

============================================================
GlyphScribe Batch Generator (Google Drive)
============================================================

[1/5] Connecting to Google Drive...
✓ Authenticated with Google Drive
  Folder URL: https://drive.google.com/drive/folders/xxxxx

[2/5] Loading dataset (streaming mode)...
✓ Sampling 10 random texts from dataset...
✓ Loaded 10 samples

[3/5] Finding fonts...
✓ Found 45 fonts

[4/5] Initializing GlyphScribe...
✓ Ready

[5/5] Generating and uploading 10 images to Google Drive...

Progress: 100%|████████████| 10/10 [00:45<00:00,  4.5s/it]

============================================================
✓ Generation Complete!
============================================================
Successful: 10/10

Google Drive Folder: https://drive.google.com/drive/folders/xxxxx
  - Images: batch/images/
  - JSON:   batch/json/
============================================================
```

## 🎨 Image Types Generated

### Multi-line Images (`generate_batch.py`)
- 50% single-line (short text, ~80 chars)
- 50% multi-line (longer text, ~300 chars)
- Random fonts from your collection
- Mostly clean (minimal augmentation)
- Random angles (mostly straight)

### Single-word Images (`single_word_img.py`)
- Individual words from dataset
- Random positioning (left/center/right)
- Various font sizes
- Augmentation for realism

## 📋 Next Steps

1. ✅ Run `python generate_batch.py` to test
2. ✅ Check your Google Drive for the uploaded images
3. ✅ Adjust `NUM_IMAGES` to generate more data
4. ✅ Use the generated images for training your HTR model!

## 🎉 You're All Set!

Your GlyphScribe is now configured for space-efficient, cloud-based image generation. Happy generating! 🚀

---

**Need help?** Check `README_GDRIVE.md` for detailed documentation.
