#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import PageList
from bakery.views import BuildableListView


class SitemapView(BuildableListView):
    """
    A list of all static pages in a Sitemap ready for Google.
    """
    build_path = 'projects/sitemap.xml'
    template_name = 'bigbuild/sitemap.xml'

    def get_queryset(self):
        return [p for p in PageList() if p.show_in_feeds]

    def render_to_response(self, context):
        return super(SitemapView, self).render_to_response(
            context,
            content_type='text/xml'
        )


class GoogleNewsSitemapView(SitemapView):
    """
    A list of the most recent graphics in a Sitemap ready for Google News.
    """
    build_path = 'projects/google-news-sitemap.xml'
    template_name = 'bigbuild/google-news-sitemap.xml'

    def get_queryset(self):
        return [p for p in PageList() if p.show_in_feeds][:25]
