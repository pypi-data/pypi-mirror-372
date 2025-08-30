from unittest import TestCase

from foliant.contrib.header_anchors import make_unique_confluence
from foliant.contrib.header_anchors import make_unique_mkdocs
from foliant.contrib.header_anchors import make_unique_pandoc
from foliant.contrib.header_anchors import make_unique_slate
from foliant.contrib.header_anchors import to_id_aglio
from foliant.contrib.header_anchors import to_id_confluence
from foliant.contrib.header_anchors import to_id_mdtopdf
from foliant.contrib.header_anchors import to_id_pandoc
from foliant.contrib.header_anchors import to_id_slate


class TestToIdPandoc(TestCase):
    def test_strip_everything_before_first_letter(self):
        self.assertEqual(to_id_pandoc('qwerty'), 'qwerty')
        self.assertEqual(to_id_pandoc('___qwerty'), 'qwerty')
        self.assertEqual(to_id_pandoc('127qwerty'), 'qwerty')
        self.assertEqual(to_id_pandoc('$%^&*(qwerty'), 'qwerty')

    def test_accept_alphanumeric_underscore_hyphen_dot(self):
        self.assertEqual(to_id_pandoc('q1werty'), 'q1werty')
        self.assertEqual(to_id_pandoc('q12-werty'), 'q12-werty')
        self.assertEqual(to_id_pandoc('q12-w_erty'), 'q12-w_erty')
        self.assertEqual(to_id_pandoc('q12-w_e.rty'), 'q12-w_e.rty')

    def test_remove_unsupported(self):
        self.assertEqual(to_id_pandoc('qw%^&erty'), 'qwerty')
        self.assertEqual(to_id_pandoc('qw^er$t#y'), 'qwerty')

    def test_lower(self):
        self.assertEqual(to_id_pandoc('QwErTy'), 'qwerty')
        self.assertEqual(to_id_pandoc('QWERTY'), 'qwerty')

    def test_space_to_hyphen(self):
        self.assertEqual(to_id_pandoc('q w e r t y'), 'q-w-e-r-t-y')
        self.assertEqual(to_id_pandoc('qwe       rty'), 'qwe-rty')

    def test_all_removed(self):
        self.assertEqual(to_id_pandoc('&*#@'), 'section')


class TestMdToPdf(TestCase):
    def test_lower(self):
        self.assertEqual(to_id_mdtopdf('QwErTy'), 'qwerty')
        self.assertEqual(to_id_mdtopdf('QWERTY'), 'qwerty')

    def test_accept_alphanumeric_underscore_hyphen(self):
        self.assertEqual(to_id_mdtopdf('q1werty'), 'q1werty')
        self.assertEqual(to_id_mdtopdf('q12-werty'), 'q12-werty')
        self.assertEqual(to_id_mdtopdf('q12-w_erty'), 'q12-w_erty')

    def test_remove_unsupported(self):
        self.assertEqual(to_id_mdtopdf('qw%^&erty'), 'qwerty')
        self.assertEqual(to_id_mdtopdf('qw^er$t#y'), 'qwerty')

    def test_space_to_hyphen(self):
        self.assertEqual(to_id_mdtopdf('q w e r t y'), 'q-w-e-r-t-y')
        self.assertEqual(to_id_mdtopdf('qwe       rty'), 'qwe-------rty')


class TestAglio(TestCase):
    def test_lower(self):
        self.assertEqual(to_id_aglio('QwErTy'), 'header-qwerty')
        self.assertEqual(to_id_aglio('QWERTY'), 'header-qwerty')

    def test_special_symbols_to_hyphens(self):
        self.assertEqual(to_id_aglio('q w"e/r:t<y'), 'header-q-w-e-r-t-y')
        self.assertEqual(to_id_aglio('q=w>e\\rty'), 'header-q-w-e-rty')

    def test_dashes_and_commas_collapse(self):
        self.assertEqual(to_id_aglio('q-w-e-r-t-y'), 'header-q-w-e-r-t-y')
        self.assertEqual(to_id_aglio('q,w,e,r,t,y'), 'header-q,w,e,r,t,y')
        self.assertEqual(to_id_aglio('q,,w,,,e,,,,r,,,,,t,,,,,,y'), 'header-q,w,e,r,t,y')

    def test_beautify_replace(self):
        self.assertEqual(to_id_aglio("q'w...e---r--ty"), 'header-q’w…e—r–ty')


class TestToIdConfluence(TestCase):
    def test_remove_spaces(self):
        self.assertEqual(to_id_confluence('q w e r t y'), 'qwerty')
        self.assertEqual(to_id_confluence('qwe       rty'), 'qwerty')

    def test_beautify_replace(self):
        self.assertEqual(to_id_confluence("q'w...e---r--ty"), 'q’w…e—r–ty')


# uslugify tested here:
# https://github.com/facelessuser/pymdown-extensions/blob/main/tests/test_extensions/test_slugs.py

class TestToIdSlate(TestCase):
    def test_special_symbols_to_hyphens(self):
        self.assertEqual(to_id_slate('q w_e%%$r#()t+y17'), 'q-w_e-r-t-y17')

    def test_html_escape(self):
        self.assertEqual(to_id_slate('''q&w"e'r>t<y'''), 'q-amp-w-quot-e-39-r-gt-t-lt-y')

    def test_strip_sep(self):
        self.assertEqual(to_id_slate('%%%-++qwerty###@'), 'qwerty')

    def test_remove_tags(self):
        self.assertEqual(to_id_slate('<a href="asd">qwerty</a> very <b>BIG</b> change'), 'qwerty-very-big-change')

    def test_hash_for_empty_string(self):
        self.assertEqual(to_id_slate('%# -!!@'), 'bcb3049620')


class TestMakeUniqueMkdocs(TestCase):
    def test_first_occurence_no_change(self):
        self.assertEqual(make_unique_mkdocs('qwerty', 1), 'qwerty')

    def test_empty_string(self):
        self.assertEqual(make_unique_mkdocs('', 1), '_1')
        self.assertEqual(make_unique_mkdocs('', 7), '_7')

    def test_second_plus_occurence(self):
        self.assertEqual(make_unique_mkdocs('qwerty', 2), 'qwerty_1')
        self.assertEqual(make_unique_mkdocs('qwerty', 7), 'qwerty_6')


class TestMakeUniquePandoc(TestCase):
    def test_first_occurence_no_change(self):
        self.assertEqual(make_unique_pandoc('qwerty', 1), 'qwerty')

    def test_second_plus_occurence(self):
        self.assertEqual(make_unique_pandoc('qwerty', 2), 'qwerty-1')
        self.assertEqual(make_unique_pandoc('qwerty', 7), 'qwerty-6')


class TestMakeUniqueConfluence(TestCase):
    def test_first_occurence_no_change(self):
        self.assertEqual(make_unique_confluence('qwerty', 1), 'qwerty')

    def test_second_plus_occurence(self):
        self.assertEqual(make_unique_confluence('qwerty', 2), 'qwerty.1')
        self.assertEqual(make_unique_confluence('qwerty', 7), 'qwerty.6')


class TestMakeUniqueSlate(TestCase):
    def test_first_occurence_no_change(self):
        self.assertEqual(make_unique_slate('qwerty', 1), 'qwerty')

    def test_second_plus_occurence(self):
        self.assertEqual(make_unique_slate('qwerty', 2), 'qwerty-2')
        self.assertEqual(make_unique_slate('qwerty', 7), 'qwerty-7')
