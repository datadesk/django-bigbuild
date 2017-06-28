#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from bigbuild.tests import TestBase
from bigbuild.views import PageListView, PageDetailView
logging.disable(logging.CRITICAL)


class TestViews(TestBase):
    """
    Tests that run against fake pages.
    """
    def test_views(self):
        PageListView.as_view()
        PageDetailView.as_view()
