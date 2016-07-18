#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import PageList
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Tests if page directories are valid'

    def handle(self, *args, **options):
        page_list = PageList()
        self.stdout.write(
            self.style.SUCCESS('All %s pages are valid' % len(page_list))
        )
