#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from git import Repo
from django.conf import settings
from django.utils.version import get_version
default_app_config = 'bigbuild.apps.BigbuildConfig'

VERSION = (0, 4, 1, 'final', 0)
__version__ = get_version(VERSION)


def get_build_directory():
    """
    Returns the django-bakery BUILD_DIR where pages will be built.
    """
    # If the user has configured a BIGBUILD_BUILD_DIR, use that.
    if getattr(settings, 'BUILD_DIR', None):
        return settings.BUILD_DIR
    else:
        # And if they don't return the default
        return os.path.join(settings.BASE_DIR, '.build')


def get_page_directory():
    """
    Returns the BIGBUILD_PAGE_DIR where dynamic pages are configured.
    """
    # Return the PAGE_DIR settings, if it's been set, or fall back to the default.
    path = getattr(
        settings,
        'BIGBUILD_PAGE_DIR',
        os.path.join(settings.BASE_DIR, 'pages')
    )
    # Make the directory if it doesn't exist already
    os.path.exists(path) or os.mkdir(path)
    # Return the path
    return path


def get_archive_directory():
    """
    Returns the BIGBUILD_ARCHIVE_DIR where archived pages are configured.
    """
    # Return the BIGBUILD_ARCHIVE_DIR settings, if it's been set, or fall back to the default.
    path = getattr(
        settings,
        'BIGBUILD_ARCHIVE_DIR',
        os.path.join(settings.BASE_DIR, '.archive')
    )

    # Make the directory if it doesn't exist already
    os.path.exists(path) or os.mkdir(path)

    # Make the two expected subdirectories if they do not already exist
    static_archive = os.path.join(path, 'static')
    dynamic_archive = os.path.join(path, 'dynamic')
    os.path.exists(static_archive) or os.mkdir(static_archive)
    os.path.exists(dynamic_archive) or os.mkdir(dynamic_archive)

    # Return the roo archive path
    return path


def get_repo_branch():
    """
    Returns the name of the current git branch.
    """
    if getattr(settings, 'BIGBUILD_GIT_BRANCH', None):
        return settings.BIGBUILD_GIT_BRANCH
    repo_path = getattr(settings, 'BIGBUILD_GIT_DIR', settings.BASE_DIR)
    branch = Repo(repo_path).active_branch
    return branch.name


def get_base_url():
    """
    Returns the base URL for site.
    """
    base_url = getattr(settings, 'BIGBUILD_BASE_URL', '')
    base_url = base_url.lstrip("/")

    if getattr(settings, 'BIGBUILD_BRANCH_BUILD', False):
        # Get the branch name
        repo_branch = get_repo_branch()
        # Put the branch name ahead of the base url
        return os.path.join("/", repo_branch, base_url)
    else:
        return os.path.join("/", base_url)
