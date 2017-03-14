import os
from MTShowcase.secrets import db_dic, secret_key, email_pw, production
import MTShowcase.names as names
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key
# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = not production
#DEBUG = True
# TODO
AUTH_DEBUG = True  # enable/disable debug printing for auth workflow

if production:
    ALLOWED_HOSTS = ['showcase.mt.haw-hamburg.de', '141.22.50.244']
else:
    ALLOWED_HOSTS = []

# MAIL HANDLING
SITE = names.project_name

if production:
    DOMAIN = "showcase.mt.haw-hamburg.de"
else:
    DOMAIN = "localhost:8000"


# TODO: Use HAW Mail Host
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mtshowcase.haw@gmail.com'  # TODO: Move to secrets.py
EMAIL_HOST_PASSWORD = email_pw
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ACCOUNT_ACTIVATION_DAYS = 7

AUTH_USER_MODEL = 'authentication.AuthEmailUser'
AUTHENTICATION_BACKENDS = ('apps.authentication.backend.EmailBackend', 'django.contrib.auth.backends.ModelBackend')

# Application definition

INSTALLED_APPS = [
    # DJANGO
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # INTERNAL APPS
    'apps.home',
    'apps.administration',
    'apps.project',
    'apps.user',
    'apps.authentication',
    # EXTERNAL APPS
    'crispy_forms',
    'compressor'  # LESS
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# LESS
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} > {outfile}'),
)

COMPRESS_ENABLED = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

INTERNAL_IPS = ('127.0.0.1',)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler"
]

ROOT_URLCONF = 'MTShowcase.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', '/home/showcase/MTShowcase/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.authentication.context_processor.include_login_form',
                'apps.authentication.context_processor.include_register_form',
                'apps.authentication.context_processor.include_production_flag',
            ],
        },
    },
]

WSGI_APPLICATION = 'MTShowcase.wsgi.application'

# Database

DATABASES = db_dic

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'de_DE'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# TODO: nginx

STATIC_URL = '/static/'
STATICFILES_DIRS = ['static/']
if production:
    STATIC_ROOT = "/home/showcase/static/"
    #STATIC_ROOT = os.path.join(BASE_DIR, "static/")
else:
    COMPRESS_ROOT = BASE_DIR

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
