#!/usr/bin/env python3

from argparse import ArgumentParser
from urllib.parse import urlparse
from base64 import b64decode
from itertools import count

import os
import sys
import json
import shutil

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


__appname__ = 'har-extractor'
__version__ = '0.2.1'

NAME_VERSION = '%s %s' % (__appname__, __version__)
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
    request = entry.get('request', {})
    response = entry.get('response', {})
    content = response.get('content', {})
    return '%s %s -> %s %s %s %s' % (
        request.get('method', '<no method>'),
        request.get('url', '<no url>'),
        response.get('status', '<no status>'),
        response.get('statusText', '<no status text>'),
        content.get('mimeType', '<no mime type>'),
        format_size(content.get('size', -1))
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

def get_entry_path(entry, subdirs=False):
    try:
        url = urlparse(entry['request']['url'])
    except KeyError:
        raise ValueError('Invalid entry: missing request URL: %s' % repr(entry))

    fname = url.path.strip('/')
    if fname == '':
        fname = 'index.html'

    if subdirs:
        return os.path.join(url.netloc, fname)
    return os.path.basename(fname)

def get_entries(fp, iterative=True):
    if fp is sys.stdin:
        iterative = True
        fp = fp.buffer

    if ijson is None or not iterative:
        data = fp.read()
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        data = json.loads(data)
        return data['log']['entries']
    else:
        return ijson.items(fp, 'log.entries.item')

def get_out_dir(path, default):
    if not path:
        return default
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError('"%s" is not a directory' % path)
        return os.path.join(path, default)
    return path

def dirnames(entry, root):
    path = os.path.relpath(entry, root)
    ret = []
    path = os.path.dirname(path)
    while path:
        ret.append(os.path.join(root, path))
        path = os.path.dirname(path)
    return ret

def move_files_to_dir(path, first):
    dirname, name = os.path.split(path)
    name, ext = os.path.splitext(name)
    shutil.move(first, os.path.join(path, 'index.html'))
    for i in count(1):
        fpath = os.path.join(dirname, '%s.%d%s' % (name, i, ext))
        if not os.path.exists(fpath):
            return
        fname = 'index.%d.html' % i
        shutil.move(fpath, os.path.join(path, fname))

def make_entry_dirs(root, entry):
    try:
        os.makedirs(os.path.dirname(entry), exist_ok=True)
        return
    except OSError:
        for path in reversed(dirnames(entry, root)):
            if not os.path.exists(path):
                os.mkdir(path)
            elif not os.path.isdir(path):
                tmp = get_unused_name(path)
                shutil.move(path, tmp)
                os.mkdir(path)
                move_files_to_dir(path, tmp)


def extract(entries, outdir=None,
            subdirs=False, verbose=False, exit_on_error=True):
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

            fname = get_entry_path(entry, subdirs)
            fname = os.path.join(outdir, fname)
            fname = get_unused_name(fname)
            if verbose:
                print('\t---->', fname)

            try:
                if subdirs:
                    make_entry_dirs(outdir, fname)
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


def main(args=None):
    parser = ArgumentParser(args)

    parser.add_argument('file', metavar='FILE', help='HAR file')

    parser.add_argument('-V', '--version',
                        action='version', version=NAME_VERSION)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='list extracted files')

    parser.add_argument('-l', '--list', action='store_true',
                        help='list the contents of input file')

    parser.add_argument('-i', '--iterative',
                        action='store_true',
                        help='iteratively parse input file')

    parser.add_argument('-s', '--strict',
                        action='store_true',
                        help='exit and delete extracted data after first error')

    parser.add_argument('-d', '--directories',
                        action='store_true',
                        help='create url directories')

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
            entries = get_entries(fp, args.iterative)
            extract(entries, outdir,
                    args.directories, args.verbose, args.strict)
    except (ValueError, IOError) as err:
        if args.strict:
            shutil.rmtree(outdir)
        print(err, file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
