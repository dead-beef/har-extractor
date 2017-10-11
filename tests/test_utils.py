from unittest import TestCase
from unittest.mock import patch, mock_open

from har_extractor import (
    format_size, get_unused_name, write, get_out_dir,
    format_entry, get_entry_content, get_entry_path
)


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
