from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re


transcript_file_path = r"transcript.txt"


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




def get_transcript(video_id):
    """
    Fetches transcript from YouTube video using its video ID.
    Tries to get the transcript in English first, then in any available language.
    """
    try:
        transcript = None

        try:
            # Attempt to fetch the transcript in English.
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            print("English transcript not found. Attempting to fetch in any available language...")
            # If English transcript is not found, attempt to list and fetch any available transcript.
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for available_transcript in transcript_list:
                transcript = available_transcript.fetch()
                break  # Fetch the first available transcript.

        # Check if the fetched transcript is empty or None.
        if not transcript:
            raise ValueError("Transcript is empty or not available.")

        # Write the transcript to a file.
        with open(transcript_file_path, 'w', encoding='utf-8') as file:
            file.write(str(transcript))

        return transcript

    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return 'N/A'
    
    except NoTranscriptFound:
        print("No transcript could be found for the given video ID.")
        return 'No transcript found'
    
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return 'No available transcript'
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 'Error'



def format_timestamp(seconds):
    """
    Converts seconds to a min:sec format, rounding down to the nearest minute.
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def group_transcript_by_time(transcript, batch_time=300):
    """
    Groups transcript into batches of specified time (in seconds).
    """
    batches = []
    current_batch = []
    current_batch_start = 0
    current_batch_end = 0

    for entry in transcript:
        start_time = entry['start']
        duration = entry['duration']
        end_time = start_time + duration
        text = entry['text']
        
        # If this entry starts a new batch
        if start_time >= current_batch_end:
            # Save the previous batch if it exists
            if current_batch:
                batches.append({
                    'start_time': current_batch_start,
                    'end_time': current_batch_end,
                    'text': ' '.join(current_batch)
                })
            # Start a new batch
            current_batch = [text]
            current_batch_start = start_time
            current_batch_end = start_time + batch_time
        else:
            # Add to the current batch
            current_batch.append(text)
        
        # Update the end time of the current batch if necessary
        if end_time > current_batch_end:
            current_batch_end = min(end_time, current_batch_start + batch_time)

    # Add the last batch if it exists
    if current_batch:
        batches.append({
            'start_time': current_batch_start,
            'end_time': current_batch_end,
            'text': ' '.join(current_batch)
        })
  
    return batches

def save_transcript_to_file(transcript_batches, filename=transcript_file_path):
    with open(filename, 'w', encoding='utf-8') as file:
        for i, batch in enumerate(transcript_batches):
            start_time = format_timestamp(batch['start_time'])
            end_time = format_timestamp(batch['end_time'])  # Removed the "+ 1"
            file.write(f"{start_time} to {end_time} - {batch['text']}\n\n")

def process_transcript(video_id):
    transcript = get_transcript(video_id)
    if transcript == 'N/A' or transcript == 'error':
        print('No transcript found')
        return None
  
    transcript_batches = group_transcript_by_time(transcript, batch_time=300)  # 300 seconds = 5 minutes
    save_transcript_to_file(transcript_batches)

    
# if __name__ == "__main__":
#     # Replace with your actual video URL or video ID.
#     url = input('Enter YouTube URL here: ')
#     video_id = extract_youtube_video_id(url)
#     if video_id:
#         process_transcript(video_id)
#     else:
#         print("Invalid URL or unable to extract video ID.")

