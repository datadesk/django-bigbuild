#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import Page
from greeking import latimes_ipsum
from bigbuild.management.commands.createpage import Command as BaseCommand


class Command(BaseCommand):
    help = 'Creates a new page directory for an interactive infographic'
    INDEX_TEMPLATE_NAME = 'bigbuild/pages/graphic_index.html'

    def create_page(self, slug):
        obj = latimes_ipsum.get_story()
        return Page(
            slug,
            headline=obj.headline,
            description=obj.description,
            byline=obj.byline,
            extra=dict(
                credits='Credits TK',
                sources='Sources TK',
                more_like_this=[o.__dict__ for o in latimes_ipsum.get_related_items()],
            )
        )
