#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import six
import sys
import csv
import json
import yaml
import codecs
import logging
import archieml
import validictory
import frontmatter
from django.apps import apps
from datetime import datetime
from django.core.serializers.base import DeserializationError
from bigbuild.exceptions import MissingRecommendedMetadataWarning
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.pyyaml import Serializer as YAMLSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
logger = logging.getLogger(__name__)


class BigBuildJSONSerializer(JSONSerializer):
    """
    A custom JSON serializer for bigbuild models.
    """
    pass


def BigBuildJSONDeserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of JSON data.
    """
    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        objects = json.loads(stream_or_string)
        for obj in PythonDeserializer(objects, **options):
            yield obj
    except GeneratorExit:
        raise
    except Exception as e:
        # Map to deserializer error
        six.reraise(DeserializationError, DeserializationError(e), sys.exc_info()[2])


class BigBuildFrontmatterSerializer(YAMLSerializer):
    """
    A custom YAML frontmatter serializer for bigbuild models.
    """
    def get_dump_object(self, obj):
        # Restructure to YAML schema preferred by frontmatter
        obj.metadata = self.get_metadata(obj)
        # Pass it out
        return obj

    def end_serialization(self):
        # Dump each object into the stream as as frontmatter
        content = [frontmatter.dumps(o) for o in self.objects]
        # Write out as text to the stream in a safe string format
        [self.stream.write(six.text_type(chunk)) for chunk in content]

    def get_metadata(self, obj):
        """
        Returns the structured "metadata" associated with this page expected by Jekyll's frontmatter.
        """
        # Structure the metadata
        d = dict([
            ('headline', obj.headline),
            ('byline', obj.byline),
            ('description', obj.description),
            ('image_url', obj.image_url),
            ('pub_date', obj.pub_date),
            ('published', obj.published),
            ('show_in_feeds', obj.show_in_feeds),
        ])
        if obj.extra:
            d['extra'] = obj.extra
        if obj.data:
            d['data'] = obj.data

        # Make sure the page is valid
        if not self.is_metadata_valid(d):
            raise ValueError("Metadata is not valid for %s" % obj)

        return d

    def is_metadata_valid(self, metadata):
        """
        Tests if the metadata is valid and returns True or False.
        """
        schema = {
            "type": "object",
            "properties": {
                'headline': {"type": "string", "blank": True},
                'byline': {"type": "string", "blank": True},
                'description': {"type": "string", "blank": True},
                'image_url': {"type": "any", "blank": True},
                'pub_date': {"type": "any"},
                'published': {"type": "boolean"},
                'show_in_feeds': {"type": "boolean"},
            }
        }
        try:
            validictory.validate(metadata, schema)
            if not isinstance(metadata['pub_date'], datetime):
                return False
            return True
        except:
            return False


class BaseBigBuildFrontmatterDeserializer(object):
    """
    Abstract method for deserializing YAML data from Jekyll's frontmatter format.
    """
    def deserialize(self, slug):
        """
        Retrieves the provided slug and returns a bigbuild object
        """
        logger.debug("Retrieving {} as {} object".format(
            slug,
            self.model.__name__
        ))
        obj = self.model.create(slug=slug, skip_create_directory=True)
        try:
            # Sync the metadata from the YAML frontmatter with the object
            obj = self.set_metadata(obj)
            # Pass it out
            return obj
        except Exception as e:
            # Map to deserializer error
            six.reraise(DeserializationError, DeserializationError(e), sys.exc_info()[2])

    def set_metadata(self, obj):
        """
        Syncs metadata with YAML frontmatter with provided bigbuild model object.
        """
        stream = open(obj.frontmatter_path, 'r')
        post = frontmatter.load(stream)

        # Set the basic frontmatter metadata
        obj.headline = post.metadata['headline']
        obj.byline = post.metadata['byline']
        obj.description = post.metadata['description']
        obj.image_url = post.metadata['image_url']
        obj.pub_date = post.metadata['pub_date']
        obj.published = post.metadata['published']
        obj.show_in_feeds = post.metadata['show_in_feeds']

        # Attach any extra stuff
        try:
            obj.extra = post.metadata['extra']
        except KeyError:
            obj.extra = {}

        try:
            obj.data = post.metadata['data']
        except KeyError:
            obj.data = {}

        # Pull in the content as is
        obj.content = post.content

        # Render it out as flat HTML
        obj.content = obj.rendered_content

        # Make sure the page has recommended metadata
        # ... if it's ready to publish
        if obj.pub_status in ['live', 'pending']:
            if not obj.has_recommended_metadata():
                logger.warn(MissingRecommendedMetadataWarning(obj))

        # Pass it back out
        return obj


class PageFrontmatterDeserializer(BaseBigBuildFrontmatterDeserializer):
    """
    Deserializes Jekyll frontmatter from YAML to a bigbuild Page object.
    """
    def __init__(self):
        self.model = apps.get_app_config('bigbuild').get_model('Page')

    def set_metadata(self, obj):
        """
        Extends the base deserialization with techniques for syncing data files.
        """
        obj = super(PageFrontmatterDeserializer, self).set_metadata(obj)

        # Reopen the YAML frontmatter
        stream = open(obj.frontmatter_path, 'r')
        post = frontmatter.load(stream)

        # Loop through any data files
        for key, path in post.metadata.get('data', {}).items():

            # Generate the path if it's stored in the default `data` directory
            data_dir = os.path.join(obj.page_directory_path, 'data')
            p = os.path.join(data_dir, path)
            # If it doesn't exist, see if it's in another folder
            if not os.path.exists(p):
                p = os.path.join(obj.page_directory_path, path)
                # If it's not there either, throw an error
                if not os.path.exists(p):
                    logging.debug("Data file could not be found at %s" % p)

            # Open the file
            with codecs.open(p, 'r') as f:
                # If it's a CSV file open it that way...
                if p.endswith(".csv"):
                    obj.data_objects[key] = list(csv.DictReader(f))
                # If it's a JSON file open it this way ...
                elif p.endswith(".json"):
                    obj.data_objects[key] = json.load(f)
                # If it's a YAML file open it t'other way ...
                elif (p.endswith(".yml") or p.endswith(".yaml")):
                    obj.data_objects[key] = yaml.load(f)
                elif p.endswith(".aml"):
                    obj.data_objects[key] = archieml.load(f)
                # If it's none of those throw an error.
                else:
                    logging.debug("Data file at %s not recognizable type" % path)

        # Pass it back out
        return obj


class ArchivedPageFrontmatterDeserializer(BaseBigBuildFrontmatterDeserializer):
    """
    Deserializes Jekyll frontmatter from YAML to a bigbuild ArchivedPage object.
    """
    def __init__(self):
        self.model = apps.get_app_config('bigbuild').get_model('ArchivedPage')


#
# Lookups
#


deserializers = {
    'Page': PageFrontmatterDeserializer,
    'ArchivedPage': ArchivedPageFrontmatterDeserializer
}
