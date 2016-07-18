#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bakery.management.commands.build import Command as Build


class Command(Build):
    """
    An override of Django's base `build` command that changes some of the
    options to defaults we'd prefer here on this site.
    """
    verbosity = 1

    def handle(self, *args, **options):
        # Cut out some of the bakery defaults we don't want
        options['skip_static'] = True
        options['skip_media'] = True

        # Run the standard bakery build
        super(Command, self).handle(*args, **options)
