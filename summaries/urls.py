from django.urls import path
from .views import GenerateYouTubeSummaryView,submit_feedback,UserProfileView

urlpatterns = [
    path('summaries/', GenerateYouTubeSummaryView.as_view(), name='summaries'),
    path('feedback/', submit_feedback, name='feedback'),
    path('profile/', UserProfileView.as_view(), name='profile'),


]