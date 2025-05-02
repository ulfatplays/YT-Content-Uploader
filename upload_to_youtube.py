import os
import json
import mimetypes
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# SCOPES for YouTube & Drive
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/drive.readonly']

# Authenticate
def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file('oauth2.json', SCOPES)
    creds = flow.run_console()
    return build('youtube', 'v3', credentials=creds)

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("drive_creds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("drive_creds.txt")
    return GoogleDrive(gauth)

# Download from Drive
def download_from_drive(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        fname = file['title']
        if fname.startswith("YTVideo") or fname.startswith("YTShorts"):
            file.GetContentFile(fname)
            print(f"Downloaded: {fname}")
            return fname
    return None

# Upload to YouTube
def upload_to_youtube(youtube, file_name):
    title = "Amazing PUBG Gameplay!" if "Shorts" not in file_name else "Crazy PUBG Short!"
    description = "Watch thrilling moments from PUBG battles. Like & Subscribe!"
    category_id = "20"  # Gaming
    privacy = "public"

    media = MediaFileUpload(file_name, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category_id
            },
            "status": {"privacyStatus": privacy}
        },
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")
    print("Upload complete!")

# Main
if __name__ == '__main__':
    drive = authenticate_drive()
    file_name = download_from_drive(drive, os.environ["GOOGLE_DRIVE_FOLDER_ID"])
    if file_name:
        youtube = authenticate_youtube()
        upload_to_youtube(youtube, file_name)
    else:
        print("No matching video file found in Drive folder.")
