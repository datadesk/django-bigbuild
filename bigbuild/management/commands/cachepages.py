#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import six
import bigbuild
from bigbuild.models import PageList
from django.core.management.base import BaseCommand
from bigbuild.serializers import BigBuildJSONSerializer


class Command(BaseCommand):
    help = "Cache page metadata to increase the application speed"

    def handle(self, *args, **options):
        # Set the cache path for archived pages
        archive_cache_path = os.path.join(bigbuild.get_archive_directory(), '.cache')

        # Delete it if it already exists
        if os.path.exists(archive_cache_path):
            os.remove(archive_cache_path)

        # Pull the live PageList from the YAML files
        page_list = PageList()

        # Create a JSON serializer
        serializer = BigBuildJSONSerializer()

        # Save the archived pages out to a new cache
        with io.open(archive_cache_path, 'w', encoding='utf8') as f:
            data = serializer.serialize(page_list.archived_pages)
            f.write(six.text_type(data))
