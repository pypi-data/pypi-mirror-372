# TODO: check all files in the path, if it statisfies the norm
import os
import sys
import logging
sys.path.insert(0,
os.path.dirname(os.path.dirname(
os.path.abspath(__file__))))
from baisstools.files import findpath

logger = logging.getLogger(__name__)

class BaissNormalizationError(Exception):
    """Exception raised for errors in the normalization process."""
    pass

class BaissNormalizer:
    """Base class for all normalization classes."""
    def __init__(self,):
        pass

    def normfile(self, filename: str):
        """
        Normalize a single file.
        """
        return True

    def normdir(self, path: str):
        """
        Normalize all files in a directory.
        Args:
            path (str): Path to the directory to normalize.
        Returns:
            bool: True if all files were normalized successfully, False otherwise.
        """
        for filename in findpath(path):
            if not self.normfile(filename):
                return False
        return True

if __name__ == "__main__":
    BaissNormalizer().normdir("/goinfre/ahabachi/codes/")
