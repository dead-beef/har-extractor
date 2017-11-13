#!/bin/sh

rm -rfv build/* dist/* \
    && (sed -r 's/`([^`]+)`/\1/g' README.md \
        | pandoc -f markdown_github -t rst >README.rst) \
    && python3 setup.py sdist bdist_wheel
