import re
import traceback
import threading

from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Union

from foliant.preprocessors.base import BasePreprocessor
from foliant.utils import output


def run_in_thread(fn):
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run


def allow_fail(msg: str = 'Failed to process tag. Skipping.') -> Callable:
    """
    If function func fails for some reason, warning is issued but preprocessor
    doesn't terminate. In this case the tag remains unchanged.
    Decorator issues a warning to user with BasePreprocessorExt _warning method.
    If first positional argument is a match object, it is passed as context.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs) -> Optional[str]:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                if args and isinstance(args[0], re.Match):
                    self._warning(f'{msg} {e}',
                                  context=self.get_tag_context(args[0]),
                                  error=e)
                    return args[0].group(0)
                else:
                    self._warning(f'{msg} {e}', error=e)
                    return None
        return wrapper
    return decorator


class BasePreprocessorExt(BasePreprocessor):
    """Extension of BasePreprocessor with useful helper methods"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_filename = ''
        self.current_pos = 0
        self.current_func = None
        self.buffer = {}

    @staticmethod
    def get_tag_context(match: re.Match,
                        limit: int = 100,
                        full_tag: bool = False) -> str:
        '''
        Get context of the tag match object.

        Returns a string with <limit> symbols before match, the match string and
        <limit> symbols after match.

        If full_tag == False, matched string is limited too: first <limit>/2
        symbols of match and last <limit>/2 symbols of match.
        '''

        source = match.string
        start = max(0, match.start() - limit)  # index of context start
        end = min(len(source), match.end() + limit)  # index of context end
        span = match.span()  # indeces of match (start, end)
        result = '...' if start != 0 else ''  # add ... at beginning if cropped
        if span[1] - span[0] > limit and not full_tag:  # if tag contents longer than limit
            bp1 = match.start() + limit // 2
            bp2 = match.end() - limit // 2
            result += f'{source[start:bp1]} <...> {source[bp2:end]}'
        else:
            result += source[start:end]
        if end != len(source):  # add ... at the end if cropped
            result += '...'
        return result

    def _warning(self,
                 msg: str,
                 context: str = '',
                 error: Exception = None,
                 debug_msg: str = '') -> None:
        '''
        Log warning and print to user.

        If debug mode — print also context (if sepcified) and error (if specified).

        :param msg:       — message which should be logged;
        :param context:   — tag context got with get_tag_context function. If
                            specified — will be logged. If debug = True it
                            will also go to STDOUT.
        :param error:     — exception which was caught before warning. If specified —
                            error traceback whill be added to log (and debug output) message.
        :param debug_msg: — message to additionally print to stdout in debug mode.
        '''

        output_message = ''
        if self.current_filename:
            output_message += f'[{self.current_filename}] '
        output_message += msg + '\n'
        log_message = output_message
        if debug_msg:
            log_message += f'{debug_msg}\n'
        if context:
            log_message += f'Context:\n---\n{context}\n---\n'
        if error:
            tb_str = traceback.format_exception(etype=type(error),
                                                value=error,
                                                tb=error.__traceback__)
            log_message += '\n'.join(tb_str)
        if self.debug:
            output_message = log_message
        output(f'WARNING: {output_message}', self.quiet)
        self.logger.warning(log_message)

    def pos_injector(self, block: re.Match) -> str:
        """
        Save offset of match object to self.current_pos and run
        self.current_func with this match object.
        """

        self.current_pos = block.start()
        return self.current_func(block)

    def save_file(self, path: Union[str, Path], content: str) -> None:
        with open(path, 'w', encoding='utf8') as f:
            f.write(content)

    def _process_tags_for_all_files(self,
                                    func: Callable,
                                    log_msg: str = 'Applying preprocessor',
                                    buffer: bool = False) -> None:
        '''
        Apply function func to all Markdown-files in the working dir

        :param func: function that should be applied to each found tag. Function
                     must accept 1 parameter: regex match object (found tag)
        :param log_msg: message text which will be logged at the beginning
        :param buffer: if True, processed text of each file will be buffered and
                       at the end all files will be saved at once.
        '''
        self.logger.info(log_msg)

        @run_in_thread
        def process(self, markdown_file_path):
            self.current_filepath = Path(markdown_file_path)
            self.current_filename = str(self.current_filepath.
                                        relative_to(self.working_dir))

            with open(markdown_file_path,
                      encoding='utf8') as markdown_file:
                content = markdown_file.read()

            self.current_func = func
            self.current_pos = 0
            processed_content = self.pattern.sub(self.pos_injector, content)

            if isinstance(processed_content, str):
                if buffer:
                    self.buffer[markdown_file_path] = processed_content
                else:
                    self.save_file(markdown_file_path, processed_content)
        for markdown_file_path in self.working_dir.rglob('*.md'):
            process(self, markdown_file_path)
        self.current_filename = ''

        for path, content in self.buffer.items():
            self.save_file(path, content)
        self.buffer = {}

    def _process_all_files(self,
                           func: Callable,
                           log_msg: str = 'Applying preprocessor',
                           buffer: bool = False) -> None:
        '''Apply function func to all Markdown-files in the working dir'''
        self.logger.info(log_msg)

        @run_in_thread
        def process(markdown_file_path):
            self.current_filepath = Path(markdown_file_path)
            self.current_filename = str(self.current_filepath.
                                        relative_to(self.working_dir))

            with open(markdown_file_path,
                      encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = func(content)
            if isinstance(processed_content, str):
                if buffer:
                    self.buffer[markdown_file_path] = processed_content
                else:
                    self.save_file(markdown_file_path, processed_content)
        for markdown_file_path in self.working_dir.rglob('*.md'):
            process(markdown_file_path)
        self.current_filename = ''

        for path, content in self.buffer.items():
            self.save_file(path, content)
        self.buffer = {}
