#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "xenoslib"))
import about  # noqa

# from about import __version__  # noqa

setup(
    name=about.__title__,
    version=about.__version__,
    packages=find_packages(),
    description=about.__description__,
    long_description_content_type="text/markdown",
    author=about.__author__,
    author_email=about.__author_email__,
    license=about.__license__,
    url=about.__url__,
    install_requires=[
        "PyYAML>=5.4",
        "IMAPClient>=2.3.1",
    ],
    python_requires=">=3.7",
    extras_require={
        ':"linux" in sys_platform': [],
        ':sys_platform == "win32"': ["pywin32>=225"],
        ':python_version >= "3.10"': ["requests>=2.19"],
        ':python_version <= "3.9"': ["requests>=2.0.0"],
        'colorful:sys_platform == "win32"': ["colorama>=0.4.4"],
        "mock": ["requests_mock>=1.9.3"],
    },
    tests_require=["pytest>=2.8.0"],
)
