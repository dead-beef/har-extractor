#!/bin/sh

if [ -d env ]; then
    . env/bin/activate
fi

rm -rfv build/* dist/* && python3 setup.py sdist bdist_wheel
