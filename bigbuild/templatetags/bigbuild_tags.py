#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django import template
from bigbuild.models import Page
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
register = template.Library()


@register.filter(needs_autoescape=True)
def dropcap(text, autoescape=True):
    """
    Wraps the first character in a <span> tag with a .dropcap class
    that can be used to make it bigger than the surrounding text.
    """
    if not text:
        return ''
    first, other = text[0], text[1:]
    if autoescape:
        esc = conditional_escape
    else:
        def esc(x): return x
    template = "<span class='dropcap'>{}</span>{}"
    html = template.format(esc(first.upper()), esc(other))
    return mark_safe(html)


@register.filter
def jsonify(obj):
    """
    Returns an object in JSON format.
    """
    if isinstance(obj, Page):
        return json.dumps(obj.to_json())
    return json.dumps(obj)
