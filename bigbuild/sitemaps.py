#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse
from bigbuild.models import PageList
from bakery.views import BuildableListView


class SitemapView(BuildableListView):
    """
    A list of all static pages in a Sitemap ready for Google.
    """
    template_name = 'bigbuild/sitemap.xml'

    @property
    def build_path(self):
        return reverse('bigbuild-sitemap').lstrip("/")

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
    template_name = 'bigbuild/google-news-sitemap.xml'

    @property
    def build_path(self):
        return reverse('bigbuild-google-news-sitemap').lstrip("/")

    def get_queryset(self):
        return [p for p in PageList() if p.show_in_feeds][:25]
