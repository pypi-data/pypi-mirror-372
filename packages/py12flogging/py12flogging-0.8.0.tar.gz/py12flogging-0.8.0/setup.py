#!/usr/bin/env python3
# Author(s): Toni Sissala
# Copyright 2025 Finnish Social Science Data Archive FSD / University of Tampere
# Licensed under the EUPL. See LICENSE.txt for full license.

from setuptools import setup, find_packages


with open('README.rst', 'r') as fh:
    long_description = fh.read()


with open('VERSION', 'r') as fh:
    version = fh.readline().strip()


setup(
    name='py12flogging',
    version=version,
    url='https://gitlab.tuni.fi/fsd/py12flogging',
    description='Python logging module for developing microservices '
    'conforming to 12 Factor App methodology.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    license='EUPL v1.2',
    author='Toni Sissala',
    author_email='support.fsd+py12flogging@tuni.fi',
    packages=find_packages(),
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    )
)
