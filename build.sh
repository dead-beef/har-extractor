#!/bin/sh

rm -rfv build/* dist/* && python3 setup.py sdist bdist_wheel
