#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import tempfile
from datetime import datetime
from bigbuild.models import Page
from django.utils.text import slugify
from django.test import SimpleTestCase, override_settings
logging.disable(logging.CRITICAL)

TEMP_DIR = tempfile.mkdtemp()
BUILD_DIR = os.path.join(TEMP_DIR, '.build')
BIGBUILD_PAGE_DIR = os.path.join(TEMP_DIR, '.pages')
BIGBUILD_ARCHIVE_DIR = os.path.join(TEMP_DIR, '.archive')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BIGBUILD_PAGE_DIR, BIGBUILD_ARCHIVE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [],
        },
    },
]


@override_settings(BIGBUILD_ARCHIVE_DIR=BIGBUILD_ARCHIVE_DIR)
@override_settings(BUILD_DIR=BUILD_DIR)
@override_settings(BIGBUILD_PAGE_DIR=BIGBUILD_PAGE_DIR)
@override_settings(TEMPLATES=TEMPLATES)
@override_settings(COMPRESS_ROOT=BIGBUILD_PAGE_DIR)
class TestBase(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBase, cls).setUpClass()
        # Create some pages
        pages = [
            Page.create(slug=slugify('My Fake Page'), published=True),
            Page.create(
                slug=slugify('My Second Fake Page'),
                published=True,
                description="TK"
            ),
            Page.create(
                slug='a-unpublished-fake-page',
                published=False,
                description="TK"
            ),
            Page.create(
                slug='a-future-fake-page',
                published=True,
                pub_date=datetime(2030, 1, 1, 0, 0, 0),
                description=''
            ),
            Page.create(
                slug='a-working-page',
                published=False,
                description='Foobar'
            ),
            Page.create(
                slug='a-live-page',
                published=True,
                pub_date=datetime(2001, 1, 1, 0, 0, 0),
                description='Foobar'
            ),
            Page.create(
                slug='an-archived-page',
                published=True,
                pub_date=datetime(2001, 1, 1, 0, 0, 0),
                description='Foobar'
            )
        ]

        # Make directories for all of them
        [p.create_directory(force=True) for p in pages]

        # Create a blacklisted file to test that
        with open(os.path.join(BIGBUILD_PAGE_DIR, '.DS_Store'), 'w+') as f:
            f.write("foo")
