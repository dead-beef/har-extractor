from unittest import TestCase
from unittest.mock import patch, mock_open
from io import StringIO

from har_extractor import main


@patch('sys.stderr', new_callable=StringIO)
@patch('builtins.open', new_callable=mock_open)
@patch('har_extractor.get_out_dir', return_value='outdir')
@patch('har_extractor.extract')
class TestMain(TestCase):
    @patch('sys.exit')
    def test_error(self, exit_, extract, *_):
        self.assertEqual(main(['-v']), 1)
        exit_.assert_called_with(2)
        self.assertEqual(extract.call_count, 0)

    def test_default(self, extract, get_out_dir, open_, stderr):
        handle = open_()
        self.assertEqual(main(['file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        get_out_dir.assert_called_with(None, 'file.d')
        open_.assert_called_with('file', 'rb')
        extract.assert_called_with(handle, 'outdir', False, False)

    def test_list(self, extract, get_out_dir, open_, stderr):
        handle = open_()
        self.assertEqual(main(['-l', 'file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        self.assertEqual(get_out_dir.call_count, 0)
        open_.assert_called_with('file', 'rb')
        extract.assert_called_with(handle, None, False, False)

    def test_args(self, extract, get_out_dir, open_, stderr):
        handle = open_()
        self.assertEqual(main(['-v', '-o', 'dir', 'file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        get_out_dir.assert_called_with('dir', 'file.d')
        open_.assert_called_with('file', 'rb')
        extract.assert_called_with(handle, 'outdir', True, False)

    def test_getdir_error(self, extract, get_out_dir, open_, stderr):
        get_out_dir.side_effect = ValueError('value error')
        self.assertEqual(main(['-v', 'file']), 1)
        stderr.seek(0)
        self.assertEqual(stderr.read(), 'value error\n')
        get_out_dir.assert_called_with(None, 'file.d')
        self.assertEqual(open_.call_count, 0)
        self.assertEqual(extract.call_count, 0)

    def test_extract_error(self, extract, get_out_dir, open_, stderr):
        handle = open_()
        extract.side_effect = IOError('io error')
        self.assertEqual(main(['file']), 1)
        stderr.seek(0)
        self.assertEqual(stderr.read(), 'io error\n')
        get_out_dir.assert_called_with(None, 'file.d')
        open_.assert_called_with('file', 'rb')
        extract.assert_called_with(handle, 'outdir', False, False)
