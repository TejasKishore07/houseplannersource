To get your Django frontend working on Render with the provided settings.py, you need to configure it for production. This primarily involves setting DEBUG=False, using environment variables, configuring WhiteNoise to serve static files, and setting the STATIC_ROOT.
Here is the complete, corrected settings.py file, incorporating best practices for a Render deployment:
"""
Django settings for smart_house_planner project.
"""

from pathlib import Path
import os
import dj_database_url # We'll need this for production database

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(_file_).resolve().parent.parent

# --------------------------------------------------------------------------
# CORE SECURITY & ENVIRONMENT
# --------------------------------------------------------------------------

# SECURITY WARNING: keep the secret key used in production secret!
# Use an environment variable for the secret key in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-smart-house-planner-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
# Set DEBUG based on environment variable (e.g., set DEBUG=False on Render)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Allow the Render hostname
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# --------------------------------------------------------------------------
# APPLICATION DEFINITION
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    # NOTE: You'll need to install WhiteNoise: pip install whitenoise
    # 'whitenoise.runserver_nostatic', # Optional: To prevent collectstatic from running in DEV
    'planner',
]

MIDDLEWARE = [
    # WhiteNoise must be placed directly after SecurityMiddleware for static files
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # 👈 ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_house_planner.urls'

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

WSGI_APPLICATION = 'smart_house_planner.wsgi.application'

# --------------------------------------------------------------------------
# DATABASE
# --------------------------------------------------------------------------

# Use environment variable for production database (PostgreSQL on Render)
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --------------------------------------------------------------------------
# STATIC FILES (CSS, JavaScript, Images) & MEDIA FILES
# --------------------------------------------------------------------------

# The URL for serving static files
STATIC_URL = 'static/'

# Directories where Django will look for static files in development
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# The directory where collectstatic will gather all static files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # 👈 CRUCIAL

# WhiteNoise storage to compress and cache static files
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # CompressedManifestStaticFilesStorage for WhiteNoise
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------------------------------
# OTHER SETTINGS
# --------------------------------------------------------------------------

# Password validation (No changes needed)
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

Action Plan to Deploy on Render
After updating this file, you must complete the following steps:
 * Install Dependencies: Install the necessary packages for production:
   pip install whitenoise dj-database-url gunicorn
pip freeze > requirements.txt

 * Commit and Push: Commit the changes to your settings.py and requirements.txt.
 * Update Render Build Command: Ensure your Render service's Build Command includes collectstatic:
   pip install -r requirements.txt
python manage.py collectstatic --no-input  # Gathers static files
python manage.py migrate

 * Set Environment Variables: In your Render dashboard, set the following environment variables for the service:
   * DEBUG: False
   * ALLOWED_HOSTS: your-app-name.onrender.com (and any other domain)
   * SECRET_KEY: A long, random string
   * DATABASE_URL: The external connection URL from your Render PostgreSQL database.
Once you push your code, Render will redeploy, run collectstatic to prepare the frontend files, and WhiteNoise will correctly serve them.
