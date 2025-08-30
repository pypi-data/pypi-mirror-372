from concurrent.futures import ThreadPoolExecutor
from os import makedirs, listdir
from os.path import join
from pathlib import Path
from shutil import move
from typing import Union


def prepend_file(
    filepath: Union[str, Path],
    content: str,
    before_yfm: bool = False,
    before_heading: bool = True
):
    '''
    Insert `content` at the beginning of the file `filepath`.

    :param filepath: path to file which needs to be prepended.
    :param content: content to be inserted.
    :before_yfm: if file starts with YAML Front Matter, insert content before it
    :before_heading: if file starts with a heading, insert content before it
    '''
    with open(filepath, encoding='utf8') as f:
        source = f.read()

    start = 0

    if not before_yfm and source.startswith('---\n'):
        yfm_end = source.find('\n---\n', 1)
        start = yfm_end + len('\n---\n') if yfm_end != -1 else 0
        # add line break for not to break the heading
        content = '\n' + content
    if not before_heading and source.startswith('#'):
        start = source.find('\n', 1) + 1
        if start == 0:
            start = len(source)
        # add line break for not to break the heading
        content = '\n' + content

    processed_content = source[:start] + content + source[start:]

    with open(filepath, 'w', encoding='utf8') as f:
        f.write(processed_content)


def move_files_threadpool(src: Path, dest: Path, n_workers: int = 64):
    """Move files from one directory to another with ThreadPoolExecutor

    :param src: path to source directory
    :param dest: path to the destination directory
    :param n_workers: number of workers in ThreadPool
    """
    def move_files(src_paths, dest_dir):
        for src_path in src_paths:
            move(src_path, dest_dir)

    makedirs(dest, exist_ok=True)
    files = [join(src, name) for name in listdir(src)]
    chunksize = round(len(files) / n_workers)
    chunksize = 1 if chunksize == 0 else chunksize
    with ThreadPoolExecutor(n_workers) as exe:
        for i in range(0, len(files), chunksize):
            filenames = files[i:(i + chunksize)]
            _ = exe.submit(move_files, filenames, dest)
