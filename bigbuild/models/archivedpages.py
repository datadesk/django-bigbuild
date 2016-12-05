#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from bigbuild.models import BasePage


class ArchivedPage(BasePage):
    """
    An archived custom page.
    """
    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        return os.path.join(self.archive_dynamic_directory_path, 'metadata.md')
