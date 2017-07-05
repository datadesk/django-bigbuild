#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import six
import logging
import bigbuild
from django.conf import settings
from collections import Sequence
from bigbuild.serializers import deserializers
from bigbuild.serializers import BigBuildJSONDeserializer
logger = logging.getLogger(__name__)


class PageList(Sequence):
    """
    A list of all the Page objects in the application.
    """
    def __init__(self):
        # Set the page directories
        self.dynamic_directory = bigbuild.get_page_directory()
        self.archived_directory = bigbuild.get_archive_directory()

        # Set the cache path
        self.archived_cache_path = os.path.join(self.archived_directory, '.cache')

        # Pull the pages
        self.dynamic_pages = self.get_dynamic_pages()
        self.archived_pages = self.get_archived_pages()

        # Create a combined list of live pages and archived pages
        self.pages = []
        self.pages.extend(self.dynamic_pages)
        self.pages.extend(self.archived_pages)

        # Sort first by reverse chron
        self.pages = sorted(
            self.pages,
            key=lambda o: o.pub_date,
            reverse=True
        )

        # Then sort the working pages to the top
        self.pages = sorted(self.pages, key=lambda o: o.is_live())

    def __iter__(self):
        """
        What to use when this PageList is used in a for loop.
        """
        return iter(self.pages)

    def __len__(self):
        """
        Returns the number of pages in this PageList.
        """
        return len(self.pages)

    def __getitem__(self, key):
        """
        Pull items either with a slug key or an integer index.
        """
        if isinstance(key, six.string_types):
            try:
                return [i for i in self.pages if i.slug == key][0]
            except IndexError:
                raise KeyError("No page with that slug was found")
        elif isinstance(key, int):
            try:
                return self.pages[key]
            except IndexError:
                raise IndexError("No page with this key could be found")

    @staticmethod
    def get_page(slug, pagetype):
        """
        Returns a list of Page objects from the provided slug directory.
        """
        # Create a Page object from the directory slug
        deserializer = deserializers[pagetype]()
        return deserializer.deserialize(slug)

    def get_directory_list(self, path):
        """
        Returns the list of slugged page modules in the provided directory.
        """
        # Get the list of directories found on the filesystem
        dir_list = os.listdir(path)

        # Omit any that are on our blacklist
        blacklist = getattr(settings, 'BIGBUILD_PAGE_BLACKLIST', ['.DS_Store'])
        dir_list = [d for d in dir_list if d not in blacklist]

        # Return what remains
        return dir_list

    def get_dynamic_pages(self):
        """
        Returns a list of Page objects ready to be built in this environment.
        """
        page_list = []
        for d in self.get_directory_list(self.dynamic_directory):
            page = self.get_page(d, 'Page')
            if page and page.should_build():
                page_list.append(page)
        logger.debug("{} dynamic pages retrieved from YAML".format(len(page_list)))
        return page_list

    def get_archived_pages(self):
        """
        Returns a list of ArchivedPage objects ready to be built in this environment.
        """
        # Pull the cached data if it exists
        if os.path.exists(self.archived_cache_path):
            with open(self.archived_cache_path, 'r') as f:
                page_list = [
                    o.object for o in
                    BigBuildJSONDeserializer(f.read())
                    if o.object.should_build()
                ]
            logger.debug("{} archived pages retrieved from cache".format(len(page_list)))
        # Otherwise get them from the YAML
        else:
            page_list = []
            for d in self.get_directory_list(os.path.join(self.archived_directory, 'static')):
                page = self.get_page(d, 'ArchivedPage')
                if page and page.should_build():
                    page_list.append(page)
            logger.debug("{} archived pages retrieved from YAML".format(len(page_list)))

        # Log and return
        return page_list
