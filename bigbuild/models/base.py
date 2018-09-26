#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import copy
import json
import yaml
import archieml
import codecs
import logging
import bigbuild
import jsonfield
from django.db import models
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from greeking import latimes_ipsum
from django.test import RequestFactory
from bigbuild import context_processors
from bigbuild.serializers import deserializers
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
    show_in_feeds = models.BooleanField(default=True)
    content = models.TextField(blank=True)
    extra = jsonfield.JSONField(blank=True)
    data = jsonfield.JSONField(blank=True)

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

    #
    # Dynamic content
    #

    def set_data_objects(self):
        # Loop through any data files
        for key, path in self.data.items():

            # Generate the path if it's stored in the default `data` directory
            data_dir = os.path.join(self.page_directory_path, 'data')
            p = os.path.join(data_dir, path)
            # If it doesn't exist, see if it's in another folder
            if not os.path.exists(p):
                p = os.path.join(self.page_directory_path, path)
                # If it's not there either, throw an error
                if not os.path.exists(p):
                    logging.debug("Data file could not be found at %s" % p)

            # Open the file
            with codecs.open(p, 'r') as f:
                # If it's a CSV file open it that way...
                if p.endswith(".csv"):
                    self.data_objects[key] = list(csv.DictReader(f))
                # If it's a JSON file open it this way ...
                elif p.endswith(".json"):
                    self.data_objects[key] = json.load(f)
                # If it's a YAML file open it t'other way ...
                elif (p.endswith(".yml") or p.endswith(".yaml")):
                    self.data_objects[key] = yaml.load(f)
                elif p.endswith(".aml"):
                    self.data_objects[key] = archieml.load(f)
                # If it's none of those throw an error.
                else:
                    logging.debug("Data file at %s not recognizable type" % path)


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
        obj = copy.deepcopy(self)
        obj.set_data_objects()
        obj.data = obj.data_objects
        context = RequestContext(
            RequestFactory().get(self.get_absolute_url()),
            {
                "object": obj,
                'STATIC_URL': obj.get_static_url()
            },
            [context_processors.bigbuild]
        )
        return template.render(context)

    #
    # Actions
    #

    @classmethod
    def create(cls, **fields):
        """
        Create a new object.
        """
        # Pop out any extra inputs for the directory
        try:
            force = fields.pop("force")
        except KeyError:
            force = False

        try:
            index_template_name = fields.pop("index_template_name")
        except KeyError:
            index_template_name = 'bigbuild/pages/default_index.html'

        try:
            index_template_context = fields.pop("index_template_context")
        except KeyError:
            index_template_context = {}

        try:
            skip_create_directory = fields.pop("skip_create_directory")
        except KeyError:
            skip_create_directory = False

        # Create the object
        obj = cls(**fields)

        # Cache attribute to store rendered data files
        obj.data_objects = {}

        if not skip_create_directory:

            # If the directory already exists and we're not forcing creation
            # an error should be thrown.
            if os.path.exists(obj.page_directory_path) and not force:
                raise ValueError('Page directory already exists')
            elif os.path.exists(obj.archive_dynamic_directory_path) and not force:
                raise ValueError('Page directory already exists')

            # Create directory with any extra options passed in
            obj.create_directory(
                force=force,
                index_template_name=index_template_name,
                index_template_context=index_template_context,
            )

        # Return the object
        return obj

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

    def refresh_from_yaml(self):
        """
        Reads in the frontmatter from metadata.yaml and syncs it with the object.
        """
        deserializer = deserializer = deserializers[self.__class__.__name__]()
        yaml_obj = deserializer.deserialize(self.slug)
        for field in yaml_obj._meta.fields:
            setattr(self, field.name, getattr(yaml_obj, field.name))
        self.data_objects = yaml_obj.data_objects or {}

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
