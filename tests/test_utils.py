# pylint:disable=too-many-arguments

from unittest import TestCase
from unittest.mock import patch, mock_open, call

from io import BytesIO

import json

from har_extractor import (
    format_size, get_unused_name, write, get_out_dir,
    format_entry, get_entry_content, get_entry_path,
    get_entries, dirnames, move_files_to_dir, make_entry_dirs
)

from data import TEST_ARCHIVE


class TestUtils(TestCase):
    def test_format_size(self):
        self.assertEqual(format_size(-1), '<invalid size>')
        self.assertEqual(format_size(0), '0B')
        self.assertEqual(format_size(512), '512B')
        self.assertEqual(format_size(1024), '1K')
        self.assertEqual(format_size(2048), '2K')
        self.assertEqual(format_size(1536), '1.50K')
        self.assertEqual(format_size(4 * (1024 ** 2)), '4M')
        self.assertEqual(format_size(4 * (1024 ** 3) + 1), '4.00G')
        self.assertEqual(format_size(1024 ** 4), '1T')

    @staticmethod
    @patch('builtins.open', new_callable=mock_open)
    def test_write(open_mock):
        handle = open_mock()
        write('content', 'fname')
        open_mock.assert_called_with('fname', 'w')
        handle.write.assert_called_with('content')
        write(b'\x01\x02\x03', '')
        open_mock.assert_called_with('', 'wb')
        handle.write.assert_called_with(b'\x01\x02\x03')

    @patch('os.path.exists')
    def test_get_unused_name(self, exists):
        exists.side_effect = [False]
        self.assertEqual(get_unused_name('/dir/name.ext'), '/dir/name.ext')
        exists.side_effect = [True, False]
        self.assertEqual(get_unused_name('/dir/name.ext'), '/dir/name.1.ext')
        exists.side_effect = [True, True, True, False]
        self.assertEqual(get_unused_name('/dir/name.ext'), '/dir/name.3.ext')

    @patch('os.path.exists', return_value=False)
    @patch('os.path.isdir', return_value=True)
    def test_get_out_dir(self, isdir, exists):
        self.assertEqual(get_out_dir(None, 'default'), 'default')
        self.assertEqual(get_out_dir('', 'default'), 'default')
        self.assertEqual(exists.call_count, 0)
        self.assertEqual(isdir.call_count, 0)

        self.assertEqual(get_out_dir('path', 'default'), 'path')
        exists.assert_called_with('path')
        exists.reset_mock()
        self.assertEqual(isdir.call_count, 0)

        exists.return_value = True
        self.assertEqual(get_out_dir('path', 'default'), 'path/default')
        exists.assert_called_with('path')
        isdir.assert_called_with('path')

        with self.assertRaises(ValueError):
            isdir.return_value = False
            get_out_dir('path', 'default')

    @patch('har_extractor.format_size', return_value='<size>')
    def test_format_entry(self, format_size_mock):
        entry = {
            'request': {
                'method': 'METHOD',
                'url': '/url'
            },
            'response': {
                'status': 123,
                'statusText': 'Status Text',
                'content': {
                    'mimeType': 'mime/type',
                    'size': 321
                }
            }
        }
        formatted = 'METHOD /url -> 123 Status Text mime/type <size>'
        self.assertEqual(format_entry(entry), formatted)
        format_size_mock.assert_called_with(321)

    def test_format_entry_invalid(self):
        formatted = '<no method> <no url> -> <no status>' \
                    ' <no status text> <no mime type> <invalid size>'
        self.assertEqual(format_entry({}), formatted)

    def test_get_entry_path(self):
        test = lambda url: get_entry_path({'request': {'url': url}})
        self.assertEqual(test('http://127.0.0.1'), 'index.html')
        self.assertEqual(test('http://127.0.0.1/'), 'index.html')
        self.assertEqual(test('http://127.0.0.1/dir/'), 'dir')
        self.assertEqual(test('http://127.0.0.1/dir'), 'dir')
        self.assertEqual(test('http://127.0.0.1/dir/name'), 'name')
        self.assertEqual(test('http://127.0.0.1/dir/name/'), 'name')
        self.assertEqual(test('http://127.0.0.1/dir/name?arg'), 'name')
        self.assertEqual(test('http://127.0.0.1/dir/name/?arg'), 'name')
        with self.assertRaises(ValueError):
            get_entry_path({})

    def test_get_entry_path_subdirs(self):
        test = lambda url: get_entry_path({'request': {'url': url}}, True)
        self.assertEqual(test('http://127.0.0.1'), '127.0.0.1/index.html')
        self.assertEqual(test('http://127.0.0.1/'), '127.0.0.1/index.html')
        self.assertEqual(test('http://127.0.0.1/dir/'), '127.0.0.1/dir')
        self.assertEqual(test('http://127.0.0.1/dir'), '127.0.0.1/dir')
        self.assertEqual(test('http://127.0.0.1/dir/name'), '127.0.0.1/dir/name')
        self.assertEqual(test('http://127.0.0.1/dir/name/'), '127.0.0.1/dir/name')
        self.assertEqual(test('http://127.0.0.1/dir/name?arg'), '127.0.0.1/dir/name')
        self.assertEqual(test('http://127.0.0.1/dir/name/?arg'), '127.0.0.1/dir/name')

    def test_get_entry_content(self):
        entry = {
            'response': {
                'content': {
                }
            }
        }
        self.assertIsNone(get_entry_content({}))
        self.assertIsNone(get_entry_content(entry))

        entry['response']['content']['text'] = ''
        self.assertIsNone(get_entry_content(entry))

        entry['response']['content']['text'] = 'test'
        self.assertEqual(get_entry_content(entry), 'test')

        entry['response']['content']['text'] = 'dGVzdA=='
        entry['response']['content']['encoding'] = 'base64'
        self.assertEqual(get_entry_content(entry), b'test')

        with self.assertRaises(ValueError):
            entry['response']['content']['encoding'] = 'encoding'
            get_entry_content(entry)

    def test_dirnames(self):
        self.assertEqual(dirnames('/x/y/z/', '/x/'), ['/x/y'])
        self.assertEqual(dirnames('/x/y/z/', '/x'), ['/x/y'])
        self.assertEqual(dirnames('/x/y/z', '/x'), ['/x/y'])
        self.assertEqual(dirnames('/x/y/z/u/v', '/x/'),
                         ['/x/y/z/u', '/x/y/z', '/x/y'])

    @patch('shutil.move')
    @patch('os.path.exists', side_effect=[True, True, False])
    def test_move_files_to_dir(self, exists, move):
        move_files_to_dir('/a/b/c.d', '/a/b/c.3.d')
        exists.assert_has_calls([
            call('/a/b/c.%d.d' % i) for i in range(1, 4)
        ])
        self.assertEqual(exists.call_count, 3)
        move.assert_has_calls([
            call('/a/b/c.3.d', '/a/b/c.d/index.html'),
            call('/a/b/c.1.d', '/a/b/c.d/index.1.html'),
            call('/a/b/c.2.d', '/a/b/c.d/index.2.html')
        ])
        self.assertEqual(move.call_count, 3)

    @patch('har_extractor.move_files_to_dir')
    @patch('shutil.move')
    @patch('os.makedirs')
    @patch('os.mkdir')
    def test_make_entry_dirs(self, mkdir, mkdirs, move, move_files_to_dir_):
        make_entry_dirs('/root', '/root/dir/entry')
        mkdirs.assert_called_with('/root/dir', exist_ok=True)
        self.assertEqual(mkdirs.call_count, 1)
        self.assertEqual(mkdir.call_count, 0)
        self.assertEqual(move.call_count, 0)
        self.assertEqual(move_files_to_dir_.call_count, 0)

    @patch('har_extractor.get_unused_name', return_value='unused')
    @patch('har_extractor.move_files_to_dir')
    @patch('shutil.move')
    @patch('os.makedirs', side_effect=OSError)
    @patch('os.mkdir')
    @patch('os.path.exists', side_effect=[False, True, True])
    @patch('os.path.isdir', side_effect=[False, True])
    def test_make_entry_dirs_error(self, isdir, exists,
                                   mkdir, mkdirs, move,
                                   move_files_to_dir_, get_unused_name_):
        make_entry_dirs('/root/dir', '/root/dir/dir2/dir3/4/entry')

        mkdirs.assert_called_with('/root/dir/dir2/dir3/4', exist_ok=True)
        self.assertEqual(mkdirs.call_count, 1)

        exists.assert_has_calls([
            call('/root/dir/dir2'),
            call('/root/dir/dir2/dir3'),
            call('/root/dir/dir2/dir3/4')
        ])
        self.assertEqual(exists.call_count, 3)

        isdir.assert_has_calls([
            call('/root/dir/dir2/dir3'),
            call('/root/dir/dir2/dir3/4')
        ])
        self.assertEqual(isdir.call_count, 2)

        mkdir.assert_has_calls([
            call('/root/dir/dir2'),
            call('/root/dir/dir2/dir3')
        ])
        self.assertEqual(mkdir.call_count, 2)

        get_unused_name_.assert_called_with('/root/dir/dir2/dir3')
        self.assertEqual(get_unused_name_.call_count, 1)

        move.assert_called_with('/root/dir/dir2/dir3', 'unused')
        self.assertEqual(move.call_count, 1)

        move_files_to_dir_.assert_called_with('/root/dir/dir2/dir3', 'unused')
        self.assertEqual(move_files_to_dir_.call_count, 1)


class TestGetEntries(TestCase):
    def test_iterative(self):
        fp = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        items = get_entries(fp, True)
        self.assertNotIsInstance(items, list)
        self.assertEqual(list(items), TEST_ARCHIVE['log']['entries'])

    def test_not_iterative(self):
        fp = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        items = get_entries(fp, False)
        self.assertIsInstance(items, list)
        self.assertEqual(items, TEST_ARCHIVE['log']['entries'])

    @patch('sys.stdin')
    def test_stdin(self, stdin):
        stdin.buffer = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        items = get_entries(stdin, False)
        self.assertNotIsInstance(items, list)
        self.assertEqual(list(items), TEST_ARCHIVE['log']['entries'])

    @patch('har_extractor.ijson', new=None)
    def test_no_ijson(self):
        fp = BytesIO(json.dumps(TEST_ARCHIVE).encode('utf-8'))
        items = get_entries(fp, True)
        self.assertIsInstance(items, list)
        self.assertEqual(items, TEST_ARCHIVE['log']['entries'])
