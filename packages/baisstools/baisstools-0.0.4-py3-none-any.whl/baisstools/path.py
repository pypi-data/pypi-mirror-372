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
  * File   : path.py
  * Created: 2025/08/25 13:57:24 GMT+1
  * Updated: 2025/08/26 20:32:44 GMT+1
</license>
'''

import os

class Path:

    """
    A utility class for handling file paths.
    This class provides static methods for joining path components
    in a platform-independent manner.
    Example:
        result = Path.join("folder", "subfolder", "file.txt")
        print(result)  # Output: "folder/subfolder/file.txt" on Unix-like systems
                       #         "folder\\subfolder\\file.txt" on Windows systems
    Raises:
        ValueError: If an invalid name is provided.
    """

    @staticmethod
    def join(*args):
        """
        Join one or more path components.
        Args:
            *args: One or more path components to join.
        Returns:
            str: The joined path.
        Raises:
            ValueError: If an invalid name is provided.
            ValueError: If no path components are provided.
        Example:
            args  : ["folder", "subfolder", "file.txt"]
            result: "folder/subfolder/file.txt"
        """
        if not args:
            raise ValueError("At least one path component must be provided")
        fullpath: str = ""
        for name in args:
            if not name:
                continue
            name = str(name).replace("\\", "/")
            if ( "://" in name ) and ( "/" in name.split("://")[0] ):
                raise ValueError(f"Ivalid name: {name}")
            if fullpath:
                fullpath += "/"
            fullpath += name
        fullpath = fullpath.replace("://", ":\\\\")
        while ("//" in fullpath):
            fullpath = fullpath.replace("//", "/")
        fullpath = fullpath.replace(":\\\\", "://")
        return fullpath.replace("/", os.sep)
