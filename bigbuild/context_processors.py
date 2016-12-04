#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from bigbuild import get_base_url
from bigbuild import get_repo_branch


def bigbuild(request):
    """
    Adds env-related context variables to the context.
    """
    return {
        'BIGBUILD_BIGBAR': getattr(settings, 'BIGBUILD_BIGBAR', True),
        'BIGBUILD_GIT_BRANCH': get_repo_branch(),
        'BIGBUILD_BASE_URL': get_base_url()
    }
