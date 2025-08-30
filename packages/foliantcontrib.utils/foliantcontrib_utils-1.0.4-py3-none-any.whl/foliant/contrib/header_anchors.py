import re
import unicodedata

from hashlib import sha1
from urllib.parse import quote
from typing import Dict

FALLBACK_BACKEND = 'pandoc'
FLAT_BACKENDS = ['pandoc', 'slate', 'aglio', 'mdtopdf']


class IDGenerator:
    '''
    This class generates IDs but counts the number of times they were called.
    Before returning the generated ID it passes it through the make_unique
    function to generate the unique ID.
    '''

    def __init__(self, backend: str):
        self.registry: Dict[str, int] = {}
        self.backend = backend

    def generate(self, heading: str) -> str:
        '''
        Generate the unique ID for the `heading`.

        :param heading: heading to be converted to ID.

        :returns: unique ID for the heading.
        '''
        id_ = to_id(heading, self.backend)
        self.registry[id_] = self.registry.setdefault(id_, 0) + 1
        return make_unique(id_, self.registry[id_], self.backend)

    def reset(self) -> None:
        '''
        Reset all ID count to 0.
        '''
        self.registry = {}


def is_flat(backend: str) -> bool:
    '''Determine whether backend is flat or not.'''
    return backend in FLAT_BACKENDS


def to_id(input_: str, backend: str) -> str:
    '''
    Convert a heading title to proper id for backend. If backend not found,
    fallback backend is used.

    :param input_: heading title
    :param backend: name of the backend

    :returns: converted id
    '''
    BACKEND_MAP = {
        'pandoc': to_id_pandoc,
        'mdtopdf': to_id_mdtopdf,
        'aglio': to_id_aglio,
        'mkdocs': to_id_mkdocs,
        'slate': to_id_slate,
        'confluence': to_id_confluence,
        'no_transform': to_id_no_transform,
    }
    if backend not in BACKEND_MAP:
        backend = FALLBACK_BACKEND
    return BACKEND_MAP[backend](input_)


def make_unique(input_: str, occurrence: int, backend: str) -> str:
    '''
    Make an id, converted from the title, unique according to backend rules.
    If backend not found, fallback backend is used.

    :param input_: potentially dublicate header id
    :param occurrence: number of occurrence of the header with this title
    :param backend: name of the backend

    :returns: unique id
    '''
    BACKEND_MAP = {
        'pandoc': make_unique_pandoc,
        'mdtopdf': make_unique_pandoc,
        'aglio': make_unique_pandoc,
        'mkdocs': make_unique_mkdocs,
        'slate': make_unique_slate,
        'confluence': make_unique_confluence,
    }
    if backend not in BACKEND_MAP:
        backend = FALLBACK_BACKEND
    return BACKEND_MAP[backend](input_, occurrence)


def to_id_pandoc(input_: str) -> str:
    """
    Quote from docs:

    The default algorithm used to derive the identifier from the heading text is:

        * Remove all formatting, links, etc.
        * Remove all footnotes.
        * Remove all non-alphanumeric characters, except underscores, hyphens, and periods.
        * Replace all spaces and newlines with hyphens.
        * Convert all alphabetic characters to lowercase.
        * Remove everything up to the first letter (identifiers may not begin with a number or punctuation mark).
        * If nothing is left after this, use the identifier section.
    """
    def accept(char: str) -> bool:
        if char in ALPHA:
            return True
        elif char.isalpha():
            return True
        elif char.isdigit():
            return True
        return False
    ALPHA = '_-.'
    result = ''
    source = input_.lower()
    accum = False

    # strip everything before first letter
    while source and not source[0].isalpha():
        source = source[1:]

    for char in source:
        if accept(char):
            if accum:
                accum = False
                result += f'-{char.lower()}'
            else:
                result += char.lower()
        elif char.isspace():
            accum = True
        else:
            pass

    if not result:
        return 'section'
    else:
        return result


def to_id_mdtopdf(input_: str) -> str:
    def accept(char: str) -> bool:
        return char in ALPHA or char.isalpha() or char.isdigit()
    ALPHA = '_-'
    result = ''
    source = input_.lower().strip()

    result = re.sub(r'\s', '-', result)

    for char in source:
        if accept(char):
            result += char
        elif char.isspace():
            result += '-'
        else:  # remove all other symbols
            pass

    return result


