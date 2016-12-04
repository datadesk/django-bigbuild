#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from bigbuild import views, feeds, sitemaps, get_base_url


urlpatterns = [
    # Index redirect
    url(
        r'^$',
        views.IndexRedirectView.as_view(),
        name="bigbuild-index-redirect"
    ),

    # Pages
    url(
        r'^{0}$'.format(get_base_url()[1:]),
        views.PageListView.as_view(),
        name='bigbuild-page-list'
    ),
    url(
        r'^{0}(?P<slug>[-\w]+)/$'.format(get_base_url()[1:]),
        views.PageDetailView.as_view(),
        name='bigbuild-page-detail'
    ),

    # Static assets
    url(
        r'^{0}(?P<slug>[-\w]+)/static/(?P<path>.*)$'.format(get_base_url()[1:]),
        views.page_static_serve,
        name='bigbuild-page-detail-static'
    ),

    # Machine-readable feeds
    url(
        r'^{0}sitemap.xml$'.format(get_base_url()[1:]),
        sitemaps.SitemapView.as_view(),
        name='bigbuild-sitemap'
    ),
    url(
        r'^{0}google-news-sitemap.xml$'.format(get_base_url()[1:]),
        sitemaps.GoogleNewsSitemapView.as_view(),
        name='bigbuild-google-news-sitemap'
    ),
    url(
        r'^{0}feeds/latest.xml$'.format(get_base_url()[1:]),
        feeds.LatestPages(),
        name="bigbuild-feeds-latest"
    ),
]
