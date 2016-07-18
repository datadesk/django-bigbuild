#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import BasePage


class RetiredPage(BasePage):
    """
    A retired custom page published via static.latimes.com
    """
    # The directory where pages are stored
    DIR_NAME = 'RETIRED_DIR'
