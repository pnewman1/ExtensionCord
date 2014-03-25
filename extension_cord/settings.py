####
#
# Copyright (c) 2013, Deem Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
####
import os
import sys
import logging

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.append(SITE_ROOT)
try: 
    from ldap_groups.settings import *
    LDAP = True
except ImportError:
    LDAP = False

# Django settings for Extension Cord project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ),  # disable e-mail
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'extension_cord',  # Or path to database file if using sqlite3.
        'USER': 'extension_cord',  # Not used with sqlite3.
        'PASSWORD': 'extension_cord',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }

    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Pacific'

#USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = 'extension_cord/static/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vqg_^)_#+i0x6%s8)g7-e_)w=4m$xjror(tm&amp;28a6(oj@am3r)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.contrib.auth.context_processors.auth',
#     'django.contrib.messages.context_processors.messages',
#     )

ROOT_URLCONF = 'extension_cord.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'extension_cord.wsgi.application'

TEMPLATE_DIRS = (
    SITE_ROOT + "/templates/",
    # Put strings here, like "/home/html/django_templates"
    #   or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    'ldap_groups',
    # must define ecapp/extension_cord before admin, or any
    # static/ overlay wont work when ./manage.py collect_static runs
    'ecapp',
    'extension_cord',
    #'bootstrap',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'ecapp',
    'extension_cord',
    'south',
)

if DEBUG:
    # will output to your console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )
else:
    # will output to logging file
    logging.basicConfig(
        level=logging.WARN,
        format='%(asctime)s %(levelname)s %(message)s',
        filename='extension_cord.log',
        filemode='a'
    )

if LDAP == True:
    AUTHENTICATION_BACKENDS = (
        'ldap_groups.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',
            'django.contrib.auth.backends.ModelBackend',
    )
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

#CUSTOM_VARIABLES
ELEMENTS_PER_PAGE = 20

# Set the bug server information here:
BUG_SERVER = 'http://jira.yourcompany.com'
BUG_TRACKING_URL = BUG_SERVER + '/browse/'
BUG_USER = 'user'
BUG_PASSWORD = 'password'

# local_settings.py variables override those in this file
# local_settings.py is in .gitignore and isn't checked in
# but an example is included
try:
    from extension_cord.local_settings import *
except ImportError:
    pass
