#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import Page
from django.utils.text import slugify
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a new page directory'
    INDEX_TEMPLATE_NAME = 'bigbuild/pages/default_index.html'

    def add_arguments(self, parser):
        """
        Custom arguments for this command
        """
        parser.add_argument('slug', nargs='+', type=str)
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force overwrite of the page directory if it already exists'
        )

    def set_options(self, *args, **options):
        """
        Configures the command based on user input.
        """
        self.force = options['force']
        self.slug_list = [slugify(s) for s in options['slug']]

    def create_page(self, slug):
        """
        Returns a new Page object given the slug submitted by the user.
        """
        return Page.create(
            slug=slug,
            force=self.force,
            index_template_name=self.INDEX_TEMPLATE_NAME
        )

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        # Set the options
        self.set_options(*args, **options)

        # Loop through the slugs and create pages
        for slug in self.slug_list:

            # Create the Page
            page = self.create_page(slug)

            # Print out the result
            self.stdout.write(self.style.SUCCESS('Created page "%s"' % page))
