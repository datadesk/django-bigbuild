#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import BasePage
from bigbuild import get_retired_directory


class RetiredPage(BasePage):
    """
    A retired custom page published via static.latimes.com
    """
    @property
    def base_directory(self):
        """
        Returns retired directory for pages.
        """
        return get_retired_directory()
