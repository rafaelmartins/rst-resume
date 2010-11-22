#!/usr/bin/env python
# -*- coding: utf-8 -*-

from babel.messages import frontend as babel
from distutils.command.build import build as _build
from glob import glob
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as _sdist

import os
import rst_resume


class build(_build):
    def run(self):
        self.run_command('compile_catalog')
        _build.run(self)


class sdist(_sdist):
    def run(self):
        self.run_command('compile_catalog')
        _sdist.run(self)
        

setup(
    name = 'rst-resume',
    version = rst_resume.__version__,
    license = rst_resume.__license__,
    description = rst_resume.__description__,
    long_description = rst_resume.__doc__,
    author = rst_resume.__author__,
    author_email = rst_resume.__email__,
    url = rst_resume.__url__,
    packages = find_packages(),
    include_package_data = True,
    scripts = ['bin/rst-resume'],
    install_requires = [
        'Flask>=0.6',
        'Flask-Babel>=0.6',
        'Jinja2>=2.5.2',
        'docutils>=0.7',
        'rst2pdf>=0.16',
	'reportlab>=2.5',
    ],
    cmdclass = {
        'build': build,
        'sdist': sdist,
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog
    },
)