def to_id_aglio(input_: str) -> str:
    repl_dict = {
        "'": '’',
        '...': '…',
        '---': '—',
        '--': '–',
    }
    result = 'header-' + input_.lower().strip()

    for source, repl in repl_dict.items():
        result = result.replace(source, repl)
    result = re.sub(r'[\s"/:<=>\\]', '-', result)
    # result = re.sub(r'-+', '-', result)
    result = re.sub(r',+', ',', result)
    return result


def to_id_confluence(input_: str) -> str:
    repl_dict = {
        "'": '’',
        '...': '…',
        '---': '—',
        '--': '–',
    }
    result = re.sub(r'\s', '', input_)

    for source, repl in repl_dict.items():
        result = result.replace(source, repl)
    return result


def slugify(value: str, separator: str) -> str:
    """
    Slugify a string, to make it URL friendly.

    This function is copied from `markdown` python package
    (https://github.com/Python-Markdown/markdown/).

    Mkdocs uses it by default to generate heading IDs
    """
    normalized = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    shaved = re.sub(r'[^\w\s-]', '', normalized.decode('ascii')).strip().lower()
    return re.sub(r'[%s\s]+' % separator, separator, shaved)


RE_TAGS = re.compile(r'</?[^>]*>', re.UNICODE)
NO_CASED = 0
UNICODE_CASED = 1
RE_ASCII_LETTERS = re.compile(r'[A-Z]', re.UNICODE)
RE_INVALID_SLUG_CHAR = re.compile(r'[^\w\- ]', re.UNICODE)
RE_SEP = re.compile(r' ', re.UNICODE)


def uslugify(text: str,
             sep:str,
             cased: int = NO_CASED,
             percent_encode: bool = False):
    """
    Unicode slugify (`utf-8`).

    This function is copied from `pymdownx.slugs` python package
    (https://github.com/facelessuser/pymdown-extensions/).
    """

    # Normalize, Strip html tags, strip leading and trailing whitespace, and lower
    slug = RE_TAGS.sub('', unicodedata.normalize('NFC', text)).strip()

    if cased == NO_CASED:
        slug = slug.lower()
    elif cased == UNICODE_CASED:

        def lower(m):
            """Lowercase character."""
            return m.group(0).lower()

        slug = RE_ASCII_LETTERS.sub(lower, slug)

    # Remove non word characters, non spaces, and non dashes, and convert spaces to dashes.
    slug = RE_SEP.sub(sep, RE_INVALID_SLUG_CHAR.sub('', slug))

    return quote(slug.encode('utf-8')) if percent_encode else slug


def to_id_mkdocs(input_: str) -> str:
    return uslugify(input_, '-')


def parameterize_slate(string_to_clean: str, sep: str = '-') -> str:
    """
    Port of Rails `parameterize` function by Vinicius Quaiato.
    """
    HTML_ESCAPE = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&39;",
        "<": "&lt;",
        ">": "&gt;"
    }

    parameterized_string = unicodedata.normalize('NFKD', string_to_clean).encode('ASCII', 'ignore').decode()

    for char, repl in HTML_ESCAPE.items():
        parameterized_string = parameterized_string.replace(char, repl)

    parameterized_string = re.sub("[^a-zA-Z0-9_]+", sep, parameterized_string)

    if sep is not None and sep != '':
        parameterized_string = parameterized_string.strip(sep)
    return parameterized_string.lower()


def to_id_slate(input_: str) -> str:
    # removing tags
    source = re.sub(r'<[/\w_:=" ]*>', '', input_)
    source = parameterize_slate(source)
    return source if source else sha1(input_.encode('utf-8')).hexdigest()[:10]


def to_id_no_transform(input_: str) -> str:
    return input_


def make_unique_mkdocs(input_: str, occurrence: int = 1) -> str:
    if input_ == '':
        occurrence += 1
    if occurrence == 1:
        return input_
    else:
        return input_ + '_' + str(occurrence - 1)


def make_unique_pandoc(input_: str, occurrence: int = 1) -> str:
    if occurrence == 1:
        return input_
    else:
        return input_ + '-' + str(occurrence - 1)


def make_unique_confluence(input_: str, occurrence: int = 1) -> str:
    if occurrence == 1:
        return input_
    else:
        return input_ + '.' + str(occurrence - 1)


def make_unique_slate(input_: str, occurrence: int = 1) -> str:
    if occurrence == 1:
        return input_
    else:
        return input_ + f'-{occurrence}'
