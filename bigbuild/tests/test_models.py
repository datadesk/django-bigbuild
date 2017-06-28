#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from bigbuild import exceptions
from bigbuild.tests import TestBase
from django.test import override_settings
from bigbuild.views import PageDetailView
from bigbuild.models import PageList, Page
from django.core.serializers.base import DeserializationError
logging.disable(logging.CRITICAL)


class TestModels(TestBase):

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

    def test_sans(self):
        p = Page(slug='test-sans', published=True)
        p.create_directory(index_template_context={'sans': True})

    def test_dark(self):
        p = Page.create(slug='test-dark')
        p.create_directory(index_template_context={'dark': True})

    def test_deletepage(self):
        p = PageList()[0]
        p.delete()

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
