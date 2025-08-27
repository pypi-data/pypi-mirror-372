'''
<license>
  * Copyright (C) 2024-2025 https://tbeninnovation.com.
  *
  * https://tbeninnovation.com
  * https://github.com/tbeninnovation-mobileapp/baisstools
  *
  * Permission is hereby granted, free of charge, to any person obtaining
  * a copy of this software and associated documentation files (the
  * "Software"), to deal in the Software without restriction, including
  * without limitation the rights to use, copy, modify, merge, publish,
  * distribute, sublicense, and/or sell copies of the Software, and to
  * permit persons to whom the Software is furnished to do so, subject to
  * the following conditions:
  *
  * The above copyright notice and this permission notice shall be
  * included in all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * File   : __init__.py
  * Created: 2025/07/28 11:37:57 GMT+1
  * Updated: 2025/07/28 11:41:57 GMT+1
</license>
'''

import os
import re
import sys
import hashlib
from typing import Optional, List, Any

__author__ = "Tbeninnovation"
__github__ = "https://github.com/tbeninnovation-mobileapp/baisstools"

def insert_syspath(
        caller   : str,
        matcher  : Optional[List[str]] = None,
        sys      : Optional[Any]       = sys,
        match_all: bool                = False
    ) -> List[str]:
    """
    Inserts the directory of the given caller file into sys.path.
    :param caller: The caller file path.
    :param bases: Optional list of base directories to check for existence.
    If not provided, defaults to checking for ".git" and "README.md".
    """
    if not matcher:
        matcher = [".git", "README.md"]
    path  = os.path.abspath(caller)
    paths = []
    while ( path and (path != os.path.dirname(path)) ):
        matched = 0
        for base in matcher:
            try   : basenames = os.listdir(path)
            except: continue
            for basename in basenames:
                if (basename == base) or re.match(base, basename):
                    matched += 1
        found = False
        if match_all and (matched >= len(matcher)):
            found = True
        elif (not match_all) and (matched > 0):
            found = True
        if found:
            paths.append(path)
        path = os.path.dirname(path)
    paths = sorted(list(set(paths)))
    for path in paths:
        sys.path.insert(0, path)
    return paths

class platform:

    @staticmethod
    def is_windows() -> bool:
        """Check if the platform is Windows."""
        return sys.platform.startswith('win')

    @staticmethod
    def is_linux() -> bool:
        """Check if the platform is Linux."""
        return sys.platform.startswith('linux')

    @staticmethod
    def is_macos() -> bool:
        """Check if the platform is macOS."""
        return sys.platform.startswith('darwin')
