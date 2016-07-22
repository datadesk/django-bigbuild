#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import six
import logging
from django.conf import settings
from collections import Sequence
from bigbuild.exceptions import (
    MissingMetadataWarning,
    MissingRecommendedMetadataWarning
)
from bigbuild.models import Page, RetiredPage
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
        # Create a combined list of live pages and retired pages
        self.pages = []
        self.pages.extend(self.get_dynamic_pages())
        self.pages.extend(self.get_retired_pages())
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

    def get_page_list(self, path, pagetype):
        """
        Returns a list of Page objects from the provided directory path.
        """
        page_list = []
        # Loop through all of the directories in the page directory
        for d in os.listdir(path):
            # Ignore any names in our blacklist
            if d in getattr(settings, 'PAGE_BLACKLIST', ['.DS_Store']):
                continue

            # Create a Page object from the directory slug
            page = pagetype(d)

            # Verify it has frontmatter and is a qualified page
            if not os.path.exists(page.frontmatter_path):
                # If it doesn't have frontmatter broadcast a warning
                # to the developer and skip this directory.
                warning = MissingMetadataWarning(page)
                logger.warn(warning)
                continue

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

            page_list.append(page)

        # Return the page_list
        return page_list

    def get_dynamic_pages(self):
        """
        Returns a list of Page objects ready to be built
        in this environment.
        """
        return [
            p for p in self.get_page_list(self.dynamic_directory, Page)
            if p.should_build()
        ]

    def get_retired_pages(self):
        """
        Returns a list of RetiredPage objects ready to be built
        in this environment.
        """
        return [
            p for p in self.get_page_list(self.retired_directory, RetiredPage)
            if p.should_build()
        ]
