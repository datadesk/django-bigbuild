#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from bigbuild.models import BasePage
from bigbuild import get_archive_directory


class ArchivedPage(BasePage):
    """
    An archived custom page.
    """
    @property
    def base_directory(self):
        """
        Returns archive directory for pages.
        """
        return get_archive_directory()

    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        return os.path.join(self.archive_dynamic_directory_path, 'metadata.md')
