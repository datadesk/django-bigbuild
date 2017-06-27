#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six
import sys
import json
import validictory
import frontmatter
from datetime import datetime
from django.core.serializers.base import DeserializationError
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.pyyaml import Serializer as YAMLSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer


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
        [frontmatter.dump(o, self.stream) for o in self.objects]

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
