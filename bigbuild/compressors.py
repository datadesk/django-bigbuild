#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slimmed down subclasses of django-compressor internals that aim to work
without django.contrib.staticfiles installed.
"""
import codecs
from django.conf import settings
from bigbuild import get_base_url
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
    def get_basename(self, url):
        """
        Takes full path to a static file (eg. "/static/css/style.css") and
        returns path with storage's base url removed (eg. "css/style.css").
        """
        base_url = get_base_url()
        if not url.startswith(base_url):
            raise UncompressableFileError("'%s' isn't accessible via "
                                          "COMPRESS_URL ('%s') and can't be "
                                          "compressed" % (url, base_url))
        basename = url.replace(base_url, "", 1)
        # drop the querystring, which is used for non-compressed cache-busting.
        return basename.split("?", 1)[0]

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
    """
    Our custom CSS compressor.
    """
    def __init__(self, content=None, output_prefix="css", context=None):
        """
        Override that introduces a new setting, COMPRESS_CSS_ENABLED, that lets only CSS compression be turned off.
        """
        if getattr(settings, 'COMPRESS_CSS_ENABLED', True):
            filters = list(settings.COMPRESS_CSS_FILTERS)
        else:
            filters = list()
        super(CssCompressor, self).__init__(content, output_prefix, context, filters)


class SimpleJsCompressor(JsCompressor, SimpleCompressor):
    """
    Our custom JavaScript compressor.
    """
    def __init__(self, content=None, output_prefix="js", context=None):
        """
        Override that introduces a new setting, COMPRESS_HS_ENABLED, that lets only JS compression be turned off.
        """
        if getattr(settings, 'COMPRESS_JS_ENABLED', True):
            filters = list(settings.COMPRESS_JS_FILTERS)
        else:
            filters = []
        super(JsCompressor, self).__init__(content, output_prefix, context, filters)
