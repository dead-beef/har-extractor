# pylint:disable=too-many-arguments

from unittest import TestCase
from unittest.mock import patch, call
from io import StringIO

import os

from har_extractor import extract

from data import (
    TEST_ARCHIVE, TEST_ARCHIVE_LIST, TEST_ARCHIVE_CONTENTS,
    TEST_ARCHIVE_VERBOSE, TEST_ARCHIVE_INVALID_VERBOSE,
    TEST_ARCHIVE_INVALID, TEST_ARCHIVE_INVALID_LIST
)

@patch('os.path.exists', return_value=False)
@patch('os.makedirs')
@patch('har_extractor.make_entry_dirs')
@patch('har_extractor.write')
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
class TestDoExtract(TestCase):
    def test_extract(self, stdout, stderr,
                     write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE['log']['entries'], 'dir/')
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_has_calls([
            call(content, os.path.join('dir', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(stdout.read(), '')
        self.assertEqual(stderr.read(), '')

    def test_extract_subdirs(self, stdout, stderr,
                             write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE['log']['entries'], 'dir/', subdirs=True)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_has_calles([
            call('dir/', exist_ok=True),
            call('dir/127.0.0.1', exist_ok=True)
        ])
        write.assert_has_calls([
            call(content, os.path.join('dir/127.0.0.1', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        make_entry_dirs.assert_has_calls([
            call('dir/', os.path.join('dir/127.0.0.1', fname))
            for _, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(make_entry_dirs.call_count, 2)
        self.assertEqual(stdout.read(), '')
        self.assertEqual(stderr.read(), '')

    def test_extract_verbose(self, stdout, stderr,
                             write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE['log']['entries'], 'dir/', verbose=True)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_has_calls([
            call(content, os.path.join('dir', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_VERBOSE)
        self.assertEqual(stderr.read(), '')

    def test_extract_invalid_all(self, stdout, stderr,
                                 write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE_INVALID['log']['entries'],
                'dir/', verbose=True, exit_on_error=False)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_called_with('404', 'dir/404')
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_INVALID_VERBOSE)
        self.assertNotEqual(stderr.read(), '')

    def test_extract_invalid(self, stdout, stderr,
                             write, make_entry_dirs, makedirs, _):
        output = TEST_ARCHIVE_INVALID_LIST.split('\n')
        output = output[0] + '\n'
        with self.assertRaises(ValueError):
            extract(TEST_ARCHIVE_INVALID['log']['entries'],
                    'dir/', verbose=True)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(write.call_count, 0)
        self.assertEqual(stdout.read(), output)
        self.assertEqual(stderr.read(), '')

    def test_extract_ioerror(self, stdout, stderr,
                             write, make_entry_dirs, makedirs, _):
        write.side_effect = IOError

        extract(TEST_ARCHIVE['log']['entries'],
                'dir/', verbose=True, exit_on_error=False)

        makedirs.assert_called_with('dir/', exist_ok=True)
        stdout.seek(0)
        stderr.seek(0)
        write.assert_has_calls([
            call(content, os.path.join('dir', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_VERBOSE)
        self.assertNotEqual(stderr.read(), '')

        with self.assertRaises(IOError):
            extract(TEST_ARCHIVE['log']['entries'], 'dir/', verbose=True)

    def test_extract_list(self, stdout, stderr,
                          write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE['log']['entries'], None)
        stdout.seek(0)
        stderr.seek(0)
        self.assertEqual(makedirs.call_count, 0)
        self.assertEqual(write.call_count, 0)
        self.assertEqual(make_entry_dirs.call_count, 0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_LIST)
        self.assertEqual(stderr.read(), '')

    def test_extract_list_invalid(self, stdout, stderr,
                                  write, make_entry_dirs, makedirs, _):
        extract(TEST_ARCHIVE_INVALID['log']['entries'], None)
        stdout.seek(0)
        stderr.seek(0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_INVALID_LIST)
        self.assertEqual(stderr.read(), '')
        self.assertEqual(makedirs.call_count, 0)
        self.assertEqual(write.call_count, 0)
        self.assertEqual(make_entry_dirs.call_count, 0)
        #extract(TEST_ARCHIVE_INVALID['log']['entries'], None, False, False)
