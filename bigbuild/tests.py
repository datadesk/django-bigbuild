#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import tempfile
from datetime import datetime
from bigbuild import exceptions
from greeking import latimes_ipsum
from bigbuild.models import PageList, Page
from bigbuild import get_archive_directory
from django.core.management import call_command
from bigbuild.compressors import SimpleCompressor
from django.core.management.base import CommandError
from bigbuild.templatetags.bigbuild_tags import jsonify
from bigbuild.views import PageListView, PageDetailView
from compressor.exceptions import UncompressableFileError
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
class FakePagesTest(SimpleTestCase):
    """
    Tests that run against fake pages.
    """
    @classmethod
    def setUpClass(cls):
        super(FakePagesTest, cls).setUpClass()
        pages = [
            Page(slug='My Fake Page', published=True),
            Page(
                slug='My Second Fake Page',
                published=True,
                description="TK"
            ),
            Page(
                slug='a-unpublished-fake-page',
                published=False,
                description="TK"
            ),
            Page(
                slug='a-future-fake-page',
                published=True,
                pub_date=datetime(2030, 1, 1, 0, 0, 0),
                description=''
            ),
            Page(
                slug='a-working-page',
                published=False,
                description='Foobar'
            ),
            Page(
                slug='a-live-page',
                published=True,
                pub_date=datetime(2001, 1, 1, 0, 0, 0),
                description='Foobar'
            )
        ]
        [p.create_directory() for p in pages]
        pages[0].create_directory(force=True)
        call_command("archivepage", pages[0].slug)
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

        with self.assertRaises(ValueError):
            obj.create_directory()
        self.assertTrue(obj.is_metadata_valid())

        obj.image_url = ''
        obj.pub_date = 'foobar'
        self.assertFalse(obj.is_metadata_valid())

        obj.image_url = 'http://www.foobar.com'
        obj.pub_date = datetime.now()
        self.assertTrue(obj.is_metadata_valid())

        obj.headline = latimes_ipsum.get_story().headline
        obj.published = True
        self.assertFalse(obj.has_recommended_metadata())

        obj.byline = "foobar"
        obj.headline = "something else"
        obj.description = "even more"
        self.assertTrue(obj.has_recommended_metadata())

    def test_archivedpage(self):
        p = PageList()['my-fake-page']
        p.__str__()
        p.__repr__()
        p.get_absolute_url()
        p.page_directory_path
        p.metadata
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
        self.assertTrue(os.path.exists(
            os.path.join(
                BUILD_DIR,
                PageList()['my-fake-page'].get_absolute_url().lstrip("/"),
                'index.html'
            )
        ))
        PageList()[0].build()

    def test_validatepages(self):
        call_command("validatepages")
        p = Page(slug='my-invalid-page', pub_date=1)
        p.create_directory()
        with self.assertRaises(ValueError):
            call_command("validatepages")

    def test_createpage(self):
        call_command("createpage", "test-page")
        with self.assertRaises(CommandError):
            call_command("createpage", "test-page")

    def test_archivepage(self):
        p = Page(slug='test-archived-page', published=True, description="TK")
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
        exceptions.MissingMetadataWarning('slug').__str__()
        exceptions.MissingRecommendedMetadataWarning('slug').__str__()

    def test_malformed_yaml(self):
        p = Page(slug='test-bad-yaml', published=True)
        p.create_directory()

        yaml = open(p.frontmatter_path).read()

        bad = open(p.frontmatter_path, 'w')
        bad.write("""
---
foo:: bar;:
---
""")
        bad.close()

        with self.assertRaises(exceptions.BadMetadata):
            p.sync_frontmatter()

        good = open(p.frontmatter_path, 'w')
        good.write(yaml)
        good.close()

    def test_delete(self):
        p = PageList()[0]
        p.delete()

    def test_missingmetadata(self):
        p = Page(slug='test-no-yaml', published=True)
        p.create_directory()
        os.remove(p.frontmatter_path)
        PageList()
        p.delete()

    def test_data(self):
        p = PageList()['my-second-fake-page']
        data_path = os.path.join(p.page_directory_path, 'data')
        static_path = os.path.join(p.page_directory_path, 'static')

        p.data = {"foo": "bar.csv"}
        p.write_frontmatter()
        with open(os.path.join(data_path, 'bar.csv'), 'w+') as f:
            f.write('foo,bar')
        p.sync_frontmatter()
        p.metadata['data']['foo']

        p.data = {"foo": "bar.json"}
        p.write_frontmatter()
        with open(os.path.join(data_path, 'bar.json'), 'w+') as f:
            f.write('[{"foo": "bar"}]')
        p.sync_frontmatter()
        p.metadata['data']['foo']

        p.data = {"foo": "bar.yml"}
        p.write_frontmatter()
        with open(os.path.join(data_path, 'bar.yml'), 'w+') as f:
            f.write('- foo: bar')
        p.sync_frontmatter()
        p.metadata['data']['foo']

        p.data = {"foo": "data/bar.csv"}
        p.write_frontmatter()
        with open(os.path.join(data_path, 'bar.csv'), 'w+') as f:
            f.write('foo,bar')
        p.sync_frontmatter()
        p.metadata['data']['foo']

        p.data = {"foo": "static/bar.csv"}
        p.write_frontmatter()
        with open(os.path.join(static_path, 'bar.csv'), 'w+') as f:
            f.write('foo,bar')
        p.sync_frontmatter()
        p.metadata['data']['foo']

    def test_aml(self):
        p = Page(slug='test-aml', published=True)
        p.create_directory()
        static_path = os.path.join(p.page_directory_path, 'static')

        p.data = {"foo": "static/bar.aml"}
        p.write_frontmatter()
        with open(os.path.join(static_path, 'bar.aml'), 'w+') as f:
            f.write("""

key: value
[array]
* 1
* 2
* 3

""")
        p.sync_frontmatter()
        p.metadata['data']['foo']
        self.assertEqual(p.data_objects['foo']['key'], 'value')

        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

    def test_baddata(self):
        p = PageList()['my-second-fake-page']

        p.data = {"foo": "bar.csv"}
        p.write_frontmatter()
        with self.assertRaises(exceptions.BadMetadata):
            p.sync_frontmatter()
        p.data = {}
        p.write_frontmatter()

        data_path = os.path.join(p.page_directory_path, 'data')
        os.path.exists(data_path) or os.mkdir(data_path)
        with open(os.path.join(data_path, 'foo.txt'), 'w+') as f:
            f.write("foo,bar")
        p.data = {"foo": "foo.txt"}
        p.write_frontmatter()
        with self.assertRaises(exceptions.BadMetadata):
            p.sync_frontmatter()
        p.data = {}
        p.write_frontmatter()

    def test_sans(self):
        p = Page(slug='test-sans', published=True)
        p.create_directory(index_template_context={'sans': True})

    def test_dark(self):
        p = Page(slug='test-dark', published=True)
        p.create_directory(index_template_context={'dark': True})

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


class JsonifyTest(SimpleTestCase):
    """
    Test the jsonify template filter
    """
    def test_jsonify(self):
        p = Page(slug='test-sans', published=True)
        jsonify(p)
        jsonify(dict(foo="bar"))
