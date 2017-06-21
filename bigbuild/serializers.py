import six
import sys
import json
import frontmatter
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
        obj.metadata = self.get_metadata(obj)
        return obj

    def end_serialization(self):
        [frontmatter.dump(o, self.stream) for o in self.objects]

    def get_metadata(self, obj):
        """
        Returns the structured "metadata" associated with this page expected by Jekyll's frontmatter.
        """
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
        return d
