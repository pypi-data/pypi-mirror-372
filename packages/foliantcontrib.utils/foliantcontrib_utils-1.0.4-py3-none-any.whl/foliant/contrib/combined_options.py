import yaml

from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Collection
from typing import Sequence
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

class ValidationError(Exception):
    '''Error for validations when validation is failed'''
    pass


class RequiredParamsMissingError(Exception):
    '''Error for required params checking when requirement is not satisfied'''
    pass


class Options:
    '''
    Helper class which imitates dictionary with options but has some
    handy methods like option validation and conversion.
    '''

    def __init__(self,
                 options: dict,
                 defaults: Optional[Dict[str, Any]] = None,
                 convertors: Optional[Dict[str, Callable]] = None,
                 validators: Optional[Dict[str, Callable]] = None,
                 required: Optional[Union[List[str], List[List[str]]]] = None):
        '''
        options (dict)    — options dictionary,
        defaults (dict)   — dictionary with default values,
        convertors (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option
                            before storing in class.
        validators (dict) — dictionary with key = option name, value = function
                            which will be applied to the value of this option.
                            Function should check for validity and raise
                            ValidationError if the check fails.
        required (list)   - list of required params or list of tuples with
                            combinations of required params.
        '''
        self.defaults = dict(defaults) if defaults else {}
        self._options = {**self.defaults, **options}
        self._validators = dict(validators) if validators else {}
        self._convertors = dict(convertors) if convertors else {}
        self._required = list(required) if required else []
        self.validate()
        self._convert()

    @property
    def options(self) -> dict:
        '''Actual options dictionary'''
        return self._options

    def validate(self) -> None:
        '''
        Validate all options with supplied validators and check for required
        params.
        Raises ValidationError if any of validation checks fails.
        Raises RequiredParamsMissingError if required params are not supplied.
        '''
        def _check_required(combination: Collection) -> bool:
            for param in combination:
                if param not in self.options:
                    return False
            return True

        for key in self._validators:
            if key in self.options:
                try:
                    self._validators[key](self.options[key])
                except ValidationError as e:
                    raise ValidationError(f'Error in option "{key}": {e}')
        if self._required:
            if isinstance(self._required[0], str):
                if not _check_required(self._required):
                    raise RequiredParamsMissingError(
                        f'Not all required params are supplied: {self._required}')
            else:  # several combinations of required params are possible
                check_result = any(_check_required(comb) for comb in self._required)
                if not check_result:
                    required_combs = "\nor:\n".\
                        join(str(comb).strip('()[]') for comb in self._required)
                    raise RequiredParamsMissingError(
                        f'Not all required params are supplied. '
                        f'Required parameter combinations are:\n{required_combs}')

    def _convert(self) -> None:
        '''
        Convert all options with supplied convertors and replace values in
        options dictionary in place.
        '''
        if not self._convertors:
            return

        for key in self._convertors:
            if key in self.options:
                convertor = self._convertors[key]
                self.options[key] = convertor(self.options[key])

    def is_default(self, option: str) -> bool:
        '''return True if option value is same as default'''
        if option in self.defaults:
            return self.options[option] == self.defaults[option]
        return False

    def __str__(self):
        return f'<{self.__class__.__name__}{self.options}>'

    def __getitem__(self, ind: str) -> Any:
        return self.options[ind]

    def __setitem__(self, ind: str, val: Any):
        self.options[ind] = val
        self.validate()

    def __contains__(self, ind: str) -> bool:
        return ind in self.options

    def __iter__(self):
        return iter(self.options.keys())

    def __bool__(self) -> bool:
        return bool(self.options)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.options.get(key, default)

    def keys(self):
        return self.options.keys()

    def items(self):
        return self.options.items()

    def values(self):
        return self.options.values()


