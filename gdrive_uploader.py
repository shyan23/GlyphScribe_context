"""
Google Drive Uploader Module
Handles authentication and file uploads to Google Drive using PyDrive2
"""
import os
import json
import io
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from PIL import Image


class GDriveUploader:
    """Handle Google Drive uploads with folder organization"""

    def __init__(self, credentials_file="credentials.json", folder_name="GlyphScribe_Output"):
        """
        Initialize Google Drive uploader

        Args:
            credentials_file: Path to OAuth credentials JSON file
            folder_name: Root folder name in Google Drive
        """
        self.credentials_file = credentials_file
        self.root_folder_name = folder_name
        self.drive = None
        self.root_folder_id = None
        self.folder_cache = {}  # Cache folder IDs to avoid repeated lookups

        self._authenticate()
        self._setup_root_folder()

    def _authenticate(self):
        """Authenticate with Google Drive"""
        gauth = GoogleAuth()

        # Set the path to client secrets (your credentials.json)
        gauth.settings['client_config_file'] = 'credentials.json'

        # Try to load saved credentials from a separate file
        saved_creds_file = 'gdrive_token.json'
        gauth.LoadCredentialsFile(saved_creds_file)

        if gauth.credentials is None:
            # Authenticate if credentials don't exist
            print("First-time authentication required...")
            print("A browser window will open for Google login.")
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh if expired
            print("Refreshing expired token...")
            gauth.Refresh()
        else:
            # Initialize with saved credentials
            gauth.Authorize()

        # Save credentials for next run
        gauth.SaveCredentialsFile(saved_creds_file)

        self.drive = GoogleDrive(gauth)
        print("✓ Authenticated with Google Drive")

    def _setup_root_folder(self):
        """Create or get root folder in Google Drive"""
        # Check if folder already exists
        file_list = self.drive.ListFile({
            'q': f"title='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        }).GetList()

        if file_list:
            self.root_folder_id = file_list[0]['id']
            print(f"✓ Using existing folder: {self.root_folder_name}")
        else:
            # Create new folder
            folder = self.drive.CreateFile({
                'title': self.root_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            })
            folder.Upload()
            self.root_folder_id = folder['id']
            print(f"✓ Created new folder: {self.root_folder_name}")

        self.folder_cache[self.root_folder_name] = self.root_folder_id

    def _get_or_create_folder(self, folder_path, parent_id=None):
        """
        Get or create a folder in Google Drive

        Args:
            folder_path: Folder path (e.g., "batch/images")
            parent_id: Parent folder ID (default: root folder)

        Returns:
            Folder ID
        """
        if parent_id is None:
            parent_id = self.root_folder_id

        # Check cache
        cache_key = f"{parent_id}/{folder_path}"
        if cache_key in self.folder_cache:
            return self.folder_cache[cache_key]

        # Split path into parts
        parts = folder_path.split('/')
        current_parent = parent_id

        for part in parts:
            # Check if folder exists
            file_list = self.drive.ListFile({
                'q': f"title='{part}' and '{current_parent}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            }).GetList()

            if file_list:
                current_parent = file_list[0]['id']
            else:
                # Create folder
                folder = self.drive.CreateFile({
                    'title': part,
                    'parents': [{'id': current_parent}],
                    'mimeType': 'application/vnd.google-apps.folder'
                })
                folder.Upload()
                current_parent = folder['id']

        # Cache the result
        self.folder_cache[cache_key] = current_parent
        return current_parent

    def upload_image(self, image, filename, folder_path="images"):
        """
        Upload PIL Image directly to Google Drive

        Args:
            image: PIL Image object
            filename: Name of the file (e.g., "image_000001.png")
            folder_path: Subfolder path within root (e.g., "batch/images")

        Returns:
            Google Drive file ID
        """
        # Get or create folder
        folder_id = self._get_or_create_folder(folder_path)

        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Create file in Google Drive
        file = self.drive.CreateFile({
            'title': filename,
            'parents': [{'id': folder_id}]
        })

        # Set content from bytes
        file.content = img_byte_arr
        file.Upload()

        return file['id']

    def upload_json(self, json_data, filename, folder_path="json"):
        """
        Upload JSON data directly to Google Drive

        Args:
            json_data: Dictionary to convert to JSON
            filename: Name of the file (e.g., "image_000001.json")
            folder_path: Subfolder path within root (e.g., "batch/json")

        Returns:
            Google Drive file ID
        """
        # Get or create folder
        folder_id = self._get_or_create_folder(folder_path)

        # Convert dict to JSON string
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        # Create file in Google Drive
        file = self.drive.CreateFile({
            'title': filename,
            'parents': [{'id': folder_id}],
            'mimeType': 'application/json'
        })

        # Set content from string
        file.SetContentString(json_str)
        file.Upload()

        return file['id']

    def get_folder_url(self):
        """Get the URL to the root folder in Google Drive"""
        return f"https://drive.google.com/drive/folders/{self.root_folder_id}"


# Convenience function for easy import
def create_uploader(folder_name="GlyphScribe_Output"):
    """Create and return a GDriveUploader instance"""
    return GDriveUploader(folder_name=folder_name)
