import os
from setuptools import setup
from distutils.core import Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': 'test.db',
                    'TEST_NAME': 'test.db',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS = (
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.staticfiles',
                'compressor',
                'greeking',
                'bigbuild',
            ),
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [],
                    'APP_DIRS': False,
                    'OPTIONS': {},
                },
            ],
            BASE_DIR=os.path.dirname(__file__),
            BAKERY_GZIP=False,
            BAKERY_VIEWS=(
                'bigbuild.views.IndexRedirectView',
                'bigbuild.views.PageListView',
                'bigbuild.views.PageDetailView',
                'bigbuild.views.Static404View',
                'bigbuild.views.RobotsView',
                'bigbuild.sitemaps.SitemapView',
                'bigbuild.sitemaps.GoogleNewsSitemapView',
                'bigbuild.feeds.LatestPages',
            ),
            STATIC_ROOT="./.static",
            STATIC_URL = "/static/",
            COMPRESS_ENABLED = True,
            COMPRESS_JS_COMPRESSOR = "bigbuild.compressors.SimpleJsCompressor",
            COMPRESS_CSS_COMPRESSOR = "bigbuild.compressors.SimpleCssCompressor",
            STATICFILES_FINDERS = (
                'compressor.finders.CompressorFinder',
            ),
            COMPRESS_CSS_FILTERS = [
                'compressor.filters.cssmin.rCSSMinFilter'
            ],
            COMPRESS_JS_FILTERS = [
                'compressor.filters.jsmin.JSMinFilter',
            ],
            COMPRESS_PRECOMPILERS = (
                ('text/coffeescript', 'coffee --compile --stdio'),
                ('text/less', 'lessc {infile} {outfile}'),
                ('text/x-sass', 'sass {infile} {outfile}'),
            ),
            COMPRESS_CACHEABLE_PRECOMPILERS = (),
            USE_TZ = True,
            ROOT_URLCONF = 'bigbuild.urls',
            BIGBUILD_GIT_BRANCH = os.environ.get("BIGBUILD_GIT_BRANCH", None),
            BIGBUILD_BRANCH_BUILD = True,
        )
        from django.core.management import call_command
        import django
        django.setup()
        call_command('test', 'bigbuild')


setup(
    name='django-bigbuild',
    version='0.5.11',
    description="The open-source engine that powers bigbuilder, the Los Angeles Times Data Desk's \
system for publishing standalone pages",
    author='The Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/django-bigbuild/',
    zip_safe=False,
    packages=(
        'bigbuild',
        'bigbuild.management',
        'bigbuild.management.commands',
        'bigbuild.models',
        'bigbuild.templatetags',
    ),
    include_package_data=True,
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'python-frontmatter>=0.4.2',
        'django-bakery>=0.10.2',
        'validictory>=1.0.1',
        'django-compressor>=2.0',
        'greeking>=2.2.0',
        'GitPython>=2.0.8',
        'python-dateutil>=2.6.0',
        'archieml>=0.3.1',
        'pytz',
        'six',
    ],
    cmdclass={'test': TestCommand}
)
