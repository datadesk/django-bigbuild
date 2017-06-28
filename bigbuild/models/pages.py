#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import io
import os
import codecs
import shutil
import logging
from bigbuild.models import BasePage
from django.template import Engine, Context
from django.utils.encoding import python_2_unicode_compatible
from bigbuild.serializers import BigBuildFrontmatterSerializer
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Page(BasePage):
    """
    A custom page published via static.latimes.com
    """
    def __str__(self):
        return self.slug

    def delete(self):
        """
        Delete the page directory.
        """
        shutil.rmtree(self.page_directory_path)

    @property
    def frontmatter_path(self):
        """
        Returns the metadata.md path where this page will be configured.
        """
        return os.path.join(self.page_directory_path, 'metadata.md')

    def create_directory(
        self,
        force=False,
        index_template_name='bigbuild/pages/default_index.html',
        index_template_context={},
    ):
        """
        Creates a new directory for the page.

        Returns the path to the directory that has been created, which is
        the same as the self.page_directory_path property.

        Throws an error if the directory already exists. You can force it
        to overwrite a pre-existing directory by submitting the force keyword
        argument as true.
        """
        # Check if the directory exists already and act accordingly
        if os.path.exists(self.page_directory_path):
            if force:
                shutil.rmtree(self.page_directory_path)
            else:
                raise ValueError(
                    "Page directory already exists at %s" % self.page_directory_path
                )

        # Make the directory
        os.mkdir(self.page_directory_path)

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
        return self.page_directory_path

    def write_index(self, template_name, template_context={}):
        """
        Creates index.html in the page directory.
        """
        template = self.get_template(template_name)
        html = template.render(Context(template_context))
        index_path = os.path.join(self.page_directory_path, 'index.html')
        with codecs.open(index_path, 'w', 'utf-8') as f:
            f.write(html)

    def write_frontmatter(self, path=None):
        """
        Creates metadata.yaml in the page directory, or a supplied target directory.
        """
        serializer = BigBuildFrontmatterSerializer()
        with io.open(path or self.frontmatter_path, 'w', encoding='utf8') as f:
            f.write(serializer.serialize([self]))

    def write_static(self):
        """
        Creates a ./static/ subdirectory within the page directory.
        """
        static_path = os.path.join(self.page_directory_path, 'static')
        os.mkdir(static_path)

        css_path = os.path.join(static_path, 'style.css')
        css = self.get_template("bigbuild/pages/style.css-tpl").source
        with codecs.open(css_path, 'w', 'utf-8') as f:
            f.write(css)

        js_path = os.path.join(static_path, 'app.js')
        js = self.get_template("bigbuild/pages/app.js-tpl").source
        with codecs.open(js_path, 'w', 'utf-8') as f:
            f.write(js)

    def write_checklist(self):
        """
        Creates checklist.md in the page directory.
        """
        template = self.get_template("bigbuild/pages/checklist.md-tpl")
        md = template.render(Context(dict(object=self)))
        checklist_path = os.path.join(self.page_directory_path, 'checklist.md')
        with codecs.open(checklist_path, 'w', 'utf-8') as f:
            f.write(md)

    def get_template(self, name):
        """
        Returns a Django template of the provided name ready to render.
        """
        engine = Engine.get_default()
        return engine.get_template(name)
