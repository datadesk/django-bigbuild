#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import Page
from django.core.management.base import BaseCommand, CommandError


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
        parser.add_argument(
            '--sans',
            action='store_true',
            dest='sans',
            default=False,
            help='Create a page that uses our alternative sans-serif theme'
        )
        parser.add_argument(
            '--dark',
            action='store_true',
            dest='dark',
            default=False,
            help='Create a page that uses our alternative dark theme'
        )

    def set_options(self, *args, **options):
        """
        Configures the command based on user input.
        """
        self.force = options['force']
        self.sans = options['sans']
        self.dark = options['dark']
        self.slug_list = options['slug']

    def create_page(self, slug):
        """
        Returns a new Page object given the slug submitted by the user.
        """
        return Page(slug)

    def handle(self, *args, **options):
        """
        Make it happen.
        """
        # Set the options
        self.set_options(*args, **options)

        # Loop through the slugs and create pages
        for slug in self.slug_list:

            # Create the Page
            page = self.create_page(options['slug'])

            # If the directory already exists and we're not forcing creation
            # an error should be thrown.
            if (
                page.directory_exists or page.retired_directory_exists
            ) and not self.force:
                    raise CommandError(
                        self.style.ERROR('Page directory already exists')
                    )
            # Otherwise we make the page
            else:
                page.create_directory(
                    force=self.force,
                    index_template_name=self.INDEX_TEMPLATE_NAME,
                    index_template_context=dict(
                        sans=self.sans,
                        dark=self.dark,
                    )
                )

            # Print out the result
            self.stdout.write(self.style.SUCCESS('Created page "%s"' % page))
