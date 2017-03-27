#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild import get_base_url
from django.conf.urls import url, include
from bigbuild import views, feeds, sitemaps


basepatterns = [
    # Pages
    url(
        r'^$',
        views.PageListView.as_view(),
        name='bigbuild-page-list'
    ),
    url(
        r'^(?P<slug>[-\w]+)/$',
        views.PageDetailView.as_view(),
        name='bigbuild-page-detail'
    ),

    # Static assets
    url(
        r'^(?P<slug>[-\w]+)/static/(?P<path>.*)$',
        views.page_static_serve,
        name='bigbuild-page-detail-static'
    ),

    # Machine-readable feeds
    url(
        r'^sitemap.xml$',
        sitemaps.SitemapView.as_view(),
        name='bigbuild-sitemap'
    ),
    url(
        r'^google-news-sitemap.xml$',
        sitemaps.GoogleNewsSitemapView.as_view(),
        name='bigbuild-google-news-sitemap'
    ),
    url(
        r'^feeds/latest.xml$',
        feeds.LatestPages(),
        name="bigbuild-feeds-latest"
    ),
    url(
        r'^robots.txt$',
        views.RobotsView.as_view(),
        name="bigbuild-robots-txt"
    ),
]


urlpatterns = [
    # Index redirect
    url(
        r'^$',
        views.IndexRedirectView.as_view(),
        name="bigbuild-index-redirect"
    ),

    # All the base patterns prefixed
    url('^{}'.format(get_base_url().lstrip("/")), include(basepatterns)),
]
