import requests
from bs4 import BeautifulSoup
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os

# Replace with the URL of the website with download buttons
url = "https://www.keralanotes.com/2021/12/KTU-S3-Discrete-Mathematical-Structure-Notes.html#"
download_button_class = 'buttonDownload'  # Replace with the correct class name
print("Script started")

# Specify the directory where you want to save the downloaded files
download_directory = "/home/coding/study/pdf"  # Change this to your desired directory

try:
    # Send an HTTP GET request to the website
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all download buttons or links
    download_links = soup.find_all('a', class_=download_button_class)

    # Initialize Google Drive API
    credentials = service_account.Credentials.from_service_account_file('credits.json', scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)

    def is_google_drive_link(link):
        return 'drive.google.com' in link

    # Filter and download files
    for link in download_links:
        # Extract the download URL
        download_url = link.get('href')

        # Decode the URL (if needed)
        download_url = urllib.parse.unquote(download_url)
        print("Processing", download_url)

        if is_google_drive_link(download_url):
            # Extract the file ID from the download URL
            file_id = download_url.split('/')[-2]

            # Construct the direct download link
            direct_download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # Get the file name from the link
            filename = download_url.split('/')[-1]
            local_file_path = os.path.join(download_directory, filename)  # Specify local file path

            print("Downloading", filename)

            # Download the file and save it locally
            with open(local_file_path, 'wb') as f:
                response = requests.get(direct_download_link)
                response.raise_for_status()
                f.write(response.content)

            print(f"Downloaded: {filename} to {local_file_path}")

    print("Script completed")

except Exception as e:
    print("Error:", str(e))
