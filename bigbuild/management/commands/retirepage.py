#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from django.conf import settings
from bigbuild.views import PageRetireView
from bigbuild.models import PageList, Page
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Retire a page directory by permanently rendering its HTML"
    args = "<slug>"

    def add_arguments(self, parser):
        parser.add_argument('slug', nargs='+', type=str)

    def handle(self, *args, **options):
        # Loop through the slugs
        for slug in options['slug']:
            # Pull the object
            try:
                p = PageList()[slug]
            except:
                raise CommandError("Slug provided (%s) does not exist" % slug)

            if not isinstance(p, Page):
                raise CommandError("Slug (%s) is not a Page object" % slug)

            # Build it
            PageRetireView().build_object(p)

            # If the retired directory exists, kill it
            if os.path.exists(p.retired_directory_path):
                shutil.rmtree(p.retired_directory_path)  # pragma: no cover

            # Save that directory to the retired folder
            shutil.copytree(
                os.path.join(settings.BUILD_DIR, 'projects', p.slug),
                p.retired_directory_path,
            )

            # Save the metadata to the retired folder
            shutil.copy2(
                p.frontmatter_path,
                os.path.join(p.retired_directory_path, 'metadata.md'),
            )

            # Delete the page folder
            shutil.rmtree(p.directory_path)
