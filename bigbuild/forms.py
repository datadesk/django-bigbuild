#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .models import Page
from django.forms import ModelForm


class PageForm(ModelForm):
    """
    Form for editing pages.
    """
    class Meta:
        model = Page
        fields = [
            'headline',
            'byline',
            'description',
            'image_url',
            'pub_date',
            'published',
            'show_in_feeds',
            'content',
            'extra'
        ]
