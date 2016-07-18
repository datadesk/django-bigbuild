#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings


def environment(request):
    """
    Adds env-related context variables to the context.
    """
    return {
        'DEVELOPMENT': settings.DEVELOPMENT,
        'STAGING': settings.STAGING,
        'PRODUCTION': settings.PRODUCTION,
        'BIGBAR': settings.BIGBAR
    }
