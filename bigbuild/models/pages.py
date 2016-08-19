#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import csv
import json
import yaml
import codecs
import shutil
import logging
import frontmatter
from bigbuild.models import BasePage
from bigbuild.exceptions import BadMetadata
from django.template import Engine, Context
from bigbuild import get_page_directory, get_retired_directory
logger = logging.getLogger(__name__)


class Page(BasePage):
    """
    A custom page published via static.latimes.com
    """
    @property
    def base_directory(self):
        """
        Returns base directory for pages.
        """
        return get_page_directory()

    @property
    def retired_directory_path(self):
        """
        Returns the path where this page would be retired, if it were retired.
        """
        return os.path.join(get_retired_directory(), self.slug)

    @property
    def retired_directory_exists(self):
        """
        Tests whether a retired directory for this slug already exists.
        """
        return os.path.exists(self.retired_directory_path)

    def create_directory(
        self,
        force=False,
        index_template_name='bigbuild/pages/default_index.html',
        index_template_context={},
    ):
        """
        Creates a new directory for the page.

        Returns the path to the directory that has been created, which is
        the same as the self.directory_path property.

        Throws an error if the directory already exists. You can force it
        to overwrite a pre-existing directory by submitting the force keyword
        argument as true.
        """
        # Check if the directory exists already and act accordingly
        if self.directory_exists:
            if force:
                shutil.rmtree(self.directory_path)
            else:
                raise ValueError(
                    "Page directory already exists at %s" % self.directory_path
                )

        # Make the directory
        os.mkdir(self.directory_path)

        # Add the index template
        self.write_index(
            template_name=index_template_name,
            template_context=index_template_context,
        )

        # Create the metadata configuration file
        self.write_frontmatter()

        # Create the ./static/ directory for extra stuff
        self.write_static()

        # Create the checklist file
        self.write_checklist()

        # Return the directory path
        return self.directory_path

    def write_index(self, template_name, template_context={}):
        """
        Creates index.html in the page directory.
        """
        template = self.get_template(template_name)
        html = template.render(Context(template_context))
        with codecs.open(self.index_path, 'w', 'utf-8') as f:
            f.write(html)

    def write_frontmatter(self):
        """
        Creates metadata.yaml in the page directory.
        """
        frontmatter.dump(self, self.frontmatter_path)

    def write_static(self):
        """
        Creates a ./static/ subdirectory within the page directory.
        """
        os.mkdir(self.static_path)

        css_path = os.path.join(self.static_path, 'style.css')
        css = self.get_template("bigbuild/pages/style.css-tpl").source
        with codecs.open(css_path, 'w', 'utf-8') as f:
            f.write(css)

        js_path = os.path.join(self.static_path, 'app.js')
        js = self.get_template("bigbuild/pages/app.js-tpl").source
        with codecs.open(js_path, 'w', 'utf-8') as f:
            f.write(js)

    def write_checklist(self):
        """
        Creates checklist.md in the page directory.
        """
        template = self.get_template("bigbuild/pages/checklist.md-tpl")
        md = template.render(Context(dict(object=self)))
        with codecs.open(self.checklist_path, 'w', 'utf-8') as f:
            f.write(md)

    def get_template(self, name):
        """
        Returns a Django template of the provided name ready to render.
        """
        engine = Engine.get_default()
        return engine.get_template(name)

    def sync_frontmatter(self):
        super(Page, self).sync_frontmatter()
        with codecs.open(self.frontmatter_path) as f:
            # Parse the YAML with confidence since the super call above
            # has already weeded out any errors
            post = frontmatter.load(f)
            # Loop through any data files
            self.data = {}
            for key, path in post.metadata.get('data', {}).items():
                # Generate what the path to the file ought to be
                p = os.path.join(self.data_path, path)
                # Toss an error if it doesn't exist
                if not os.path.exists(p):
                    raise BadMetadata("Data file could not be found at %s" % p)
                # Open the file
                with codecs.open(p, 'r') as f:
                    # If it's a CSV file open it that way...
                    if p.endswith(".csv"):
                        self.data[key] = list(csv.DictReader(f))
                    # If it's a JSON file open it this way ...
                    elif p.endswith(".json"):
                        self.data[key] = json.load(f)
                    # If it's a YAML file open it t'other way ...
                    elif (p.endswith(".yml") or p.endswith(".yaml")):
                        self.data[key] = yaml.load(f)
                    # If it's none of those throw an error.
                    else:
                        raise BadMetadata(
                            "Data file at %s not recognizable type" % path
                        )
