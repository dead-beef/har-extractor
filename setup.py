#!/usr/bin/env python3

from unittest import TestLoader
from setuptools import setup

def tests():
    return TestLoader().discover('tests')

setup(
    name='har-extractor',
    version='0.1',
    description='HTTP Archive extractor',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
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
    include_package_data=True,
    zip_safe=False
)
