"""
Django settings for split project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import paypalrestsdk

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('STAGE', 0)) < 2

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "ni^)v*b622$&8@8mf)l!&0()iotz4s%#o-f$q_g6v719p6n_3e" if DEBUG else os.environ.get('SECRET_KEY')
SECRET_TOKEN = bytes("test", "utf-8") if DEBUG else bytes(os.environ.get('SECRET_TOKEN'), "utf-8")


ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '52.178.136.18', '40.112.78.121']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': "DEBUG" if DEBUG else "ERROR",
        },
    },
}


# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    #'django.contrib.admin',
    'split.apps.SplitAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'prettyjson',
    'api.apps.ApiConfig',
    'eip',
    'split_dashboard',
]

MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# STATICFILES_STORAGE = 'split.storage.WhiteNoiseStaticFilesStorage'

ROOT_URLCONF = 'split.urls'

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

WSGI_APPLICATION = 'split.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
	    'USER': 'split-api',
            'PASSWORD': '&M6fn1VHqSkY707a',
            'HOST': '23.102.37.65',
            'PORT': 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'HOST': 'db',
            'PORT': 5432,
        }
    }
    #DATABASES = {
    #    'default': {
    #        'ENGINE': 'django.db.backends.sqlite3',
    #        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #    }
    #}

AUTH_USER_MODEL = 'api.User'


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + STATIC_URL

MEDIA_URL= '/media/'
MEDIA_ROOT = BASE_DIR + MEDIA_URL


# Jet

JET_INDEX_DASHBOARD = 'split_dashboard.dashboard.SplitIndexDashboard'
JET_APP_INDEX_DASHBOARD = 'split_dashboard.dashboard.SplitIndexDashboard'

JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': "split",
        'color': '#473280',
        'title': "Split"
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]


## PayPal
if DEBUG: 
    paypalrestsdk.configure({
        'mode': "sandbox",
        'client_id': "ATa_26DBlcPtxaYCchJf4IeRU2OnzJD8eSoV2ZyKkUHgHZ5f5UH0SO4vwTtH7ESaK61F8KwHGCh_misI",
        'client_secret': "ED-j2wGi56NAFH5BqUy4eHnCZmE9sRr4USIXwsc7FrvLr1ClpIb26qryDUN4yLTdeCDBTshCUssabgP2"
    })
else:
    paypalrestsdk.configure({
        'mode': "live",
        'client_id': os.environ.get("PAYPAL_ID"),
        'client_secret': os.environ.get("PAYPAL_SECRET")
    })
