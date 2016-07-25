#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from bigbuild import views, feeds, sitemaps


urlpatterns = [
    # Index redirect
    url(r'^$', views.IndexRedirectView.as_view(), name="index-redirect"),

    # Pages
    url(r'^projects/$', views.PageListView.as_view(), name='page-list'),
    url(
        r'^projects/(?P<slug>[-\w]+)/$',
        views.PageDetailView.as_view(),
        name='page-detail'
    ),

    # Static assets
    url(
        r'^projects/(?P<slug>[-\w]+)/static/(?P<path>.*)$',
        views.page_static_serve,
        name='page-detail-static'
    ),

    # Machine-readable feeds
    url(
        r'^projects/sitemap.xml$',
        sitemaps.SitemapView.as_view(),
        name='sitemap'
    ),
    url(
        r'^projects/google-news-sitemap.xml$',
        sitemaps.GoogleNewsSitemapView.as_view(),
        name='google-news-sitemap'
    ),
    url(
        r'^projects/feeds/latest.xml$',
        feeds.LatestPages(),
        name="feeds-latest"
    ),
]
