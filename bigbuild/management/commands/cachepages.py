#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime
from bigbuild.models import PageList
from bigbuild import get_archive_directory
from django.core.management.base import BaseCommand


def serializer(obj):
    """
    JSON serializer for objects not serializable by default json code
    """
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


class Command(BaseCommand):
    help = "Cache page metadata to increase the application speed"

    def handle(self, *args, **options):
        # Set the cache path for archived pages
        archive_cache_path = os.path.join(get_archive_directory(), '.cache')

        # Delete it if it already exists
        if os.path.exists(archive_cache_path):
            os.remove(archive_cache_path)

        # Pull the live PageList from the YAML files
        page_list = PageList()

        # Save the archived pages out to a new cache
        with open(archive_cache_path, 'w') as f:
            json.dump(
                dict(archived_pages=[p.to_json() for p in page_list.archived_pages]),
                f,
                default=serializer
            )
