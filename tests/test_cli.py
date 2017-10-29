# pylint:disable=too-many-arguments

from unittest import TestCase
from unittest.mock import patch, mock_open
from io import StringIO

from har_extractor import main


@patch('sys.stderr', new_callable=StringIO)
@patch('shutil.rmtree')
@patch('builtins.open', new_callable=mock_open)
@patch('har_extractor.get_out_dir', return_value='outdir')
@patch('har_extractor.get_entries', return_value='entries')
@patch('har_extractor.extract')
class TestMain(TestCase):
    @patch('sys.exit')
    def test_error(self, exit_, extract, *_):
        self.assertEqual(main(['-v']), 1)
        exit_.assert_called_with(2)
        self.assertEqual(extract.call_count, 0)

    def test_default(self, extract, get_entries,
                     get_out_dir, open_, rmtree, stderr):
        handle = open_()
        self.assertEqual(main(['file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        self.assertEqual(rmtree.call_count, 0)
        get_out_dir.assert_called_with(None, 'file.d')
        open_.assert_called_with('file', 'rb')
        get_entries.assert_called_with(handle, False)
        extract.assert_called_with('entries', 'outdir', False, False, False)

    def test_list(self, extract, get_entries,
                  get_out_dir, open_, rmtree, stderr):
        handle = open_()
        self.assertEqual(main(['-l', 'file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        self.assertEqual(rmtree.call_count, 0)
        self.assertEqual(get_out_dir.call_count, 0)
        open_.assert_called_with('file', 'rb')
        get_entries.assert_called_with(handle, False)
        extract.assert_called_with('entries', None, False, False, False)

    def test_args(self, extract, get_entries,
                  get_out_dir, open_, rmtree, stderr):
        handle = open_()
        self.assertEqual(main(['-v', '-i', '-o', 'dir', 'file']), 0)
        stderr.seek(0)
        self.assertEqual(stderr.read(), '')
        self.assertEqual(rmtree.call_count, 0)
        get_out_dir.assert_called_with('dir', 'file.d')
        open_.assert_called_with('file', 'rb')
        get_entries.assert_called_with(handle, True)
        extract.assert_called_with('entries', 'outdir', False, True, False)

    def test_getdir_error(self, extract, get_entries,
                          get_out_dir, open_, rmtree, stderr):
        get_out_dir.side_effect = ValueError('value error')
        self.assertEqual(main(['-v', 'file']), 1)
        stderr.seek(0)
        self.assertEqual(stderr.read(), 'value error\n')
        self.assertEqual(rmtree.call_count, 0)
        get_out_dir.assert_called_with(None, 'file.d')
        self.assertEqual(open_.call_count, 0)
        self.assertEqual(get_entries.call_count, 0)
        self.assertEqual(extract.call_count, 0)

    def test_extract_error(self, extract, get_entries,
                           get_out_dir, open_, rmtree, stderr):
        handle = open_()
        extract.side_effect = IOError('io error')
        self.assertEqual(main(['file']), 1)
        stderr.seek(0)
        self.assertEqual(stderr.read(), 'io error\n')
        self.assertEqual(rmtree.call_count, 0)
        get_out_dir.assert_called_with(None, 'file.d')
        open_.assert_called_with('file', 'rb')
        get_entries.assert_called_with(handle, False)
        extract.assert_called_with('entries', 'outdir', False, False, False)

    def test_extract_error_strict(self, extract, get_entries,
                                  get_out_dir, open_, rmtree, stderr):
        handle = open_()
        extract.side_effect = IOError('io error')
        self.assertEqual(main(['-s', 'file']), 1)
        stderr.seek(0)
        self.assertEqual(stderr.read(), 'io error\n')
        rmtree.assert_called_with('outdir')
        get_out_dir.assert_called_with(None, 'file.d')
        open_.assert_called_with('file', 'rb')
        get_entries.assert_called_with(handle, False)
        extract.assert_called_with('entries', 'outdir', False, False, True)
