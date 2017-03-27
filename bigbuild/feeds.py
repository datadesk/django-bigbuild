#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse
from bigbuild.models import PageList
from django.test import RequestFactory
from bakery.feeds import BuildableFeed


class FakeRequestFactory(RequestFactory):
    """
    A custom request faker that will make sure our domain comes out
    the right way in the RSS urls.
    """
    def get_host(self):
        return 'www.latimes.com'

    def is_secure(self):
        return False

    @property
    def path(self):
        return reverse('bigbuild-feeds-latest').lstrip("/")


class LatestPages(BuildableFeed):
    """
    RSS feed of the latest pages.
    """
    title = "Latest projects - Los Angeles Times"
    link = 'http://www.latimes.com/projects/latest/feeds/latest.xml'

    @property
    def build_path(self):
        return reverse('bigbuild-feeds-latest').lstrip("/")

    def items(self):
        """
        Excludes pages that have their `show_in_feeds` attribute set to False.
        """
        return [p for p in PageList() if p.show_in_feeds]

    def item_title(self, obj):
        return obj.headline

    def item_description(self, obj):
        if obj.description:
            return obj.description
        else:
            return ''

    def item_pubdate(self, obj):
        return obj.pub_date

    def item_link(self, obj):
        return obj.get_absolute_url()

    def get_feed(self, obj, request):
        request = FakeRequestFactory()
        return super(LatestPages, self).get_feed(obj, request)
