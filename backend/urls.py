from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # for google oauth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # will not be using this api endpoint as we are using the RefreshToken in views.py to generate access and refresh token on login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # this will be used to refresh access and refresh tokens
    path('auth/',include('core.urls')), # for user login, logout, social oauth and registration
    path('api/',include('summaries.urls')), #for summaries app data fetching and uploading,
]




