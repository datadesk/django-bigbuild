#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shelve
from bigbuild.models import PageList
from bigbuild import get_retired_directory
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cache page metadata to increase the application speed"

    def handle(self, *args, **options):
        # Set the cache path for retired pages
        retired_cache_path = os.path.join(get_retired_directory(), '.cache')

        # Delete it if it already exists
        if os.path.exists(retired_cache_path):
            os.remove(retired_cache_path)

        # Pull the live PageList from the YAML files
        page_list = PageList()

        # Save the retired pages out to a new cache
        d = shelve.open(retired_cache_path)
        d['retired_pages'] = page_list.retired_pages
        d.close()
