from unittest import TestCase
from unittest.mock import patch, call
from io import StringIO, BytesIO

import os
import json

from har_extractor import do_extract, extract

from data import (
    TEST_ARCHIVE, TEST_ARCHIVE_LIST, TEST_ARCHIVE_CONTENTS,
    TEST_ARCHIVE_VERBOSE, TEST_ARCHIVE_INVALID_VERBOSE,
    TEST_ARCHIVE_INVALID, TEST_ARCHIVE_INVALID_LIST
)

@patch('os.path.exists', return_value=False)
@patch('os.makedirs')
@patch('har_extractor.write')
@patch('sys.stderr', new_callable=StringIO)
@patch('sys.stdout', new_callable=StringIO)
class TestDoExtract(TestCase):
    def test_do_extract(self, stdout, stderr, write, makedirs, _):
        do_extract(TEST_ARCHIVE['log']['entries'], 'dir/')
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_has_calls([
            call(content, os.path.join('dir', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(stdout.read(), '')
        self.assertEqual(stderr.read(), '')

    def test_do_extract_verbose(self, stdout, stderr, write, makedirs, _):
        do_extract(TEST_ARCHIVE['log']['entries'], 'dir/', True)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_has_calls([
            call(content, os.path.join('dir', fname))
            for content, fname in TEST_ARCHIVE_CONTENTS
        ])
        self.assertEqual(stdout.read(), TEST_ARCHIVE_VERBOSE)
        self.assertEqual(stderr.read(), '')

    def test_do_extract_invalid(self, stdout, stderr, write, makedirs, _):
        write.side_effect = IOError
        do_extract(TEST_ARCHIVE_INVALID['log']['entries'], 'dir/', True, False)
        stdout.seek(0)
        stderr.seek(0)
        makedirs.assert_called_with('dir/', exist_ok=True)
        write.assert_called_with('404', 'dir/404')
        self.assertEqual(stdout.read(), TEST_ARCHIVE_INVALID_VERBOSE)
        self.assertNotEqual(stderr.read(), '')

    def test_do_extract_list(self, stdout, stderr, write, makedirs, _):
        do_extract(TEST_ARCHIVE['log']['entries'], None)
        stdout.seek(0)
        stderr.seek(0)
        self.assertEqual(makedirs.call_count, 0)
        self.assertEqual(write.call_count, 0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_LIST)
        self.assertEqual(stderr.read(), '')

    def test_do_extract_list_invalid(self, stdout, stderr, write, makedirs, _):
        with self.assertRaises(ValueError):
            do_extract(TEST_ARCHIVE_INVALID['log']['entries'], None)
        stdout.seek(0)
        stderr.seek(0)
        self.assertEqual(stdout.read(), '')
        self.assertEqual(stderr.read(), '')

        do_extract(TEST_ARCHIVE_INVALID['log']['entries'], None, False, False)
        stdout.seek(0)
        stderr.seek(0)
        self.assertEqual(stdout.read(), TEST_ARCHIVE_INVALID_LIST)
        self.assertNotEqual(stderr.read(), '')
        self.assertEqual(makedirs.call_count, 0)
        self.assertEqual(write.call_count, 0)

@patch('har_extractor.do_extract')
class TestExtract(TestCase):
    def test_extract(self, do_extract_mock):
        fp = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        extract(fp)
        self.assertEqual(do_extract_mock.call_count, 1)
        args = do_extract_mock.call_args[0]
        self.assertEqual(args[1:], (None, False, True))
        self.assertEqual(list(args[0]), TEST_ARCHIVE['log']['entries'])

    @staticmethod
    @patch('har_extractor.ijson', new=None)
    def test_extract_no_ijson(_, do_extract_mock):
        fp = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        extract(fp, 'dir/', True, False)
        do_extract_mock.assert_called_with(
            TEST_ARCHIVE['log']['entries'], 'dir/', True, False
        )
