#!/usr/bin/env python3

from distutils.core import setup

setup(
    name = 'HarExtractor',
    version = '0.1',
    description = 'Extractor for HAR, HTTP Archive format',
    author = 'dead-beef',
    url = 'https://github.com/dead-beef/har-extractor',
    scripts = [ 'har-extractor' ],
)
