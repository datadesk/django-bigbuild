#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from bakery.management.commands.publish import Command as BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        # When in BIGBUILD_BRANCH_BUILD don't delete because we'll be syncing
        # a different subdirectory for each one of our git branches
        if getattr(settings, 'BIGBUILD_BRANCH_BUILD', False):
            options['no_delete'] = True
        super(Command, self).handle(*args, **options)
