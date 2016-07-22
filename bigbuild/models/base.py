#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import yaml
import shutil
import logging
import validictory
import frontmatter
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from greeking import latimes_ipsum
from django.test import RequestFactory
from bigbuild.exceptions import BadMetadata
from django.template import Engine, RequestContext
from django.template.defaultfilters import slugify
logger = logging.getLogger(__name__)


class BasePage(object):
    """
    An abstract base class with methods shared by all page classes.
    """
    def __init__(
        self,
        slug,
        headline="",
        byline="",
        description="",
        pub_date=None,
        published=False,
        show_in_feeds=True,
        content='',
        extra={},
        data={}
    ):
        # The metadata
        self.slug = slugify(slug)
        self.headline = headline
        self.byline = byline
        self.description = description
        self.image_url = ""
        self.pub_date = pub_date or datetime.now().replace(
            second=0,
            microsecond=0
        )
        self.published = published
        self.show_in_feeds = show_in_feeds
        # The content
        self.content = content
        # Any extras
        self.extra = extra
        # Any structured data
        self.data = data

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.__str__())

    def __str__(self):
        return str(self.slug)

    def to_json(self):
        d = self.__dict__
        d['pub_date'] = str(d['pub_date'])
        return d

    @property
    def metadata(self):
        """
        Returns the structured metadata associated with this page.

        For the purpose of deconstructing this object to Jekyll frontmatter.
        """
        d = dict([
            ('slug', str(self.slug)),
            ('headline', self.headline),
            ('byline', self.byline),
            ('description', self.description),
            ('image_url', self.image_url),
            ('pub_date', self.pub_date),
            ('published', self.published),
            ('show_in_feeds', self.show_in_feeds),
        ])
        if self.extra:
            d['extra'] = self.extra
        if self.data:
            d['data'] = self.data
        return d

    def get_absolute_url(self):
        return '/projects/%s/' % self.slug

    def get_static_url(self):
        return os.path.join(self.get_absolute_url(), 'static') + "/"

    def delete(self):
        """
        Delete the page directory.
        """
        shutil.rmtree(self.directory_path)

    def build(self):
        """
        Builds this page via the PageDetailView.
        """
        from bigbuild.views import PageDetailView
        view = PageDetailView()
        view.build_object(self)

    @property
    def directory_path(self):
        """
        Returns the directory path where this page will exist.
        """
        return os.path.join(self.base_directory, self.slug)

    @property
    def directory_exists(self):
        """
        Tests whether the page directory for this object exists.

        Returns True or False
        """
        return os.path.exists(self.directory_path)

    @property
    def index_path(self):
        """
        Returns the index.html path where this page will be marked up.
        """
        return os.path.join(self.directory_path, 'index.html')

    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        return os.path.join(self.directory_path, 'metadata.md')

    @property
    def static_path(self):
        """
        Returns the path to the static subdirectory for extra files.
        """
        return os.path.join(self.directory_path, 'static')

    @property
    def checklist_path(self):
        """
        Returns the checklist.md path where the checklist will be stored.
        """
        return os.path.join(self.directory_path, 'checklist.md')

    @property
    def data_path(self):
        """
        Returns the path to the data subdirectory for structured data files.
        """
        return os.path.join(self.directory_path, 'data')

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
            self.slug = post.metadata['slug']
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

            # Render the content as a Django template
            engine = Engine.get_default()
            template = engine.from_string(post.content)
            context = RequestContext(
                RequestFactory().get(self.get_absolute_url()),
                {
                    "object": self,
                    'STATIC_URL': self.get_static_url()
                }
            )
            content = template.render(context)
            self.content = content

    def is_metadata_valid(self):
        """
        Tests if the metadata is valid and returns True or False.
        """
        schema = {
            "type": "object",
            "properties": {
                'slug': {"type": "string"},
                'headline': {"type": "string", "blank": True},
                'byline': {"type": "string", "blank": True},
                'description': {"type": "string", "blank": True},
                'image_url': {"type": "string", "blank": True},
                'pub_date': {"type": "any"},
                'published': {"type": "boolean"},
                'show_in_feeds': {"type": "boolean"},
            }
        }
        try:
            validictory.validate(self.metadata, schema)
            if not isinstance(self.pub_date, datetime):
                return False
            return True
        except:
            return False

    def has_recommended_metadata(self):
        """
        Tests if the metadata has the fields we recommend are present
        for every page have been filled.

        Returns True or False.
        """
        recommended_fields = ['headline', 'description', 'byline', 'image_url']
        md = self.metadata
        boilerplate = latimes_ipsum.get_story()
        for f in recommended_fields:
            # If it's an empty string cry foul
            if not md.get(f, ''):
                return False
            # Same thing if the value is from our boilerplate
            if md[f] == getattr(boilerplate, f):
                return False
        return True

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
        status = getattr(settings, 'PAGE_PUBLICATION_STATUS', 'working')
        # If we are in 'working' mode everything gets built
        if status == 'working':
            return True
        # Otherwise default to the object's status
        return self.is_live()
