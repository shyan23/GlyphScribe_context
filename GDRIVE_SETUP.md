# Google Drive Setup Guide

This guide will help you set up Google Drive integration for GlyphScribe to save disk space by uploading images directly to Google Drive.

## Prerequisites

- Google Account (you already have Google One subscription ✓)
- Google Cloud Console access
- Docker and Docker Compose installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "GlyphScribe" (or any name you prefer)
4. Click "Create"

## Step 2: Enable Google Drive API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

## Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"

3. **Configure OAuth consent screen** (if prompted):
   - Click "Configure Consent Screen"
   - Choose "External" (unless you have a Google Workspace)
   - Fill in:
     - App name: `GlyphScribe`
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add your email as a test user
   - Click "Save and Continue"

4. **Create OAuth Client ID**:
   - Application type: "Desktop app"
   - Name: "GlyphScribe Desktop"
   - Click "Create"

5. **Download credentials**:
   - A dialog will appear with your Client ID and Client Secret
   - Click "Download JSON"
   - Save this file

## Step 4: Place Credentials File

1. Rename the downloaded file to `credentials.json`
2. Move it to your GlyphScribe project directory:
   ```bash
   mv ~/Downloads/client_secret_*.json /home/shyan/Desktop/Research/GRAD-HTR/GlyphScribe/credentials.json
   ```

## Step 5: First-Time Authentication

The first time you run the Docker container, PyDrive2 will need to authenticate:

1. Run the generator:
   ```bash
   ./run.sh batch
   ```

2. **If running in Docker**, you'll see a message with a URL:
   ```
   Go to the following link in your browser:
   https://accounts.google.com/o/oauth2/auth?...
   ```

3. **Copy the entire URL** and paste it in your web browser

4. **Sign in** with your Google account

5. **Grant permissions** when prompted:
   - Click "Continue" if you see a warning about unverified app
   - Click "Allow" to grant GlyphScribe access to Google Drive

6. **Copy the authorization code** from the browser

7. **Paste it back** into the Docker terminal when prompted:
   ```
   Enter verification code: [paste code here]
   ```

8. Authentication is now complete! The credentials are saved for future runs.

## Step 6: Run the Generators

### Upload to Google Drive (Recommended - Saves Space)
```bash
# Make script executable (first time only)
chmod +x run.sh

# Run both generators
./run.sh both

# Or run individually
./run.sh batch        # Multi-line images only
./run.sh single       # Single-word images only
```

### Save Locally (if needed for testing)
```bash
./run.sh local-both
./run.sh local-batch
./run.sh local-single
```

## Folder Structure in Google Drive

After running, your Google Drive will have:
```
Google Drive/
└── GlyphScribe_Output/
    ├── batch/
    │   ├── images/
    │   │   ├── image_000001.png
    │   │   ├── image_000002.png
    │   │   └── ...
    │   └── json/
    │       ├── image_000001.json
    │       ├── image_000002.json
    │       └── ...
    └── single_words/
        ├── images/
        │   └── ...
        └── json/
            └── ...
```

## Troubleshooting

### "credentials.json not found"
Make sure the file is in the project root directory:
```bash
ls -la /home/shyan/Desktop/Research/GRAD-HTR/GlyphScribe/credentials.json
```

### "Access denied" or "Invalid credentials"
1. Delete the credentials.json file
2. Go back to Google Cloud Console
3. Create new OAuth credentials
4. Download and replace credentials.json

### Authentication fails in Docker
If the browser-based auth doesn't work:
1. Run authentication locally first:
   ```bash
   python3 -c "from gdrive_uploader import GDriveUploader; GDriveUploader()"
   ```
2. This will create authentication tokens in `gdrive_token/`
3. Then run Docker normally

### "Quota exceeded" errors
Google Drive API has quotas:
- Free tier: 1 billion queries per day
- This should be more than enough for image generation
- If you hit limits, wait 24 hours or request quota increase

### Upload is slow
- Uploading to Google Drive is network-dependent
- Large batches may take time
- Consider reducing `NUM_IMAGES` in the scripts for testing

## Configuration

### Change Google Drive folder name
Edit `generate_batch_gdrive.py` or `single_word_img_gdrive.py`:
```python
GDRIVE_FOLDER = "MyCustomFolder"  # Change this
```

### Number of images to generate
In `generate_batch_gdrive.py`:
```python
NUM_IMAGES = 10  # Change this number
```

In `single_word_img_gdrive.py`:
```python
NUM_IMAGES = 10  # Change this number
```

## Security Notes

- **credentials.json** contains sensitive OAuth information
- The file is added to `.gitignore` (never commit it!)
- The credentials only grant access to your Google Drive
- You can revoke access anytime from Google Account settings
- Tokens are stored in `gdrive_token/` (also in `.gitignore`)

## Benefits of Google Drive Mode

✅ **Saves disk space**: No local storage needed
✅ **Automatic backup**: Files are in the cloud
✅ **Accessible anywhere**: Access from any device
✅ **Organized**: Automatic folder structure
✅ **Free storage**: Up to 15GB free (or more with Google One)

## Switching Between Modes

You can use both modes:
- Google Drive for production runs (saves space)
- Local storage for quick tests and debugging

The Docker setup supports both!
