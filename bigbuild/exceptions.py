#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom exceptions and warnings
"""
from django.template import Engine, Context
from django.utils.termcolors import colorize


class BadMetadata(Exception):
    """
    A custom exception to raise when the page configuration file has
    malformed metadata.
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class BaseWarning(Warning):
    """
    A base Warning class with elements we want to reuse across all of
    our custom warnings.
    """
    BANNER_TEMPLATE = "bigbuild/warnings/banner.txt"
    FOOTER_TEMPLATE = "bigbuild/warnings/footer.txt"
    BOTTOM_BORDER = "bigbuild/warnings/bottom_border.txt"

    def render_template(self, name, context={}):
        """
        Returns the rendered template with the provided name.
        """
        engine = Engine.get_default()
        return engine.get_template(name).render(Context(context))

    def hilight(self, s):
        """
        Returns a colorized version of the provided string that is red
        and bold.
        """
        return colorize(s, fg="red", opts=('bold',))

    @property
    def banner(self):
        """
        Returns the top of every warning message
        """
        message = self.render_template(self.BANNER_TEMPLATE)
        return self.hilight(message)

    @property
    def footer(self):
        """
        Returns the bottom of every warning message
        """
        footer_message = self.render_template(self.FOOTER_TEMPLATE)
        border_message = self.render_template(self.BOTTOM_BORDER)
        return footer_message + self.hilight(border_message)

    def get_context_data(self):
        """
        Returns the data to be passed into the message template as context.
        """
        return {}

    def __str__(self):
        """
        Returns the full message for this warning, which will be what's
        printed to the console when it is logged.
        """
        message = self.render_template(
            self.template_name,
            self.get_context_data()
        )
        return self.banner + message + self.footer


class MissingMetadataWarning(BaseWarning):
    """
    A custom warning to broadcast when a page directory does not
    have a metadata.md configuration file.
    """
    template_name = "bigbuild/warnings/missing_metadata.txt"

    def __init__(self, page):
        self.page = page

    def get_context_data(self):
        return dict(page=self.page)


class MissingRecommendedMetadataWarning(BaseWarning):
    """
    A custom warning that will be raised when a published page is missing
    recommended metadata values.

    For instance, things like a headline and description are
    not required to publish a page, but you're likely to have bugs
    with how your page appears on social media if you lack them.
    """
    template_name = "bigbuild/warnings/missing_recommended_metadata.txt"

    def __init__(self, page):
        self.page = page

    def get_context_data(self):
        return dict(page=self.page)
