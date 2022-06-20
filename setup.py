#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name                ="gravityspawner",
    version             ="0.0.2",
    author              = "LALALA",
    author_email        = "toorxkh@gmail.com",
    description         = """GravitySpawner: A spawner for Jupyterhub to let user select and input options at the same time""",
    long_description    =long_description,
    long_description_content_type="text/markdown",
    url                 ="https://github.com/lalalabox/gravityspawner",
    project_urls        ={
        "Bug Tracker": "https://github.com/lalalabox/gravityspawner/issues",
    },
    license             = "BSD",
    platforms           = "Linux, Mac OS X",
    classifiers         =[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    package_dir         ={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires     =">=3.7",
)