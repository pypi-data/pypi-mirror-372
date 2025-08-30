from os import getenv, uname, path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages
import random
import string
import re
from importlib.metadata import version
from pathlib import Path

def get_version():
    try:
        import tomllib
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]
    except:
        try:
            return version("piprints")
        except:
            return "???"

VERSION = get_version()

caratteri = string.ascii_letters + string.digits

load_dotenv()  # take environment variables from .env.

def getenvBool(varname, default=False):
    val = getenv(varname)
    if val is None:
        return default
    return {
        'true': True,
        'yes': True,
        '1': True,
        'false': False,
        'no': False,
        '0': False
    }[val.lower()]


DEBUG = getenvBool("DEBUG", True)
SITE_ID = int(getenv("SITE_ID", '2'))

HOST = uname()[1]

BASE_ROOT = path.dirname(path.abspath(__file__))
BASE_ROOT = getenv("BASE_ROOT", path.dirname(path.abspath(__file__)))
USER_HOME = getenv("USER_HOME", path.expanduser('~'))

# Make this unique, and don't share it with anybody.
SECRET_KEY = getenv("SECRET_KEY", ''.join(random.choices(caratteri, k=80)))

HOSTNAME = getenv("HOSTNAME", 'localhost')
SERVER_URL = getenv("SERVER_URL", 'http://localhost')
ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", '127.0.0.1,localhost').split(',')
ROOT_URL = getenv("ROOT_URL", '/')
STATIC_ROOT = getenv("STATIC_ROOT", path.join(BASE_ROOT, 'static_root'))
STATICFILES_DIRS = getenv("STATIC_DIRS", path.join(BASE_ROOT, 'static')).split(',')
STATIC_URL = getenv("STATIC_URL", '/static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_ROOT = getenv("MEDIA_ROOT", path.join(BASE_ROOT, 'media'))
MEDIA_URL = getenv("MEDIA_URL", '/media/')

TEMPLATE_DIRS = getenv("TEMPLATE_DIRS", path.join(BASE_ROOT, 'templates')).split(',')

# codice per la verifica della proprieta' del sito web
# per google webmasters
GOOGLE_SITE_VERIFICATION = getenv("GOOGLE_SITE_VERIFICATION", None)

GOOGLE_ANALYTICS_ACCOUNT = getenv("GOOGLE_ANALYTICS_ACCOUNT", '')
PIWIK_URL = getenv("PIWIK_URL", '')
PIWIK_SITE_ID = getenv("PIWIK_SITE_ID", '')
SECURE_SSL_REDIRECT = getenvBool("SECURE_SSL_REDIRECT", False)
PIWIK_URL = getenv("PIWIK_URL", '')
PIWIK_SITE_ID = getenv("PIWIK_SITE_ID", '')

# [database] section: database settings
DATABASE_NAME = getenv("DATABASE_NAME", 'piprintsdb')
DATABASE_USER = getenv("DATABASE_USER", 'piprints')
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD", '')
DATABASE_HOST = getenv("DATABASE_HOST", '')
DATABASE_PORT = getenv("DATABASE_PORT", '')
DATABASE_ENGINE = getenv("DATABASE_ENGINE", 'sqlite3')

# [preferences] section: these settings can be choosen at will
ADMINS = getenv("ADMINS", 'admin <admin@email.com>').split(',')
admin_re = re.compile(r'^\s*(.*?)\s*<(.*)>\s*$')
try:
    ADMINS = [admin_re.match(x).groups() for x in ADMINS]
except:
    raise ValueError("ADMINS must be a comma-separated list of 'name <email>'")
MANAGERS = ADMINS
ADMIN_EMAIL = ADMINS[0][1] if ADMINS else None
BULLETIN_EMAIL = getenv("BULLETIN_EMAIL", '')
SERVER_EMAIL = getenv("SERVER_EMAIL", '')
CONTACT_EMAIL = getenv("CONTACT_EMAIL", '')
USE_PERSONAL_EMAIL = getenvBool("USE_PERSONAL_EMAIL", True)
PERSONAL_EMAIL_TEMPLATE = getenv("PERSONAL_EMAIL_TEMPLATE", '{person.firstname} {person.lastname} <noreply@noreply.com>')
FAKE_EMAILS = getenvBool("FAKE_EMAILS", True)

# Mail is sent using the SMTP host and port specified in the EMAIL_HOST 
# and EMAIL_PORT settings. The EMAIL_HOST_USER and EMAIL_HOST_PASSWORD 
# settings, if set, are used to authenticate to the SMTP server, 
# and the EMAIL_USE_TLS and EMAIL_USE_SSL settings control whether 
# a secure connection is used.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIMEZONE = getenv("TIMEZONE", 'Europe/Rome')

LANGUAGE = getenv("LANGUAGE", 'en-us')
DATE_FORMAT = getenv("DATE_FORMAT", 'j b Y')
TIME_FORMAT = getenv("TIME_FORMAT", 'H:i')
LIST_AUTHORS_BY_PAPERS = getenvBool("LIST_AUTHORS_BY_PAPERS", True)
INSTANCE = getenv("INSTANCE", '')
SITE_NAME = getenv("SITE_NAME", '')
PREPRINT = getenv("PREPRINT", ' preprint')
SHOW_SEMINAR_PLACE = getenvBool("SHOW_SEMINAR_PLACE", False)
SHOW_PARENTED_SEMINARS = getenvBool("SHOW_PARENTED_SEMINARS", False)
COOKIES_ALERT_ENABLED = getenvBool("COOKIES_ALERT_ENABLED", True)
PAPERS_ENABLED = getenvBool("PAPERS_ENABLED", True)
APPEND_SLASH = getenvBool("APPEND_SLASH", True)

MESSAGE_TAGS = {
    messages.DEBUG: 'bg-secondary',
    messages.INFO: 'bg-info',
    messages.SUCCESS: 'bg-success',
    messages.WARNING: 'bg-warning',
    messages.ERROR: 'bg-danger',
}

BASE_ROOT = getenv("BASE_ROOT")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'TEST': {
            'NAME': DATABASE_NAME + '_test',
            }
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Più sicuro    
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# add custom authentication method
AUTHENTICATION_BACKENDS = ['piprints.main.auth.UserBackend','piprints.main.auth.ImpersonificationBackend']

AUTH_USER_MODEL = 'main.User'

ROOT_URLCONF = 'piprints.urls'

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

TEMPLATES = [
    {
        'NAME': 'custom',
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': TEMPLATE_DIRS,
        'OPTIONS': {
            'environment': 'piprints.main.template.MyEnvironment',
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
#            'loaders': [
#                 'piprints.main.template.DjangoLoader',
#            ]
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
        'APP_DIRS': True,
    },
]


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',

    'piprints.main',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
}

## LOGGING con disabilitazione messaggio ALLOWED HOST
## vedi http://stackoverflow.com/questions/15384250/suppress-admin-email-on-django-allowed-hosts-exception

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

###### Andrea 27 apr 2021
## https://security.stackexchange.com/a/8970
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
## https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER
# questo non serve perché stiamo usando wsgi
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
## https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect


