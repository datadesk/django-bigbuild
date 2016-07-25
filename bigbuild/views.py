#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from django.http import Http404
from django.conf import settings
from django.views.static import serve
from bigbuild.models import PageList, Page, RetiredPage
from bigbuild import get_page_directory, get_retired_directory
from bigbuild.management.commands.build import Command as Build
from bakery.views import (
    BuildableTemplateView,
    BuildableDetailView,
    Buildable404View,
    BuildableRedirectView
)


class Static404View(Buildable404View):
    """
    The 404 page.
    """
    template_name = "bigbuild/404.html"
    build_path = "404.html"


class RobotsView(BuildableTemplateView):
    """
    The robots.txt file.
    """
    template_name = "bigbuild/robots.txt"
    build_path = "projects/robots.txt"


class IndexRedirectView(BuildableRedirectView):
    """
    Redirects the root URL to /projects/
    """
    build_path = "index.html"
    url = "/projects/"


class PageListView(BuildableTemplateView):
    """
    Renders a homepage with a list of all the pages.
    """
    template_name = "bigbuild/page_list.html"
    build_path = "projects/index.html"

    def get_context_data(self):
        PAGE_PUBLICATION_STATUS = getattr(
            settings,
            'PAGE_PUBLICATION_STATUS',
            'working'
        )
        return {
            'object_list': PageList(),
            'PAGE_PUBLICATION_STATUS': PAGE_PUBLICATION_STATUS
        }


class PageDetailView(BuildableDetailView):
    """
    Renders one of the page objects as an HTML response.
    """
    def get_queryset(self):
        return PageList()

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

    def build_static_directory(self, obj):
        """
        Builds an object's static subdirectory.
        """
        source_dir = obj.static_path
        target_dir = os.path.join(
            settings.BUILD_DIR,
            'projects',
            obj.slug,
            'static'
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
        elif isinstance(obj, RetiredPage):
            target = os.path.join(settings.BUILD_DIR, 'projects', obj.slug)
            os.path.exists(target) and shutil.rmtree(target)
            if settings.BAKERY_GZIP:
                Build().copytree_and_gzip(
                    obj.directory_path,
                    target
                )
            else:
                shutil.copytree(obj.directory_path, target)

    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]


class PageRetireView(PageDetailView):

    def get_context_data(self, object=None):
        context = super(PageRetireView, self).get_context_data(object=object)
        context['RETIREMENT'] = True
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
    # If it can't try to fallback to the RETIRED_DIR
    except Http404:
        return serve(
            request,
            path,
            document_root=get_retired_directory(),
            show_indexes=True
        )
