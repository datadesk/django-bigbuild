"""
Django settings for example project.

Generated by 'django-admin startproject' using Django 1.9.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8s235s89o=5wl2o70zwio(y0p^@^m+*1m_3y=0d!%+f^bo+-d2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'compressor',
    'bigbuild',
    'greeking',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "pages"),],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]

BIGBUILD_GIT_DIR = os.path.join(BASE_DIR, "../")
BIGBUILD_BASE_URL = "/projects/"

BUILD_DIR = os.path.join(BASE_DIR, "..", ".build")
BAKERY_GZIP=False
BAKERY_VIEWS=(
    'bigbuild.views.IndexRedirectView',
    'bigbuild.views.PageListView',
    'bigbuild.views.PageDetailView',
    'bigbuild.views.Static404View',
    'bigbuild.views.RobotsView',
    'bigbuild.sitemaps.SitemapView',
    'bigbuild.sitemaps.GoogleNewsSitemapView',
    'bigbuild.feeds.LatestPages',
)
STATIC_ROOT=os.path.join(BASE_DIR, "pages")
STATIC_URL = "/static/"
COMPRESS_ENABLED = True
COMPRESS_CSS_ENABLED = False
COMPRESS_JS_ENABLED = False
COMPRESS_JS_COMPRESSOR = "bigbuild.compressors.SimpleJsCompressor"
COMPRESS_CSS_COMPRESSOR = "bigbuild.compressors.SimpleCssCompressor"
STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
)
COMPRESS_CSS_FILTERS = [
    'compressor.filters.cssmin.rCSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]
COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'sass {infile} {outfile}'),
)
COMPRESS_CACHEABLE_PRECOMPILERS = ()
USE_TZ = True
