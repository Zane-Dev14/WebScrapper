import requests
from bs4 import BeautifulSoup
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import re
# Replace with the URL of the website with download buttons
url = "https://www.keralanotes.com/2021/12/KTU-S3-CSE-Notes-Syllabus-Qbank-Textbook.html#"

download_button_class = 'buttonDownload'  # Replace with the correct class name
print("Script started")

# Specify the directory where you want to save the downloaded files
 # Change this to your desired directory

try:
    # Send an HTTP GET request to the website
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    soup = BeautifulSoup(response.text, 'html.parser')
    all_links = soup.select('div.aaaa a.hello')

    # Filter out the scheme links based on link text or URL pattern
    note_links = []
    for link in all_links:
        link_text = link.get_text().strip()  # Get the text within the link
        link_url = link['href']  # Get the link URL

        # Exclude links that have certain keywords (e.g., "Syllabus")
        if "Notes" in link_url:
            note_links.append(link_url)

    # Print the extracted note links
    for link in note_links:
        # print(link)
        response = requests.get(link)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        subname=" ".join(link.split("/")[-1].split("-")[2:-2])
        
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

            # Decode the URL (if needed
            download_url = urllib.parse.unquote(download_url)
            # print("Processing", download_url)

            if is_google_drive_link(download_url):
                # Extract the file ID from the download URL
                file_id = download_url.split('/')[-2]
                # print("File ID is ",file_id)
                # Construct the direct download link
                direct_download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
                # print("Downliad is ",direct_download_link )
                file = drive_service.files().get(fileId=file_id).execute()
                filename = file['name']
                try:
                    os.mkdir("/home/coding/study/pdf/"+subname)
                except:
                    print()
                # Get the file name from the link
                # filename = download_url.split('/')[-2]
                # content_disposition = response.headers.get("Content-Disposition")
                # if content_disposition:
                #     match = re.search('filename="(.+)"', content_disposition)
                #     if match:
                #         filename = match.group(1)
                #     else:
                #         filename = "downloaded_file.bin"  # Default filename if not found in the header
                # else:
                #     filename = "downloaded_file.bin" 
                download_directory = "/home/coding/study/pdf/"+subname 
                # print(download_directory)
                c=1

                local_file_path = os.path.join(download_directory, filename)  # Specify local file path
                
                # print("Downloading", filename)

                # Download the file and save it locally
                with open(local_file_path, 'wb') as f:
                    response = requests.get(direct_download_link)
                    response.raise_for_status()
                    f.write(response.content)
                    c+=1

                print(f"Downloaded: {filename} to {local_file_path}")

    print("Script completed")

except Exception as e:
    print("Error:", str(e))
