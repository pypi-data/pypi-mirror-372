"""
Utils for testing with local files.

Things like:

Making folder paths (and ensuring things about them):

>>> import os
>>> f = temp_dirpath()
>>> assert os.path.isdir(f)  # the directory exists (by default)
>>> assert dir_is_empty(f)  # ... and is empty (by default)

Making file paths (and ensuring things about them):

>>> filepath = temp_filepath()
>>> containing_dirpath = os.path.dirname(filepath)
>>> assert os.path.isdir(containing_dirpath)

"""
import tempfile
import shutil
import os
from typing import Optional
from pathlib import Path

file_sep = os.path.sep
DFLT_SUBPATH = 'tempdir'


def non_empty_tail(path):
    """The tail of the path, disregarding trailing slash if present.

    If / is the separator, this means:

    ```
        This/is/a/path -> path
        This/is/a/path/ -> path
    ```

    >>> path = os.path.join('This', 'is', 'a', 'path')
    >>> non_empty_tail(path)
    'path'
    >>> non_empty_tail(path + os.path.sep)
    'path'
    """
    if path.endswith(file_sep):
        path = path[:-1]
    return os.path.basename(path)


def empty_dir(dirpath):
    """Empty a directory of it's contents (and recreated the directory)
    Note: This means that the directory creation date will be now.
    """

    shutil.rmtree(dirpath)  # delete dir and all contents
    os.makedirs(dirpath)  # recreate the dir


def dir_is_empty(dirpath):
    """

    :param path:
    :return:

    >>> dirpath = temp_dirpath(ensure_is_empty=True)
    >>> dir_is_empty(dirpath)
    True
    """
    return not any(Path(dirpath).iterdir())


def temp_dirpath(
    subpath: str = DFLT_SUBPATH,
    ensure_exists: Optional[bool] = True,
    ensure_is_empty: Optional[bool] = True,
):
    """Get a fresh temporary folder path with assurances about existence and emptiness.

    :param subpath: The (relative) name of the folder.
    :param ensure_exists:
    :param ensure_is_empty:
    :return: A path (string) of a directory in a temporary


    >>> import os
    >>> from tested.local_files import temp_dirpath, non_empty_tail, dir_is_empty
    >>>
    >>> f = temp_dirpath()
    >>> assert non_empty_tail(f) == 'tempdir'
    >>> f = temp_dirpath('your_choice_of_a_dirname')
    >>> assert non_empty_tail(f) == 'your_choice_of_a_dirname'  # the directory name is indeed what you asked for
    >>> assert os.path.isdir(f)  # the directory exists!
    >>> assert dir_is_empty(f)  # ... and is empty
    >>> assert os.listdir(f) == []  # see!

    Let's write stuff in it:

    >>> import pathlib
    >>> p = pathlib.Path(f)
    >>> contents = 'hello world!'
    >>> assert p.joinpath('temp_file.txt').write_text(contents) == len(contents)
    >>> assert p.joinpath('temp_file.txt').read_text() == contents
    >>> assert os.listdir(f) == ['temp_file.txt']

    By default ``ensure_is_empty=True``, so you got an empty directory. But if you say False...

    >>> ff = temp_dirpath('your_choice_of_a_dirname', ensure_is_empty=False)
    >>> assert ff == f  # same path as before, but...
    >>> assert not dir_is_empty(f)
    >>> assert os.listdir(f) == ['temp_file.txt']
    >>>
    >>>
    >>> ff = temp_dirpath('your_choice_of_a_dirname', ensure_is_empty=True)
    >>> assert ff == f  # same path as before, but...
    >>> assert os.listdir(f) == []

    By default ``ensure_exists=True``, but the value could be:
    - None; meaning don't even check
    - False; meaning check, and if it exists, remove it

    >>> ff = temp_dirpath('your_choice_of_a_dirname', ensure_exists=None)
    >>> assert ff == f  # same path as before
    >>> assert os.path.isdir(ff)
    >>>
    >>> f = temp_dirpath('your_choice_of_a_dirname', ensure_exists=False)
    >>> assert not os.path.isdir(f)

    """
    dirpath = os.path.join(tempfile.gettempdir(), subpath)

    dir_exists = os.path.isdir(dirpath)
    if ensure_exists is True and not dir_exists:
        os.makedirs(dirpath)
    elif ensure_exists is False and dir_exists:
        os.removedirs(dirpath)
    if ensure_is_empty is not None:
        if ensure_is_empty and os.path.isdir(dirpath):
            shutil.rmtree(dirpath)  # delete dir and all contents
            os.makedirs(dirpath)  # recreate the dir
    return dirpath


def temp_filepath(
    filename='temp_file',
    subdir='temp_filepaths/',
    ensure_containing_dirs_exist=True,
    ensure_file_does_not_exist=False,
):
    """Make a temp filepath, ensuring (by default) that the containing directories exist,
    and (optionally) that the file doesn't exist either.

    >>> filepath = temp_filepath()
    >>> containing_dirpath = os.path.dirname(filepath)
    >>> assert os.path.isdir(containing_dirpath)
    >>> filepath = temp_filepath('my_own_name.txt')
    >>> assert os.path.basename(filepath) == 'my_own_name.txt'

    Let's write something in that file.

    >>> _ = Path(filepath).write_text('hello file!')  # but we can write in it
    >>> assert os.path.isfile(filepath)  # and now it exists
    >>> assert Path(filepath).read_text() == 'hello file!'  # here's what we wrote

    If you ask for that filepath again (a short time later), you'll get the same filepath,
    and the file will already exist. If you want to check if the file exists and delete it
    if it does, use ``ensure_file_does_not_exist==True``:

    >>> assert os.path.isfile(filepath)  # before
    >>> filepath2 = temp_filepath('my_own_name.txt', ensure_file_does_not_exist=True)
    >>> assert filepath2 == filepath
    >>> assert not os.path.isfile(filepath)  # after (it doesn't exist!)

    """
    dirpath = temp_dirpath(subdir, ensure_exists=True, ensure_is_empty=False)
    filepath = os.path.join(dirpath, filename)
    if ensure_containing_dirs_exist:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if ensure_file_does_not_exist and os.path.isfile(filepath):
        os.remove(filepath)
    return filepath
