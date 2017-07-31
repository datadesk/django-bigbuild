#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slimmed down subclasses of django-compressor internals that aim to work
without django.contrib.staticfiles installed.
"""
import os
from django.apps import apps
from bigbuild.models import PageList
from compressor_toolkit.precompilers import BaseCompiler
toolkit_config = apps.get_app_config('compressor_toolkit')


def get_all_static():
    """
    Returns the static directory path of all dynamic pages.
    """
    return [os.path.join(p.page_directory_path, 'static') for p in PageList().dynamic_pages]


class ES6Compiler(BaseCompiler):
    """
    django-compressor pre-compiler for ES6 files.
    """
    command = toolkit_config.ES6_COMPILER_CMD
    options = (
        ('browserify_bin', toolkit_config.BROWSERIFY_BIN),
        # Pull all the static file paths from dynamic pages plus the node_modules install directory
        ('paths', os.pathsep.join(get_all_static() + [toolkit_config.NODE_MODULES])),
        ('node_modules', toolkit_config.NODE_MODULES)
    )
    infile_ext = '.js'
