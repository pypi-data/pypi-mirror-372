import os
import shutil
from unittest import TestCase
from pathlib import Path

from foliant.contrib.utils import prepend_file


def rel_name(path: str):
    return os.path.join(os.path.dirname(__file__), path)


TEST_DATA_PATH = Path(os.path.dirname(__file__)) / 'test_data' / 'utils'


class TestPrependFile(TestCase):
    def setUp(self):
        self.content = \
'''Prepended paragraph

Second prepended paragraph\n\n'''

        for source in TEST_DATA_PATH.glob('*.md'):
            if not str(source).startswith('exp'):
                cp = source.parent / f'cp_{source.name}'
                shutil.copyfile(source, cp)

    def tearDown(self):
        for source in TEST_DATA_PATH.glob('cp_*.md'):
            os.remove(source)

    def test_simple(self):
        filepath = TEST_DATA_PATH / 'cp_simple.md'
        with open(TEST_DATA_PATH / 'exp_simple.md') as f:
            expected = f.read()

        prepend_file(filepath, self.content)

        with open(TEST_DATA_PATH / 'cp_simple.md') as f:
            result = f.read()

        self.assertEqual(result, expected)

    def test_heading_before(self):
        filepath = TEST_DATA_PATH / 'cp_heading.md'
        with open(TEST_DATA_PATH / 'exp_heading_before.md') as f:
            expected = f.read()

        prepend_file(filepath, self.content, before_heading=True)

        with open(TEST_DATA_PATH / 'cp_heading.md') as f:
            result = f.read()

        self.assertEqual(result, expected)

    def test_heading_not_before(self):
        filepath = TEST_DATA_PATH / 'cp_heading.md'
        with open(TEST_DATA_PATH / 'exp_heading_not_before.md') as f:
            expected = f.read()

        prepend_file(filepath, self.content, before_heading=False)

        with open(TEST_DATA_PATH / 'cp_heading.md') as f:
            result = f.read()

        self.assertEqual(result, expected)

    def test_yfm_before(self):
        filepath = TEST_DATA_PATH / 'cp_yfm.md'
        with open(TEST_DATA_PATH / 'exp_yfm_before.md') as f:
            expected = f.read()

        prepend_file(filepath, self.content, before_yfm=True)

        with open(TEST_DATA_PATH / 'cp_yfm.md') as f:
            result = f.read()

        self.assertEqual(result, expected)

    def test_yfm_not_before(self):
        filepath = TEST_DATA_PATH / 'cp_yfm.md'
        with open(TEST_DATA_PATH / 'exp_yfm_not_before.md') as f:
            expected = f.read()

        prepend_file(filepath, self.content, before_yfm=False)

        with open(TEST_DATA_PATH / 'cp_yfm.md') as f:
            result = f.read()

        self.assertEqual(result, expected)
