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

# Authenticate YouTube manually (for standalone runs, not used in automation)
def authenticate_youtube():
    flow = InstalledAppFlow.from_client_secrets_file('oauth2.json', SCOPES)
    creds = flow.run_console()
    return build('youtube', 'v3', credentials=creds)

# Authenticate Google Drive
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("drive_creds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    gauth.SaveCredentialsFile("drive_creds.txt")
    return GoogleDrive(gauth)

# Download first matching video file from Drive folder
def download_from_drive(drive, folder_id):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        fname = file['title']
        if fname.startswith("YTVideo") or fname.startswith("YTShorts"):
            file.GetContentFile(fname)
            print(f"Downloaded: {fname}")
            return fname
    return None

# Main YouTube uploader for automation
def upload_video(file_path, title, description, category_id, credentials):
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
        },
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/*")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")
    print("Upload successful. Video ID:", response["id"])
    return response

# Optional manual test block
if __name__ == '__main__':
    drive = authenticate_drive()
    file_name = download_from_drive(drive, os.environ["GOOGLE_DRIVE_FOLDER_ID"])
    if file_name:
        youtube = authenticate_youtube()
        upload_video(
            file_path=file_name,
            title="Amazing PUBG Gameplay!",
            description="Watch thrilling moments from PUBG battles. Like & Subscribe!",
            category_id="20",
            credentials=youtube._http.credentials
        )
    else:
        print("No matching video file found in Drive folder.")
