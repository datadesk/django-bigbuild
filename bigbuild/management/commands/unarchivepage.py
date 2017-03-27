#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from django.core.management import call_command
from bigbuild.models import PageList, ArchivedPage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Retrieve an archived page and return it to our dynamic page directory"
    args = "<slug>"

    def add_arguments(self, parser):
        parser.add_argument('slug', nargs='+', type=str)

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        # Loop through the slugs
        for slug in options['slug']:
            try:
                p = PageList()[slug]
            except:
                raise CommandError("Slug provided (%s) does not exist" % slug)

            # Make sure it's an archived page
            if not isinstance(p, ArchivedPage):
                raise CommandError("Slug (%s) is not a ArchivedPage object" % slug)

            # Make sure the dynamic page is archived (some of our older retired pages are static-only)
            if not os.path.exists(p.archive_dynamic_directory_path):
                raise CommandError("Slug (%s) does not have dynamic content archived. It cannot be retrieved." % slug)

            # Copy the archive's dynamic page to our live dynamic directory
            shutil.copytree(p.archive_dynamic_directory_path, p.page_directory_path)

            # Delete the archived directories
            p.delete()

        # Update the cache
        call_command("cachepages")
