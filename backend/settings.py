#for render postgresql database
import dj_database_url


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent




# importing module to load env file from django backend folder
import os
# from dotenv import load_dotenv
# load_dotenv()  #will load env variables


# uploading env variables using os.environ instead of os.getenv
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
DJANGO_SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG_STATUS = os.environ.get('DEBUG_STATUS')
BACKEND_ALLOWED_HOSTS = os.environ.get('BACKEND_ALLOWED_HOSTS')
POSTGRESQL_URL = os.environ.get('INTERNAL_POSTGRESQL_PATH')
BACKEND_CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_STATUS.lower() == 'true'

# ALLOWED_HOSTS = ['localhost','127.0.0.1']
ALLOWED_HOSTS = BACKEND_ALLOWED_HOSTS.split(' ')

SITE_ID = 3   #ALWAYS CHECK FOR CURRENT SITE ID on DJANGO ADMIN INTEFACE WHILE CLICKING ON THE SITE IN URL



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core','summaries', # apps
    'rest_framework',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'corsheaders',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist'


]



AUTH_USER_MODEL = 'core.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'CLIENT_ID': GOOGLE_CLIENT_ID,
        'SECRET': GOOGLE_CLIENT_SECRET,
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',  # let access refresh token so it escapes users from re-login.
        },
    },
}





MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS middleware should be first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # added middleware for render deploy
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',

]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Replace the SQLite DATABASES configuration with PostgreSQL:
DATABASES['default'] = dj_database_url.parse(POSTGRESQL_URL)

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# for render deploy
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'







# Below are the settings made by me

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)


# Simple JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30), # set it to minutes = 60
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # set it to days = 7
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


#Redirect URLs
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email verification
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True

# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:5173','http://127.0.0.1:8000'  # Add your React app's origin
# ]

CORS_ALLOWED_ORIGINS = BACKEND_CORS_ALLOWED_ORIGINS.split(' ')

CORS_ALLOW_CREDENTIALS = True  # If your requests include credentials (e.g., cookies)
# CORS_ALLOW_ALL_ORIGINS = True  #not for production level (only for development time)

SOCIALACCOUNT_LOGIN_ON_GET = True
