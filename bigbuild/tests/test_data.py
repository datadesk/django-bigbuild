#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from bigbuild.tests import TestBase
from bigbuild.models import PageList
from django.core.management import call_command
logging.disable(logging.CRITICAL)


class TestData(TestBase):

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
        p.refresh_from_db()

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
        p.refresh_from_db()

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
        p.refresh_from_db()

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
        p.refresh_from_db()

        # Make sure everything matches
        self.assertEqual(p.metadata['data']['foo'], "static/bar.yaml")
        self.assertEqual(p.data_objects['foo'][0]['key'], 'value')

        # Make sure we can archive aml
        call_command("archivepage", p.slug)
        call_command("unarchivepage", p.slug)

        p.delete()
