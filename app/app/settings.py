import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6w5!q4)j3&84#0tsmx!4a$sdno^t!zb$j*a-a=4$os_2_qf7#b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if os.environ.get("DEBUG", False) == "False" else True
PROD = not DEBUG

if not PROD:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = []


# Application definition

AUTH_USER_MODEL = "user.MyUser"

PROJECT_APPS = [
    'user.apps.UserConfig',
    'stories.apps.StoriesConfig',
    'core.apps.CoreConfig',
    'news.apps.NewsConfig',
    'photos.apps.PhotosConfig',
    'videos.apps.VideosConfig',
    # 'search_indexes.apps.SearchIndexesConfig',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'knox',
    'drf_yasg',
    'celery',
    'django_celery_results',
    'django_celery_beat',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'corsheaders',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
]

ROOT_URLCONF = 'app.urls'

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

LOGIN_URL = '/user/login/'

LOGIN_REDIRECT_URL = '/'

# Elasticsearch
#https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html#install-and-configure
# if PROD:
#     ELASTICSEARCH_DSL={
#         'default': {
#                 'hosts': 'elasticsearch:9200'
#         },
#     }
# else:
#     ELASTICSEARCH_DSL={
#         'default': {
#             'hosts': 'localhost:9200'
#         },
#     }

WSGI_APPLICATION = 'app.wsgi.application'

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.TokenAuthentication',
    # ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),

    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ],

    'JSON_UNDERSCOREIZE': {
        'no_underscore_before_number': True,
    },
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', "db_name"),
        'USER': os.environ.get('POSTGRES_USER', "db_user"),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', "6NwpPtvGyCsMLAKDZtazEP9WjANze25eP3e2UJdWrgrrKq"),
        'HOST': os.environ.get('POSTGRES_HOST', "localhost"),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

ELASTICSEARCH_INDEX_NAMES = {
    'app.documents.post': 'posts',
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = ()

CSRF_TRUSTED_ORIGINS = (
    'localhost',
)

SITE_ID = 1

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Baku'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOG_LEVEL = 'ERROR' if PROD else 'DEBUG'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': not DEBUG,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:=> %(message)s',
        },
        'focused': {
            'format': '\n----------------------\n%(asctime)s [%(levelname)s] %(name)s:=> %(message)s \n----------------------',
        },
    },
    'handlers': {
        'my_custom_debug': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'focused',
        },
        'request_handler': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['my_custom_debug'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
    },
}
