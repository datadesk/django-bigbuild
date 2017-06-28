#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from bigbuild.tests import TestBase
from django.test import override_settings
from django.core.management import call_command
from bigbuild.compressors import SimpleCompressor
from compressor.exceptions import UncompressableFileError
logging.disable(logging.CRITICAL)


class TestStatic(TestBase):

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
