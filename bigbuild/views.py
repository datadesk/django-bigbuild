#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from django.urls import reverse
from django.http import Http404
from django.conf import settings
from django.views.static import serve
from bigbuild.models import PageList, Page, ArchivedPage
from bigbuild import get_page_directory, get_archive_directory, get_base_url
from bigbuild.management.commands.build import Command as Build
from bakery.views import (
    BuildableTemplateView,
    BuildableDetailView,
    Buildable404View,
    BuildableRedirectView
)


class BigBuildMixin(object):
    """
    A class-based view mixin with utilities for our bigbuild pages.
    """
    def joinpath(self, *args):
        """
        Returns a joined path with the front slash of the first argument always sliced off.

        Allows for automatically generated URLs from elsewhere in the app be used as relative build paths.
        """
        args = list(args)
        first = args.pop(0)[1:]
        args.insert(0, first)
        return os.path.join(*args)


class Static404View(Buildable404View):
    """
    The 404 page.
    """
    template_name = "bigbuild/404.html"
    build_path = "404.html"


class RobotsView(BuildableTemplateView, BigBuildMixin):
    """
    The robots.txt file.
    """
    template_name = "bigbuild/robots.txt"

    @property
    def build_path(self):
        return self.joinpath(get_base_url(), "robots.txt")


class IndexRedirectView(BuildableRedirectView, BigBuildMixin):
    """
    Redirects the root URL to /projects/
    """
    url = get_base_url()

    @property
    def build_path(self):
        return self.joinpath(reverse('bigbuild-index-redirect'), "index.html")


class PageListView(BuildableTemplateView, BigBuildMixin):
    """
    Renders a homepage with a list of all the pages.
    """
    template_name = "bigbuild/page_list.html"

    @property
    def build_path(self):
        return self.joinpath(reverse('bigbuild-page-list'), "index.html")

    def get_context_data(self):
        PAGE_PUBLICATION_STATUS = getattr(
            settings,
            'PAGE_PUBLICATION_STATUS',
            'working'
        )
        return {
            'object_list': [p for p in PageList() if p.show_in_feeds],
            'PAGE_PUBLICATION_STATUS': PAGE_PUBLICATION_STATUS
        }


class PageDetailView(BuildableDetailView):
    """
    Renders one of the page objects as an HTML response.
    """
    _queryset = None

    def get_queryset(self):
        if self._queryset:
            return self._queryset
        else:
            qs = PageList()
            self._queryset = qs
            return qs

    def get_object(self):
        qs = self.get_queryset()
        return qs[self.kwargs.get("slug")]

    def get_template_names(self):
        return [os.path.join(self.object.slug, "index.html")]

    def get_context_data(self, object=None):
        return {
            'metadata': self.object.metadata,
            'object': self.object,
            'STATIC_URL': self.object.get_static_url()
        }

    def get_build_directory(self):
        if getattr(settings, 'BUILD_DIR', False):
            return settings.BUILD_DIR
        else:
            return os.path.join(settings.BASE_DIR, '.build')

    def build_static_directory(self, obj):
        """
        Builds an object's static subdirectory.
        """
        source_dir = obj.static_path
        target_dir = os.path.join(
            self.get_build_directory(),
            obj.get_static_url()[1:]
        )
        if settings.BAKERY_GZIP:
            Build().copytree_and_gzip(
                source_dir,
                target_dir
            )
        else:
            os.path.exists(target_dir) and shutil.rmtree(target_dir)
            shutil.copytree(source_dir, target_dir)

    def build_object(self, obj):
        if isinstance(obj, Page):
            super(PageDetailView, self).build_object(obj)
            self.build_static_directory(obj)
        elif isinstance(obj, ArchivedPage):
            target = os.path.join(self.get_build_directory(), obj.get_absolute_url()[1:])
            os.path.exists(target) and shutil.rmtree(target)
            if settings.BAKERY_GZIP:
                Build().copytree_and_gzip(
                    obj.archive_static_directory_path,
                    target
                )
            else:
                shutil.copytree(obj.archive_static_directory_path, target)

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]


class PageArchiveView(PageDetailView):

    def get_context_data(self, object=None):
        context = super(PageArchiveView, self).get_context_data(object=object)
        context['ARCHIVAL'] = True
        return context


def page_static_serve(request, slug, path):  # pragma: no cover
    """
    Serves files from the ./static/ subdirectory for every page.
    """
    # Set the path to the file
    path = os.path.join(slug, 'static', path)
    # First test if it can be found in the PAGE_DIR
    try:
        return serve(
            request,
            path,
            document_root=get_page_directory(),
            show_indexes=True
        )
    # If it can't try to fallback to the BIGBUILD_ARCHIVE_DIR
    except Http404:
        return serve(
            request,
            path,
            document_root=os.path.join(get_archive_directory(), 'static'),
            show_indexes=True
        )
