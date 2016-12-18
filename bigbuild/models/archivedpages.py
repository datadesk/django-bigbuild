#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from bigbuild.models import BasePage


class ArchivedPage(BasePage):
    """
    An archived custom page.
    """
    def delete(self):
        """
        Delete the page directory.
        """
        if os.path.exists(self.archive_dynamic_directory_path):
            shutil.rmtree(self.archive_dynamic_directory_path)
        if os.path.exists(self.archive_static_directory_path):
            shutil.rmtree(self.archive_static_directory_path)

    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        return os.path.join(self.archive_static_directory_path, 'metadata.md')
