from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

# for registering user
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny,IsAuthenticated

# for check user details when logging in
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken 
from rest_framework.views import APIView


class CheckAuth(APIView):

    def get(self, request):
        
        return Response({"data": 'Authenticated'}, status=status.HTTP_200_OK)
  



# For google authentication
@permission_classes([AllowAny])
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
  
        # Assuming 'user' is now authenticated
        user = self.request.user
        if user.is_authenticated:
            # Generate JWT tokens as defualt way our view will send Oauth tokens
            refresh = RefreshToken.for_user(user)
            response.data['access'] = str(refresh.access_token)
            response.data['refresh'] = str(refresh)
        
            # Add user data to response
            response.data['user'] = {   
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        
        return response



# For registering user
User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    """
    Register a new user.
    """

    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')

    if not all([email, password]): 
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email is already registered. Try logging in."}, status=status.HTTP_400_BAD_REQUEST)

    # Generate a unique username based on first and last name
    username = f"{first_name.lower()}_{last_name.lower()}"
    if User.objects.filter(username=username).exists():
        # If the username already exists, append a number
        i = 1
        while User.objects.filter(username=f"{username}{i}").exists():
            i += 1
        username = f"{username}{i}"

    user = User(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=make_password(password),  # Ensure the password is hashed
    )

    user.save()

    return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):



    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'Please provide email and password.'}, status=status.HTTP_400_BAD_REQUEST)

    # Attempt to authenticate the user

    try:
        user_details = User.objects.get(email=email)
        username = user_details.username
    except User.DoesNotExist:
        return Response({'detail': 'Invalid credentials. Please try again.'}, status=status.HTTP_401_UNAUTHORIZED)


    user = authenticate(request, username=username, password=password)


    if user is not None:
        # Log the user in 
        login(request, user)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'detail': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            
        }, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid credentials. Please try again.'}, status=status.HTTP_401_UNAUTHORIZED)
    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get("refreshToken")
            if refresh_token:
                print('refresh token received from frontend for logging out')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=200)   # forcing the view to log out anyhow
        
