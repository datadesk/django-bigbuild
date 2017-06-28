#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import tempfile
from datetime import datetime
from bigbuild import exceptions
from greeking import latimes_ipsum
from django.utils.text import slugify
from bigbuild.models import PageList, Page
from bigbuild import get_archive_directory
from django.core.management import call_command
from bigbuild.compressors import SimpleCompressor
from django.core.management.base import CommandError
from bigbuild.views import PageListView, PageDetailView
from compressor.exceptions import UncompressableFileError
from django.test import SimpleTestCase, override_settings
from django.core.serializers.base import DeserializationError
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
class FakePagesTest(SimpleTestCase):
    """
    Tests that run against fake pages.
    """
    @classmethod
    def setUpClass(cls):
        super(FakePagesTest, cls).setUpClass()
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
        [p.create_directory() for p in pages]

        # Archive one of them
        call_command("archivepage", 'an-archived-page')

        # Create a blacklisted file to test that
        with open(os.path.join(BIGBUILD_PAGE_DIR, '.DS_Store'), 'w+') as f:
            f.write("foo")

    @override_settings(BAKERY_GZIP=True)
    def test_gzip(self):
        call_command("build")

    def test_page(self):
        obj = PageList()[0]
        obj.__str__()
        obj.__repr__()
        obj.get_absolute_url()

    def test_cant_remake_directory(self):
        obj = PageList()[0]
        with self.assertRaises(ValueError):
            obj.create_directory()

    def test_force_new_directory(self):
        obj = PageList()[0]
        obj.create_directory(force=True)

    def test_archivedpage(self):
        p = PageList()['an-archived-page']
        p.__str__()
        p.__repr__()
        p.get_absolute_url()
        p.page_directory_path
        PageDetailView().build_object(p)

    def test_pagelist(self):
        with override_settings(PAGE_PUBLICATION_STATUS='working'):
            page_list = PageList()
            self.assertTrue(len(page_list) > 0)
        with override_settings(PAGE_PUBLICATION_STATUS='live'):
            page_list = PageList()
            self.assertTrue(len(page_list) > 0)
        page_list = PageList()
        with self.assertRaises(KeyError):
            page_list['foobar']
        with self.assertRaises(IndexError):
            page_list[100]

    def test_views(self):
        PageListView.as_view()
        PageDetailView.as_view()

    def test_build(self):
        call_command("build")
        self.assertTrue(os.path.exists(BUILD_DIR))
        expected_index = os.path.join(
            BUILD_DIR,
            PageList()['my-fake-page'].get_absolute_url().lstrip("/"),
            'index.html'
        )
        self.assertTrue(os.path.exists(expected_index))
        PageList()[0].build()

    def test_validatepages(self):
        call_command("validatepages")

    def test_createpage(self):
        call_command("createpage", "test-page")
        with self.assertRaises(CommandError):
            call_command("createpage", "test-page")
        call_command("createpage", "test-page", force=True)

    def test_sans(self):
        p = Page(slug='test-sans', published=True)
        p.create_directory(index_template_context={'sans': True})

    def test_dark(self):
        p = Page.create(slug='test-dark')
        p.create_directory(index_template_context={'dark': True})

    def test_deletepage(self):
        p = PageList()[0]
        p.delete()

    def test_archivepage(self):
        p = Page.create(slug='test-archived-page')
        p.create_directory()
        call_command("archivepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("archivepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("archivepage", "hello-wtf")
        call_command("unarchivepage", "test-archived-page")

    def test_warnings(self):
        exceptions.BadMetadata()
        exceptions.BaseWarning().get_context_data()
        exceptions.MissingRecommendedMetadataWarning('slug').__str__()

    def test_bad_metadata(self):
        p = Page.create(slug='test-bad-yaml')
        p.create_directory()

        yaml = open(p.frontmatter_path).read()

        bad = open(p.frontmatter_path, 'w')
        bad.write("""
---
foo:: bar;:
---
""")
        bad.close()

        with self.assertRaises(DeserializationError):
            p.sync_frontmatter()

        good = open(p.frontmatter_path, 'w')
        good.write(yaml)
        good.close()

    def test_missingmetadata(self):
        p = Page.create(slug='test-no-yaml')
        p.create_directory()
        os.remove(p.frontmatter_path)
        with self.assertRaises(DeserializationError):
            PageList()
        p.delete()

    def test_aml(self):
        # Create an object
        call_command("createpage", 'test-aml')
        p = PageList()['test-aml']

        # Make sure there's nothing there
        self.assertEqual(p.data_objects, {})

        # Update it with data path
        p.data = {"foo": "static/bar.aml"}
        p.write_frontmatter()

        # Create that data path
        static_path = os.path.join(p.page_directory_path, 'static')
        with open(os.path.join(static_path, 'bar.aml'), 'w+') as f:
            f.write("[arrayName]\nkey: value")

        # Resync the object so that it opens the data file
        p.sync_frontmatter()

        # Make sure everything matches
        self.assertEqual(p.metadata['data']['foo'], "static/bar.aml")
        self.assertEqual(p.data_objects['foo']['arrayName'][0]['key'], 'value')

        # Make sure we can archive aml
        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

        p.delete()

    def test_csv(self):
        # Create an object
        call_command("createpage", 'test-csv')
        p = PageList()['test-csv']

        # Make sure there's nothing there
        self.assertEqual(p.data_objects, {})

        # Update it with data path
        p.data = {"foo": "static/bar.csv"}
        p.write_frontmatter()

        # Create that data path
        static_path = os.path.join(p.page_directory_path, 'static')
        with open(os.path.join(static_path, 'bar.csv'), 'w+') as f:
            f.write('key,bar\nvalue,value')

        # Resync the object so that it opens the data file
        p.sync_frontmatter()

        # Make sure everything matches
        self.assertEqual(p.metadata['data']['foo'], "static/bar.csv")
        self.assertEqual(p.data_objects['foo'][0]['key'], 'value')

        # Make sure we can archive aml
        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

        p.delete()

    def test_json(self):
        # Create an object
        call_command("createpage", 'test-json')
        p = PageList()['test-json']

        # Make sure there's nothing there
        self.assertEqual(p.data_objects, {})

        # Update it with data path
        p.data = {"foo": "static/bar.json"}
        p.write_frontmatter()

        # Create that data path
        static_path = os.path.join(p.page_directory_path, 'static')
        with open(os.path.join(static_path, 'bar.json'), 'w+') as f:
            f.write('[{"key": "value"}]')

        # Resync the object so that it opens the data file
        p.sync_frontmatter()

        # Make sure everything matches
        self.assertEqual(p.metadata['data']['foo'], "static/bar.json")
        self.assertEqual(p.data_objects['foo'][0]['key'], 'value')

        # Make sure we can archive aml
        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

        p.delete()

    def test_yaml(self):
        # Create an object
        call_command("createpage", 'test-yaml')
        p = PageList()['test-yaml']

        # Make sure there's nothing there
        self.assertEqual(p.data_objects, {})

        # Update it with data path
        p.data = {"foo": "static/bar.yaml"}
        p.write_frontmatter()

        # Create that data path
        static_path = os.path.join(p.page_directory_path, 'static')
        with open(os.path.join(static_path, 'bar.yaml'), 'w+') as f:
            f.write('- key: value')

        # Resync the object so that it opens the data file
        p.sync_frontmatter()

        # Make sure everything matches
        self.assertEqual(p.metadata['data']['foo'], "static/bar.yaml")
        self.assertEqual(p.data_objects['foo'][0]['key'], 'value')

        # Make sure we can archive aml
        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

        p.delete()

    # def test_baddata(self):
    #     p = PageList()['my-second-fake-page']
    #
    #     p.data = {"foo": "bar.csv"}
    #     p.write_frontmatter()
    #     p.sync_frontmatter()
    #     p.data = {}
    #     p.write_frontmatter()
    #
    #     data_path = os.path.join(p.page_directory_path, 'data')
    #     os.path.exists(data_path) or os.mkdir(data_path)
    #     with open(os.path.join(data_path, 'foo.txt'), 'w+') as f:
    #         f.write("foo,bar")
    #     p.data = {"foo": "foo.txt"}
    #     p.write_frontmatter()
    #     p.sync_frontmatter()
    #     p.data = {}
    #     p.write_frontmatter()

    def test_nofile(self):
        """
        Test django-compressor errors
        """
        c = SimpleCompressor()
        with self.assertRaises(UncompressableFileError):
            c.get_filename("foobar.jpg")

    def test_nocompress(self):
        """
        Test compression turned off
        """
        with override_settings(COMPRESS_ENABLED=False):
            call_command("build")

    def test_cache(self):
        """
        Test the page caching
        """
        before = PageList()
        cache_path = os.path.join(get_archive_directory(), '.cache')
        if os.path.exists(cache_path):
            os.remove(cache_path)
        call_command("cachepages")
        after = PageList()
        self.assertEqual(before[0].slug, after[0].slug)
        call_command("cachepages")
