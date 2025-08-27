
import os
from typing import Dict

def findpath(
    path         : str,
    base_dir     : str            = None,
    result       : dict[str, str] = None,
    ignore_hidden: bool = True,
    include_dirs : bool = False
    ) -> Dict[str, Dict]:
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    if not path.strip():
        raise ValueError("Path cannot be empty after stripping whitespace")
    if result is None:
        result = {}
    if not os.path.exists(path):
        return result
    if os.path.isdir(path):
        if include_dirs:
            result[path] = path
    else:
        result[path] = path
    if not base_dir:
        base_dir = path
    try   : files = os.listdir(path)
    except: files = []
    if not files:
        return (result)
    for basename in files:
        if ignore_hidden and basename.startswith('.'):
            # ignore hidden files and directories
            continue
        filename = os.path.realpath(os.path.join(path, basename))
        if filename != os.path.join(path, basename):
            # ignore symlinks
            continue
        findpath(
            path     = filename,
            base_dir = base_dir,
            result   = result
        )
        if (not include_dirs) and os.path.isdir(filename):
            # ignore directories if include_dirs is False
            continue
        result[filename] = filename[len(path):].strip(os.sep)
    return result
