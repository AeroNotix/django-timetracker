"""This is an example file for which you could use in your
development environment."""
import os

# Django settings for timetracker project.
SECRET_KEY = '<SECRET_KEY>'
TEMPLATE_STRING_IF_INVALID = 'INCORRECT'
ROOT_DIR = os.path.dirname(__file__)

import logging
from django.core.mail import send_mail
from timetracker.utils.datemaps import hr_calculation

# BACKEND DJANGO SETTINGS
DEBUG = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=overtime,tracker,vcs,reporting',
    '--ignore-files=settings',
]

TEMPLATE_DEBUG = DEBUG
ADMINS = (
    ('admin', 'admin@timetracker.com'),
)
MANAGERS = ADMINS

# Email settings
EMAIL_DEBUG = True
if EMAIL_DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'email.hosting.com' if not EMAIL_DEBUG else '127.0.0.1'
EMAIL_PORT = 25 if not EMAIL_DEBUG else 1025
EMAIL_HOST_USER = "timetracker@timetracking.com"
EMAIL_HOST_PASSWORD = "password"

# Storage settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # or whatever database
                                              # you're using
        'NAME': 'db_timetracker',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Django debug tool bar settings
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

def custom_show_toolbar(request):
    return True  # Always show toolbar

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'HIDE_DJANGO_SQL': False,
    'TAG': 'div',
    'ENABLE_STACKTRACES' : True,
}

# Internationalization
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False
USE_TZ = True

SITE_ID = 1

# Static files related options
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = os.path.join(ROOT_DIR, 'collect_static/')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = (
   os.path.join(ROOT_DIR, 'static/'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Template related settings
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "timetracker.views.user_context_manager",
)

# directory for root templates
TEMPLATE_DIRS = (
    os.path.join(ROOT_DIR, 'templates/'),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'timetracker.middleware.exception_handler.UnreadablePostErrorMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'timetracker.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'timetracker.tracker',
    'timetracker.vcs',
    'timetracker.overtime',
    'timetracker.reporting',
    'django_extensions',
    'debug_toolbar',
    # 'south', enable when doing migrations, it gets in the way when
    # testing/bootstrapping etc.
    'django_coverage',
    'django_nose',
    'tastypie',
)
# logging
LOGLEVEL = logging.DEBUG
ROOT_LOG_DIR = '/var/log/timetracker/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
}

# Application settings.
CAN_CLOSE_APPROVALS = []
CAN_VIEW_JOBCODES = []
DAY_ON_DEMAND_ALLOWANCE = 4
DEFAULT_OT_THRESHOLD = 1.0
if DEBUG:
    DOMAIN_NAME = "http://localhost:8080/"
else:
    DOMAIN_NAME = "http://timetracker.com"
DOCUMENTATION_BASE_URL = DOMAIN_NAME + '/docs/'
EXTRA_ACTIVITIES = {}
FONT_DIRECTORY = '/usr/share/fonts/TTF'
HASH_PASSES = 10000
MANAGER_EMAILS_OVERRIDE = {}
MANAGER_NAMES_OVERRIDE = {}
NUM_WORKING_DAYS = 5
OT_THRESHOLDS = {}
OVERRIDE_CALCULATION = {}
PLUGIN_DIRECTORY = "/path/to/plugins/"
SENDING_APPROVAL_DIGESTS = {}
SENDING_APPROVAL_MANAGERS = {}
SENDING_APPROVAL_TL = {
    "BF": True
}
SENDING_APPROVAL = SENDING_APPROVAL_MANAGERS
SUSPICIOUS_DATE_DIFF = 60
TL_APPROVAL_CHAINS = {}
UNDER_TIME_ENABLED = {}
VCS_ENABLED = {"CZ", "BK", "BG"}
ZEROING_HOURS = {}
