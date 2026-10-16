"""
Django settings for learnhub project.

This file is environment-driven: it works out-of-the-box for local development
(SQLite, local media, DEBUG on) with zero configuration, and automatically
switches to production-ready settings (PostgreSQL, Cloudinary, HTTPS
enforcement) when you set environment variables in production.

See DEPLOYMENT.md for the full production deployment guide.
"""

import os
from pathlib import Path

import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ---- Core ----
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-k@_k3$-j&q*5ps8ebjv@-gx#g5#b&d^)2o-n1=ge8felc4nr78",
)
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# When behind a reverse proxy (Railway, Render, Heroku-style platforms) that
# terminates SSL for you, this tells Django the original request was HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Your production domain(s), e.g. "https://learnhub.example.com" - needed for
# Django's CSRF protection to trust POSTs (like login/signup) coming from your
# real domain instead of just the raw hostname.
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # LearnHub apps
    'accounts',
    'courses',
    'payments',
    'exams',
    'live_classes',
    'certificates',
    'dashboard',
]

# Cloudinary is only needed/loaded when configured (production media storage).
USE_CLOUDINARY = config("USE_CLOUDINARY", default=False, cast=bool)
if USE_CLOUDINARY:
    INSTALLED_APPS = ['cloudinary_storage'] + INSTALLED_APPS + ['cloudinary']

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:home'
LOGOUT_REDIRECT_URL = 'accounts:home'

# ---- Razorpay ----
# Get your keys from https://dashboard.razorpay.com/app/keys
# Use Test Mode keys while developing, Live Mode keys only in production.
RAZORPAY_KEY_ID = config("RAZORPAY_KEY_ID", default="rzp_test_XXXXXXXXXXXX")
RAZORPAY_KEY_SECRET = config("RAZORPAY_KEY_SECRET", default="your_test_secret_here")

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves static files efficiently in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'learnhub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'learnhub.wsgi.application'


# ---- Database ----
# Defaults to local SQLite for development. In production, set DATABASE_URL
# (Railway/Render provide this automatically when you attach a PostgreSQL
# addon), e.g.: postgres://user:password@host:5432/dbname
DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=not DEBUG)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_TZ = True


# ---- Static files (CSS, JS) ----
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # `collectstatic` output for production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---- Media files (user uploads: videos, PDFs, thumbnails, certificates) ----
# Locally: saved to /media on disk. In production: set USE_CLOUDINARY=True
# plus your Cloudinary credentials, so uploads survive redeploys (a server's
# local disk is wiped on every deploy on platforms like Railway/Render/Heroku).
if USE_CLOUDINARY:
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
        "API_KEY": config("CLOUDINARY_API_KEY", default=""),
        "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
    }
    MEDIA_URL = "/media/"
else:
    STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'


# ---- Security (auto-enabled when DEBUG=False) ----
if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
