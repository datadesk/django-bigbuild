#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bigbuild.models import PageList
from collections import OrderedDict
from django.utils.encoding import force_text
from django.core.management.base import BaseCommand
from django.core.serializers.python import Serializer


class BigBuildSerializer(Serializer):

    def get_dump_object(self, obj):
        data = OrderedDict([('model', force_text(obj._meta))])
        if not self.use_natural_primary_keys or not hasattr(obj, 'natural_key'):
            data["pk"] = force_text(obj._get_pk_val(), strings_only=True)
        data['fields'] = self._current
        return data


class Command(BaseCommand):
    help = 'Tests if page directories are valid'

    def handle(self, *args, **options):
        page_list = PageList()
        page = page_list[0]
        print(page)
