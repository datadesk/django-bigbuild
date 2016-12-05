#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
