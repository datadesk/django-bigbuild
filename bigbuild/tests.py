import os
import logging
import tempfile
from datetime import datetime
from bigbuild import exceptions
from greeking import latimes_ipsum
from bigbuild.models import PageList, Page
from django.core.management import call_command
from bigbuild.compressors import SimpleCompressor
from django.core.management.base import CommandError
from bigbuild.templatetags.bigbuild_tags import dropcap
from bigbuild.templatetags.bigbuild_tags import jsonify
from bigbuild.views import PageListView, PageDetailView
from compressor.exceptions import UncompressableFileError
from django.test import SimpleTestCase, override_settings
logging.disable(logging.CRITICAL)

TEMP_DIR = tempfile.mkdtemp()
BUILD_DIR = os.path.join(TEMP_DIR, '.build')
PAGE_DIR = os.path.join(TEMP_DIR, '.pages')
RETIRED_DIR = os.path.join(TEMP_DIR, '.retired')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PAGE_DIR, RETIRED_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [],
        },
    },
]


class RealPagesTest(SimpleTestCase):
    """
    Tests that run against our real pages.
    """
    def test_metadata_validity(self):
        """
        Validate that all of the pages have valid metadata.
        """
        for page in PageList():
            self.assertTrue(page.is_metadata_valid())


@override_settings(RETIRED_DIR=RETIRED_DIR)
@override_settings(BUILD_DIR=BUILD_DIR)
@override_settings(PAGE_DIR=PAGE_DIR)
@override_settings(TEMPLATES=TEMPLATES)
@override_settings(COMPRESS_ROOT=PAGE_DIR)
class FakePagesTest(SimpleTestCase):
    """
    Tests that run against fake pages.
    """
    @classmethod
    def setUpClass(cls):
        super(FakePagesTest, cls).setUpClass()
        os.path.exists(PAGE_DIR) or os.mkdir(PAGE_DIR)
        os.path.exists(RETIRED_DIR) or os.mkdir(RETIRED_DIR)
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
            )
        ]
        [p.create_directory() for p in pages]
        pages[0].create_directory(force=True)
        call_command("retirepage", pages[0].slug)
        # Create a blacklisted file to test that
        with open(os.path.join(PAGE_DIR, '.DS_Store'), 'w+') as f:
            f.write("foo")

    @override_settings(BAKERY_GZIP=True)
    def test_gzip(self):
        call_command("build")

    def test_page(self):
        obj = PageList()[0]
        obj.__str__()
        obj.__repr__()
        obj.get_absolute_url()

        self.assertTrue(obj.directory_exists)
        self.assertFalse(obj.retired_directory_exists)

        with self.assertRaises(ValueError):
            obj.create_directory()
        self.assertTrue(obj.is_metadata_valid())

        obj.image_url = 100
        self.assertFalse(obj.is_metadata_valid())

        obj.image_url = ''
        obj.pub_date = 'foobar'
        self.assertFalse(obj.is_metadata_valid())

        obj.image_url = 'http://www.foobar.com'
        obj.pub_date = datetime.now()
        self.assertTrue(obj.is_metadata_valid())

        obj.headline = latimes_ipsum.get_story().headline
        obj.published = True
        self.assertFalse(obj.has_recommended_metadata())

    def test_retiredpage(self):
        p = PageList()['my-fake-page']
        p.__str__()
        p.__repr__()
        p.get_absolute_url()
        p.directory_path
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
            os.path.join(BUILD_DIR, 'projects', 'my-fake-page/index.html')
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

    def test_createbigbuild(self):
        call_command("createbigbuild", "test-bigbuild")

    def test_creategraphic(self):
        call_command("creategraphic", "test-graphic")

    def test_retirepage(self):
        p = Page(slug='test-retired-page', published=True, description="TK")
        p.create_directory()
        call_command("retirepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("retirepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("retirepage", "hello-wtf")

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

        p.data = {"foo": "bar.json"}
        p.write_frontmatter()
        with open(os.path.join(p.data_path, 'bar.json'), 'w+') as f:
            f.write('[{"foo": "bar"}]')
        p.sync_frontmatter()
        p.metadata['data']['foo']

        p.data = {"foo": "bar.yml"}
        p.write_frontmatter()
        with open(os.path.join(p.data_path, 'bar.yml'), 'w+') as f:
            f.write('- foo: bar')
        p.sync_frontmatter()
        p.metadata['data']['foo']

    def test_baddata(self):
        p = PageList()['my-second-fake-page']

        p.data = {"foo": "bar.csv"}
        p.write_frontmatter()
        with self.assertRaises(exceptions.BadMetadata):
            p.sync_frontmatter()
        p.data = {}
        p.write_frontmatter()

        os.path.exists(p.data_path) or os.mkdir(p.data_path)
        with open(os.path.join(p.data_path, 'foo.txt'), 'w+') as f:
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


class DropCapTest(SimpleTestCase):
    """
    Tests for the dropcap template filter
    """
    def test_dropcap(self):
        self.assertEqual(
            dropcap("Foo bar"),
            "<span class='dropcap'>F</span>oo bar"
        )
        self.assertEqual(
            dropcap("Foo bar", autoescape=False),
            "<span class='dropcap'>F</span>oo bar"
        )
        self.assertEqual(dropcap(""), "")


class JsonifyTest(SimpleTestCase):
    """
    Test the jsonify template filter
    """
    def test_jsonify(self):
        p = Page(slug='test-sans', published=True)
        jsonify(p)
        jsonify(dict(foo="bar"))
