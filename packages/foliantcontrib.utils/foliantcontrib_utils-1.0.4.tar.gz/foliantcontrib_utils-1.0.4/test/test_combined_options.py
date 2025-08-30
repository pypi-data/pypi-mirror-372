from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from foliant.contrib.combined_options import CombinedOptions
from foliant.contrib.combined_options import Options
from foliant.contrib.combined_options import RequiredParamsMissingError
from foliant.contrib.combined_options import ValidationError
from foliant.contrib.combined_options import boolean_convertor
from foliant.contrib.combined_options import path_convertor
from foliant.contrib.combined_options import rel_path_convertor
from foliant.contrib.combined_options import val_type
from foliant.contrib.combined_options import validate_exists
from foliant.contrib.combined_options import validate_in


class TestOptions(TestCase):
    def test_no_processing(self):
        original = {'key': 'val', 'int': 12, 'bool': True}
        options = Options(original)

        self.assertEqual(options.options, original)

    def test_defaults(self):
        original = {'key': 'val', 'int': 12, 'bool': True, 'overridden': 42}
        defaults = {'defaultkey': 'defaultvalue', 'overridden': 0}

        expected = {'key': 'val', 'int': 12, 'bool': True, 'overridden': 42, 'defaultkey': 'defaultvalue'}
        options = Options(original, defaults=defaults)
        self.assertEqual(options.defaults, defaults)
        self.assertEqual(options.options, expected)

    def test_required_flat(self):
        required = ['req1', 'req2']
        set1 = {'key': 'val', 'req1': 1, 'req2': False}

        options = Options(set1, required=required)

        set2 = {'key': 'val', 'req2': False}
        with self.assertRaises(RequiredParamsMissingError):
            options = Options(set2, required=required)

    def test_required_combinations(self):
        required = [['req1', 'req2'], ['req21', 'req22'], ['req']]
        set1 = {'key': 'val', 'req1': 1, 'req2': False}

        options = Options(set1, required=required)

        set2 = {'key': 'val', 'req2': False}
        with self.assertRaises(RequiredParamsMissingError):
            options = Options(set2, required=required)

        set3 = {'key': 'val', 'req21': False, 'req22': ''}
        options = Options(set3, required=required)

        set4 = {'key': 'val', 'req': '1'}
        options = Options(set4, required=required)

    def test_validate(self):
        mock_validator1 = Mock(return_value=None)
        mock_validator2 = Mock(return_value=None)
        original = {'key': 'val', 'int': 12, 'bool': True}
        options = Options(
            original,
            validators={'key': mock_validator1, 'bool': mock_validator2}
        )

        self.assertEqual(options['key'], 'val')
        self.assertEqual(options['int'], 12)
        self.assertEqual(options['bool'], True)

        mock_validator1.assert_called_once_with('val')
        mock_validator2.assert_called_once_with(True)

    def test_validation_error(self):
        mock_validator = Mock(side_effect=[ValidationError])
        original = {'key': 'val', 'int': 12, 'bool': True}
        with self.assertRaises(ValidationError):
            options = Options(
                original,
                validators={'int': mock_validator}
            )

    def test_convert(self):
        mock_convertor = Mock(return_value='converted')
        original = {'key': 'val', 'int': 12, 'bool': True}
        options = Options(
            original,
            convertors={'int': mock_convertor}
        )

        self.assertEqual(options['int'], 'converted')
        mock_convertor.assert_called_once_with(12)

    def test_is_default(self):
        original = {'key': 'val', 'def1': 12, 'def3': 'overridden'}
        defaults = {'def1': 12, 'def2': 'Default', 'def3': 'Default'}

        options = Options(original, defaults=defaults)
        self.assertTrue(options.is_default('def1'))
        self.assertTrue(options.is_default('def2'))
        self.assertFalse(options.is_default('def3'))
        self.assertFalse(options.is_default('key'))

