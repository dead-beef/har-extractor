#!/usr/bin/env python3

import os
from unittest import TestLoader
from setuptools import setup

def tests():
    return TestLoader().discover('tests')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(BASE_DIR, 'README.rst')) as fp:
        README = fp.read()
except IOError:
    README = ''

setup(
    name='har-extractor',
    version='0.2.1',
    description='HTTP Archive extractor',
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Archiving',
        'Topic :: Utilities'
    ],
    keywords='har http archive extractor',
    url='https://github.com/dead-beef/har-extractor',
    author='dead-beef',
    author_email='contact@dead-beef.tk',
    license='MIT',
    py_modules=['har_extractor'],
    entry_points={
        'console_scripts': [
            'har-extractor=har_extractor:main'
        ]
    },
    test_suite='setup.tests',
    install_requires=['ijson'],
    extras_require={
        'dev': [
            'coverage',
            'twine>=1.8.1',
            'wheel'
        ]
    },
    python_requires='>=3',
    include_package_data=True,
    zip_safe=False
)
