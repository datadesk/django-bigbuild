#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import bigbuild
from bigbuild.tests import TestBase
from bigbuild.tests import BUILD_DIR
from django.test import override_settings
from bigbuild.models import PageList, Page
from bigbuild import get_archive_directory
from django.core.management import call_command
from django.core.management.base import CommandError
logging.disable(logging.CRITICAL)


class TestCommands(TestBase):

    def test_build(self):
        Page.create(slug="yet-another-fake-page")
        Page.create(slug="my-archived-page")
        call_command("build")
        self.assertTrue(os.path.exists(BUILD_DIR))
        expected_index = os.path.join(
            BUILD_DIR,
            PageList()['yet-another-fake-page'].get_absolute_url().lstrip("/"),
            'index.html'
        )
        self.assertTrue(os.path.exists(expected_index))
        PageList()[0].build()
        with override_settings(BUILD_DIR=''):
            bigbuild.get_build_directory()

    @override_settings(BIGBUILD_GIT_BRANCH='test', BIGBUILD_BRANCH_BUILD=True)
    def test_branch_build(self):
        call_command("build")
        self.assertTrue(os.path.exists(os.path.join(BUILD_DIR, 'test')))
        self.assertTrue('test' in bigbuild.get_base_url())

    @override_settings(BIGBUILD_BRANCH_BUILD=False)
    def test_base_url(self):
        bigbuild.get_base_url()

    @override_settings(BAKERY_GZIP=True)
    def test_gzip(self):
        call_command("build")

    def test_validatepages(self):
        call_command("validatepages")

    def test_createpage(self):
        call_command("createpage", "test-page")
        with self.assertRaises(ValueError):
            call_command("createpage", "test-page")
        call_command("createpage", "test-page", force=True)

    def test_archivepage(self):
        p = Page.create(slug='test-archived-page')
        call_command("archivepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("archivepage", p.slug)
        with self.assertRaises(CommandError):
            call_command("archivepage", "hello-wtf")
        call_command("unarchivepage", "test-archived-page")

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
