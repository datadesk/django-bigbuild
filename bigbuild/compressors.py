#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slimmed down subclasses of django-compressor internals that aim to work
without django.contrib.staticfiles installed.
"""
import codecs
from django.conf import settings
from compressor.base import Compressor
from compressor.js import JsCompressor
from compressor.css import CssCompressor
from django.template import Template, Context
from compressor.exceptions import UncompressableFileError


class SimpleCompressor(Compressor):
    """
    A simplification of django-compressor's standard compression class.

    The aim is to work without django.contrib.staticfiles installed.
    """
    def get_filename(self, basename):
        """
        A simplification of the standard method to remove a hack around
        the staticfiles caching system we don't want.
        """
        # Get the filename from our storage backend
        filename = self.storage.path(basename)

        # If it exists, return it
        if self.storage.exists(basename):
            return filename

        # If it doesn't, raise an exception
        raise UncompressableFileError(
            "'%s' could not be found in the COMPRESS_ROOT '%s'%s" %
            (basename, settings.COMPRESS_ROOT,
             self.finders and " or with staticfiles." or "."))

    def precompile(
        self,
        content,
        kind=None,
        elem=None,
        filename=None,
        charset=None,
        **kwargs
    ):
        """
        An expansion of the standard method that will halt precompilation
        when compression is off.
        """
        # If compression is off, skip it
        if not kind or not settings.COMPRESS_ENABLED:
            return False, content

        # Clear out the filename settings so the compilers will use
        # the rendered in-memory string and a temporary file instead.
        kwargs.pop("basename", "")
        filename = None

        # Otherwise compile away as usual
        return super(SimpleCompressor, self).precompile(
            content,
            kind,
            elem,
            filename,
            charset,
            **kwargs
        )

    def get_filecontent(self, filename, charset):
        """
        A custom override that renders file content as a Django template
        with the page context included.

        This allows for metadata from the page object to be included in
        static files.
        """
        if charset == 'utf-8':
            # Removes BOM
            charset = 'utf-8-sig'
        with codecs.open(filename, 'r', charset) as fd:
            # All the custom bits are right here
            content = fd.read()
            template = Template(content)
            context = Context(self.context)
            rendered_content = template.render(context)
            return rendered_content


class SimpleCssCompressor(CssCompressor, SimpleCompressor):
    pass


class SimpleJsCompressor(JsCompressor, SimpleCompressor):
    pass
