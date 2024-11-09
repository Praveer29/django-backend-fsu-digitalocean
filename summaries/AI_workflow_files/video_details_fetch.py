import os
from googleapiclient.discovery import build


video_details_file_path = r"video_details.txt"

# Function to fetch video details
def fetch_video_details(video_id, api_key):
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Request video details
    request = youtube.videos().list(
        part="snippet,contentDetails",
        id=video_id
    )
    response = request.execute()

    # Parse the response
    if 'items' in response and len(response['items']) > 0:
        video_info = response['items'][0]['snippet']
        # statistics = response['items'][0]['statistics']
        content_details = response['items'][0]['contentDetails']

        # Format the details
        video_details = {
            "Title": video_info.get('title'),
            "Description": video_info.get('description'),
            "Published At": video_info.get('publishedAt'),
            "Channel Title": video_info.get('channelTitle'),
            "Tags": video_info.get('tags', []),
            "Duration": content_details.get('duration')
        }

        # Save details to a file
        
        file_path = video_details_file_path

        with open(file_path, "w",encoding='utf-8') as file:
            for key, value in video_details.items():
                file.write(f"{key}: {value}\n")

        print("Video details saved to video_details.txt")
    else:
        print("No video details found for the provided video ID.")

# Replace with your YouTube Data API key and video ID

import os
from dotenv import load_dotenv
import re

load_dotenv()

api_key = os.getenv('YOUTUBE_DATA_API_KEY')



def extract_youtube_video_id(url):

    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:\S+)?',
        r'(?:embed\/|v\/|youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    print('error at extract_youtube_video_id')
    return None

# url = ''
# video_id = extract_youtube_video_id(url)

# # Fetch and save the video details
# fetch_video_details(video_id, api_key)                                                  







