
from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('google/', views.GoogleLogin.as_view(), name='google_login'),
    path('check-auth/', views.CheckAuth.as_view(), name='check_auth'),
]

# logout and google oauth view are class based and register and login view are function based

