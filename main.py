import os
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from upload_to_youtube import upload_video

FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def get_latest_file(drive, prefix):
    file_list = drive.ListFile({
        'q': f"'{FOLDER_ID}' in parents and trashed=false"
    }).GetList()
    
    target_files = [f for f in file_list if f['title'].startswith(prefix)]
    if not target_files:
        return None

    # Sort by createdDate, latest first
    sorted_files = sorted(target_files, key=lambda x: x['createdDate'], reverse=True)
    latest = sorted_files[0]

    file_path = f"/tmp/{latest['title']}"
    latest.GetContentFile(file_path)
    return file_path

def main():
    drive = authenticate_drive()

    # Check for Shorts first
    video_file = get_latest_file(drive, 'YTShorts')
    is_short = True

    # If no Shorts found, check for long video
    if not video_file:
        video_file = get_latest_file(drive, 'YTVideo')
        is_short = False

    if not video_file:
        print("No video found to upload.")
        return

    # Check if there's a thumbnail
    thumbnail = get_latest_file(drive, 'YTThumbnail')

    # Generate basic title
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    title = f"{'Short' if is_short else 'Video'} uploaded at {timestamp}"
    description = f"Auto-uploaded content on {timestamp} via automation."

    # Call uploader
    upload_video(video_file, title, description, thumbnail)

if __name__ == "__main__":
    main()
