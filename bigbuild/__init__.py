import os
from django.conf import settings
default_app_config = 'bigbuild.apps.BigbuildConfig'


def get_page_directory():
    """
    Returns the PAGE_DIR where dynamic pages are configured.
    """
    # Return the PAGE_DIR settings, if it's been set, or fall back to the default.
    path = getattr(
        settings,
        'PAGE_DIR',
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
        'RETIRED_DIR',
        os.path.join(settings.BASE_DIR, '.retired')
    )
    # Make the directory if it doesn't exist already
    os.path.exists(path) or os.mkdir(path)
    # Return the path
    return path
