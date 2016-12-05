import os
from git import Repo
from django.conf import settings
from django.conf.urls import url
from six.moves.urllib.parse import urljoin
default_app_config = 'bigbuild.apps.BigbuildConfig'


def get_page_directory():
    """
    Returns the PAGE_DIR where dynamic pages are configured.
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


def get_retired_directory():
    """
    Returns the RETIRED_DIR where retired pages are configured.
    """
    # Return the RETIRED_DIR settings, if it's been set, or fall back to the default.
    path = getattr(
        settings,
        'BIGBUILD_RETIRED_DIR',
        os.path.join(settings.BASE_DIR, '.retired')
    )
    # Make the directory if it doesn't exist already
    os.path.exists(path) or os.mkdir(path)
    # Return the path
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
    if base_url.startswith("/"):
        base_url = base_url[1:]

    if getattr(settings, 'BIGBUILD_BRANCH_BUILD', False):
        # Get the branch name
        repo_branch = get_repo_branch()
        # Put the branch name ahead of the base url
        return urljoin("/", repo_branch, base_url)
    else:
        return urljoin("/", base_url)
