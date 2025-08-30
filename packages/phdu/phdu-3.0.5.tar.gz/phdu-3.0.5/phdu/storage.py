"""
Move/delete data. Access memory usage of current process
"""
import os
from pathlib import Path
import re
import psutil

parent_dir =  'data'

def current_process_memory_usage():
    """
    Returns the memory used by the current process in GB.
    """
    current_process = psutil.Process()
    return current_process.memory_info().rss / 2**30

def move_files(keyword, folder=None, parent_dir=parent_dir, verbose=1):
    """
    Moves all files in the parent directory starting with a keyword to a folder.

    Attributes:
        - keyword: keyword to look for during file matching-
        - folder: Created folder to store all files matched by the keyword
        - parend_dir: Initial directory in which the files are contained.
    """
    folder = folder if folder is not None else keyword
    Path(os.path.join(parent_dir, folder)).mkdir(exist_ok=True, parents=True)
    processed = 0
    for path in os.listdir(parent_dir):
        if path == folder:
            continue
        else:
            if re.findall(key, path):
                os.rename(os.path.join(parent_dir, path),
                          os.path.join(parent_dir, folder, path))
                processed += 1
    if verbose:
        print(f"Moved {processed} files from '{parent_dir}' to '{folder}' subdirectory.")
    return

def delete_files_by_ext(parent_dir, extensions, verbose=1):
    """
    Removes files in parent_dir with extensions starting by (or being equal to) a certain character.
    """
    deleted = 0
    for path in os.listdir(parent_dir):
        for extension in extensions:
            if os.path.splitext(path)[1].startswith(extension):
                os.remove(os.path.join(parent_dir, path))
                deleted += 1
    if verbose:
        print(f"Deleted {deleted} files.")
    return

def delete_stdin_files(parent_dir="nuredduna_programmes/stdin_files", verbose=1, completed_only=True, key="Done", key_search="any"):
    """
    Removes nuredduna standard input (stdin) files, of the form python.exxxx (s. error) and python.oxxxx (s. output).
    key_search:  sets how the key is looked in a file line:    - any:   key in any position
                                                               - start.
                                                               - end.
    """
    if completed_only:
        if key_search == "any":
            find_key = lambda l: key in l
        elif key_search == "start":
            find_key = lambda l: l.startswith(key)
        elif key_search == 'end':
            find_key = lambda l: l.endswith(key)
        else:
            raise ValueError(f"key_search '{key_search}' not valid. Available: 'any', 'start', 'end'.")

        deleted_programs = 0
        deleted_files = 0
        for f in os.listdir(parent_dir):
            if f.endswith("out"):
                ff = os.path.join(parent_dir, f)
                if any(find_key(l) for l in open(ff).readlines()):
                    os.remove(ff)
                    deleted_programs += 1
                    deleted_files += 1
                    ff_err = "{}.err".format(os.path.splitext(ff)[0])
                    if Path(ff_err).exists():
                        os.remove(ff_err)
                        deleted_files += 1
        if verbose:
            print(f"Deleted {deleted_files} files ({deleted_programs} completed programmes).")
    else:
        delete_files_by_ext(parent_dir, [".e", ".o"], verbose)
    return

def empty_trash(verbose=1):
    home = os.path.expanduser("~")
    binDir = f"{home}/.local/share/Trash"
    deleted = 0
    for root, dirs, files in os.walk(binDir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
            deleted += 1
    if verbose:
        print(f"Deleted {deleted} files.")
    return


def delete_files_by_key(root, keys):
    """Delete all files in root and following subdirectories containing at least one of the keys."""
    # tree walk starting in directory 'data':
    if isinstance(keys, str):
        keys = [keys]
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        # delete files containing 'DBS' or 'control'
        for filename in filenames:
            if any(key in filename for key in keys):
                os.remove(os.path.join(dirpath, filename))
                count += 1
    print(f"Deleted {count} files containing at least one of {keys}")
    return
