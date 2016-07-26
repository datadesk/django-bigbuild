#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import Page
from greeking import latimes_ipsum
from django.template.defaultfilters import linebreaks
from bigbuild.templatetags.bigbuild_tags import dropcap
from bigbuild.management.commands.createpage import Command as BaseCommand


class Command(BaseCommand):
    help = 'Creates a new page directory for a custom "big build" story'
    INDEX_TEMPLATE_NAME = 'bigbuild/pages/bigbuild_index.html'

    def create_page(self, slug):
        obj = latimes_ipsum.get_story()
        return Page(
            slug,
            headline=obj.headline,
            description=obj.description,
            byline=obj.byline,
            content=linebreaks(dropcap(obj.content)),
            extra=dict(
                heroic_image=dict(
                    src='http://placehold.it/2000x800',
                    caption='',
                    credit=''
                ),
                credits='Credits TK',
                more_like_this=[o.__dict__ for o in latimes_ipsum.get_related_items()],
            )
        )