class TestCombinedOptions(TestCase):
    def test_combine(self):
        options1 = {'key1': 'val1', 'key2': 'val2'}
        options2 = {'key3': 'val3', 'key4': 'val4'}
        coptions = CombinedOptions({'o1': options1, 'o2': options2})

        expected = {**options1, **options2}
        self.assertEqual(coptions.options, expected)

    def test_combine_override(self):
        options1 = {'key1': 'val1', 'key2': 'val2'}
        options2 = {'key2': 'val21', 'key4': 'val4'}
        coptions = CombinedOptions({'o1': options1, 'o2': options2})

        expected = {**options2, **options1}
        self.assertEqual(coptions.options, expected)

    def test_single_priority(self):
        options1 = {'key1': 'val1', 'key2': 'val2'}
        options2 = {'key2': 'val21', 'key4': 'val4'}
        coptions = CombinedOptions(
            {'o1': options1, 'o2': options2},
            priority='o2'
        )

        expected = {**options1, **options2}
        self.assertEqual(coptions.options, expected)

    def test_priority_list(self):
        options1 = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
        options2 = {'key2': 'val22', 'key3': 'val32', 'key4': 'val42'}
        options3 = {'key2': 'val23', 'key4': 'val43'}
        expected = {'key1': 'val1', 'key2': 'val23', 'key3': 'val32', 'key4': 'val43'}
        coptions = CombinedOptions(
            {'o1': options1, 'o2': options2, 'o3': options3},
            priority=['o3', 'o2', 'o1']
        )

        self.assertEqual(coptions.options, expected)

        coptions = CombinedOptions(
            {'o1': options1, 'o2': options2, 'o3': options3},
            priority=['o3', 'o2']
        )

        self.assertEqual(coptions.options, expected)

    def test_set_priority(self):
        options1 = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
        options2 = {'key2': 'val22', 'key3': 'val32', 'key4': 'val42'}
        options3 = {'key2': 'val23', 'key4': 'val43'}
        expected1 = {'key1': 'val1', 'key2': 'val23', 'key3': 'val32', 'key4': 'val43'}
        coptions = CombinedOptions(
            {'o1': options1, 'o2': options2, 'o3': options3},
            priority=['o3', 'o2', 'o1']
        )

        self.assertEqual(coptions.options, expected1)

        coptions.priority = ['o2', 'o3', 'o1']
        expected2 = {'key1': 'val1', 'key2': 'val22', 'key3': 'val32', 'key4': 'val42'}

        self.assertEqual(coptions.options, expected2)

        coptions.priority = 'o1'
        expected2 = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3', 'key4': 'val42'}

        self.assertEqual(coptions.options, expected2)


class TestValidateIn(TestCase):
    def test_validation_pass(self):
        vals = [1, 3]
        supported = [1, 2, 3]
        validator = validate_in(supported)
        for val in vals:
            validator(val)

    def test_validation_fail(self):
        val = 'Unsupported'
        supported = [1, 2, 3]
        validator = validate_in(supported)
        with self.assertRaises(ValidationError):
            validator(val)

    def test_custom_error_message(self):
        val = 'Unsupported'
        supported = [1, 2, 3]
        validator = validate_in(supported, msg='Custom message')
        with self.assertRaises(ValidationError) as caught:
            validator(val)

        self.assertEqual(str(caught.exception), 'Custom message')


class TestValType(TestCase):
    def test_validation_pass_single(self):
        val = 'string'
        supported = str
        validator = val_type(supported)
        validator(val)

    def test_validation_pass_multiple(self):
        vals = ['string', 12, True]
        supported = [str, int]
        validator = val_type(supported)
        for val in vals:
            validator(val)

    def test_validation_pass_none(self):
        val = None
        supported = None
        validator = val_type(supported)
        validator(val)

    def test_validation_fail_single(self):
        val = 1
        supported = str
        validator = val_type(supported)
        with self.assertRaises(ValidationError):
            validator(val)

    def test_validation_fail_multiple(self):
        val = 1.12
        supported = (str, int)
        validator = val_type(supported)
        with self.assertRaises(ValidationError):
            validator(val)


class TestValidateExists(TestCase):
    def test_validation_pass_str(self):
        val = 'README.md'
        validate_exists(val)

    def test_validation_pass_path(self):
        val = Path('README.md')
        validate_exists(val)

    def test_validation_fail(self):
        val = Path('wrong.exe')
        with self.assertRaises(ValidationError):
            validate_exists(val)


class TestPathConvertor(TestCase):
    def test_str(self):
        converted = path_convertor('file.txt')
        self.assertEqual(converted, Path('file.txt'))

    def test_path(self):
        converted = path_convertor(Path('file.txt'))
        self.assertEqual(converted, Path('file.txt'))


class TestBooleanConvertor(TestCase):
    def test_true(self):
        true_vals = ['1', 'y', 'yes', 'true', True]
        for val in true_vals:
            self.assertTrue(boolean_convertor(val))

    def test_false(self):
        false_vals = ['0', 'n', 'no', 'false', False]
        for val in false_vals:
            self.assertFalse(boolean_convertor(val))

    def test_other(self):
        self.assertFalse(boolean_convertor(0))
        self.assertFalse(boolean_convertor(0.0))
        self.assertFalse(boolean_convertor([]))
        self.assertTrue(boolean_convertor(12))
        self.assertTrue(boolean_convertor(12.12))
        self.assertTrue(boolean_convertor(Path()))
        self.assertTrue(boolean_convertor('random string'))


class TestRelPathConvertor(TestCase):
    def test_str(self):
        parent = 'parent/path'
        convertor = rel_path_convertor(parent)

        self.assertEqual(convertor('rel/path'), Path('parent/path/rel/path'))

    def test_path(self):
        parent = Path('parent/path')
        convertor = rel_path_convertor(parent)

        self.assertEqual(convertor('rel/path'), Path('parent/path/rel/path'))
