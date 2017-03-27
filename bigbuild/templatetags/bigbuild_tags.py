#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django import template
from bigbuild.models import Page
register = template.Library()


@register.filter
def jsonify(obj):
    """
    Returns an object in JSON format.
    """
    if isinstance(obj, Page):
        return json.dumps(obj.to_json())
    return json.dumps(obj)
