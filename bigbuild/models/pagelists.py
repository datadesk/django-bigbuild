#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import six
import json
import logging
from django.conf import settings
from collections import Sequence
from bigbuild.exceptions import (
    MissingMetadataWarning,
    MissingRecommendedMetadataWarning
)
from bigbuild.models import Page, RetiredPage
from dateutil.parser import parse as dateparse
from bigbuild import get_page_directory, get_retired_directory
logger = logging.getLogger(__name__)


class PageList(Sequence):
    """
    A list of all the Page objects in the application.
    """
    def __init__(self):
        # Set the page directories
        self.dynamic_directory = get_page_directory()
        self.retired_directory = get_retired_directory()

        # Set the cache path
        self.retired_cache_path = os.path.join(self.retired_directory, '.cache')

        # Pull the pages
        self.dynamic_pages = self.get_dynamic_pages()
        self.retired_pages = self.get_retired_pages()

        # Create a combined list of live pages and retired pages
        self.pages = []
        self.pages.extend(self.dynamic_pages)
        self.pages.extend(self.retired_pages)

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

    def get_page(self, directory, pagetype):
        """
        Returns a list of Page objects from the provided directory path.
        """
        # Ignore any names in our blacklist
        if directory in getattr(settings, 'PAGE_BLACKLIST', ['.DS_Store']):
            return None

        # Create a Page object from the directory slug
        page = pagetype(directory)

        # Verify it has frontmatter and is a qualified page
        if not os.path.exists(page.frontmatter_path):
            # If it doesn't have frontmatter broadcast a warning
            # to the developer and skip this directory.
            warning = MissingMetadataWarning(page)
            logger.warn(warning)
            return None

        # Sync in the metadata from the filesystem to the object
        page.sync_frontmatter()

        # Make sure the page is valid
        if not page.is_metadata_valid():
            raise ValueError("Metadata is not valid for %s" % page)

        # Make sure the page has recommended metadata
        # ... if it's ready to publish
        if page.pub_status in ['live', 'pending']:
            if not page.has_recommended_metadata():
                logger.warn(MissingRecommendedMetadataWarning(page))

        return page

    def get_dynamic_pages(self):
        """
        Returns a list of Page objects ready to be built
        in this environment.
        """
        logger.debug("Retrieving dynamic page list")
        page_list = []
        for d in os.listdir(self.dynamic_directory):
            page = self.get_page(d, Page)
            if page and page.should_build():
                page_list.append(page)
        logger.debug("{} dynamic pages retrieved".format(len(page_list)))
        return page_list

    def get_retired_pages(self):
        """
        Returns a list of RetiredPage objects ready to be built
        in this environment.
        """
        # Pull the cached data if it exists
        if os.path.exists(self.retired_cache_path):
            logger.debug("Loading cached retired page list")
            with open(self.retired_cache_path, 'rb') as f:
                page_list = []
                dict_list = json.load(f)['retired_pages']
                for d in dict_list:
                    d['pub_date'] = dateparse(d['pub_date'])
                    p = RetiredPage(**d)
                    page_list.append(p)
        # Otherwise get them from the YAML
        else:
            logger.debug("Retrieving YAML retired page list")
            page_list = []
            for d in os.listdir(self.retired_directory):
                page = self.get_page(d, RetiredPage)
                if page and page.should_build():
                    page_list.append(page)

        # Log and return
        logger.debug("{} retired pages retrieved".format(len(page_list)))
        return page_list
