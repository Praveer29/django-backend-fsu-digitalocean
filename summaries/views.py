

# ai model view
from dotenv import load_dotenv
import os

load_dotenv()
yt_data_api_key = os.getenv('YOUTUBE_DATA_API_KEY')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .serializers import SummarySerializer
from rest_framework.permissions import IsAuthenticated
import logging
import os
from .models import Summary


# Import your AI workflow modules
from .AI_workflow_files.yt_transcript import extract_youtube_video_id, process_transcript
from .AI_workflow_files.video_details_fetch import fetch_video_details
from .AI_workflow_files.major_topics import extracting_major_topics
from .AI_workflow_files.yt_summarizer import summarize


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_view.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GenerateYouTubeSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Extract data from request
            youtube_url = request.data.get('youtube_url')

            if not youtube_url:
                return Response(
                    {'error': 'YouTube URL is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract video ID
            video_id = extract_youtube_video_id(youtube_url)
            if not video_id:
                return Response(
                    {'error': 'Invalid YouTube URL'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process video and generate summary
            process_transcript(video_id)
            with open('transcript.txt', 'r', encoding='utf-8') as file:
                transcript_result = file.read()
            if transcript_result is None:
                return Response(
                    {'error': 'Failed to fetch video transcript'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_key = os.getenv('YOUTUBE_DATA_API_KEY')
            if not api_key:
                return Response(
                    {'error': 'YouTube API key not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            fetch_video_details(video_id, api_key)
            extracting_major_topics()
            summary_result = summarize()
            
            if not summary_result:
                return Response(
                    {'error': 'Failed to generate summary'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Read the transcript
            try:
                with open(r'transcript.txt', 'r', encoding='utf-8') as file:
                    youtube_transcript = file.read()
            except FileNotFoundError:
                youtube_transcript = "Transcript processing failed"

            # Create summary object
            summary_data = {
                'user': request.user,
                'youtube_url': youtube_url,
                'summary': summary_result['summary'],
                'timestamps': summary_result['timestamps'],
                'youtube_transcript': youtube_transcript
            }

            serializer = SummarySerializer(data=summary_data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error in GenerateYouTubeSummaryView: {str(e)}")
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """Endpoint to retrieve user's summaries"""
        try:
            summaries = Summary.objects.filter(user=request.user).order_by('-date_generated')
            serializer = SummarySerializer(summaries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in retrieving summaries: {str(e)}")
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



from rest_framework.decorators import api_view, permission_classes
from .serializers import FeedbackSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    serializer = FeedbackSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Feedback submitted successfully'}, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retrieve user profile information"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update user profile information"""
        try:
            serializer = UserProfileSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )