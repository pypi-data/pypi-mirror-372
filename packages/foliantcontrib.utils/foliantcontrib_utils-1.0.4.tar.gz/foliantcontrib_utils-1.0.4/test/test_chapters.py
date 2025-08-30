import os
from unittest import TestCase
from pathlib import Path

from foliant.contrib.chapters import Chapters
from foliant.contrib.chapters import ChapterNotFoundError
from foliant.contrib.chapters import flatten_seq

from .utils import chcwd


class TestFlattenSeq(TestCase):
    def test_plain_list(self):
        seq = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md']
        self.assertEqual(flatten_seq(seq), seq)

    def test_nested_lists(self):
        seq = [
            'ch1.md',
            'ch2.md',
            [
                'ch3.md',
                'ch4.md'
            ],
            'ch5.md',
            [
                ['ch6.md', 'ch7.md'],
            ],
            [
                'ch8.md',
                [
                    ['ch9.md'],
                    [
                        'ch10.md',
                        ['ch11.md']
                    ],
                    'ch12.md',
                ],
                'ch13.md'
            ]
        ]

        expected = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md', 'ch7.md', 'ch8.md', 'ch9.md', 'ch10.md', 'ch11.md', 'ch12.md', 'ch13.md']

        self.assertEqual(flatten_seq(seq), expected)

    def test_dict(self):
        seq = {'Title1': 'ch1.md', 'Title2': 'ch2.md', 'Title3': 'ch3.md'}
        expected = ['ch1.md', 'ch2.md', 'ch3.md']
        self.assertEqual(flatten_seq(seq), expected)

    def test_nested_lists_and_dicts(self):
        seq = [
            'ch1.md',
            {'Title2': 'ch2.md'},
            ['ch3.md', 'ch4.md'],
            [
                {
                    'Title5': 'ch5.md',
                    'Title6': [
                        'ch6.md',
                        'ch7.md'
                    ]
                }
            ],
            {'Title8': 'ch8.md'},
        ]

        expected = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', 'ch6.md', 'ch7.md', 'ch8.md']

        self.assertEqual(flatten_seq(seq), expected)


class TestChapters(TestCase):
    test_data_path = 'test/test_data/chapters'

    def test_from_config(self):
        chapters = ['ch1.md', 'ch2.md', {'Title3': 'ch3.md'}, {'Title4': ['ch4.md', 'ch5.md']}]
        config = {'chapters': chapters, 'tmp_dir': '__folianttmp__', 'src_dir': 'src'}
        with chcwd(self.test_data_path):
            chapters_obj = Chapters.from_config(config)

        expected_flat = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md']
        expected_workingdir = (Path(self.test_data_path) / '__folianttmp__').resolve()
        expected_srcdir = (Path(self.test_data_path) / 'src').resolve()

        self.assertEqual(chapters_obj.chapters, chapters)
        self.assertEqual(chapters_obj.flat, expected_flat)
        self.assertEqual(chapters_obj.working_dir, expected_workingdir)
        self.assertEqual(chapters_obj.src_dir, expected_srcdir)

    def test_chapters_setter(self):
        chapters = ['ch1.md', 'ch2.md', {'Title3': 'ch3.md'}, {'Title4': ['ch4.md', 'ch5.md']}]
        expected_flat = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md']
        chapters_obj = Chapters({})

        chapters_obj.chapters = chapters

        self.assertEqual(chapters_obj.chapters, chapters)
        self.assertEqual(chapters_obj.flat, expected_flat)

    def test_get_chapter_by_path(self):
        chapters = ['ch1.md', 'ch2.md', 'ch3.md']
        with chcwd(self.test_data_path):
            chapters_obj = Chapters(chapters,
                                    working_dir='__folianttmp__',
                                    src_dir='src')
            ch1 = 'src/ch1.md'
            ch1_full = os.path.join(os.getcwd(), 'src/ch1.md')
            ch2_path = Path('src/ch2.md').resolve()
            ch3 = 'src/ch3.md'
            ch4 = 'src/ch4.md'

            self.assertEqual(chapters_obj.get_chapter_by_path(ch1), 'ch1.md')
            self.assertEqual(chapters_obj.get_chapter_by_path(ch1_full), 'ch1.md')
            self.assertEqual(chapters_obj.get_chapter_by_path(ch2_path), 'ch2.md')

            # present only in src:
            self.assertEqual(chapters_obj.get_chapter_by_path(ch3), 'ch3.md')

            with self.assertRaises(ChapterNotFoundError):
                chapters_obj.get_chapter_by_path(ch4)

    def test_paths(self):
        chapters = ['ch1.md', 'ch2.md', {'Title3': 'ch3.md'}, {'Title4': ['ch4.md', 'ch5.md']}]
        flat_chapters = ['ch1.md', 'ch2.md', 'ch3.md', 'ch4.md', 'ch5.md', ]
        with chcwd(self.test_data_path):
            src_path = Path('src').resolve()
            workdir_path = Path('__folianttmp__').resolve()
            src_paths = [src_path / p for p in flat_chapters]
            workdir_paths = [workdir_path / p for p in flat_chapters]

            chapters_obj = Chapters(chapters,
                                    working_dir='__folianttmp__',
                                    src_dir='src')

            self.assertEqual(
                list(chapters_obj.paths(chapters_obj.src_dir)),
                src_paths
            )
            self.assertEqual(
                list(chapters_obj.paths(chapters_obj.working_dir)),
                workdir_paths
            )

    def test_get_chapter_title(self):
        chapters = [
            'ch1.md',
            'ch2.md',
            {'Title3': 'ch3.md'},
            {'Title4': ['ch4.md', 'ch5.md']},
            {
                'Section Title': [
                    'ch6.md',
                    {'Title7': 'ch7.md'}
                ]
            }
        ]

        chapters_obj = Chapters(chapters)
        self.assertEqual(chapters_obj.get_chapter_title('ch3.md'), 'Title3')
        self.assertEqual(chapters_obj.get_chapter_title('ch6.md'), '')
        self.assertEqual(chapters_obj.get_chapter_title('ch7.md'), 'Title7')
        with self.assertRaises(ChapterNotFoundError):
            chapters_obj.get_chapter_title('nonexistant.md')