class CombinedOptions(Options):
    '''
    Helper class which combines several Options objects into one. If options
    interlap the one to be returned is defined by 'priority' or by the order
    defined.

    Apart from that it is a normal Options object.
    '''

    def __init__(self,
                 options: dict,
                 priority: Optional[Union[str, Sequence[str]]] = None,
                 defaults: Optional[Dict[str, Any]] = None,
                 convertors: Optional[Dict[str, Callable]] = None,
                 validators: Optional[Dict[str, Callable]] = None,
                 required: Optional[Union[List[str], List[List[str]]]] = None):
        '''
        :param options:  dictionary where key = priority,
                         value = option dictionary.
        :param priority: initial priority  or list of prioritites.

        other parameters are same as in parent
        '''
        self.defaults = dict(defaults) if defaults else {}
        self._options_dict = dict(options) if options else {}
        self._validators = dict(validators) if validators else {}
        self._convertors = dict(convertors) if convertors else {}
        self._required = list(required) if required else []

        if isinstance(priority, (list, tuple)):
            self.priority = list(priority)
        else:
            self.priority = priority  # type: ignore

    @property
    def priority(self) -> Union[str, Sequence[str]]:
        '''returns current priority'''
        return self._priority

    @priority.setter
    def priority(self, val: Union[str, Sequence[str], None]) -> None:
        '''sets new priority and updates active options dictionary'''
        if isinstance(val, (list, tuple)):
            priority_list = val
        elif isinstance(val, str):
            priority_list = [val]
        else:
            priority_list = []

        for p in priority_list:
            if p not in self._options_dict:
                raise ValueError('Priority must be one of: '
                                 f'{", ".join(self._options_dict.keys())}. '
                                 f'Value received: {p}')
        self._priority = priority_list
        self.set_options()

    def set_options(self) -> None:
        '''
        Sets new active options dict with options combined from all options
        dicts with priority according to self.priority.
        '''

        self._options = deepcopy(self.defaults)

        for key in reversed(list(self._options_dict)):
            if key not in self.priority:
                self._options.update(self._options_dict[key])

        for priority in reversed(self.priority):
            self._options.update(self._options_dict[priority])

        self.validate()
        self._convert()


def validate_in(supported: Collection, msg: Optional[str] = None) -> Callable:
    '''
    Simple validator factory. Resulting function checks if option value
    is contained in supported collection.

    `supported` may be any collection-like object with __contains__ method.
    Raises ValueError otherwise.

    msg is message given to the ValiadtionError.

    Returns a validator function.'''

    DEFAULT_MSG = 'Unsupported option value {val}. Should be one '\
                  'of: {supported}'

    def validate(val: Any) -> None:
        if val not in supported:
            raise ValidationError(message.format(val=val, supported=', '.join(str(s) for s in supported)))

    if not hasattr(supported, '__contains__'):
        raise ValueError('`supported` should be a collection')

    message = msg if msg else DEFAULT_MSG

    return validate


NoneType = type(None)


def val_type(supported: Union[List[Union[type, NoneType]], type]) -> Callable:
    '''
    Validator factory for validating param type.

    `supported` may be a type to check, None or a list (tuple) of possible types.
    '''

    MSG = 'Unsupported option value {val}. Must be of type {supported}'

    def validate(val: Any) -> None:
        for type_ in types:
            if type_ is None:
                if val is None:
                    return
            elif isinstance(val, type_):
                return
        raise ValidationError(MSG.format(val=val, supported=', '.join(str(t) for t in types)))
    if supported is None:
        types = [None]
    elif isinstance(supported, type):
        types = [supported]
    elif isinstance(supported, Collection):
        types = supported  # type: ignore
    else:
        raise ValueError('`supported` should be a type, None or a collection of types')
    return validate


def validate_exists(val: Union[str, Path]) -> None:
    '''Validator that checks if path specified in val exists'''
    MSG = 'Path {val} does not exist.'
    if val and not Path(val).exists():
        raise ValidationError(MSG.format(val=val))


def path_convertor(option: Union[str, Path]) -> Path:
    '''convert string to Path'''
    if isinstance(option, str):
        return Path(yaml.load(option, yaml.Loader))
    elif isinstance(option, Path):
        return option


def yaml_to_dict_convertor(option):
    '''
    DEPRECATED. Foliant does it automatically since 1.0.9
    convert yaml string or dict to dict
    '''

    if type(option) is dict:
        return option
    elif type(option) is str:
        return yaml.load(option, yaml.Loader)


def boolean_convertor(option: Any) -> bool:
    '''
    Convert option to bool if necessary.

    Accepts True\False, 'tRuE' \ 'falSE', 1\0, Y \ n, yes \ no

    Other types are validated as bool(object)
    '''
    str_dict = {
        '1': True,
        '0': False,
        'y': True,
        'n': False,
        'yes': True,
        'no': False,
        'true': True,
        'false': False
    }
    if type(option) == bool:
        return option
    elif type(option) == str:
        return str_dict.get(option.lower().strip(), True)
    else:
        return bool(option)


def rel_path_convertor(parent_path: Union[str, Path]) -> Callable:
    '''
    Convertor factory which makes option path relative to parent_path supplied
    during the convertor initialization.
    '''

    def _convertor(option: Union[str, Path]) -> Any:
        if not option:
            return option
        else:
            return Path(parent_path) / option

    return _convertor
