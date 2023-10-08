import requests
from bs4 import BeautifulSoup
import urllib.parse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import time
import multiprocessing
time1=time.time()
# Replace with the URL of the website with download buttons
url = "https://www.keralanotes.com/2021/12/KTU-S3-CSE-Notes-Syllabus-Qbank-Textbook.html#"
download_button_class = 'buttonDownload'  # Replace with the correct class name
print("Script started")

# Specify the directory where you want to save the downloaded files
# Change this to your desired directory
download_directory = "/home/coding/study/pdf"  # Change this to your desired directory

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

    # Initialize Google Drive API
    credentials = service_account.Credentials.from_service_account_file('credits.json', scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)

    def is_google_drive_link(link):
        return 'drive.google.com' in link

    # Batch download size (number of files to download concurrently)
    batch_size = 4

    # Split the note_links into batches
    batches = [note_links[i:i+batch_size] for i in range(0, len(note_links), batch_size)]

    # Function to download a batch of files
    def download_batch(batch):
        for link in batch:
            response = requests.get(link)
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            subname = " ".join(link.split("/")[-1].split("-")[2:-2])

            # Find all download buttons or links
            download_links = soup.find_all('a', class_=download_button_class)

            # Filter and download files
            for link in download_links:
                # Extract the download URL
                download_url = link.get('href')

                # Decode the URL (if needed)
                download_url = urllib.parse.unquote(download_url)

                if is_google_drive_link(download_url):
                    # Extract the file ID from the download URL
                    file_id = download_url.split('/')[-2]
                    # print(file_id)
                    # Get the file metadata to obtain the filename
                    file = drive_service.files().get(fileId=file_id).execute()
                    filename = file['name']
                    # print(filename)

                    # Create a subdirectory for the batch
                    try:
                        os.mkdir("/home/coding/study/pdf/"+subname)
                    except FileExistsError:
                        pass
                    time.sleep(5)
                    # Specify the local file path
                    local_file_path = os.path.join(download_directory, subname, " ".join(filename.split()[0:3]) + ".pdf")

                    # Download the file and save it locally
# Download the file and save it locally
                    request = drive_service.files().get_media(fileId=file_id)
                    # print(file_id)
                    with open(local_file_path, 'wb') as f:
                        downloader = MediaIoBaseDownload(f, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print(f"Download {int(status.progress() * 100)}%")



                    print(f"Downloaded: {filename} to {local_file_path}")

    # Create a pool of worker processes for concurrent batch downloads
    pool = multiprocessing.Pool(processes=len(batches))

    # Use the pool to download batches concurrently
    pool.map(download_batch, batches)

    # Close the pool of worker processes
    pool.close()
    pool.join()

    print("Script completed")
    print("Program took",time.time()-time1," Seconds")
except Exception as e:
    print("Error:", str(e))
