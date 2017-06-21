#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
import logging
import bigbuild
import jsonfield
import frontmatter
from django.db import models
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from greeking import latimes_ipsum
from django.test import RequestFactory
from bigbuild import context_processors
from bigbuild.exceptions import BadMetadata
from django.template import Engine, RequestContext
from django.utils.encoding import python_2_unicode_compatible
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class BasePage(models.Model):
    """
    An abstract base class with methods shared by all page classes.
    """
    slug = models.SlugField(primary_key=True, max_length=500)
    headline = models.CharField(max_length=1000, blank=True, default="")
    byline = models.CharField(max_length=1000, blank=True, default="")
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=1000, blank=True, default="")
    pub_date = models.DateTimeField(default=datetime.now)
    published = models.BooleanField(default=False)
    show_in_feeds = models.BooleanField(default=False)
    content = models.TextField(blank=True)
    extra = jsonfield.JSONField(blank=True)
    data = jsonfield.JSONField(blank=True)
    # A cache for data objects after they've been loaded
    data_objects = {}

    class Meta:
        abstract = True

    def __str__(self):
        return self.slug

    #
    # URLs
    #

    @models.permalink
    def get_absolute_url(self):
        return ('bigbuild-page-detail', [self.slug])

    def get_static_url(self):
        return os.path.join(self.get_absolute_url(), 'static') + "/"

    @property
    def rendered_content(self):
        """
        Returns the page's contents, which can contain Django templating tags, rendered as simple HTML.
        """
        engine = Engine.get_default()
        engine.dirs.extend([
            bigbuild.get_page_directory(),
            os.path.join(bigbuild.get_archive_directory(), 'static')
        ])
        template = engine.from_string(self.content)
        context = RequestContext(
            RequestFactory().get(self.get_absolute_url()),
            {
                "object": self,
                'STATIC_URL': self.get_static_url()
            },
            [context_processors.bigbuild]
        )
        return template.render(context)

    #
    # Actions
    #

    def delete(self):
        """
        Delete the page directory.
        """
        raise NotImplementedError

    def build(self):
        """
        Builds this page via the PageDetailView.
        """
        from bigbuild.views import PageDetailView
        view = PageDetailView()
        view.build_object(self)

    def sync_frontmatter(self):
        """
        Reads in the frontmatter from metadata.yaml and syncs it with
        the object.
        """
        with open(self.frontmatter_path) as f:
            # Parse the YAML
            try:
                post = frontmatter.load(f)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError) as e:
                raise BadMetadata(
                    "THE METADATA.MD FILE FOR '%s' IS BROKEN! \n" % self.slug +
                    "Here's a clue about what's wrong: \n" +
                    "%s" % e
                )

            # Set the basic frontmatter metadata
            self.headline = post.metadata['headline']
            self.byline = post.metadata['byline']
            self.description = post.metadata['description']
            self.image_url = post.metadata['image_url']
            self.pub_date = post.metadata['pub_date']
            self.published = post.metadata['published']
            self.show_in_feeds = post.metadata['show_in_feeds']

            # Attach any extra stuff
            try:
                self.extra = post.metadata['extra']
            except KeyError:
                self.extra = {}

            try:
                self.data = post.metadata['data']
            except KeyError:
                self.data = {}

            # Pull in the content as is
            self.content = post.content
            # Render it out as flat HTML
            self.content = self.rendered_content

    #
    # File pathing
    #

    @property
    def page_directory_path(self):
        """
        Returns the directory path where this page will be stored.
        """
        return os.path.join(bigbuild.get_page_directory(), self.slug)

    @property
    def build_directory_path(self):
        """
        Returns the directory path where this page will be "baked" as flat files.
        """
        return os.path.join(bigbuild.get_build_directory(), self.get_absolute_url().lstrip("/"))

    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        raise NotImplementedError

    @property
    def archive_dynamic_directory_path(self):
        """
        Returns the path where this page's dynamic content would be archived, if it were archived.
        """
        return os.path.join(bigbuild.get_archive_directory(), 'dynamic', self.slug)

    @property
    def archive_static_directory_path(self):
        """
        Returns the path where this page's dynamic static would be archived, if it were archived.
        """
        return os.path.join(bigbuild.get_archive_directory(), 'static', self.slug)

    #
    # Validation
    #

    def has_recommended_metadata(self):
        """
        Tests if the metadata has the fields we recommend are present
        for every page have been filled.

        Returns True or False.
        """
        recommended_fields = ['headline', 'description', 'byline', 'image_url']
        boilerplate = latimes_ipsum.get_story()
        for f in recommended_fields:
            # If it's an empty string cry foul
            if not getattr(self, f, ''):
                return False
            if f == 'image_url':
                if getattr(self, f) == boilerplate.image.url:
                    return False
            # Same thing if the value is from our boilerplate
            else:
                if getattr(self, f) == getattr(boilerplate, f):
                    return False
        return True

    #
    # Publication controls
    #

    @property
    def pub_status(self):
        """
        Returns the publication status as a string.

        There are three values:

            - live
            - working
            - pending
        """
        # Drop all the working ones right away
        if self.published is not True:
            return 'working'
        # If it is published but has a future date, that means its pending
        if timezone.make_aware(self.pub_date) > timezone.now():
            return 'pending'
        # Otherwise it should go live
        return 'live'

    def is_live(self):
        """
        Tests if the object should be published on the live production site.

        Returns True or False.
        """
        status_dict = {
            'live': True,
            'pending': False,
            'working': False
        }
        return status_dict[self.pub_status]

    def should_build(self):
        """
        Tests if the object should be published in the current environment.

        Returns True or False
        """
        # Get the publication status of the current environment
        status = getattr(settings, 'BIGBUILD_PAGE_PUBLICATION_STATUS', 'working')
        # If we are in 'working' mode everything gets built
        if status == 'working':
            return True
        # Otherwise default to the object's status
        return self.is_live()
