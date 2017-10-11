#!/usr/bin/env python3

from argparse import ArgumentParser
from urllib.parse import urlparse
from base64 import b64decode

import os
import sys
import json

try:
    import ijson.backends.yajl2_cffi as ijson
except ImportError:
    try:
        import ijson.backends.yajl2 as ijson
    except ImportError:
        try:
            import ijson
        except ImportError:
            ijson = None

SIZE_UNITS = 'BKMGT'

def format_size(size):
    if size < 0:
        return '<invalid size>'
    unit_name = 'B'
    unit_value = 1
    for unit_name in SIZE_UNITS:
        if size < 1024 * unit_value:
            break
        unit_value *= 1024
    if size % unit_value == 0:
        return '%d%s' % (size // unit_value, unit_name)
    return '%.2f%s' % (size / unit_value, unit_name)

def get_unused_name(path):
    if not os.path.exists(path):
        return path
    name, ext = os.path.splitext(path)
    i = 1
    while True:
        path = '%s.%d%s' % (name, i, ext)
        if not os.path.exists(path):
            return path
        i += 1

def write(content, fname):
    if isinstance(content, bytes):
        mode = 'wb'
    else:
        mode = 'w'
    with open(fname, mode) as fp:
        fp.write(content)

def format_entry(entry):
    request = entry['request']
    response = entry['response']
    content = response['content']
    return '%s %s -> %s %s %s %s' % (
        request['method'],
        request['url'],
        response['status'],
        response['statusText'],
        content['mimeType'],
        format_size(content['size'])
    )

def get_entry_content(entry):
    try:
        content = entry['response']['content']
    except KeyError:
        return None
    try:
        text = content['text']
        if not text:
            return None
    except KeyError:
        return None

    try:
        if content['encoding'] == 'base64':
            text = b64decode(text)
        else:
            raise ValueError(
                '\tUnknown content encoding: "%s"' % content['encoding']
            )
    except KeyError:
        pass

    return text

def get_entry_path(entry):
    url = urlparse(entry['request']['url'])
    fname = os.path.basename(url.path.strip('/'))
    if fname == '':
        return 'index.html'
    return fname

def do_extract(entries, outdir=None, verbose=False, exit_on_error=True):
    if outdir is not None:
        os.makedirs(outdir, exist_ok=True)

    for entry in entries:
        try:
            if verbose or outdir is None:
                print(format_entry(entry))

            if outdir is None:
                continue

            content = get_entry_content(entry)
            if content is None:
                if verbose:
                    print('\t----> <no content>')
                continue

            fname = get_entry_path(entry)
            fname = get_unused_name(os.path.join(outdir, fname))
            if verbose:
                print('\t---->', fname)

            try:
                write(content, fname)
            except (OSError, IOError) as err:
                msg = 'Could not write "%s": %s' % (fname, repr(err))
                if exit_on_error:
                    raise IOError(msg)
                else:
                    print(msg, file=sys.stderr)
        except (KeyError, ValueError) as err:
            msg = 'Invalid entry: %s: %s' % (repr(entry), repr(err))
            if exit_on_error:
                raise ValueError(msg)
            else:
                print(msg, file=sys.stderr)

def extract(fp, outdir=None, verbose=False, exit_on_error=True):
    if ijson is None:
        data = json.loads(fp.read().decode('utf-8'))
        entries = data['log']['entries']
    else:
        entries = ijson.items(fp, 'log.entries.item')

    do_extract(entries, outdir, verbose, exit_on_error)

def get_out_dir(path, default):
    if not path:
        return default
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError('"%s" is not a directory' % path)
        return os.path.join(path, default)
    return path

def main(args=None):
    parser = ArgumentParser(args)

    parser.add_argument('file', metavar='FILE', help='HAR file')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='list extracted files')

    parser.add_argument('-l', '--list', action='store_true',
                        help='list the contents of input files')

    parser.add_argument('-o', '--output',
                        metavar='DIRECTORY', default=None,
                        help='set output directory (default: ./<filename>.d)')

    if args is not None:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    if args.file is None:
        return 1

    if args.list:
        outdir = None
    else:
        try:
            outdir = get_out_dir(args.output,
                                 os.path.basename(args.file) + '.d')
        except ValueError as err:
            print(err, file=sys.stderr)
            return 1

    try:
        with open(args.file, 'rb') as fp:
            extract(fp, outdir, args.verbose, False)
    except (ValueError, IOError) as err:
        print(err, file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
