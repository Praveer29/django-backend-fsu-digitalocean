import tiktoken
from langchain_groq import ChatGroq
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List, Dict
from datetime import datetime
import re
from dotenv import load_dotenv
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('summary_generator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TimestampEntry(BaseModel):
    start_time: str = Field(description="Start time of the segment")
    end_time: str = Field(description="End time of the segment")
    title: str = Field(description="Short title for the segment")
    description: str = Field(description="Detailed description of the segment")

    @validator('start_time', 'end_time')
    def validate_timestamp_format(cls, v):
        # Ensure timestamp is in format HH:MM:SS
        pattern = r'^\d{1,2}:\d{2}:\d{2}$'
        if not re.match(pattern, v):
            raise ValueError(f'Invalid timestamp format: {v}. Must be in HH:MM:SS format')
        return v

class OutputSchema(BaseModel):
    summary: str = Field(
        description="Comprehensive summary of the video content including overview and detailed explanation"
    )
    timestamps: List[TimestampEntry] = Field(
        description="List of timestamp entries with their descriptions"
    )

    @validator('timestamps')
    def validate_timestamps_length(cls, v):
        if len(v) > 25:
            raise ValueError('Maximum 25 timestamps allowed')
        return v

def count_tokens(text: str) -> int:
    try:
        tokenizer = tiktoken.get_encoding("cl100k_base")
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        logging.error(f"Error counting tokens: {str(e)}")
        raise

def open_file(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise

def format_timestamps(timestamps_list: List[TimestampEntry]) -> str:
    formatted_timestamps = []
    for entry in timestamps_list:
        formatted_entry = (
            f"{entry.start_time} to {entry.end_time} - {entry.title} - {entry.description}"
        )
        formatted_timestamps.append(formatted_entry)
    return "\n".join(formatted_timestamps)

def summarize():
    try:
        # Load environment variables
        load_dotenv()
        logging.info("Starting video summary generation")

        # Initialize the model
        model = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.2,
            max_tokens=3000
        )

        # Load input files
        timestamps = open_file(r"major_topics.txt")
        description = open_file(r"video_details.txt")

        # Log token counts
        logging.info(f"Timestamp token count: {count_tokens(timestamps)}")
        logging.info(f"Description token count: {count_tokens(description)}")

        # Updated prompt template
        prompt_template = """
        Analyze the following YouTube video transcript and timestamps:

        TIMESTAMPS (are provided in the MM:SS format, which highlights important topic from each batch timestamp):
        {text}

        VIDEO DESCRIPTION:
        {desc}

        Generate a response in the following format:

        1. Create a comprehensive summary that includes:
           - A brief overview of the main topic
           - Explanation of key terminology
           - How different concepts interact
           - Key takeaways and insights

        2. Generate timestamps in proper sequence the following format:
           HH:MM:SS to HH:MM:SS - [Short Title] - [Detailed Description]

        Requirements:
        - Cover the whole video with their timestamps.
        - Use HH:MM:SS format for all timestamps
        - If transcript is unavailable, return: "Timestamps not available due to missing transcript"
        - Highlight key terms in descriptions only if they are in an informative language

        Ensure all timestamps are properly formatted and descriptions are informative and relevant.
        """

        # Format and validate prompt
        prompt = prompt_template.format(text=timestamps, desc=description)
        prompt_token_count = count_tokens(prompt)
        logging.info(f"Prompt token count: {prompt_token_count}")

        # Generate response with structured output
        model_with_schema = model.with_structured_output(OutputSchema)
        response = model_with_schema.invoke(prompt)
        logging.info('Summary generated successfully')

        # Format output as dictionary
        output_dict = {
            'summary': response.summary,
            'timestamps': format_timestamps(response.timestamps)
        }

        # Save output
        output_path = r'summary.json'
        import json
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(output_dict, file, indent=2, ensure_ascii=False)
        
        logging.info(f'Summary saved to {output_path}')
        return output_dict

    except Exception as e:
        logging.error(f"Error in summary generation: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        result = summarize()
        print("Summary generated successfully!")
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        sys.exit(1)



