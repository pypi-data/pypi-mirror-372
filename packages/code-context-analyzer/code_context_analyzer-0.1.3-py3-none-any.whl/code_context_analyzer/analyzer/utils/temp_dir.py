import shutil
import tempfile
from contextlib import contextmanager


@contextmanager
def temp_directory(suffix="", prefix="tmp", dir=None, auto_cleanup=True):
    """
    Creates a temporary directory and cleans it up on exit.

    :param suffix: Suffix for the temp dir name.
    :param prefix: Prefix for the temp dir name.
    :param dir: Parent directory (optional).
    :param auto_cleanup: If False, keeps the directory after use.
    """
    path = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield path
    finally:
        if auto_cleanup:
            shutil.rmtree(path, ignore_errors=True)
